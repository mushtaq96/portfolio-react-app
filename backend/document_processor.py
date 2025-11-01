import os
import PyPDF2
from docx import Document
import chromadb
from chromadb.utils import embedding_functions
import fitz  # PyMuPDF
import pptx
from email import message_from_string, policy
import easyocr
import pandas as pd
import yaml
import zipfile
import tempfile
import re
from pathlib import Path

MULTILINGUAL_EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def initialize_collection(db_path="./.chroma_db", collection_name="portfolio_docs"):
    """Initialize the ChromaDB client and get/create the collection with the multilingual embedding function."""
    chroma_client = chromadb.PersistentClient(path=db_path)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=MULTILINGUAL_EMBEDDING_MODEL_NAME
    )
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=sentence_transformer_ef
    )
    print(
        f"Initialized ChromaDB collection '{collection_name}' with embedding model '{MULTILINGUAL_EMBEDDING_MODEL_NAME}' at path '{db_path}'.")
    return collection


def extract_text_from_pdf(filepath):
    """Extract text from PDF using PyMuPDF (fitz) - often more reliable than PyPDF2."""
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {filepath}: {e}")
        return ""


def extract_text_from_docx(filepath):
    """Extract text from DOCX."""
    try:
        doc = Document(filepath)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return ""


def extract_text_from_pptx(filepath):
    """Extract text from PPTX."""
    try:
        prs = pptx.Presentation(filepath)
        text_runs = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text_runs.append(shape.text)
        return "\n".join(text_runs)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return ""


def extract_text_from_txt_md_log(filepath):
    """Extract text from TXT, MD, LOG."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""


def extract_text_from_eml(filepath):
    """Extract text from EML (email) file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            msg_str = f.read()
        msg = message_from_string(msg_str, policy=policy.default)
        text_parts = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    text_parts.append(part.get_payload(
                        decode=True).decode('utf-8', errors='ignore'))
        else:
            text_parts.append(msg.get_payload(
                decode=True).decode('utf-8', errors='ignore'))
        return "\n".join(text_parts)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return ""


def extract_text_from_image(filepath):
    """Extract text from image using OCR."""
    try:
        reader = easyocr.Reader(['en'])  # Add more languages if needed
        # detail=0 returns only text
        result = reader.readtext(filepath, detail=0)
        return "\n".join(result)
    except Exception as e:
        print(f"Error performing OCR on {filepath}: {e}")
        return ""


def extract_text_from_csv_xlsx(filepath):
    """Extract text from CSV or XLSX using pandas."""
    try:
        if filepath.lower().endswith('.csv'):
            df = pd.read_csv(filepath)
        else:  # .xlsx
            df = pd.read_excel(filepath)
        # Convert DataFrame to string, separating cells with newlines
        # This might need refinement based on how tables are expected to be understood
        # Using sep='\n' might not be ideal
        text = df.to_csv(index=False, sep='\n')
        # A better approach might be to iterate rows/columns explicitly
        text = df.to_string(index=False)
        return text
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return ""


def extract_text_from_json(filepath):
    """Extract text from JSON, focusing on string values."""
    try:
        import json
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        # This is a simple approach, might need adjustment for complex nested structures

        def extract_strings(obj):
            strings = []
            if isinstance(obj, dict):
                for v in obj.values():
                    strings.extend(extract_strings(v))
            elif isinstance(obj, list):
                for item in obj:
                    strings.extend(extract_strings(item))
            elif isinstance(obj, str):
                strings.append(obj)
            return strings
        text_list = extract_strings(data)
        return "\n".join(text_list)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return ""


def extract_text_from_zip(filepath, collection, language_tag=None):
    """Extract and process files within a ZIP archive."""
    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            for member_name in zip_ref.namelist():
                # Only process files within the ZIP
                if not member_name.endswith('/'):  # Skip directories
                    with tempfile.TemporaryDirectory() as temp_dir:
                        extracted_path = zip_ref.extract(
                            member_name, path=temp_dir)
                        # Recursively process the extracted file
                        process_document(
                            collection, extracted_path, language_tag)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False  # Indicate failure for the zip itself


