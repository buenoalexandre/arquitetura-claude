# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). O projeto
segue [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não publicado]

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
