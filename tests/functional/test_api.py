"""Testes ponta a ponta pela API HTTP."""

import pytest
from fastapi.testclient import TestClient

from app.llm.fake_provider import FakeProvider
from tests.conftest import ClientFactory

pytestmark = pytest.mark.functional


def test_health_is_public(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json()["llm_circuit"] == "closed"


def test_chat_flow(client: TestClient, user_headers: dict[str, str]) -> None:
    response = client.post(
        "/v1/chat", headers=user_headers, json={"session_id": "abc", "message": "Olá"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reply"]
    assert body["prompt_version"] == "assistant@v1"
    assert body["usage"]["input_tokens"] > 0
    assert response.headers["x-request-id"]


def test_request_id_is_propagated(client: TestClient, user_headers: dict[str, str]) -> None:
    response = client.get("/health", headers={"X-Request-ID": "req-123", **user_headers})
    assert response.headers["x-request-id"] == "req-123"


def test_validation_error(client: TestClient, user_headers: dict[str, str]) -> None:
    response = client.post("/v1/chat", headers=user_headers, json={"session_id": "a b"})
    assert response.status_code == 422


def test_memory_remember_and_forget(client: TestClient, user_headers: dict[str, str]) -> None:
    stored = client.post("/v1/memory", headers=user_headers, json={"content": "Gosto de café"})
    assert stored.json()["stored"] is True
    forgotten = client.delete("/v1/memory", headers=user_headers)
    assert forgotten.json()["deleted_long_term"] == 1


def test_llm_outage_returns_503_without_internal_details(
    make_client: ClientFactory, user_headers: dict[str, str]
) -> None:
    client = make_client(FakeProvider(fail_times=100))
    response = client.post(
        "/v1/chat", headers=user_headers, json={"session_id": "x", "message": "oi"}
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_unavailable"


def test_metrics_requires_admin(
    client: TestClient, user_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    client.post("/v1/chat", headers=user_headers, json={"session_id": "m", "message": "oi"})
    assert client.get("/v1/metrics", headers=user_headers).status_code == 403
    metrics = client.get("/v1/metrics", headers=admin_headers).json()
    assert "llm_requests_total" in metrics
    assert "llm_latency_ms" in metrics
