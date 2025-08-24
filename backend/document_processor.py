import os
import PyPDF2
import chromadb

def initialize_collection():
    chroma_client = chromadb.PersistentClient(path="./.chroma_db")
    collection = chroma_client.get_or_create_collection(
        name="portfolio_docs"
    )
    return collection

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
        
        collection.upsert(
            documents=chunks,
            ids=ids
        )
        print(f"Processing {filepath}, adding {len(chunks)} chunks.")


if __name__ == "__main__":
    collection = initialize_collection()
    for filename in os.listdir(".documents"):
        if filename.endswith(".pdf"):
            process_pdf(collection, f".documents/{filename}")
    print("Documents processed successfully!")