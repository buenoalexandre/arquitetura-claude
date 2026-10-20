"""Autenticação (API key ou JWT) e autorização baseada em papéis (RBAC)."""

from __future__ import annotations

import hmac
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

import jwt

from app.core.config import SecuritySettings
from app.core.errors import AuthenticationError


class Role(StrEnum):
    VIEWER = "viewer"
    USER = "user"
    ADMIN = "admin"


ROLE_PERMISSIONS: dict[Role, frozenset[str]] = {
    Role.VIEWER: frozenset({"health:read"}),
    Role.USER: frozenset({"health:read", "chat:write", "memory:write", "memory:delete"}),
    Role.ADMIN: frozenset(
        {"health:read", "chat:write", "memory:write", "memory:delete", "metrics:read"}
    ),
}


@dataclass(frozen=True)
class Principal:
    subject: str
    role: Role

    def can(self, permission: str) -> bool:
        return permission in ROLE_PERMISSIONS[self.role]


def authenticate_api_key(api_key: str, settings: SecuritySettings) -> Principal:
    for known_key, role in settings.parsed_api_keys().items():
        # Comparação em tempo constante evita ataques de timing.
        if hmac.compare_digest(api_key.encode(), known_key.encode()):
            return Principal(subject=f"apikey:{known_key[:4]}", role=Role(role))
    raise AuthenticationError()


def create_access_token(subject: str, role: Role, settings: SecuritySettings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "role": role.value,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_ttl_minutes),
    }
    return jwt.encode(
        payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm
    )


def authenticate_jwt(token: str, settings: SecuritySettings) -> Principal:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "role"]},
        )
        return Principal(subject=str(payload["sub"]), role=Role(payload["role"]))
    except (jwt.PyJWTError, ValueError) as exc:
        raise AuthenticationError() from exc
