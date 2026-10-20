"""Memória de longo prazo em processo, com busca por sobreposição de termos.

É a implementação de referência do contrato ``LongTermStore``. Para busca semântica real,
implemente o mesmo contrato sobre um banco vetorial (pgvector, Qdrant, Chroma) — ver
docs/architecture/adr/0005-memory-strategy.md.
"""

from __future__ import annotations

import asyncio
import re
from collections import defaultdict
from datetime import datetime

from app.memory.base import MemoryRecord, utcnow

_WORD = re.compile(r"\w{3,}", re.UNICODE)


def _terms(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text)}


class InMemoryLongTermStore:
    def __init__(self) -> None:
        self._records: dict[str, list[MemoryRecord]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def put(self, record: MemoryRecord) -> None:
        async with self._lock:
            existing = self._records[record.namespace]
            # Atualização: mesmo conteúdo substitui o registro anterior em vez de duplicar.
            existing[:] = [r for r in existing if r.content != record.content]
            existing.append(record)

    async def search(self, namespace: str, query: str, limit: int) -> list[MemoryRecord]:
        now = utcnow()
        query_terms = _terms(query)
        scored: list[tuple[int, datetime, MemoryRecord]] = []
        for record in self._records.get(namespace, []):
            if record.is_expired(now):
                continue
            score = len(query_terms & _terms(record.content))
            if score or record.kind == "preference":
                scored.append((score, record.created_at, record))
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [record for _, _, record in scored[:limit]]

    async def forget_namespace(self, namespace: str) -> int:
        async with self._lock:
            return len(self._records.pop(namespace, []))

    async def purge_expired(self, now: datetime) -> int:
        async with self._lock:
            removed = 0
            for namespace, records in self._records.items():
                kept = [r for r in records if not r.is_expired(now)]
                removed += len(records) - len(kept)
                self._records[namespace] = kept
            return removed
