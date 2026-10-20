"""Modelos de domínio e contratos da API (independentes do provedor de LLM)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["user", "assistant"]


class Message(BaseModel):
    role: Role
    content: str


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_\-]+$")
    message: str = Field(min_length=1)
    prompt: str = Field(default="assistant", pattern=r"^[a-z0-9_\-]+$")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    model: str
    prompt_version: str
    usage: Usage
    guardrail_flags: list[str] = Field(default_factory=list)


class RememberRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    kind: Literal["fact", "preference"] = "fact"


class RememberResponse(BaseModel):
    id: str
    stored: bool
    reason: str | None = None


class ForgetResponse(BaseModel):
    deleted_long_term: int
    cleared_sessions: int
