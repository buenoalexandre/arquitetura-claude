"""Trilha de auditoria das interações com IA.

Registra quem fez o quê, com qual prompt/modelo e a que custo — sem gravar o conteúdo
bruto das mensagens (apenas tamanho e hash), para não transformar o log em vazamento de dados.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass

from app.core.logging import get_logger

_audit_log = get_logger("audit")


def content_fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class AuditEvent:
    actor: str
    action: str
    resource: str
    outcome: str
    prompt_name: str | None = None
    prompt_version: str | None = None
    prompt_sha: str | None = None
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    input_sha: str | None = None
    input_chars: int = 0
    flags: tuple[str, ...] = ()


class AuditLogger:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []  # útil em testes; produção usa só o log

    def record(self, event: AuditEvent) -> None:
        self.events.append(event)
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
        _audit_log.info("audit_event", **asdict(event))
