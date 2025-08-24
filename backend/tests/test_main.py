# backend/tests/test_main.py
import pytest

def test_chat_api(client):  # Simple synchronous test
    response = client.post("/api/chat", json={
        "message": "Hello",
        "history": [],
        "language": "en"
    })
    assert response.status_code == 200
    assert "response" in response.json()
    assert "context" in response.json()