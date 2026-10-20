"""Composição de dependências (composition root).

Único lugar que conhece as implementações concretas. Serviços recebem interfaces, o que
permite trocar provedores e armazenamentos por configuração ou em testes.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings
from app.domain.services.chat_service import ChatService
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.fake_provider import FakeProvider
from app.llm.provider import LLMProvider
from app.llm.resilience import ResilientLLMClient
from app.memory.long_term import InMemoryLongTermStore
from app.memory.policies import MemoryPolicy
from app.memory.short_term import InMemoryShortTermStore
from app.observability.audit import AuditLogger
from app.observability.metrics import Metrics
from app.prompts.loader import PromptRegistry


@dataclass
class Container:
    settings: Settings
    metrics: Metrics
    audit: AuditLogger
    llm: ResilientLLMClient
    chat_service: ChatService


def build_provider(settings: Settings) -> LLMProvider:
    if settings.llm.provider == "anthropic":
        return AnthropicProvider(timeout_seconds=settings.llm.timeout_seconds)
    return FakeProvider()


def build_container(settings: Settings, provider: LLMProvider | None = None) -> Container:
    metrics = Metrics()
    audit = AuditLogger()
    llm = ResilientLLMClient(provider or build_provider(settings), settings.llm, metrics)
    prompts = PromptRegistry(
        settings.resolve_path(settings.prompts.directory),
        settings.resolve_path(settings.prompts.registry_file),
    )
    chat_service = ChatService(
        settings=settings,
        llm=llm,
        prompts=prompts,
        short_term=InMemoryShortTermStore(),
        long_term=InMemoryLongTermStore(),
        memory_policy=MemoryPolicy(settings.memory),
        audit=audit,
        metrics=metrics,
    )
    return Container(
        settings=settings, metrics=metrics, audit=audit, llm=llm, chat_service=chat_service
    )
