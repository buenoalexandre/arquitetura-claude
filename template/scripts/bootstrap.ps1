# Prepara o ambiente de desenvolvimento no Windows (PowerShell 5.1+).
$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Instale o uv: winget install --id=astral-sh.uv -e   (ou: pip install uv)"
    exit 1
}

if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path CLAUDE.local.md)) { Copy-Item CLAUDE.local.md.example CLAUDE.local.md }

uv sync --group dev
if ($?) { uv run pre-commit install --hook-type pre-commit --hook-type commit-msg }
if ($?) { uv run python scripts/check_template.py }
if ($?) { Write-Host "Ambiente pronto. Rode: uv run uvicorn app.main:create_app --factory --app-dir src --reload" }
