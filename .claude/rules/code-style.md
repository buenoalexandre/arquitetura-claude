# Estilo de código

Vale para `src/**/*.py`, `tests/**/*.py` e `scripts/**/*.py`.

## Ferramentas (aplicadas automaticamente)

- `ruff format` e `ruff check` (configuração em `pyproject.toml`). O hook PostToolUse formata
  cada arquivo editado.
- `mypy --strict` em `src/`. Código novo não pode adicionar `# type: ignore` sem justificativa
  na mesma linha.

## Convenções

- Python 3.11+, `from __future__ import annotations` em todo módulo.
- Nomes em inglês no código; docstrings, comentários e mensagens ao usuário em português.
- Arquivos e slugs em kebab-case fora do código (`security-review`), snake_case em Python.
- Interfaces com `typing.Protocol`; dados imutáveis com `@dataclass(frozen=True)`; contratos
  de API com Pydantic.
- Dependências entram pelo construtor. Nada de singletons globais além de `get_settings()`.
- Funções com até ~40 linhas; extraia quando passar disso ou quando houver mais de um nível
  de abstração.
- Comentários explicam o **porquê**. O "o quê" deve ficar claro pelo código.

## Camadas (regra de dependência)

```
api  ──►  domain  ──►  (llm, memory, prompts, guardrails, observability)  ──►  core
```

- `domain` não importa `fastapi`, `anthropic` nem nenhum SDK externo.
- Somente `container.py` conhece implementações concretas.
- Erros de domínio herdam de `app.core.errors.AppError`.
