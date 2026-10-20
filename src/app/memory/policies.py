"""Políticas de memória: o que pode ser guardado, por quanto tempo e em que forma."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from app.core.config import MemorySettings
from app.guardrails.input import detect_prompt_injection, redact_pii
from app.memory.base import MemoryKind, MemoryRecord, utcnow


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str | None = None


class MemoryPolicy:
    def __init__(self, settings: MemorySettings) -> None:
        self._settings = settings

    def evaluate(self, content: str) -> PolicyDecision:
        if len(content.strip()) < 3:
            return PolicyDecision(False, "conteúdo vazio ou trivial")
        if detect_prompt_injection(content):
            # Memória envenenada é um vetor de injeção persistente: nunca armazenar.
            return PolicyDecision(False, "conteúdo com padrão de injeção de prompt")
        return PolicyDecision(True)

    def build_record(self, namespace: str, content: str, kind: MemoryKind) -> MemoryRecord:
        if self._settings.redact_pii:
            content = redact_pii(content)
        return MemoryRecord(
            namespace=namespace,
            content=content.strip(),
            kind=kind,
            expires_at=utcnow() + timedelta(days=self._settings.long_term_ttl_days),
        )
