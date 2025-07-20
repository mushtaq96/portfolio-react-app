from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import whisper
import torch
import os
from typing import List, Dict

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
device = "cuda" if torch.cuda.is_available() else "cpu"
stt_model = whisper.load_model("small").to(device)

class ChatInput(BaseModel):
    message: str
    history: List[Dict[str, str]]
    language: str = "en"

@app.post("/api/chat")
async def chat(input: ChatInput):
    """Handle chat messages with RAG"""
    # In a real implementation, you'd query ChromaDB here
    # For now, we'll return a placeholder
    return {
        "response": f"I received your message about: {input.message}",
        "context": ["Example context chunk 1", "Example context chunk 2"]
    }

@app.post("/api/audio/input")
async def process_audio(file: UploadFile):
    """Convert speech to text"""
    try:
        # Save audio temporarily
        temp_path = f"static/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Transcribe
        result = stt_model.transcribe(temp_path)
        os.remove(temp_path)
        
        return {"text": result["text"]}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.on_event("startup")
async def startup():
    """Initialize services"""
    if not os.path.exists("static"):
        os.makedirs("static")