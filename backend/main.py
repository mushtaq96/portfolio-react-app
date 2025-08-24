from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import whisper
import torch
import os
from typing import List, Dict
from document_processor import initialize_collection, process_pdf

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

collection = None

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

@app.post("/api/chat")
async def chat(input: ChatInput):
    """Handle chat messages with RAG"""
    # In a real implementation, you'd query ChromaDB here
    # For now, we'll return a placeholder
    return {
        "response": f"I received your message about: {input.message}",
        "context": ["Example context chunk 1", "Example context chunk 2"]
    }
