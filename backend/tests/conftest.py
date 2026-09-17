# backend/tests/conftest.py
"""
Shared test fixtures.

Two things this file is careful about, because both were the reason the old
suite could not run:

1. `main.py` constructs a Groq client at import time, which raises if no API key
   is present. We set a dummy key *before* anything imports `main`. It is never
   used to make a real call — every test replaces `main.groq_client`.

2. The rate-limit middleware keeps per-process state in `main.usage`. Without
   resetting it between tests, the 6th request to `/api/chat` across the whole
   suite would start returning 429. We clear it around every test.
"""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make `main`, `prompts`, `document_processor` importable when pytest is run
# from the `backend/` directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Provide a dummy key so `Groq(api_key=...)` at import time in main.py succeeds.
# Tests never exercise the real client; they patch `main.groq_client`.
os.environ.setdefault("GROQ_API_KEY", "test-key-not-used")
os.environ["TESTING"] = "1"


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    """Clear the in-memory rate-limit state before and after each test."""
    import main
    main.usage.clear()
    yield
    main.usage.clear()


@pytest.fixture
def client():
    """
    A TestClient with the vector DB fully mocked so app startup does no real
    I/O and loads no embedding model. Individual tests override
    `main.chroma_collection` / `main.groq_client` to program behaviour.
    """
    with patch("main.chromadb.PersistentClient") as mock_persistent:
        mock_collection = MagicMock()
        mock_persistent.return_value.get_collection.return_value = mock_collection

        from fastapi.testclient import TestClient
        import main

        with TestClient(main.app) as test_client:
            # Expose the startup-installed mock for convenience.
            test_client.chroma_collection = mock_collection
            yield test_client
