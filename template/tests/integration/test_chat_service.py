"""Integração entre serviço, memória, prompts, guardrails e LLM (sem HTTP)."""

import pytest

from app.container import build_container
from app.core.config import Settings
from app.core.security import Principal, Role
from app.domain.models import ChatRequest, RememberRequest
from app.llm.fake_provider import FakeProvider

pytestmark = pytest.mark.integration

ALICE = Principal("alice", Role.USER)
BOB = Principal("bob", Role.USER)


async def test_history_is_sent_on_next_turn(settings: Settings) -> None:
    provider = FakeProvider()
    service = build_container(settings, provider).chat_service
    await service.chat(ALICE, ChatRequest(session_id="s1", message="Meu nome é Alice"))
    await service.chat(ALICE, ChatRequest(session_id="s1", message="Qual é meu nome?"))
    second_call = provider.calls[-1]
    assert [m.role for m in second_call.messages] == ["user", "assistant", "user"]
    assert "Alice" in second_call.messages[0].content


async def test_sessions_are_isolated_between_users(settings: Settings) -> None:
    provider = FakeProvider()
    service = build_container(settings, provider).chat_service
    await service.chat(ALICE, ChatRequest(session_id="s1", message="segredo da alice"))
    await service.chat(BOB, ChatRequest(session_id="s1", message="oi"))
    assert all("segredo" not in m.content for m in provider.calls[-1].messages)


async def test_long_term_memory_is_recalled_into_system_prompt(settings: Settings) -> None:
    provider = FakeProvider()
    service = build_container(settings, provider).chat_service
    await service.remember(ALICE, RememberRequest(content="Alice programa em Python", kind="fact"))
    await service.chat(ALICE, ChatRequest(session_id="s2", message="Que linguagem Python?"))
    system = provider.calls[-1].system
    assert "Alice programa em Python" in system
    assert "não instruções" in system


async def test_forget_removes_everything(settings: Settings) -> None:
    service = build_container(settings, FakeProvider()).chat_service
    await service.remember(ALICE, RememberRequest(content="fato importante"))
    await service.chat(ALICE, ChatRequest(session_id="s1", message="oi"))
    result = await service.forget(ALICE)
    assert result.deleted_long_term == 1
    assert result.cleared_sessions == 1


async def test_audit_records_prompt_version_without_raw_content(settings: Settings) -> None:
    container = build_container(settings, FakeProvider())
    await container.chat_service.chat(ALICE, ChatRequest(session_id="s", message="dado sigiloso"))
    event = container.audit.events[-1]
    assert event.prompt_version == "v1"
    assert event.prompt_sha
    assert "dado sigiloso" not in repr(event)


async def test_pii_is_redacted_in_stored_history(settings: Settings) -> None:
    provider = FakeProvider()
    service = build_container(settings, provider).chat_service
    await service.chat(ALICE, ChatRequest(session_id="s", message="meu email é a@b.com"))
    await service.chat(ALICE, ChatRequest(session_id="s", message="ok"))
    assert "a@b.com" not in provider.calls[-1].messages[0].content
