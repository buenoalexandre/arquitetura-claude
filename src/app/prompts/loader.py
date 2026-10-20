"""Registro central de prompts versionados.

Os prompts vivem em ``prompts/`` como arquivos Markdown, fora do código, e são declarados em
``prompts/registry.yaml``. Cada renderização devolve nome, versão e hash SHA-256, que vão
para a auditoria — assim toda resposta é rastreável até o texto exato que a gerou.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any

import yaml

from app.core.errors import PromptError


@dataclass(frozen=True)
class RenderedPrompt:
    name: str
    version: str
    text: str
    sha256: str


class PromptRegistry:
    def __init__(self, prompts_dir: Path, registry_file: Path) -> None:
        self._dir = prompts_dir
        data: dict[str, Any] = yaml.safe_load(registry_file.read_text(encoding="utf-8")) or {}
        self._prompts: dict[str, Any] = data.get("prompts", {})

    def names(self) -> list[str]:
        return sorted(self._prompts)

    def active_version(self, name: str) -> str:
        return str(self._entry(name)["active"])

    def render(
        self, name: str, variables: Mapping[str, str], version: str | None = None
    ) -> RenderedPrompt:
        entry = self._entry(name)
        version = version or str(entry["active"])
        spec = entry.get("versions", {}).get(version)
        if spec is None:
            raise PromptError(f"Versão '{version}' do prompt '{name}' não existe")

        missing = [v for v in spec.get("variables", []) if v not in variables]
        if missing:
            raise PromptError(f"Variáveis ausentes para '{name}': {missing}")

        parts = [self._read(spec["file"])] + [self._read(p) for p in spec.get("policies", [])]
        try:
            text = Template("\n\n".join(parts)).substitute(variables)
        except (KeyError, ValueError) as exc:
            raise PromptError(f"Falha ao renderizar '{name}': {exc}") from exc
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return RenderedPrompt(name=name, version=version, text=text.strip(), sha256=digest)

    def _entry(self, name: str) -> dict[str, Any]:
        entry = self._prompts.get(name)
        if entry is None:
            raise PromptError(f"Prompt '{name}' não registrado")
        return dict(entry)

    def _read(self, relative: str) -> str:
        path = (self._dir / relative).resolve()
        if self._dir.resolve() not in path.parents:
            raise PromptError(f"Caminho de prompt fora do diretório permitido: {relative}")
        return path.read_text(encoding="utf-8").strip()
