# portfolio-react-app/backend/document_processor.py
import os
import PyPDF2
import chromadb
# 1. Import the required embedding function utility from ChromaDB
# This utility makes it easy to use Sentence Transformers models with ChromaDB
from chromadb.utils import embedding_functions

# --- Define the multilingual embedding function ---
# Specify the model name you want to use
MULTILINGUAL_EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def initialize_collection():
    """Initialize the ChromaDB client and get/create the collection with the multilingual embedding function."""
    # Path to the ChromaDB persistent storage
    chroma_client = chromadb.PersistentClient(path="./.chroma_db")
    
    # 2. Create the embedding function instance
    # This tells ChromaDB how to generate embeddings for the documents and queries
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=MULTILINGUAL_EMBEDDING_MODEL_NAME
    )
    
    # 3. Get or create the collection, passing the embedding function
    # The name "portfolio_docs" identifies your collection
    collection = chroma_client.get_or_create_collection(
        name="portfolio_docs",
        # 4. Pass the embedding function here
        embedding_function=sentence_transformer_ef 
    )
    print(f"Initialized ChromaDB collection 'portfolio_docs' with embedding model '{MULTILINGUAL_EMBEDDING_MODEL_NAME}'.")
    return collection

def process_pdf(collection, filepath, language_tag=None):
    """Process a single PDF file into chunks and add them to the collection."""
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # Extract text from all pages
            text = "\n".join([page.extract_text() for page in reader.pages])
            
            # --- Simple chunking (Consider improving later with semantic chunking) ---
            chunk_size = 1000
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            
            # --- Generate unique IDs for each chunk ---
            # Include language tag in ID for better uniqueness if needed
            doc_id_base = os.path.splitext(os.path.basename(filepath))[0] # Filename without extension
            doc_id = f"{doc_id_base}_{language_tag}" if language_tag else doc_id_base
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

            # --- Prepare metadata (optional but useful) ---
            # Store the original language and source document name
            metadatas = [{"language": language_tag, "source_doc": doc_id_base} for _ in chunks] if language_tag else None

            # --- Upsert into ChromaDB ---
            # ChromaDB will automatically use the embedding function specified during collection creation
            # to generate embeddings for the 'documents' before storing them.
            collection.upsert(
                documents=chunks, # The text chunks to store
                ids=ids,         # Unique IDs for the chunks
                metadatas=metadatas # Optional metadata
                # Note: No need to manually pass embeddings; ChromaDB handles it via the embedding_function
            )
            print(f"Processing {filepath} (Language: {language_tag}), adding {len(chunks)} chunks.")
    except Exception as e:
        # Basic error handling
        print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    # Initialize the collection with the multilingual embedding function
    collection = initialize_collection()

    # --- Process English documents ---
    english_docs_path = ".documents/english"
    if os.path.exists(english_docs_path):
        print(f"Processing documents in '{english_docs_path}'...")
        for filename in os.listdir(english_docs_path):
            if filename.lower().endswith(".pdf"):
                process_pdf(collection, os.path.join(english_docs_path, filename), language_tag="en")
    else:
        print(f"Directory '{english_docs_path}' not found. Skipping English documents.")

    # --- Process German documents ---
    german_docs_path = ".documents/german"
    if os.path.exists(german_docs_path):
        print(f"Processing documents in '{german_docs_path}'...")
        for filename in os.listdir(german_docs_path):
            if filename.lower().endswith(".pdf"):
                process_pdf(collection, os.path.join(german_docs_path, filename), language_tag="de")
    else:
        print(f"Directory '{german_docs_path}' not found. Skipping German documents.")

    print("All documents processed successfully with multilingual embeddings!")
