# Checklist resumido para a skill new-ai-project

A versão completa e comentada está em `docs/checklist/project-validation-checklist.md`.
Os itens marcados com 🤖 são verificados por `scripts/check_template.py`.

- [ ] 🤖 `CLAUDE.md`, `.claude/settings.json`, `.claude/rules/` e hooks presentes
- [ ] 🤖 `.gitignore` cobre `.env`, `CLAUDE.local.md` e `settings.local.json`
- [ ] 🤖 `.env.example` existe e nenhum `.env` está versionado
- [ ] 🤖 `config/` com base, development, staging e production
- [ ] 🤖 `prompts/registry.yaml` válido e todos os arquivos referenciados existem
- [ ] 🤖 Datasets de eval presentes e com IDs únicos
- [ ] 🤖 Workflows de CI, segurança e evals presentes
- [ ] 🤖 Documentação mínima (arquitetura, instalação, segurança, checklist) presente
- [ ] `CLAUDE.md` descreve o domínio real e a seção "Padrões que NÃO usamos"
- [ ] Domínio não importa SDK de LLM nem framework web
- [ ] Toda rota exige autenticação e permissão explícita
- [ ] Guardrails de entrada e saída aplicados em todo fluxo com LLM
- [ ] Memória isolada por usuário, com TTL e direito ao esquecimento
- [ ] Logs estruturados com `correlation_id`; métricas de latência, tokens e custo
- [ ] Retentativas, timeout, circuit breaker, rate limit e fallback configurados
- [ ] Cobertura ≥ 80% e evals com taxa mínima definida
- [ ] Branch `main` protegida, CODEOWNERS e template de PR configurados
- [ ] ADRs registrados para cada desvio do template
