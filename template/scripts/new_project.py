"""Cria um novo projeto a partir deste template.

Uso:
    python scripts/new_project.py <destino> --name <nome-do-projeto>

Copia o template sem histórico git, ambientes virtuais, caches nem arquivos locais, e troca o
nome do projeto nos arquivos de configuração.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_NAME = "ai-app"

IGNORED = shutil.ignore_patterns(
    ".git",
    ".venv",
    "__pycache__",
    "*.pyc",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".coverage",
    "coverage.xml",
    "htmlcov",
    ".env",
    "CLAUDE.local.md",
    "settings.local.json",
    "reports",
    "*.egg-info",
)

RENAME_IN = ["pyproject.toml", "config/base.yaml", "README.md"]


def _changelog(name: str) -> str:
    return (
        "# Changelog\n\n"
        "Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).\n\n"
        "## [Não publicado]\n\n"
        f"## [0.1.0] - {date.today().isoformat()}\n\n"
        f"### Adicionado\n- Projeto `{name}` criado a partir do template de IA.\n"
    )


def create_project(destination: Path, name: str) -> Path:
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,48}", name):
        raise ValueError("O nome deve estar em kebab-case: letras minúsculas, números e hífens")
    destination = destination.resolve()
    if destination == TEMPLATE_ROOT or TEMPLATE_ROOT in destination.parents:
        raise ValueError("O destino não pode ficar dentro do próprio template")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"{destination} já existe e não está vazio")

    shutil.copytree(TEMPLATE_ROOT, destination, ignore=IGNORED, dirs_exist_ok=True)
    for relative in RENAME_IN:
        path = destination / relative
        path.write_text(
            path.read_text(encoding="utf-8").replace(TEMPLATE_NAME, name), encoding="utf-8"
        )
    readme = destination / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace("# Template de projetos com IA", f"# {name}", 1),
        encoding="utf-8",
    )
    (destination / "CHANGELOG.md").write_text(_changelog(name), encoding="utf-8")
    return destination


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # acentos corretos no console do Windows
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("destination", type=Path)
    parser.add_argument("--name", required=True, help="nome do projeto em kebab-case")
    args = parser.parse_args()
    try:
        path = create_project(args.destination, args.name)
    except (ValueError, FileExistsError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print(f"Projeto criado em {path}")
    print("Próximos passos: cd para a pasta, cp .env.example .env, make install && make check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
