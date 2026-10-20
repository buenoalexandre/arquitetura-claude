"""Contrato agnóstico de provedor de LLM.

O domínio depende apenas desta interface. Trocar de provedor (Anthropic, Bedrock, Vertex,
modelo local) significa escrever uma nova implementação, sem tocar nos serviços.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from app.domain.models import Message


@dataclass(frozen=True)
class LLMRequest:
    system: str
    messages: list[Message]
    model: str
    max_tokens: int
    effort: str = "medium"


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str
    metadata: dict[str, str] = field(default_factory=dict)


class TransientLLMError(Exception):
    """Falha temporária (rede, timeout, 429, 5xx): pode ser retentada."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class PermanentLLMError(Exception):
    """Falha que não melhora com retentativa (400, 401, 404, modelo inválido)."""


class RefusalError(Exception):
    """O modelo recusou a solicitação por política de segurança."""


class LLMProvider(Protocol):
    name: str

    async def complete(self, request: LLMRequest) -> LLMResponse: ...
