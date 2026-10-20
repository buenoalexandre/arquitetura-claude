#!/usr/bin/env bash
# Prepara o ambiente de desenvolvimento (Linux, macOS, WSL ou Git Bash).
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "Instalando uv..."
  curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh
  sh /tmp/uv-install.sh
fi

[ -f .env ] || cp .env.example .env
[ -f CLAUDE.local.md ] || cp CLAUDE.local.md.example CLAUDE.local.md

uv sync --group dev
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
uv run python scripts/check_template.py
echo "Ambiente pronto. Rode 'make run' e abra http://localhost:8000/docs"
