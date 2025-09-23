# embedding_api/embedding_service.py
import torch
from sentence_transformers import SentenceTransformer
import logging
import os
from functools import lru_cache
import threading
from typing import Dict, List, Optional
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
load_dotenv()  # Load environment variables from .env file

# Singleton service to manage the embedding model
class EmbeddingService:
    _instance: Optional['EmbeddingService'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        # Ensure only one instance and handle initialization correctly
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    instance = super(EmbeddingService, cls).__new__(cls)
                    # Read model name from environment variable
                    model_name_env = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2") # Default to a small one
                    logger.info(f"Initializing EmbeddingService with model name from env: '{model_name_env}'")

                    # Construct the correct local path
                    base_path = os.path.join(os.path.dirname(__file__), "local_models")
                    model_dir_name = f"models--sentence-transformers--{model_name_env}"
                    model_path = os.path.join(base_path, model_dir_name)
                    logger.info(f"Constructed base model path: {model_path}")

                    if not os.path.exists(model_path):
                        raise FileNotFoundError(f"Model directory not found at expected local path: {model_path}. Ensure the model is correctly placed in embedding_api/local_models/ and tracked by Git LFS.")

                    snapshots_path = os.path.join(model_path, "snapshots")
                    if not os.path.exists(snapshots_path):
                        raise FileNotFoundError(f"Snapshots directory not found for model: {model_path}")

                    snapshot_dirs = os.listdir(snapshots_path)
                    if not snapshot_dirs:
                        raise FileNotFoundError(f"No snapshot found in: {snapshots_path}")

                    # Use the first snapshot (assuming one exists)
                    # For production, you might want to sort and pick the latest based on naming convention
                    snapshot_hash = snapshot_dirs[0]
                    full_model_path = os.path.join(snapshots_path, snapshot_hash)
                    logger.info(f"Using model snapshot path: {full_model_path}")

                    instance.model_name = model_name_env
                    instance.model_path = full_model_path
                    instance.model = None # Initialize model attribute
                    instance._load_model()
                    cls._instance = instance
        return cls._instance

    def _load_model(self):
        # Determine device
        if torch.cuda.is_available():
            device = "cuda"
            logger.info("CUDA available, attempting to load model on GPU.")
        elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
            device = "mps"
            logger.info("MPS available, attempting to load model on MPS.")
        else:
            device = "cpu"
            logger.info("Using CPU for model loading.")

        logger.info(f"Loading SentenceTransformer model from local path '{self.model_path}' on device '{device}'...")
        try:
            # --- Fix 4: Pass the full local path to SentenceTransformer ---
            self.model = SentenceTransformer(self.model_path, device=device)
            logger.info(f"✅ Model '{self.model_name}' successfully loaded from local path '{self.model_path}' on device '{device}'.")
        except Exception as e:
            logger.error(f"❌ Error loading model from '{self.model_path}': {e}", exc_info=True) # Log full traceback
            raise # Re-raise to prevent service startup

    # Use lru_cache carefully. It caches based *only* on the 'text' argument.
    # If device/context changes, cache might be stale. For simplicity, keep it.
    @lru_cache(maxsize=512)
    def get_embedding(self, text: str) -> List[float]:
        if self.model is None:
             logger.error("Embedding service model is not initialized.")
             return None
        logger.debug(f"Creating embedding for text (truncated): '{text[:50]}{'...' if len(text) > 50 else ''}'")
        try:
            # SentenceTransformer.encode can handle a single string or a list
            embeddings = self.model.encode(text, convert_to_tensor=False) # Returns numpy array or list
            embedding_list = embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
            logger.debug(f"Embedding successfully created, dimension: {len(embedding_list)}")
            return embedding_list
        except Exception as e:
            logger.error(f"Error creating embedding for text '{text[:30]}...': {e}", exc_info=True)
            return None

# Ensure logging is configured if this module is run directly or imported early
if __name__ == "__main__" or not logging.root.handlers:
    logging.basicConfig(level=logging.INFO)
