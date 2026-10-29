"""Fixtures compartilhadas. Todos os testes rodam offline com o FakeProvider."""

from __future__ import annotations

import os
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

os.environ.setdefault("APP_ENV", "test")

from app.core.config import LLMSettings, SecuritySettings, Settings
from app.llm.fake_provider import FakeProvider
from app.main import create_app

USER_KEY = "user-key-123"
ADMIN_KEY = "admin-key-456"
VIEWER_KEY = "viewer-key-789"

ClientFactory = Callable[[FakeProvider], TestClient]


@pytest.fixture
def settings() -> Settings:
    return Settings(
        env="test",
        llm=LLMSettings(
            provider="fake",
            max_retries=3,
            retry_wait_base_seconds=0,
            timeout_seconds=2,
            requests_per_minute=1000,
        ),
        security=SecuritySettings(
            api_keys=SecretStr(f"{USER_KEY}:user,{ADMIN_KEY}:admin,{VIEWER_KEY}:viewer"),
            jwt_secret=SecretStr("test-secret-with-at-least-32-bytes!!"),
        ),
    )


@pytest.fixture
def fake_provider() -> FakeProvider:
    return FakeProvider()


@pytest.fixture
def make_client(settings: Settings) -> ClientFactory:
    def factory(provider: FakeProvider) -> TestClient:
        return TestClient(create_app(settings, provider))

    return factory


@pytest.fixture
def client(make_client: ClientFactory, fake_provider: FakeProvider) -> TestClient:
    return make_client(fake_provider)


@pytest.fixture
def user_headers() -> dict[str, str]:
    return {"X-API-Key": USER_KEY}


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"X-API-Key": ADMIN_KEY}


@pytest.fixture
def viewer_headers() -> dict[str, str]:
    return {"X-API-Key": VIEWER_KEY}
