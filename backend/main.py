# portfolio-react-app/backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List
import chromadb 
from groq import Groq
from dotenv import load_dotenv
from prompts import get_base_instruction, is_value_question, get_language_instruction

app = FastAPI()
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for the collection used by the indexing endpoint
indexing_collection = None

@app.post("/api/index-documents")
async def index_documents():
    global indexing_collection
    try:
        # Import the unified document processor
        from document_processor import initialize_collection, process_document

        # Initialize or get existing collection for indexing
        indexing_collection = initialize_collection()
        documents_path = ".documents"
        indexed_count = 0
        
        if os.path.exists(documents_path):
            for filename in os.listdir(documents_path):
                full_path = os.path.join(documents_path, filename)
                if os.path.isdir(full_path):
                    # It's a subdirectory (e.g., english, german)
                    for sub_filename in os.listdir(full_path):
                        # Process both PDF and Word files
                        if sub_filename.lower().endswith((".pdf", ".docx")):
                            lang_tag = filename  # Use subdirectory name as language tag
                            process_document(indexing_collection, os.path.join(full_path, sub_filename), language_tag=lang_tag)
                            indexed_count += 1
                # Process files directly in .documents (fallback)
                elif filename.lower().endswith((".pdf", ".docx")):
                    process_document(indexing_collection, full_path)
                    indexed_count += 1
                    
        print(f"Indexing complete. Processed {indexed_count} files.")
        return {"detail": f"Indexed {indexed_count} documents successfully."}
    except Exception as e:
        print(f"Error during indexing: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

# Global ChromaDB collection
chroma_collection = None

@app.on_event("startup")
async def startup_event():
    """Initialize resources when the app starts."""
    global chroma_collection
    try:
        chroma_client = chromadb.PersistentClient(path="./.chroma_db")
        chroma_collection = chroma_client.get_collection(name="portfolio_docs")
        print("✅ ChromaDB collection 'portfolio_docs' initialized successfully.")
    except Exception as e:
        print(f"⚠️ Error initializing ChromaDB collection: {e}")
        chroma_collection = None

# Pydantic models
class MessageItem(BaseModel):
    text: str
    sender: str

class ChatInput(BaseModel):
    message: str
    history: List[MessageItem] = []
    language: str = "en"

@app.post("/api/chat")
async def chat(input: ChatInput):
    """Handle chat messages with RAG and LLM."""
    global chroma_collection, groq_client

    # Check if services are available
    if groq_client is None:
        return {"response": "AI assistant unavailable.", "context": []}
    
    if chroma_collection is None:
        return {"response": "Knowledge base unavailable.", "context": []}

    user_query = input.message
    user_language = input.language
    print(f"Received query: '{user_query}' (Language: {user_language})")

    try:
        # Retrieve relevant context from ChromaDB
        results = chroma_collection.query(query_texts=[user_query], n_results=3)
        
        context_text = ""
        if results and 'documents' in results and results['documents']:
            retrieved_chunks = results['documents'][0]
            context_text = "\n\n".join(retrieved_chunks)
            print(f"Retrieved context (first 200 chars): {context_text[:200]}...")
        else:
            context_text = "No relevant information found in the knowledge base."

        # Build enhanced prompt using prompts.py
        base_instruction = get_base_instruction(is_value_question(user_query))
        language_instruction = get_language_instruction(user_language)

        full_prompt = f"""{base_instruction}
{language_instruction}

Context:
{context_text}

Question:
{user_query}

Answer (concise and professional):"""

        print(f"Sending prompt to LLM (first 300 chars): {full_prompt[:300]}...")

        # Call the LLM via Groq API
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": full_prompt}],
                model="llama-3.1-8b-instant", 
                temperature=0.7,
                max_tokens=200,
                top_p=0.9,
                stream=False,
            )
            
            llm_response_text = chat_completion.choices[0].message.content.strip()
            print(f"LLM Response: {llm_response_text}")

            return {
                "response": llm_response_text,
                "context": [context_text] if context_text else []
            }

        except Exception as api_error:
            print(f"❌ Groq API error: {api_error}")
            return {
                "response": "Sorry, I encountered an error while processing your request.",
                "context": [f"API Error: {str(api_error)}"]
            }

        

    except Exception as e:
        print(f"Error during processing: {e}")
        return {
            "response": "Sorry, I encountered an error while processing your request.",
            "context": [f"Error: {str(e)}"]
        }

# Health check endpoints
@app.get("/")
async def root():
    return {"message": "Portfolio Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "portfolio-backend"}