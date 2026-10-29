"""Endpoints de memória de longo prazo e direito ao esquecimento."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import ContainerDep, require
from app.core.security import Principal
from app.domain.models import ForgetResponse, RememberRequest, RememberResponse

router = APIRouter(prefix="/v1/memory", tags=["memory"])


@router.post("")
async def remember(
    body: RememberRequest,
    container: ContainerDep,
    principal: Annotated[Principal, Depends(require("memory:write"))],
) -> RememberResponse:
    return await container.chat_service.remember(principal, body)


@router.delete("")
async def forget(
    container: ContainerDep,
    principal: Annotated[Principal, Depends(require("memory:delete"))],
) -> ForgetResponse:
    return await container.chat_service.forget(principal)
