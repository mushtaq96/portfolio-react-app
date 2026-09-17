# backend/tests/test_document_processor.py
"""
Tests for document_processor.

Fixes over the previous version:
- Patch `chromadb.PersistentClient` (what the code actually uses), not
  `chromadb.Client`, and at the module's import site.
- Assert on `upsert` (what process_pdf actually calls), not `add`, and check the
  chunk ids/shape rather than just "was called".
"""
from unittest.mock import MagicMock, patch

from document_processor import initialize_collection, process_pdf, process_document


def create_dummy_pdf(path):
    """Create a minimal one-line PDF for extraction tests."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas(str(path), pagesize=letter)
    c.drawString(100, 750, "Test PDF Content")
    c.save()


def test_initialize_collection_uses_persistent_client_and_names_collection():
    with patch("document_processor.chromadb.PersistentClient") as mock_client, \
         patch("document_processor.embedding_functions.SentenceTransformerEmbeddingFunction") as mock_ef:
        mock_collection = MagicMock()
        mock_collection.name = "portfolio_docs"
        mock_client.return_value.get_or_create_collection.return_value = mock_collection

        col = initialize_collection()

        assert col.name == "portfolio_docs"
        mock_client.assert_called_once()
        mock_client.return_value.get_or_create_collection.assert_called_once()
        # The embedding function was constructed and passed to the collection.
        mock_ef.assert_called_once()


def test_process_pdf_upserts_chunks_with_language_tagged_ids(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    create_dummy_pdf(pdf_path)

    mock_collection = MagicMock()
    result = process_pdf(mock_collection, str(pdf_path), language_tag="en")

    assert result is True
    mock_collection.upsert.assert_called_once()

    kwargs = mock_collection.upsert.call_args.kwargs
    assert kwargs["documents"], "expected at least one text chunk"
    assert len(kwargs["ids"]) == len(kwargs["documents"])
    assert all(chunk_id.startswith("test_en_chunk_") for chunk_id in kwargs["ids"])


def test_process_pdf_returns_false_on_bad_file():
    mock_collection = MagicMock()
    result = process_pdf(mock_collection, "/does/not/exist.pdf")
    assert result is False
    mock_collection.upsert.assert_not_called()


def test_process_document_rejects_unsupported_type():
    assert process_document(MagicMock(), "notes.txt") is False