def extract_text_from_py(filepath):
    """Extract text from Python file (comments, docstrings, strings)."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Simple regex to find comments and docstrings
        # This is basic and might miss complex cases or parse errors
        comment_pattern = r'#[^\n]*'
        docstring_pattern = r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''

        comments = re.findall(comment_pattern, content)
        docstrings = re.findall(docstring_pattern, content)

        all_text = "\n".join(comments + docstrings)
        # Optionally, also include the raw code content
        # all_text += "\n" + content
        return all_text
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return ""


def extract_text_from_yml(filepath):
    """Extract text from YAML file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = yaml.safe_load(f)
        # This is basic, loads structure, might need specific key extraction
        # For now, just convert the loaded data to string
        # This might not be ideal for complex structures or if only specific keys are relevant
        import json  # Use json for simple string representation
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return ""


def extract_text_from_tex(filepath):
    """Extract text from TeX file (basic approach, might not handle complex macros well)."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # Remove common LaTeX commands and environments for basic text extraction
        # This is a very simple approach
        # text = re.sub(r'\\[a-zA-Z]+', '', content) # Remove commands
        # text = re.sub(r'\\begin\{.*?\}.*?\\end\{.*?\}', '', content, flags=re.DOTALL) # Remove environments
        # A more robust solution might require a LaTeX parser like plasTeX
        # For now, just return the content, assuming the LLM might understand some LaTeX
        # Or use a library like latex2text if available and suitable
        # return latex2text.LatexNodes2Text().latex_to_text(content)
        # As a fallback, just return the raw content for the LLM to process
        return content
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return ""


def process_document(collection, filepath, language_tag=None):
    """Process any supported document type."""
    # --- NEW: Handle ZIP files first ---
    if filepath.lower().endswith('.zip'):
        print(f"Processing ZIP file: {filepath}")
        extract_text_from_zip(filepath, collection, language_tag)
        # ZIP processing involves adding sub-files, so no direct upsert here
        return True  # Assume successful processing of the zip container itself

    # Determine text extraction function based on file extension
    ext = os.path.splitext(filepath)[1].lower()
    text_extractor = {
        '.pdf': extract_text_from_pdf,
        '.docx': extract_text_from_docx,
        '.pptx': extract_text_from_pptx,
        '.txt': extract_text_from_txt_md_log,
        '.md': extract_text_from_txt_md_log,
        '.log': extract_text_from_txt_md_log,
        '.eml': extract_text_from_eml,
        '.png': extract_text_from_image,
        '.jpg': extract_text_from_image,
        '.gif': extract_text_from_image,
        '.csv': extract_text_from_csv_xlsx,
        '.xlsx': extract_text_from_csv_xlsx,
        '.json': extract_text_from_json,
        '.py': extract_text_from_py,
        '.yml': extract_text_from_yml,
        '.yaml': extract_text_from_yml,  # Handle .yaml as well
        '.tex': extract_text_from_tex,
    }.get(ext)

    if not text_extractor:
        print(f"Unsupported file type: {filepath}")
        return False

    try:
        print(f"Processing {filepath}...")
        text = text_extractor(filepath)
        if not text.strip():
            print(f"Warning: No text extracted from {filepath}")
            # Decide: return False to indicate failure, or continue with empty text (maybe not ideal)
            # For now, continue but log if empty
            if not text.strip():
                print(f"  -> Extracted text was empty or whitespace only.")
                # Consider returning False here if empty text is problematic
                # return False

        # Chunk the text (reuse existing logic)
        chunk_size = 1000
        chunks = [text[i:i+chunk_size]
                  for i in range(0, len(text), chunk_size)]
        doc_id_base = os.path.splitext(os.path.basename(filepath))[0]
        doc_id = f"{doc_id_base}_{language_tag}" if language_tag else doc_id_base
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"language": language_tag, "source_doc": doc_id_base, "file_path": filepath}
                     for _ in chunks] if language_tag else [{"source_doc": doc_id_base, "file_path": filepath} for _ in chunks]

        collection.upsert(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        print(f"  -> Added {len(chunks)} chunks to ChromaDB.")
        return True
    except Exception as e:
        print(f"Error processing {filepath} after extraction: {e}")
        return False
