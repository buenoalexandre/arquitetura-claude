"""Memória de curto prazo em processo.

Mantém o histórico por sessão e devolve a janela mais recente que cabe no orçamento de
tokens. Em produção com várias réplicas, troque por Redis mantendo o mesmo contrato.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict

from app.domain.models import Message
from app.llm.tokens import estimate_tokens


class InMemoryShortTermStore:
    def __init__(self, max_messages_per_session: int = 200) -> None:
        self._sessions: dict[str, list[Message]] = defaultdict(list)
        self._max_messages = max_messages_per_session
        self._lock = asyncio.Lock()

    async def append(self, session_key: str, message: Message) -> None:
        async with self._lock:
            history = self._sessions[session_key]
            history.append(message)
            if len(history) > self._max_messages:
                del history[: len(history) - self._max_messages]

    async def window(self, session_key: str, max_tokens: int) -> list[Message]:
        """Mensagens mais recentes cujo total cabe em ``max_tokens``.

        A janela sempre começa em uma mensagem do usuário, exigência da API de mensagens.
        """
        history = list(self._sessions.get(session_key, []))
        selected: list[Message] = []
        budget = max_tokens
        for message in reversed(history):
            cost = estimate_tokens(message.content)
            if cost > budget and selected:
                break
            selected.append(message)
            budget -= cost
        selected.reverse()
        while selected and selected[0].role != "user":
            selected.pop(0)
        return selected

    async def clear(self, session_key: str) -> None:
        async with self._lock:
            self._sessions.pop(session_key, None)

    async def clear_prefix(self, prefix: str) -> int:
        async with self._lock:
            keys = [k for k in self._sessions if k.startswith(prefix)]
            for key in keys:
                del self._sessions[key]
            return len(keys)
