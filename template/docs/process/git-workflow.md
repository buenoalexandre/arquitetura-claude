# Fluxo de Git, branches e commits

## Estratégia: GitHub Flow

```
main ─────●─────────●──────────●───── (sempre implantável; tag vX.Y.Z = produção)
           \       /  \        /
            feat/42   fix/57-x
```

- A `main` é protegida: só recebe merge por PR com CI verde e aprovação.
- Branches curtas (idealmente menos de 3 dias), criadas a partir da `main` atualizada.
- Releases por tag SemVer na `main`. Hotfix é uma branch `fix/` comum, com nova tag `PATCH`.

**Por que não Git Flow?** Branches `develop` e `release` de longa duração atrasam a integração e
fazem pouco sentido com deploy contínuo. Git Flow continua sendo uma opção para produtos com
versões instaladas em clientes (on-premises), registrada em ADR.

## Nomes de branch

`<tipo>/<issue>-<descricao-curta>`: `feat/42-memoria-redis`, `fix/57-timeout-stream`,
`prompt/63-assistente-v2`, `docs/70-runbook`.

## Conventional Commits

```
<tipo>(<escopo opcional>): <descrição no imperativo, minúscula>

<corpo: o porquê da mudança>

<rodapé: Closes #42 | BREAKING CHANGE: ...>
```

| Tipo | Uso | Efeito na versão |
|---|---|---|
| `feat` | Nova funcionalidade | MINOR |
| `fix` | Correção de bug | PATCH |
| `prompt` | Nova versão ou ativação de prompt | MINOR (comportamento muda) |
| `perf` | Melhoria de desempenho ou custo | PATCH |
| `refactor`, `test`, `docs`, `chore`, `ci` | Sem mudança de comportamento | nenhum |
| `feat!` ou `BREAKING CHANGE:` | Quebra de contrato | MAJOR |

O hook `commit-msg` do pre-commit e o job `commits` do CI validam o formato.

## Configuração do repositório

1. Proteção da `main`: PR obrigatório, 1 aprovação, revisão de CODEOWNERS, checks `CI` e
   `Security` obrigatórios, conversa resolvida, histórico linear e sem push forçado.
2. Merge permitido somente por squash; branch apagada após o merge.
3. Segredos e environments: ver [implantação](../guides/deployment.md).
4. Varredura de segredos e push protection habilitados.

## Repositório remoto deste template

```bash
git remote add origin git@github.com:buenoalexandre/template-ia.git
git push -u origin main
```
