import pytest
from pydantic import SecretStr

from app.core.config import SecuritySettings
from app.core.errors import AuthenticationError
from app.core.security import (
    Principal,
    Role,
    authenticate_api_key,
    authenticate_jwt,
    create_access_token,
)

pytestmark = pytest.mark.unit

SETTINGS = SecuritySettings(
    api_keys=SecretStr("abc123:user"), jwt_secret=SecretStr("unit-test-secret-32-bytes-long!!")
)


def test_api_key_authenticates() -> None:
    assert authenticate_api_key("abc123", SETTINGS).role is Role.USER


def test_invalid_api_key_rejected() -> None:
    with pytest.raises(AuthenticationError):
        authenticate_api_key("wrong", SETTINGS)


def test_jwt_round_trip() -> None:
    token = create_access_token("alice", Role.ADMIN, SETTINGS)
    assert authenticate_jwt(token, SETTINGS) == Principal("alice", Role.ADMIN)


def test_tampered_jwt_rejected() -> None:
    token = create_access_token("alice", Role.USER, SETTINGS)
    with pytest.raises(AuthenticationError):
        authenticate_jwt(token[:-2] + "xx", SETTINGS)


def test_rbac_permissions() -> None:
    assert Principal("a", Role.ADMIN).can("metrics:read")
    assert not Principal("u", Role.USER).can("metrics:read")
    assert not Principal("v", Role.VIEWER).can("chat:write")
