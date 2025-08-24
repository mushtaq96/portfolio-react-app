# backend/tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

# Set testing environment
os.environ["TESTING"] = "1"

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session", autouse=True)
def mock_chromadb():
    with patch('chromadb.Client') as mock_client:
        mock_client.return_value.get_or_create_collection.return_value.name = "portfolio_docs"
        mock_client.return_value.add.return_value = None
        yield mock_client

@pytest.fixture(scope="session", autouse=True)
def mock_embedding_func():
    with patch('chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction') as mock_func:
        yield mock_func

@pytest.fixture(scope="session", autouse=True)
def mock_whisper():
    with patch('main.whisper.load_model') as mock:
        mock.return_value.transcribe.return_value = {"text": "test transcription"}
        yield mock