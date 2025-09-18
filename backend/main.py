# portfolio-react-app/backend/main.py
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# import whisper  # Commented out as Whisper integration is paused for MVP (client-side STT)
# import torch    # Commented out as Whisper integration is paused for MVP
import os
from typing import List, Dict
# Import for document processing endpoint (if needed)
# from document_processor import initialize_collection, process_pdf
import chromadb # Import chromadb directly
import ollama # Import the ollama client library

app = FastAPI()

# CORS setup (Keep this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. Initialize ChromaDB Collection at Startup (Better Practice) ---
# Global variable to hold the collection reference
chroma_collection = None # <-- Corrected variable name

@app.on_event("startup")
async def startup_event():
    """Initialize resources when the app starts."""
    global chroma_collection # <-- Use the correct global variable name
    try:
        # Use the path specified in your document_processor.py
        chroma_client = chromadb.PersistentClient(path="./.chroma_db")
        # Get the existing collection (it should already be created by document_processor.py)
        chroma_collection = chroma_client.get_collection(name="portfolio_docs")
        print("ChromaDB collection 'portfolio_docs' initialized successfully.")
    except Exception as e:
        print(f"Error initializing ChromaDB collection: {e}")
        # Depending on your strategy, you might want to raise an exception here
        # or handle it gracefully (e.g., disable chat functionality)
        chroma_collection = None # Indicate failure

# --- Keep the document indexing endpoint if you want to trigger it via API ---
# Note: This part still uses the functions from document_processor.py
# You might need to adjust the import or logic if you changed document_processor.py significantly.
# from document_processor import initialize_collection, process_pdf # Uncomment if using this endpoint

# Global variable for the collection used by the indexing endpoint
# (This is separate from the one initialized at startup for chat)
indexing_collection = None

