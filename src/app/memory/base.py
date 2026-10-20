"""Contratos de memória da aplicação.

- Memória de curto prazo: histórico da conversa atual, limitado por orçamento de tokens.
- Memória de longo prazo: fatos/preferências duráveis por usuário, com TTL e direito ao
  esquecimento. Ver docs/ai/memory-strategy.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import uuid4

from app.domain.models import Message

MemoryKind = Literal["fact", "preference", "summary"]


def utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass
class MemoryRecord:
    namespace: str
    content: str
    kind: MemoryKind = "fact"
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: datetime = field(default_factory=utcnow)
    expires_at: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at is not None and self.expires_at <= now


class ShortTermStore(Protocol):
    async def append(self, session_key: str, message: Message) -> None: ...
    async def window(self, session_key: str, max_tokens: int) -> list[Message]: ...
    async def clear(self, session_key: str) -> None: ...
    async def clear_prefix(self, prefix: str) -> int: ...


class LongTermStore(Protocol):
    async def put(self, record: MemoryRecord) -> None: ...
    async def search(self, namespace: str, query: str, limit: int) -> list[MemoryRecord]: ...
    async def forget_namespace(self, namespace: str) -> int: ...
    async def purge_expired(self, now: datetime) -> int: ...
