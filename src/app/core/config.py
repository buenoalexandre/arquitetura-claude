"""Configuração tipada e em camadas.

Precedência (da menor para a maior):
    config/base.yaml < config/<APP_ENV>.yaml < .env < variáveis de ambiente APP_* < argumentos

Variáveis aninhadas usam ``__``: ``APP_LLM__PROVIDER=anthropic`` sobrescreve ``llm.provider``.
Segredos nunca ficam nos YAML: vêm do ambiente ou de um cofre (ver docs/guides/configuration.md).
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, SecretStr, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

ROOT_DIR = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT_DIR / "config"
INSECURE_DEFAULT_SECRET = "change-me-in-every-environment"  # noqa: S105 - valor sentinela

Environment = Literal["development", "test", "staging", "production"]
Effort = Literal["low", "medium", "high", "xhigh", "max"]


class CircuitBreakerSettings(BaseModel):
    failure_threshold: int = 5
    reset_timeout_seconds: float = 30.0


class LLMSettings(BaseModel):
    provider: Literal["fake", "anthropic"] = "fake"
    model: str = "claude-opus-5-5"
    fallback_model: str | None = "claude-sonnet-5-5"
    max_tokens: int = 16000
    effort: Effort = "medium"
    timeout_seconds: float = 60.0
    max_retries: int = 3
    retry_wait_base_seconds: float = 0.5
    requests_per_minute: int = 60
    circuit_breaker: CircuitBreakerSettings = Field(default_factory=CircuitBreakerSettings)


class MemorySettings(BaseModel):
    short_term_max_tokens: int = 8000
    long_term_ttl_days: int = 90
    long_term_recall_limit: int = 5
    redact_pii: bool = True


class PromptSettings(BaseModel):
    directory: str = "prompts"
    registry_file: str = "prompts/registry.yaml"
    default_variables: dict[str, str] = Field(
        default_factory=lambda: {"product_name": "AI App", "max_sentences": "3"}
    )


class GuardrailSettings(BaseModel):
    max_input_chars: int = 20000
    block_prompt_injection: bool = True


class SecuritySettings(BaseModel):
    # Formato: "<chave>:<papel>,<chave>:<papel>"
    api_keys: SecretStr = SecretStr("")
    jwt_secret: SecretStr = SecretStr(INSECURE_DEFAULT_SECRET)
    jwt_algorithm: str = "HS256"
    jwt_ttl_minutes: int = 60

    def parsed_api_keys(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for item in self.api_keys.get_secret_value().split(","):
            key, sep, role = item.strip().partition(":")
            if key and sep:
                result[key] = role
        return result


class ObservabilitySettings(BaseModel):
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = True
    trace_enabled: bool = True
    service_name: str = "ai-app"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} deve conter um mapeamento YAML")
    return data


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


class YamlConfigSource(PydanticBaseSettingsSource):
    """Lê config/base.yaml e sobrepõe config/<APP_ENV>.yaml."""

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        env = os.environ.get("APP_ENV", "development")
        base = _load_yaml(CONFIG_DIR / "base.yaml")
        return _deep_merge(base, _load_yaml(CONFIG_DIR / f"{env}.yaml"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    env: Environment = "development"
    app_name: str = "ai-app"
    llm: LLMSettings = Field(default_factory=LLMSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    prompts: PromptSettings = Field(default_factory=PromptSettings)
    guardrails: GuardrailSettings = Field(default_factory=GuardrailSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSource(settings_cls),
        )

    @model_validator(mode="after")
    def _forbid_insecure_defaults(self) -> Settings:
        if self.env in ("staging", "production"):
            if self.security.jwt_secret.get_secret_value() == INSECURE_DEFAULT_SECRET:
                raise ValueError("APP_SECURITY__JWT_SECRET precisa ser definido fora de dev")
            if self.llm.provider == "fake":
                raise ValueError("O provedor 'fake' não pode ser usado em staging/produção")
        return self

    def resolve_path(self, relative: str) -> Path:
        return ROOT_DIR / relative


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
