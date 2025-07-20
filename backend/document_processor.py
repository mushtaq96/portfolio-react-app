import os
import PyPDF2
from chromadb import Client, Settings
from chromadb.utils import embedding_functions

def initialize_collection():
    """Initialize ChromaDB collection with embeddings"""
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        "all-MiniLM-L6-v2"
    )
    client = Client(settings=Settings(
        persist_directory="./chroma_db",
        allow_reset=True
    ))
    return client.get_or_create_collection(
        name="portfolio_docs",
        embedding_function=embedding_func
    )

def process_pdf(collection, filepath):
    """Process a single PDF file into chunks"""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = "\n".join([page.extract_text() for page in reader.pages])
        
        # Semantic chunking would be better, but simple splitting works for demo
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # Generate unique IDs for each chunk
        doc_id = os.path.basename(filepath)
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        
        collection.add(
            documents=chunks,
            ids=ids
        )

if __name__ == "__main__":
    collection = initialize_collection()
    for filename in os.listdir("documents"):
        if filename.endswith(".pdf"):
            process_pdf(collection, f"documents/{filename}")
    print("Documents processed successfully!")