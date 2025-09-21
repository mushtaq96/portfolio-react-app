# portfolio-react-app/backend/document_processor.py
import os
import PyPDF2
from docx import Document
import chromadb
# 1. Import the required embedding function utility from ChromaDB
# This utility makes it easy to use Sentence Transformers models with ChromaDB
from chromadb.utils import embedding_functions

# --- Define the multilingual embedding function ---
# Specify the model name you want to use
# Note: This model name is used during collection creation in initialize_collection
# and determines which model ChromaDB will try to load for query-time embedding
# if it needs to (e.g., if persistence doesn't fully capture it or on first query).
MULTILINGUAL_EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def initialize_collection(db_path="./.chroma_db", collection_name="portfolio_docs"):
    """Initialize the ChromaDB client and get/create the collection with the multilingual embedding function."""
    # Path to the ChromaDB persistent storage
    # Using PersistentClient ensures data is saved to disk
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    # 2. Create the embedding function instance
    # This tells ChromaDB how to generate embeddings for the documents and queries
    # The model specified here is crucial for both indexing (build_db.py) and querying (main.py)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=MULTILINGUAL_EMBEDDING_MODEL_NAME
    )
    
    # 3. Get or create the collection, passing the embedding function
    # The name identifies your collection
    # The embedding_function is associated with the collection for future use
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        # 4. Pass the embedding function here
        embedding_function=sentence_transformer_ef 
    )
    print(f"Initialized ChromaDB collection '{collection_name}' with embedding model '{MULTILINGUAL_EMBEDDING_MODEL_NAME}' at path '{db_path}'.")
    return collection

def process_word_file(collection, filepath, language_tag=None):
    """Process Word documents (.docx)"""
    try:
        doc = Document(filepath)
        # Extract text from all paragraphs
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        # Simple chunking
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # Generate IDs
        doc_id_base = os.path.splitext(os.path.basename(filepath))[0]
        doc_id = f"{doc_id_base}_{language_tag}" if language_tag else doc_id_base
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

        # Prepare metadata
        metadatas = [{"language": language_tag, "source_doc": doc_id_base} for _ in chunks] if language_tag else None

        # Upsert into ChromaDB
        collection.upsert(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        print(f"Processing {filepath} (Language: {language_tag}), adding {len(chunks)} chunks.")
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

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
            return True
    except Exception as e:
        # Basic error handling
        print(f"Error processing {filepath}: {e}")
        return False

def process_document(collection, filepath, language_tag=None):
    """Process any supported document type"""
    if filepath.lower().endswith('.pdf'):
        return process_pdf(collection, filepath, language_tag)
    elif filepath.lower().endswith('.docx'):
        return process_word_file(collection, filepath, language_tag)
    else:
        print(f"Unsupported file type: {filepath}")
        return False

# --- IMPORTANT ---
# The `if __name__ == "__main__":` block IS REMOVED from this file.
# Its functionality is moved to the separate `build_db.py` script.
# This file now purely contains the functions for document processing and collection interaction.
# --- END IMPORTANT ---