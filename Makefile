# Atalhos de desenvolvimento. No Windows, use Git Bash/WSL ou rode os comandos `uv run ...` direto.
UV ?= uv
RUN = $(UV) run

.PHONY: install lint format test evals evals-live security check run docker clean

install: ## Instala dependências e hooks de pre-commit
	$(UV) sync --group dev
	$(RUN) pre-commit install --hook-type pre-commit --hook-type commit-msg

lint: ## Lint, formatação e tipos
	$(RUN) ruff check .
	$(RUN) ruff format --check .
	$(RUN) mypy

format: ## Aplica formatação e correções automáticas
	$(RUN) ruff format .
	$(RUN) ruff check . --fix

test: ## Testes offline com cobertura
	$(RUN) pytest -m "not live" --cov --cov-fail-under=80

evals: ## Evals offline (datasets e corretores)
	$(RUN) pytest -m "evals and not live" tests/evals

evals-live: ## Evals contra o modelo real (custa tokens; exige ANTHROPIC_API_KEY)
	$(RUN) pytest -m live tests/evals

security: ## SAST, auditoria de dependências e testes de segurança
	$(RUN) bandit -c pyproject.toml -r src
	$(RUN) pip-audit --strict
	$(RUN) pytest -m security

check: lint test ## Gate completo (o mesmo do CI)
	$(RUN) python scripts/check_template.py

run: ## API local com recarga automática
	$(RUN) uvicorn app.main:create_app --factory --app-dir src --reload

docker: ## Sobe a API em container
	docker compose up --build

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov coverage.xml .coverage
