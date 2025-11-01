# portfolio-react-app/backend/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List
import chromadb
from groq import Groq
from dotenv import load_dotenv
from prompts import get_base_instruction, is_value_question, get_language_instruction
import httpx
from collections import defaultdict
import time
from pathlib import Path
import json
from datetime import datetime

app = FastAPI()
load_dotenv()

# === ADD RATE LIMITING HERE ===
# Simple in-memory rate limiting
usage = defaultdict(list)  # {ip: [timestamp1, timestamp2, ...]}
MAX_REQUESTS = 5
TIME_WINDOW = 3600  # 1 hour

# Middleware to enforce rate limiting


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Only apply rate limiting to the chat endpoint
    if request.url.path == "/api/chat":
        client_ip = request.client.host
        now = time.time()

        # Clean old requests (older than TIME_WINDOW)
        usage[client_ip] = [t for t in usage[client_ip] if now - t < TIME_WINDOW]

        # Check if limit exceeded
        if len(usage[client_ip]) >= MAX_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. You can only ask 5 questions per hour. Please contact me directly for more information."
            )

        # Record this request
        usage[client_ip].append(now)

    response = await call_next(request)
    return response

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Get the Embedding API URL from environment variable
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL")
# Create an httpx client for making requests to the Embedding API
# Consider using a lifespan or dependency for more robust client management in production
# Set a reasonable timeout (e.g., 30 seconds)
httpx_client = httpx.AsyncClient(timeout=30.0) if EMBEDDING_API_URL else None

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only enable the indexing endpoint if the environment variable is set.
# This prevents accidental re-indexing
ALLOW_INDEXING = os.getenv("ALLOW_INDEXING", "false").lower() == "true"

PROCESSED_FILES_LOG = "./processed_files.json"
# Path to the challenge data folder
DATA_ROOT_DIR = "./Material_GreenHorizon"


