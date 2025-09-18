from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Dict
# from document_processor import initialize_collection, process_pdf
import chromadb
import ollama

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

collection = None

@app.on_event("startup")
async def startup_event():
    """Initialize resources when the app starts."""
    global chroma_collection
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

class ChatInput(BaseModel):
    message: str
    history: List[Dict[str, str]]
    language: str = "en"

@app.post("/api/index-documents")
async def index_documents():
    global collection
    try:
        # Initialize or get existing collection
        collection = initialize_collection()
        documents_path = ".documents"
        for filename in os.listdir(documents_path):
            if filename.endswith(".pdf"):
                process_pdf(collection, f"{documents_path}/{filename}")
        return {"detail": f"Indexed documents in {documents_path} successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

# --- 2. Update the /api/chat endpoint ---
@app.post("/api/chat")
async def chat(input: ChatInput):
    """Handle chat messages with RAG and LLM."""
    global chroma_collection

    # 1. Check if ChromaDB is initialized
    if chroma_collection is None:
        print("ChromaDB collection is not initialized.")
        return {
            "response": "I'm currently unable to access my knowledge base. Please try again later.",
            "context": []
        }

    user_query = input.message
    print(f"Received query: {user_query}")

    try:
        # 2. Retrieve relevant context from ChromaDB
        # Query the collection
        # n_results: Number of relevant document chunks to retrieve
        # Adjust n_results based on testing (e.g., 2, 3, 5)
        results = chroma_collection.query(query_texts=[user_query], n_results=3)

        # 3. Extract context text
        context_text = ""
        if results and 'documents' in results and results['documents']:
            # results['documents'] is a list of lists (because you can query multiple texts)
            # We queried one text, so take the first list
            retrieved_chunks = results['documents'][0]
            # Join the retrieved chunks into a single string
            context_text = "\n\n".join(retrieved_chunks)
            print(f"Retrieved context (first 200 chars): {context_text[:200]}...")
        else:
            print("No relevant context found in ChromaDB.")
            context_text = "No relevant information found in the knowledge base."

        # 4. Construct the prompt for the LLM
        # Explicitly instruct the LLM to use the context
        full_prompt = f"""Use the following context to answer the query accurately and concisely.
If the context doesn't contain the information needed to answer the query, say so.

Context:
{context_text}

Query:
{user_query}

Answer:"""

        print(f"Sending prompt to LLM (first 200 chars): {full_prompt[:200]}...")

        # 5. Call the local LLM via Ollama
        # Choose your model (ensure it's pulled via `ollama pull <model_name>`)
        # Example: 'phi3:mini', 'llama3.2:1b', 'tinyllama'
        chosen_model = 'tinyllama' # <--- CHOOSE YOUR MODEL HERE ---
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
    
