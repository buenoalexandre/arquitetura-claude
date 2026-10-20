# Gestão de dependências

## Princípios

- Poucas dependências, bem mantidas. Toda dependência nova é justificada no PR (o que ela
  resolve, por que não usar a biblioteca padrão, licença e manutenção ativa).
- Faixas de versão em `pyproject.toml` (`>=x,<major+1`) e versões exatas no `uv.lock`
  (versionado).
- Dependências de desenvolvimento ficam no grupo `dev` e nunca vão para a imagem de produção.

## Atualizações

| Tipo | Como | Frequência |
|---|---|---|
| Patch e minor | PR agrupado do Dependabot; merge com CI verde | Semanal |
| Major | PR manual, leitura do changelog e do guia de migração | Planejada (semestral) |
| Segurança (CVE) | `pip-audit` no CI e no agendamento semanal | Imediata conforme a severidade |
| SDK do provedor de LLM | Ler o changelog; rodar evals live antes do merge | A cada release relevante |
| GitHub Actions | Dependabot (`github-actions`) | Semanal |

## Critérios para aceitar uma dependência

- Licença permissiva (MIT, BSD, Apache-2.0). Licenças copyleft precisam de aprovação do jurídico.
- Release nos últimos 12 meses e mais de um mantenedor ativo.
- Sem CVEs abertas de severidade alta.
- Não duplica uma dependência que já usamos.

## Remoção

Dependências sem uso são removidas (`uv remove <pacote>`). Revise trimestralmente com
`uv tree`.
