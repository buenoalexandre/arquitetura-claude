"""Valida automaticamente os itens estruturais do checklist de projeto.

Uso: python scripts/check_template.py [raiz-do-projeto]
Sai com código 1 se algum item obrigatório falhar. Os itens que exigem julgamento humano
estão em docs/checklist/project-validation-checklist.md.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import yaml

REQUIRED_FILES = [
    "README.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    ".env.example",
    ".gitignore",
    ".mcp.json",
    ".claude/settings.json",
    "ARQUITETURA.md",
    ".claude/hooks/pre_tool_use.py",
    ".claude/hooks/post_tool_use.py",
    ".claude/rules/testing.md",
    ".claude/rules/api-design.md",
    ".claude/skills/security-review/SKILL.md",
    ".claude/commands/fix-issue.md",
    ".claude/agents/code-reviewer.md",
    ".claude/output-styles/code-reviewer.md",
    ".claude/workflows/review-changes.js",
    "memory/MEMORY.md",
    "config/base.yaml",
    "config/development.yaml",
    "config/staging.yaml",
    "config/production.yaml",
    "prompts/registry.yaml",
    ".github/workflows/ci.yml",
    ".github/workflows/security.yml",
    ".github/workflows/evals.yml",
    ".github/pull_request_template.md",
    ".github/CODEOWNERS",
    "docs/architecture/overview.md",
    "docs/guides/installation.md",
    "docs/security/threat-model.md",
    "docs/checklist/project-validation-checklist.md",
]

REQUIRED_DIRS = [".claude/rules", ".claude/agents", ".claude/commands", "docs/architecture/adr"]
GITIGNORE_ENTRIES = [".env", "CLAUDE.local.md", ".claude/settings.local.json"]

Check = Callable[[Path], list[str]]


def check_files(root: Path) -> list[str]:
    errors = [f"arquivo ausente: {f}" for f in REQUIRED_FILES if not (root / f).is_file()]
    errors += [
        f"pasta ausente ou vazia: {d}"
        for d in REQUIRED_DIRS
        if not (root / d).is_dir() or not any((root / d).iterdir())
    ]
    return errors


def check_gitignore(root: Path) -> list[str]:
    path = root / ".gitignore"
    if not path.is_file():
        return []
    lines = {line.strip() for line in path.read_text(encoding="utf-8").splitlines()}
    return [f".gitignore não cobre {entry}" for entry in GITIGNORE_ENTRIES if entry not in lines]


def check_no_tracked_env(root: Path) -> list[str]:
    if not (root / ".git").exists():
        return []
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=False
    )
    tracked = [
        f
        for f in result.stdout.splitlines()
        if Path(f).name.startswith(".env") and Path(f).name != ".env.example"
    ]
    return [f"arquivo de ambiente versionado: {f}" for f in tracked]


def check_json_files(root: Path) -> list[str]:
    errors = []
    for relative in [".mcp.json", ".claude/settings.json"]:
        path = root / relative
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{relative} inválido: {exc}")
    return errors


def check_prompt_registry(root: Path) -> list[str]:
    path = root / "prompts" / "registry.yaml"
    if not path.is_file():
        return []
    errors = []
    prompts = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("prompts", {})
    for name, entry in prompts.items():
        versions = entry.get("versions", {})
        if entry.get("active") not in versions:
            errors.append(f"prompt {name}: versão ativa não existe")
        if not entry.get("owner"):
            errors.append(f"prompt {name}: sem owner")
        for version, spec in versions.items():
            for file in [spec.get("file"), *spec.get("policies", [])]:
                if not file or not (root / "prompts" / file).is_file():
                    errors.append(f"prompt {name}@{version}: arquivo ausente {file}")
    return errors


def check_eval_datasets(root: Path) -> list[str]:
    datasets = list((root / "tests" / "evals" / "datasets").glob("*.jsonl"))
    if not datasets:
        return ["nenhum dataset de eval em tests/evals/datasets/"]
    ids: list[str] = []
    errors = []
    for file in datasets:
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"{file.name}:{number} não é JSON válido")
                continue
            missing = {"id", "prompt", "input", "criteria"} - case.keys()
            if missing:
                errors.append(f"{file.name}:{number} sem campos {sorted(missing)}")
            ids.append(str(case.get("id")))
    duplicates = {i for i in ids if ids.count(i) > 1}
    errors += [f"id de eval duplicado: {i}" for i in sorted(duplicates)]
    return errors


def check_claude_md(root: Path) -> list[str]:
    path = root / "CLAUDE.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    errors = []
    if "Padrões que NÃO usamos" not in text:
        errors.append("CLAUDE.md sem a seção 'Padrões que NÃO usamos'")
    if len(text.splitlines()) > 150:
        errors.append("CLAUDE.md com mais de 150 linhas: mova detalhes para .claude/rules/")
    return errors


CHECKS: list[tuple[str, Check]] = [
    ("Arquivos e pastas obrigatórios", check_files),
    ("Itens do .gitignore", check_gitignore),
    ("Nenhum .env versionado", check_no_tracked_env),
    ("JSON de configuração válido", check_json_files),
    ("Registro de prompts", check_prompt_registry),
    ("Datasets de eval", check_eval_datasets),
    ("CLAUDE.md", check_claude_md),
]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # acentos corretos no console do Windows
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    failures = 0
    for title, check in CHECKS:
        errors = check(root)
        print(f"{'OK  ' if not errors else 'FALHA'} {title}")
        for error in errors:
            print(f"       - {error}")
        failures += len(errors)
    print(f"\n{failures} problema(s) encontrado(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
