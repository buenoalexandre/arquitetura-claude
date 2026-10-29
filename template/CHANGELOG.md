# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). O projeto
segue [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não publicado]

### Adicionado
- `ARQUITETURA.md`: mapa de todos os arquivos e pastas, com o que é, quando usar e um exemplo.
- `.claude/workflows/review-changes.js`: revisão multiagente com verificação adversarial.
- `.claude/agent-memory/<agente>/`: memória própria dos subagentes `code-reviewer` e
  `security-auditor` (`memory: project`).

### Alterado
- Hooks unificados por evento: `pre_tool_use.py` (substitui `validate_bash.py` e
  `block_secrets.py`) e `post_tool_use.py` (antes `format_python.py`).
- `.claude/rules/api-conventions.md` renomeado para `api-design.md`.
- Testes de desempenho com aquecimento e margens que não dependem da velocidade da máquina.

## [0.1.0] - 2026-10-20

### Adicionado
- Estrutura base do template: API FastAPI, camadas de domínio, LLM, memória, guardrails,
  prompts versionados e observabilidade.
- Provedor Anthropic com fallback no servidor e provedor fake para desenvolvimento e testes.
- Resiliência: retentativas com backoff e jitter, timeout, circuit breaker por modelo, rate
  limit e fallback de modelo.
- Testes unitários, de integração, funcionais, de segurança, de desempenho e evals.
- Configuração do Claude Code: regras, comandos, skills, agentes, hooks e memória.
- Workflows de CI, segurança, evals e release; Dependabot; templates de PR e issue.
- Documentação técnica completa e checklist de validação.
