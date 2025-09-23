# embedding_api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
import threading
# Import the service (ensure the path is correct relative to this file)
from embedding_service import EmbeddingService
# Import memory monitor if you still want it (optional for now)
from memory_monitor import MemoryMonitor

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Embedding API", description="API for generating text embeddings.")

# Global variable for the service instance
embedding_service: EmbeddingService = None
memory_monitor = MemoryMonitor() # Optional

class EmbeddingRequest(BaseModel):
    texts: List[str]

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]

@app.on_event("startup")
async def startup_event():
    global embedding_service # , memory_monitor
    logger.info("Starting up Embedding API...")
    try:
        # Initialize the singleton embedding service
        # This will read EMBEDDING_MODEL_NAME and load the model from local path
        embedding_service = EmbeddingService()
        logger.info("Embedding service initialized successfully.")

        # Optional: Start memory monitoring in a background thread
        monitor_thread = threading.Thread(target=memory_monitor.monitor, daemon=True)
        monitor_thread.start()
        logger.info("Memory monitoring thread started.")

    except Exception as e:
        logger.error(f"Failed to initialize embedding service during startup: {e}", exc_info=True)
        # Depending on your setup, you might want to exit here if the core service fails
        # import sys; sys.exit(1) # Or let the app start but fail on first request

@app.get("/health")
async def health_check():
    model_status = "loaded" if embedding_service and embedding_service.model is not None else "not loaded"
    return {"status": "healthy", "service": "embedding-api", "model_status": model_status}

@app.post("/embed", response_model=EmbeddingResponse) # Use the response model
async def get_embeddings(request: EmbeddingRequest): # Use the request model
    global embedding_service
    if embedding_service is None:
        logger.error("Embedding service is not initialized.")
        raise HTTPException(status_code=500, detail="Embedding service not initialized.")

    logger.info(f"Received request to embed {len(request.texts)} text(s).")
    try:
        # Generate embeddings for each text in the list
        # get_embedding is cached, so repeated identical texts are fast
        embeddings_list = [embedding_service.get_embedding(text) for text in request.texts]

        # Check if any embedding failed
        if any(embedding is None for embedding in embeddings_list):
            failed_indices = [i for i, emb in enumerate(embeddings_list) if emb is None]
            logger.error(f"Failed to generate embeddings for texts at indices: {failed_indices}")
            raise HTTPException(status_code=500, detail="Failed to generate one or more embeddings.")

        logger.info("All embeddings generated successfully.")
        return EmbeddingResponse(embeddings=embeddings_list)

    except HTTPException:
        # Re-raise HTTPExceptions (e.g., from the check above)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /embed endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Embedding API is running!", "docs": "/docs"}
