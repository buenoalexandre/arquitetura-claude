"""Testes de desempenho da sobrecarga da aplicação (sem o tempo do modelo).

Medem o custo da nossa camada — guardrails, memória, prompts, serialização — usando o
FakeProvider. Para carga real ponta a ponta, use Locust ou k6 em homologação
(ver docs/guides/testing.md).
"""

import asyncio
import os
import statistics
import time

import pytest
from fastapi.testclient import TestClient

from app.container import build_container
from app.core.config import Settings
from app.core.security import Principal, Role
from app.domain.models import ChatRequest
from app.llm.fake_provider import FakeProvider

pytestmark = pytest.mark.performance

# Folga para runners de CI compartilhados; ajuste por ambiente com PERF_P95_BUDGET_MS.
P95_BUDGET_MS = float(os.environ.get("PERF_P95_BUDGET_MS", "100"))


def test_chat_overhead_p95_within_budget(client: TestClient, user_headers: dict[str, str]) -> None:
    for _ in range(5):  # aquecimento: primeira chamada inclui imports e caches frios
        client.post("/v1/chat", headers=user_headers, json={"session_id": "w", "message": "oi"})
    durations = []
    for i in range(50):
        started = time.perf_counter()
        response = client.post(
            "/v1/chat", headers=user_headers, json={"session_id": "perf", "message": f"oi {i}"}
        )
        durations.append((time.perf_counter() - started) * 1000)
        assert response.status_code == 200
    p95 = statistics.quantiles(durations, n=20)[18]
    assert p95 < P95_BUDGET_MS, f"p95={p95:.1f}ms"


async def test_concurrent_sessions(settings: Settings) -> None:
    service = build_container(settings, FakeProvider(latency_seconds=0.05)).chat_service
    principal = Principal("load", Role.USER)
    started = time.perf_counter()
    await asyncio.gather(
        *(service.chat(principal, ChatRequest(session_id=f"s{i}", message="oi")) for i in range(50))
    )
    elapsed = time.perf_counter() - started
    # Em série seriam 50 x 50 ms = 2,5 s; exigir menos da metade disso detecta serialização
    # sem depender da velocidade da máquina.
    assert elapsed < 1.25, f"chamadas concorrentes parecem serializadas ({elapsed:.2f}s)"
