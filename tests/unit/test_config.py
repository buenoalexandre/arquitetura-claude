import pytest
from pydantic import SecretStr, ValidationError

from app.core.config import LLMSettings, SecuritySettings, Settings, _deep_merge

pytestmark = pytest.mark.unit


def test_deep_merge_preserves_nested_keys() -> None:
    merged = _deep_merge({"llm": {"model": "a", "provider": "fake"}}, {"llm": {"model": "b"}})
    assert merged == {"llm": {"model": "b", "provider": "fake"}}


def test_parsed_api_keys() -> None:
    sec = SecuritySettings(api_keys=SecretStr("k1:user, k2:admin,invalid"))
    assert sec.parsed_api_keys() == {"k1": "user", "k2": "admin"}


def test_production_rejects_insecure_defaults() -> None:
    with pytest.raises(ValidationError):
        Settings(env="production", llm=LLMSettings(provider="anthropic"))


def test_production_rejects_fake_provider() -> None:
    with pytest.raises(ValidationError):
        Settings(
            env="production",
            llm=LLMSettings(provider="fake"),
            security=SecuritySettings(jwt_secret=SecretStr("a-real-secret")),
        )


def test_env_variable_overrides_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_LLM__MODEL", "claude-haiku-4-5")
    assert Settings().llm.model == "claude-haiku-4-5"


def test_environment_yaml_overrides_base(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    assert Settings().observability.log_level == "DEBUG"
