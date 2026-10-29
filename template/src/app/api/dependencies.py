"""Dependências FastAPI: container, autenticação e autorização."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Header, Request

from app.container import Container
from app.core.errors import AuthenticationError, AuthorizationError
from app.core.security import Principal, authenticate_api_key, authenticate_jwt


def get_container(request: Request) -> Container:
    container: Container = request.app.state.container
    return container


ContainerDep = Annotated[Container, Depends(get_container)]


async def get_principal(
    container: ContainerDep,
    x_api_key: Annotated[str | None, Header()] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> Principal:
    security = container.settings.security
    if x_api_key:
        return authenticate_api_key(x_api_key, security)
    if authorization and authorization.lower().startswith("bearer "):
        return authenticate_jwt(authorization[7:], security)
    raise AuthenticationError()


def require(permission: str) -> Callable[[Principal], Awaitable[Principal]]:
    async def checker(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
        if not principal.can(permission):
            raise AuthorizationError()
        return principal

    return checker
