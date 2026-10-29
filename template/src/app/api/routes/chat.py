"""Endpoints de conversa."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import ContainerDep, require
from app.core.security import Principal
from app.domain.models import ChatRequest, ChatResponse

router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat")
async def chat(
    body: ChatRequest,
    container: ContainerDep,
    principal: Annotated[Principal, Depends(require("chat:write"))],
) -> ChatResponse:
    return await container.chat_service.chat(principal, body)
