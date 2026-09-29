# backend/tests/test_main.py
"""
Behavioural tests for the backend API.

The vector store, the embedding service and Groq are all replaced with doubles, so
these tests exercise this app's own logic: prompt assembly, history handling,
error mapping, validation and rate limiting.
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from starlette.requests import Request


def _groq_returning(text: str) -> MagicMock:
    fake = MagicMock()
    fake.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=text))
    ]
    return fake


def _sent_messages(groq: MagicMock) -> list:
    return groq.chat.completions.create.call_args.kwargs["messages"]


@pytest.fixture
def wired(client, monkeypatch):
    """A client whose vector store and LLM are fakes, returned for inspection."""
    import main

    collection = MagicMock()
    collection.query.return_value = {
        "documents": [["Mushtaq has four years of cloud experience."]]
    }
    groq = _groq_returning("He has four years of cloud experience.")
    monkeypatch.setattr(main, "chroma_collection", collection)
    monkeypatch.setattr(main, "groq_client", groq)
    return SimpleNamespace(client=client, collection=collection, groq=groq)


def _post(client, message="cloud experience?", **extra):
    headers = extra.pop("headers", None)
    return client.post(
        "/api/chat", json={"message": message, "language": "en", **extra}, headers=headers
    )


# --- RAG behaviour -----------------------------------------------------------
def test_answer_is_grounded_in_retrieved_context(wired):
    resp = _post(wired.client)

    assert resp.status_code == 200
    assert "cloud" in resp.json()["response"].lower()
    wired.collection.query.assert_called_once()
    assert wired.collection.query.call_args.kwargs["query_texts"] == ["cloud experience?"]

    messages = _sent_messages(wired.groq)
    assert messages[0]["role"] == "system"
    assert "four years of cloud experience" in messages[0]["content"]
    assert messages[-1] == {"role": "user", "content": "cloud experience?"}


def test_context_is_hidden_by_default_and_available_when_debugging(wired, monkeypatch):
    import main

    assert _post(wired.client).json()["context"] == []

    monkeypatch.setattr(main, "DEBUG_CONTEXT", True)
    assert "four years" in _post(wired.client).json()["context"][0]


def test_no_retrieval_hits_still_answers_with_a_sentinel(wired):
    wired.collection.query.return_value = {"documents": [[]]}

    assert _post(wired.client).status_code == 200
    assert "No relevant information" in _sent_messages(wired.groq)[0]["content"]


# --- Conversation history ----------------------------------------------------
def test_history_becomes_conversation_turns_and_ui_bubbles_are_dropped(wired):
    history = [
        {"text": "Hi, I'm the assistant", "sender": "bot-welcome"},
        {"text": "What do you do?", "sender": "user"},
        {"text": "I build backends.", "sender": "bot"},
        {"text": "Sorry, offline", "sender": "bot-error"},
    ]

    _post(wired.client, message="Which languages do you use, exactly?", history=history)

    roles = [m["role"] for m in _sent_messages(wired.groq)]
    assert roles == ["system", "user", "assistant", "user"]
    contents = " ".join(m["content"] for m in _sent_messages(wired.groq))
    assert "Sorry, offline" not in contents and "Hi, I'm the assistant" not in contents


def test_history_is_limited_to_recent_turns(wired):
    import main

    history = [
        {"text": f"turn {i}", "sender": "user" if i % 2 == 0 else "bot"} for i in range(20)
    ]

    _post(wired.client, history=history)

    messages = _sent_messages(wired.groq)
    assert len(messages) == 1 + main.MAX_HISTORY_TURNS + 1
    assert messages[1]["content"] == f"turn {20 - main.MAX_HISTORY_TURNS}"


def test_short_followup_reuses_previous_question_for_retrieval(wired):
    history = [{"text": "Tell me about your Azure work", "sender": "user"}]

    _post(wired.client, message="and Kubernetes?", history=history)

    query = wired.collection.query.call_args.kwargs["query_texts"][0]
    assert "Azure" in query and "Kubernetes" in query


def test_long_question_is_retrieved_on_its_own(wired):
    history = [{"text": "Tell me about your Azure work", "sender": "user"}]
    question = "Which programming languages do you use most at work every day?"

    _post(wired.client, message=question, history=history)

    assert wired.collection.query.call_args.kwargs["query_texts"] == [question]


# --- Errors map to real status codes ----------------------------------------
def test_missing_knowledge_base_returns_503(client, monkeypatch):
    import main

    monkeypatch.setattr(main, "chroma_collection", None)
    assert _post(client).status_code == 503


def test_missing_llm_client_returns_503(client, monkeypatch):
    import main

    monkeypatch.setattr(main, "groq_client", None)
    assert _post(client).status_code == 503


def test_llm_failure_returns_502_and_does_not_leak_the_error(wired):
    wired.groq.chat.completions.create.side_effect = RuntimeError("secret upstream detail")

    resp = _post(wired.client)

    assert resp.status_code == 502
    assert "secret upstream detail" not in resp.text


def test_vector_store_failure_returns_502(wired):
    wired.collection.query.side_effect = RuntimeError("chroma exploded")

    resp = _post(wired.client)

    assert resp.status_code == 502
    assert "chroma exploded" not in resp.text


def test_embedding_service_down_returns_502(wired, monkeypatch):
    import main

    down = MagicMock()
    down.post = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
    monkeypatch.setattr(main, "EMBEDDING_API_URL", "http://embed.test")
    monkeypatch.setattr(main, "httpx_client", down)

    resp = _post(wired.client)

    assert resp.status_code == 502
    assert "connection refused" not in resp.text


def test_embedding_service_vector_is_used_for_the_query(wired, monkeypatch):
    import main

    reply = MagicMock()
    reply.json.return_value = {"embeddings": [[0.1, 0.2]]}
    service = MagicMock()
    service.post = AsyncMock(return_value=reply)
    monkeypatch.setattr(main, "EMBEDDING_API_URL", "http://embed.test")
    monkeypatch.setattr(main, "httpx_client", service)

    assert _post(wired.client).status_code == 200
    assert wired.collection.query.call_args.kwargs["query_embeddings"] == [[0.1, 0.2]]


def test_startup_without_a_collection_degrades_instead_of_crashing(monkeypatch):
    import main
    from fastapi.testclient import TestClient

    monkeypatch.setattr(main, "chroma_collection", None)  # so it is restored afterwards
    with patch("main.chromadb.PersistentClient") as persistent:
        persistent.return_value.get_collection.side_effect = RuntimeError("no such collection")
        with TestClient(main.app) as c:
            assert c.get("/health").json()["knowledge_base"] is False
            assert _post(c).status_code == 503


# --- Input validation --------------------------------------------------------
@pytest.mark.parametrize(
    "payload",
    [
        {"message": "", "language": "en"},
        {"message": "   ", "language": "en"},
        {"message": "x" * 1001, "language": "en"},
        {"message": "hello", "language": "fr"},
        {"language": "en"},
    ],
)
def test_invalid_input_is_rejected_with_422(wired, payload):
    assert wired.client.post("/api/chat", json=payload).status_code == 422
    wired.groq.chat.completions.create.assert_not_called()


# --- Rate limiting -----------------------------------------------------------
def test_sixth_request_is_rejected_with_429_json(wired):
    import main

    for _ in range(main.MAX_REQUESTS):
        assert _post(wired.client).status_code == 200

    resp = _post(wired.client)

    assert resp.status_code == 429
    assert "Rate limit" in resp.json()["detail"]
    assert int(resp.headers["retry-after"]) > 0


def test_429_carries_cors_headers_so_the_browser_can_read_it(wired):
    import main

    headers = {"Origin": "https://example.com"}
    for _ in range(main.MAX_REQUESTS):
        _post(wired.client, headers=headers)

    resp = _post(wired.client, headers=headers)

    assert resp.status_code == 429
    assert resp.headers["access-control-allow-origin"] == "*"


def test_limit_is_per_client_ip_from_forwarded_header(wired):
    import main

    for _ in range(main.MAX_REQUESTS):
        _post(wired.client, headers={"X-Forwarded-For": "203.0.113.7"})

    assert _post(wired.client, headers={"X-Forwarded-For": "203.0.113.7"}).status_code == 429
    assert _post(wired.client, headers={"X-Forwarded-For": "198.51.100.9"}).status_code == 200


def test_spoofing_the_left_side_of_forwarded_header_does_not_evade_the_limit(wired):
    import main

    for i in range(main.MAX_REQUESTS):
        _post(wired.client, headers={"X-Forwarded-For": f"10.0.0.{i}, 203.0.113.7"})

    resp = _post(wired.client, headers={"X-Forwarded-For": "10.9.9.9, 203.0.113.7"})

    assert resp.status_code == 429


def test_only_chat_posts_are_rate_limited(client):
    import main

    for _ in range(main.MAX_REQUESTS + 5):
        assert client.get("/health").status_code == 200


def test_health_reports_dependency_state(client):
    body = client.get("/health").json()

    assert body["status"] == "healthy"
    assert body["knowledge_base"] is True and body["llm"] is True


# --- get_client_ip -----------------------------------------------------------
def _request(forwarded=None, peer="10.0.0.1"):
    headers = [(b"x-forwarded-for", forwarded.encode())] if forwarded else []
    return Request({"type": "http", "headers": headers, "client": (peer, 1234)})


@pytest.mark.parametrize(
    "forwarded, proxies, expected",
    [
        (None, 1, "10.0.0.1"),                       # no header: direct peer
        ("203.0.113.7", 1, "203.0.113.7"),           # one proxy
        ("1.1.1.1, 203.0.113.7", 1, "203.0.113.7"),  # left entry is client-controlled
        ("203.0.113.7, 172.16.0.5", 2, "203.0.113.7"),  # two proxies
        ("203.0.113.7", 2, "10.0.0.1"),              # fewer hops than expected: don't trust
        ("203.0.113.7", 0, "10.0.0.1"),              # no proxy: ignore the header
    ],
)
def test_get_client_ip(monkeypatch, forwarded, proxies, expected):
    import main

    monkeypatch.setattr(main, "TRUSTED_PROXY_COUNT", proxies)
    assert main.get_client_ip(_request(forwarded)) == expected