if ALLOW_INDEXING:
    print("⚠️ Indexing endpoint is ENABLED. Ensure this is intentional.")
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

            # Load the log of previously processed files
            processed_files = {}
            if os.path.exists(PROCESSED_FILES_LOG):
                try:
                    with open(PROCESSED_FILES_LOG, 'r', encoding='utf-8') as f:
                        processed_files = json.load(f)
                        # Convert string keys (file paths) back to Path objects if necessary, or keep as strings
                        # Assuming paths are stored as strings in the JSON
                        # Normalize paths
                        processed_files = {
                            str(Path(k).resolve()): v for k,
                            v in processed_files.items()}
                except (json.JSONDecodeError, IOError) as e:
                    print(
                        f"Warning: Could not read {PROCESSED_FILES_LOG}, starting fresh. Error: {e}")
                    processed_files = {}

            # Walk through the DATA_ROOT_DIR recursively
            if os.path.exists(DATA_ROOT_DIR):
                print(
                    f"Scanning directory '{DATA_ROOT_DIR}' for new/modified files...")
                for root, dirs, files in os.walk(DATA_ROOT_DIR):
                    for file in files:
                        filepath = Path(root) / file
                        # Use .resolve() to get the absolute path for consistent comparison
                        abs_filepath = str(filepath.resolve())

                        # Determine if file needs processing based on modification time
                        current_mtime = filepath.stat().st_mtime
                        # Use .get() to safely retrieve the mtime, defaulting to None if key doesn't exist
                        previously_processed_mtime = processed_files.get(
                            str(abs_filepath))

                        print(
                            f"DEBUG: File {abs_filepath}, Current mtime: {current_mtime} ({datetime.fromtimestamp(current_mtime)}), Stored mtime: {previously_processed_mtime} ({datetime.fromtimestamp(previously_processed_mtime) if previously_processed_mtime else 'None'})"
                        )
                        # Check if file is new (not in log) or has been modified since last processing (mtime in log is older)
                        # If previously_processed_mtime is None, it means the file wasn't in the log, so it's new.
                        if previously_processed_mtime is None or current_mtime > previously_processed_mtime:
                            print(
                                f"Processing new/modified file: {abs_filepath}")
                            if process_document(indexing_collection, str(abs_filepath)):
                                # Update the log with the new modification time
                                processed_files[str(
                                    abs_filepath)] = current_mtime
                                indexed_count += 1
                            else:
                                print(f"Failed to process {abs_filepath}")
                        else:
                            print(
                                f"Skipping already processed file (up to date): {abs_filepath}")
            else:
                print(
                    f"Directory '{DATA_ROOT_DIR}' not found. No files to index.")
                return {"detail": f"Directory '{DATA_ROOT_DIR}' not found. No files indexed."}

            # Save the updated log of processed files
            with open(PROCESSED_FILES_LOG, 'w', encoding='utf-8') as f:
                # Convert Path keys back to strings for JSON serialization
                json.dump({str(k): v for k, v in processed_files.items()},
                          f, ensure_ascii=False, indent=4)

            print(
                f"Indexing complete. Processed {indexed_count} new/modified files.")
            return {"detail": f"Indexed {indexed_count} new/modified documents successfully."}
        except Exception as e:
            print(f"Error during indexing: {e}")
            raise HTTPException(
                status_code=500, detail=f"Indexing failed: {str(e)}")
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
        print("INFO: ChromaDB collection loaded. Querying may trigger embedding model loading.")
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

    context_text = ""
    try:
        if EMBEDDING_API_URL and httpx_client:
            # --- OPTION 1: Use External Embedding API ---
            print(
                f"Using external Embedding API at {EMBEDDING_API_URL} for query embedding.")
            try:
                # 1. Send the user's query text to the external Embedding API
                embedding_response = await httpx_client.post(
                    f"{EMBEDDING_API_URL}/embed",
                    json={"texts": [user_query]}  # Send the query as a list
                )
                # 2. Raise an exception if the API returned an error status (e.g., 4xx, 5xx)
                embedding_response.raise_for_status()
                # 3. Extract the embedding vector from the JSON response
                #    The API returns {"embeddings": [[...]]}, we want the first (and only) list
                query_embedding = embedding_response.json()["embeddings"][0]
                print("Received embedding from external API.")
                # 4. Query ChromaDB using the embedding vector we got from the external API
                results = chroma_collection.query(
                    query_embeddings=[query_embedding], n_results=3)
            except httpx.RequestError as req_err:
                # Handle network errors (timeout, DNS failure, etc.)
                print(f"❌ Error contacting Embedding API: {req_err}")
                return {
                    "response": "Sorry, I'm having trouble accessing my knowledge base right now (embedding service error).",
                    "context": [f"Embedding API Request Error: {str(req_err)}"]
                }
            except httpx.HTTPStatusError as http_err:
                # Handle HTTP errors returned by the Embedding API (e.g., 500 Internal Server Error)
                print(
                    f"❌ Embedding API returned error status: {http_err.response.status_code} - {http_err.response.text}")
                return {
                    "response": "Sorry, I encountered a problem accessing my knowledge base (embedding service failure).",
                    "context": [f"Embedding API HTTP Error ({http_err.response.status_code}): {http_err.response.text}"]
                }
            except Exception as embed_err:
                # Handle other potential errors (e.g., JSON parsing issues)
                print(
                    f"Error getting embedding from external API: {embed_err}")
                return {
                    "response": "Sorry, an error occurred while preparing to search for relevant information (embedding step).",
                    "context": [f"Embedding Error: {str(embed_err)}"]
                }
        else:
            # --- OPTION 2: Use ChromaDB's internal embedding (default/original behavior) ---
            # This path is taken if EMBEDDING_API_URL is not set or httpx_client failed to initialize.
            print(
                "Using ChromaDB's internal embedding function for query (or external API not configured).")
            # Retrieve relevant context from ChromaDB using the text query
            # ChromaDB will use its configured embedding function internally.
            results = chroma_collection.query(
                query_texts=[user_query], n_results=3)

        # Extract and concatenate retrieved chunks
        if results and 'documents' in results and results['documents']:
            retrieved_chunks = results['documents'][0]
            context_text = "\n\n".join(retrieved_chunks)
            print(
                f"Retrieved context (first 200 chars): {context_text[:200]}...")
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

        print(
            f"Sending prompt to LLM (first 300 chars): {full_prompt[:300]}...")

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

            llm_response_text = chat_completion.choices[0].message.content.strip(
            )
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
