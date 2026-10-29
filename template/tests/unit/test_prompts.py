import pytest

from app.core.config import ROOT_DIR
from app.core.errors import PromptError
from app.prompts.loader import PromptRegistry

pytestmark = pytest.mark.unit


@pytest.fixture
def registry() -> PromptRegistry:
    return PromptRegistry(ROOT_DIR / "prompts", ROOT_DIR / "prompts" / "registry.yaml")


def test_renders_active_version_with_policies(registry: PromptRegistry) -> None:
    prompt = registry.render("assistant", {"product_name": "Acme"})
    assert prompt.version == "v1"
    assert "Acme" in prompt.text
    assert "Política de segurança" in prompt.text
    assert len(prompt.sha256) == 64


def test_hash_is_stable(registry: PromptRegistry) -> None:
    first = registry.render("assistant", {"product_name": "Acme"})
    second = registry.render("assistant", {"product_name": "Acme"})
    assert first.sha256 == second.sha256


def test_missing_variable_fails(registry: PromptRegistry) -> None:
    with pytest.raises(PromptError):
        registry.render("assistant", {})


def test_unknown_prompt_fails(registry: PromptRegistry) -> None:
    with pytest.raises(PromptError):
        registry.render("nao-existe", {})


def test_every_registered_prompt_renders(registry: PromptRegistry) -> None:
    variables = {"product_name": "X", "max_sentences": "2"}
    for name in registry.names():
        assert registry.render(name, variables).text
