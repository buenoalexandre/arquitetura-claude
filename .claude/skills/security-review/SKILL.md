---
name: security-review
description: Checklist de revisão de segurança para mudanças que tocam autenticação, autorização, dados pessoais, prompts, memória, ferramentas do modelo, dependências ou pipelines. Use antes de aprovar PRs nessas áreas ou quando o usuário pedir uma auditoria de segurança.
---

# Revisão de segurança de aplicação com IA

1. Identifique o escopo: `git diff --name-only main...HEAD` (ou os arquivos indicados).
2. Classifique cada arquivo em uma ou mais áreas do `checklist.md`.
3. Para cada área tocada, percorra os itens do checklist e procure evidências no código e nos
   testes. Se for útil, delegue a análise profunda ao subagente `security-auditor`.
4. Confirme que existe teste automatizado para cada controle novo (em `tests/security/`).
5. Reporte os achados por severidade, com:
   - **Crítico**: exploração direta (ex.: rota sem autenticação, segredo exposto).
   - **Alto**: vazamento de dados entre usuários ou injeção sem mitigação.
   - **Médio**: defesa em profundidade ausente (ex.: sem rate limit).
   - **Baixo**: higiene (ex.: dependência sem pin).

Para cada achado informe o vetor, o impacto, a evidência (`arquivo:linha`) e a correção. Termine
com os itens do checklist que foram verificados e estão OK.
