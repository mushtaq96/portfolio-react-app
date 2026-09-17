# backend/tests/test_main.py
"""
Behavioural tests for the /api/chat endpoint.

The old test asserted only `status_code == 200`, which is meaningless: the
endpoint returns 200 on every path, including internal errors. These tests mock
the two external dependencies (the vector store and Groq) and assert on what the
endpoint actually does: it retrieves context and injects it into the LLM prompt.

Note: the endpoint's habit of returning 200 on upstream failure is a known
correctness smell (see TEST_AUDIT.md). It is intentionally *not* fixed in this
branch, whose scope is the test suite + CI. These tests assert current behaviour
and give a corrected version something real to lock down later.
"""
from unittest.mock import MagicMock


def _make_groq_returning(text: str) -> MagicMock:
    """Build a Groq-client double whose completion returns `text`."""
    fake_groq = MagicMock()
    fake_groq.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=text))
    ]
    return fake_groq


def test_chat_returns_answer_grounded_in_retrieved_context(client, monkeypatch):
    import main

    # Program retrieval: the internal path calls collection.query(query_texts=...).
    fake_collection = MagicMock()
    fake_collection.query.return_value = {
        "documents": [["Mushtaq has four years of cloud experience."]]
    }
    monkeypatch.setattr(main, "chroma_collection", fake_collection)
    monkeypatch.setattr(main, "groq_client",
                        _make_groq_returning("He has four years of cloud experience."))

    resp = client.post("/api/chat", json={"message": "cloud experience?", "language": "en"})

    assert resp.status_code == 200
    body = resp.json()
    assert "cloud" in body["response"].lower()

    # Retrieval actually happened.
    fake_collection.query.assert_called_once()

    # The retrieved chunk was passed to the LLM as context (the core RAG contract).
    sent_prompt = main.groq_client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "four years of cloud experience" in sent_prompt


def test_chat_handles_missing_knowledge_base(client, monkeypatch):
    import main
    monkeypatch.setattr(main, "chroma_collection", None)

    resp = client.post("/api/chat", json={"message": "hi", "language": "en"})

    assert resp.status_code == 200
    assert "unavailable" in resp.json()["response"].lower()


def test_chat_response_has_expected_shape(client, monkeypatch):
    import main
    fake_collection = MagicMock()
    fake_collection.query.return_value = {"documents": [["some context"]]}
    monkeypatch.setattr(main, "chroma_collection", fake_collection)
    monkeypatch.setattr(main, "groq_client", _make_groq_returning("an answer"))

    resp = client.post("/api/chat", json={"message": "q", "language": "en"})

    body = resp.json()
    assert set(["response", "context"]).issubset(body.keys())
    assert isinstance(body["context"], list)

# NOTE: a rate-limit test is deliberately omitted. Raising HTTPException inside a
# BaseHTTPMiddleware (which @app.middleware("http") is) is a Starlette gotcha that
# can surface as a 500 instead of the intended 429 — so the limiter's status code
# is itself suspect. That belongs with the endpoint-status-code fix tracked in
# TEST_AUDIT.md, not in this test-only branch.
