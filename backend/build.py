# portfolio-react-app/backend/build_db.py
"""
Script to build the ChromaDB index locally.
This script processes documents, generates embeddings using the specified model,
and persists the ChromaDB collection to disk.
Run this script locally before deploying to Render.
"""

import os
# Import functions from your document_processor module
from document_processor import initialize_collection, process_document

def main():
    """Main function to orchestrate the index building process."""
    print("Starting local document indexing...")
    
    # 1. Initialize the collection with the multilingual embedding function
    # This will create the collection if it doesn't exist, or get it if it does.
    # Crucially, it associates the collection with the embedding function.
    collection = initialize_collection()

    indexed_count = 0 # Counter for processed files

    # 2. --- Process English documents ---
    english_docs_path = ".documents/English" # Path relative to where the script runs (backend folder)
    if os.path.exists(english_docs_path):
        print(f"Processing documents in '{english_docs_path}'...")
        for filename in os.listdir(english_docs_path):
            if filename.lower().endswith((".pdf", ".docx")):
                full_path = os.path.join(english_docs_path, filename)
                # Pass the collection object and the file path, specify language tag
                if process_document(collection, full_path, language_tag="en"):
                    indexed_count += 1
    else:
        print(f"Directory '{english_docs_path}' not found. Skipping English documents.")

    # 3. --- Process German documents ---
    german_docs_path = ".documents/German" # Path relative to where the script runs (backend folder)
    if os.path.exists(german_docs_path):
        print(f"Processing documents in '{german_docs_path}'...")
        for filename in os.listdir(german_docs_path):
            if filename.lower().endswith((".pdf", ".docx")):
                full_path = os.path.join(german_docs_path, filename)
                # Pass the collection object and the file path, specify language tag
                if process_document(collection, full_path, language_tag="de"):
                    indexed_count += 1
    else:
        print(f"Directory '{german_docs_path}' not found. Skipping German documents.")

    print(f"Local indexing complete. Successfully processed {indexed_count} files.")
    print("The '.chroma_db' folder has been updated/created.")
    print("Ensure this folder is committed to your Git repository before deploying.")

if __name__ == "__main__":
    main()