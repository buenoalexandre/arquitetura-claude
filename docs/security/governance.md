# Governança de IA

## Papéis

| Papel | Responsabilidade |
|---|---|
| Dono do produto | Define os casos de uso permitidos e aprova a mudança de comportamento |
| Time de IA | Prompts, evals, escolha de modelo e monitoramento de qualidade |
| Segurança | Modelo de ameaças, revisão de guardrails e resposta a incidentes |
| Plataforma | Segredos, CI/CD, ambientes e observabilidade |
| DPO / Jurídico | Base legal, retenção e atendimento aos titulares (LGPD) |

## Controles

1. **Inventário:** cada projeto registra os modelos usados, os provedores, as finalidades e os
   dados enviados (seção "Projeto" do `CLAUDE.md` + ADRs).
2. **Mudanças controladas:** prompts, modelos e políticas mudam só por PR com CODEOWNERS e evals.
3. **Rastreabilidade:** cada resposta registra o modelo, a versão e o hash do prompt e o
   `correlation_id`.
4. **Avaliação contínua:** evals agendados; alertas quando a taxa de aprovação cair.
5. **Transparência:** o usuário final sabe que interage com IA, e as respostas não se passam por
   decisões humanas.
6. **Revisão humana:** decisões com impacto relevante (crédito, saúde, emprego) não são tomadas
   só pelo modelo.
7. **Fornecedores:** contratos com o provedor de LLM cobrem retenção de dados, uso para
   treinamento e região de processamento.

## Uso de agentes de código (Claude Code)

- As permissões ficam em `.claude/settings.json` (o padrão do time é versionado). As exceções
  pessoais vão em `settings.local.json`.
- Hooks impedem ações destrutivas e a gravação de segredos.
- O agente não faz commit nem push sem pedido explícito; todo código passa por PR e revisão
  humana.
- Servidores MCP compartilhados são aprovados por segurança antes de entrarem no `.mcp.json`.

## Auditoria

Os eventos de auditoria (logger `audit`) devem ir para um armazenamento imutável, com retenção
definida pelo jurídico (sugestão: 1 ano). Consultas comuns: interações por usuário, por versão de
prompt, eventos com `guardrail_flags` e eventos de esquecimento.
