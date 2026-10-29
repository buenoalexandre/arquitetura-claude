"""Provedor determinístico e offline para desenvolvimento e testes.

Permite roteirizar respostas e injetar falhas, o que torna testáveis os caminhos de
retentativa, circuit breaker e fallback sem gastar tokens nem depender de rede.
"""

from __future__ import annotations

import asyncio
from collections import deque

from app.llm.provider import LLMRequest, LLMResponse, TransientLLMError
from app.llm.tokens import estimate_tokens


class FakeProvider:
    name = "fake"

    def __init__(
        self,
        responses: list[str] | None = None,
        fail_times: int = 0,
        latency_seconds: float = 0.0,
        failing_models: set[str] | None = None,
    ) -> None:
        self._responses: deque[str] = deque(responses or [])
        self._fail_times = fail_times
        self._latency = latency_seconds
        self._failing_models = failing_models or set()
        self.calls: list[LLMRequest] = []

    async def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        if self._latency:
            await asyncio.sleep(self._latency)
        if request.model in self._failing_models:
            raise TransientLLMError(f"modelo {request.model} indisponível (simulado)")
        if self._fail_times > 0:
            self._fail_times -= 1
            raise TransientLLMError("falha transitória simulada")

        last_user = next((m.content for m in reversed(request.messages) if m.role == "user"), "")
        text = self._responses.popleft() if self._responses else f"Resposta simulada: {last_user}"
        prompt_text = request.system + "".join(m.content for m in request.messages)
        return LLMResponse(
            text=text,
            model=request.model,
            input_tokens=estimate_tokens(prompt_text),
            output_tokens=estimate_tokens(text),
            stop_reason="end_turn",
        )
