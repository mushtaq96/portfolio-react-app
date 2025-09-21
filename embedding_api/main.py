# portfolio-react-app/embedding_api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import os
import logging

# --- Basic logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Embedding API", description="API for generating text embeddings.")

# --- Load the model ONCE at startup ---
# Use the same model name as in document_processor.py
MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "./local_models/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/snapshots/86741b4e3f5cb7765a600d3a3d55a0f6a6cb443d")
embedding_model = None

@app.on_event("startup")
async def load_model():
    global embedding_model
    logger.info(f"Loading embedding model: {MODEL_NAME}...")
    try:
        # Load the model into memory
        embedding_model = SentenceTransformer(MODEL_NAME)
        logger.info(f"✅ Embedding model '{MODEL_NAME}' loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to load embedding model '{MODEL_NAME}': {e}")
        # Optionally, you might want to raise an exception here to prevent the app from starting
        # if the model is critical. For now, we'll log and let the /embed endpoint handle errors.
        embedding_model = None


# --- Define the input data structure ---
class EmbeddingRequest(BaseModel):
    texts: list[str] # Expect a list of strings to embed

# --- Define the output data structure ---
class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]] # List of embedding vectors

# --- Create the API endpoint ---
@app.post("/embed", response_model=EmbeddingResponse, summary="Generate Embeddings")
async def get_embeddings(request: EmbeddingRequest):
    """Generate embeddings for a list of texts."""
    global embedding_model
    if embedding_model is None:
        logger.error("Embedding model not loaded.")
        raise HTTPException(status_code=500, detail="Embedding model not loaded. Service might be starting up or encountered an error.")

    try:
        logger.info(f"Generating embeddings for {len(request.texts)} text(s).")
        # Use the model to encode the texts into embeddings
        # sentences_to_encode = request.texts
        embeddings_list = embedding_model.encode(request.texts).tolist() # Convert NumPy array to list
        logger.info("Embeddings generated successfully.")
        return EmbeddingResponse(embeddings=embeddings_list)
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate embeddings: {str(e)}")

@app.get("/health")
async def health_check():
    model_status = "loaded" if embedding_model else "not loaded"
    return {"status": "healthy", "service": "embedding-api", "model": MODEL_NAME, "model_status": model_status}

@app.get("/")
async def root():
    return {"message": "Embedding API is running!", "model": MODEL_NAME}
