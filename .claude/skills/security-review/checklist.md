# Checklist de segurança

## Autenticação e autorização
- [ ] Toda rota nova usa `Depends(require("recurso:acao"))`
- [ ] A permissão existe em `ROLE_PERMISSIONS` com o menor papel necessário
- [ ] Os dados são sempre filtrados por `principal.subject` (sem IDs vindos do cliente sem checagem)
- [ ] Os tokens têm expiração; as chaves são comparadas em tempo constante

## Prompts e modelo (OWASP LLM01, LLM07)
- [ ] O prompt vem do registro versionado, não de string no código
- [ ] Conteúdo externo entra delimitado e rotulado como dado
- [ ] O guardrail de entrada é aplicado; há casos novos em `injection_payloads.json` quando cabível
- [ ] O guardrail de saída impede vazamento do prompt de sistema e de PII

## Dados e memória (LLM02, LLM04, LGPD)
- [ ] PII é redigida antes de persistir
- [ ] A memória passa por `MemoryPolicy`, com TTL e esquecimento
- [ ] Logs e auditoria não contêm conteúdo bruto, segredos nem tokens

## Ferramentas e agentes (LLM06 — agência excessiva)
- [ ] Ferramentas com efeito colateral têm allowlist e confirmação humana
- [ ] Os argumentos das ferramentas são validados por schema antes da execução
- [ ] As credenciais das ferramentas têm o escopo mínimo necessário

## Consumo e disponibilidade (LLM10)
- [ ] Há limites de tamanho de entrada e de `max_tokens` e rate limit
- [ ] Timeouts e circuit breaker estão configurados; erros 5xx são genéricos

## Cadeia de suprimentos (LLM03)
- [ ] Dependência nova passou no `pip-audit` e tem licença compatível
- [ ] GitHub Actions estão fixadas por versão e workflows têm `permissions` mínimas
- [ ] Modelos e datasets de terceiros têm origem documentada
