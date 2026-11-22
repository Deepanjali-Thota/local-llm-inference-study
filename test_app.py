import json

import requests
from fastapi.testclient import TestClient

import app as app_module

client = TestClient(app_module.app)

GOOD = {"category": "billing", "priority": "high", "summary": "Double charge on card"}
TOO_LONG = {"category": "billing", "priority": "high",
            "summary": "Customer was charged twice for the monthly subscription"}


def fake_ollama(*answers):
    """Return a fake call_ollama that gives back the answers in order."""
    calls = iter(answers)
    return lambda payload: {"response": json.dumps(next(calls))}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_classify_valid_first_try(monkeypatch):
    monkeypatch.setattr(app_module, "call_ollama", fake_ollama(GOOD))
    r = client.post("/classify", json={"ticket": "charged twice"})
    assert r.status_code == 200
    assert r.json()["attempts"] == 1
    assert r.json()["result"]["category"] == "billing"


def test_classify_retry_fixes_it(monkeypatch):
    monkeypatch.setattr(app_module, "call_ollama", fake_ollama(TOO_LONG, GOOD))
    r = client.post("/classify", json={"ticket": "charged twice"})
    assert r.status_code == 200
    assert r.json()["attempts"] == 2


def test_classify_fails_gracefully(monkeypatch):
    monkeypatch.setattr(app_module, "call_ollama", fake_ollama(TOO_LONG, TOO_LONG))
    r = client.post("/classify", json={"ticket": "charged twice"})
    assert r.status_code == 502
    assert "after 2 attempts" in r.json()["detail"]


def test_ollama_down_returns_503(monkeypatch):
    def refuse(*args, **kwargs):
        raise requests.exceptions.ConnectionError()
    monkeypatch.setattr(app_module.requests, "post", refuse)
    r = client.post("/classify", json={"ticket": "charged twice"})
    assert r.status_code == 503


def test_missing_ticket_returns_422():
    r = client.post("/classify", json={})
    assert r.status_code == 422