@app.post("/api/index-documents")
async def index_documents():
    global indexing_collection
    try:
        # Import here or ensure they are available if needed for this specific endpoint
        # For now, assuming document_processor.py is structured correctly
        from document_processor import initialize_collection, process_pdf

        # Initialize or get existing collection for indexing
        indexing_collection = initialize_collection() # This should now use the multilingual embedding function
        documents_path = ".documents"
        indexed_count = 0
        if os.path.exists(documents_path):
            for filename in os.listdir(documents_path):
                 # Process files in subdirectories (english, german) if they exist
                 full_path = os.path.join(documents_path, filename)
                 if os.path.isdir(full_path):
                     # It's a subdirectory (e.g., english, german)
                     for sub_filename in os.listdir(full_path):
                         if sub_filename.lower().endswith(".pdf"):
                             lang_tag = filename # Use subdirectory name as language tag
                             process_pdf(indexing_collection, os.path.join(full_path, sub_filename), language_tag=lang_tag)
                             indexed_count += 1
                 elif filename.lower().endswith(".pdf"):
                     # Process files directly in .documents (fallback)
                     process_pdf(indexing_collection, full_path)
                     indexed_count += 1
        print(f"Indexing complete. Processed {indexed_count} files.")
        return {"detail": f"Indexed {indexed_count} documents successfully."}
    except Exception as e:
        print(f"Error during indexing: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


# Pydantic model for chat input (Keep this)

class MessageItem(BaseModel): # Define a model for individual messages
    text: str
    sender: str
    # Add context if you want to send it back from frontend too
    # context: Optional[List[str]] = None
class ChatInput(BaseModel):
    message: str
    history: List[MessageItem] = []
    language: str = "en"

# --- 2. Update the /api/chat endpoint with corrected logic and improved prompt ---
@app.post("/api/chat")
async def chat(input: ChatInput):
    """Handle chat messages with RAG and LLM."""
    global chroma_collection # <-- Use the correct global variable name

    # 1. Check if ChromaDB is initialized for chat
    if chroma_collection is None:
        print("ChromaDB collection is not initialized for chat.")
        return {
            "response": "I'm currently unable to access my knowledge base. Please try again later.",
            "context": []
        }

    user_query = input.message
    user_language = input.language # Get the language from the frontend
    print(f"Received query: '{user_query}' (Language: {user_language})")

    try:
        # 2. Retrieve relevant context from ChromaDB
        # Query the collection
        # n_results: Number of relevant document chunks to retrieve
        results = chroma_collection.query(query_texts=[user_query], n_results=3)
        # Optional: Filter by metadata language if stored and desired
        # results = chroma_collection.query(query_texts=[user_query], n_results=3, where={"language": user_language})

        # 3. Extract context text
        context_text = ""
        if results and 'documents' in results and results['documents']:
            retrieved_chunks = results['documents'][0] # Get chunks for the first query text
            context_text = "\n\n".join(retrieved_chunks) # Join chunks
            print(f"Retrieved context (first 200 chars): {context_text[:200]}...")
        else:
            print("No relevant context found in ChromaDB.")
            context_text = "No relevant information found in the knowledge base."

        # 4. Construct the improved prompt for the LLM
        # --- NEW, Improved Prompt ---
        # Base instruction
        base_instruction = "You are an AI assistant representing Mushtaq Bokhari. Answer the question using ONLY the information provided in the 'Context' section below. Be concise and professional."

        # Language-specific addition to guide the LLM
        # This helps if the query and context are in different languages
        if user_language == 'en':
            language_instruction = "The user asked in English. Please answer the user's question based on the provided context and provide the response in English."
            # Optional: If you know context is mostly German, add:
            # language_instruction = "The user asked in English, but the provided context is primarily in German. Please answer the user's English question based on the German context and provide the response in English."
        elif user_language == 'de':
            language_instruction = "Der Benutzer hat auf Deutsch gefragt. Bitte antworten Sie auf Deutsch."
            # Optional: If you know context is mostly English, add:
            # language_instruction = "Der Benutzer hat auf Deutsch gefragt, aber der bereitgestellte Kontext ist hauptsächlich auf Englisch. Bitte beantworten Sie die deutsche Frage des Benutzers anhand des englischen Kontexts und geben Sie die Antwort auf Deutsch."
        else:
            language_instruction = "" # Default if language is unexpected

        # Combine instructions
        full_prompt = f"""{base_instruction}
{language_instruction}

Context:
{context_text}

Question:
{user_query}

Answer:"""
        # --- End NEW Prompt ---

        print(f"Sending prompt to LLM (first 300 chars): {full_prompt[:300]}...")

        # 5. Call the local LLM via Ollama
        # Choose your model (ensure it's pulled via `ollama pull <model_name>`)
        # Recommendation: Use phi3:mini or llama3.2:1b instead of tinyllama for better results
        chosen_model = 'phi3:mini' # <--- CHOOSE YOUR MODEL HERE ---

        # Use ollama.generate for simple text completion
        # stream=False gets the full response at once
        ollama_response = ollama.generate(model=chosen_model, prompt=full_prompt, stream=False)

        # 6. Extract the generated text from the Ollama response
        llm_response_text = ollama_response['response'].strip()
        print(f"LLM Response: {llm_response_text}")

        # 7. Return the response and context
        return {
            "response": llm_response_text,
            # Returning context is helpful for debugging/testing the RAG part
            "context": [context_text] if context_text else []
        }

    except Exception as e:
        # Handle potential errors (e.g., ChromaDB issues, Ollama issues)
        print(f"Error during RAG/LLM processing: {e}")
        return {
            "response": "Sorry, I encountered an error while processing your request. Please try rephrasing or ask another question.",
            "context": [f"Error context: {str(e)}"] # Optional: send error info back for debugging
        }

# --- Placeholder for audio endpoint (as client-side STT is used) ---
# You can remove this if not planning to use server-side Whisper anymore for MVP
@app.post("/api/audio/input")
async def transcribe_audio(file: UploadFile):
    """Placeholder for audio transcription."""
    # In MVP, client-side STT is used. This endpoint is not actively used.
    # If you ever revert or add server-side STT, implement Whisper logic here.
    return {"text": "Audio transcription is handled client-side in this MVP."}
