# Implantação

## Pipeline

```
PR ──► ci.yml (lint, tipos, testes 3.11-3.13, checklist, título do PR)
   └─► security.yml (gitleaks, pip-audit, bandit, semgrep, CodeQL, testes de segurança)
   └─► evals.yml (se o PR tiver o label run-evals ou mudar prompts)

merge na main ──► release.yml: imagem em ghcr.io ──► deploy automático em staging ──► smoke test

tag vX.Y.Z ──► release.yml: deploy em produção (aprovação obrigatória no environment)
```

## Configuração necessária no GitHub

1. **Branch protection** na `main`: PR obrigatório, 1 aprovação (CODEOWNERS), checks de CI e
   Security obrigatórios, histórico linear e bloqueio de push forçado.
2. **Environments:** `staging`, `production` (com revisores obrigatórios) e `evals` (guarda
   `ANTHROPIC_API_KEY`).
3. **Secrets por environment:** `ANTHROPIC_API_KEY`, `APP_SECURITY__JWT_SECRET` e
   `APP_SECURITY__API_KEYS`.
4. **Label** `run-evals`.
5. Dependabot e alertas de segurança habilitados.

## Plataforma de execução

O `release.yml` deixa os passos de deploy como marcadores. Substitua conforme a plataforma:

| Plataforma | Comando típico |
|---|---|
| Kubernetes | `helm upgrade --install app ./chart --set image.tag=$TAG` |
| AWS ECS | `aws ecs update-service --force-new-deployment` |
| Google Cloud Run | `gcloud run deploy app --image ghcr.io/...:$TAG` |
| Azure Container Apps | `az containerapp update --image ...` |

Requisitos da imagem: usuário sem privilégio (UID 10001), `HEALTHCHECK` em `/health`,
readiness em `/ready` e configuração somente por variáveis de ambiente.

## Versionamento e release

- SemVer: `MAJOR` quando quebra a API, `MINOR` para funcionalidade nova, `PATCH` para correção.
- Mudança de modelo padrão ou de versão ativa de prompt é, no mínimo, `MINOR`, e vai para o
  `CHANGELOG.md`.
- Gere a release com `git tag -a v1.2.0 -m "..."` e `git push origin v1.2.0`.

## Rollback

1. Reimplante a imagem anterior (a tag `sha-<commit>` fica disponível no registry).
2. Se o problema for de prompt, volte o `active` para a versão anterior. Não é preciso reverter
   código, porque as versões são imutáveis.
3. Se o problema for de modelo, troque `APP_LLM__MODEL` pela variável de ambiente.
4. Registre o incidente conforme o [runbook](../operations/runbook.md).
