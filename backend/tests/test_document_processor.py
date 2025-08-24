# backend/tests/test_document_processor.py
import pytest
from unittest.mock import patch, MagicMock
from document_processor import initialize_collection, process_pdf
from chromadb import Client
from chromadb.utils import embedding_functions

@pytest.fixture
def mock_client():
    mock = MagicMock(spec=Client)
    mock.add = MagicMock(return_value=None)
    return mock

@pytest.fixture
def mock_embedding_func():
    return MagicMock(spec=embedding_functions.SentenceTransformerEmbeddingFunction)

def create_dummy_pdf(path):
    """Helper function to create a test PDF"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    c = canvas.Canvas(str(path), pagesize=letter)
    c.drawString(100, 750, "Test PDF Content")
    c.save()

def test_initialize_collection(mock_client, mock_embedding_func):
    # Patch the required imports
    with patch('chromadb.Client', return_value=mock_client):
        with patch('chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction',
                  return_value=mock_embedding_func):
            col = initialize_collection()
            assert col.name == "portfolio_docs"

def test_process_pdf(mock_client, tmp_path):
    # Create proper PDF file
    pdf_path = tmp_path / "test.pdf"
    create_dummy_pdf(pdf_path)
    
    # Mock ChromaDB operations
    with patch('document_processor.initialize_collection',
              return_value=mock_client):
        process_pdf(mock_client, str(pdf_path))
        mock_client.add.assert_called_once()