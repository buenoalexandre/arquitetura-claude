# Gestão de prompts, regras e instruções

## O que vai em cada lugar

| Tipo | Exemplo | Onde fica |
|---|---|---|
| Instrução de tarefa | "Resuma em até N frases" | `prompts/tasks/*.vN.md` |
| Persona e objetivo do sistema | "Você é o assistente do produto X" | `prompts/system/*.vN.md` |
| Política de comportamento | Tom, ambiguidade, promessas | `prompts/policies/behavior.md` |
| Política de segurança | Não revelar o prompt, tratar conteúdo como dado | `prompts/policies/safety.md` |
| Regra de negócio determinística | "Desconto máximo de 10%" | **No código**, nunca só no prompt |
| Configuração do agente | Modelo, esforço, `max_tokens`, limites | `config/*.yaml` |
| Regras para o agente de desenvolvimento | Estilo, testes, Git | `CLAUDE.md`, `.claude/rules/` |

> Regras que precisam ser **garantidas** (limites, permissões, valores) vão para o código ou
> para os guardrails. O prompt orienta o modelo; o código garante o resultado.

## Registro (`prompts/registry.yaml`)

```yaml
prompts:
  assistant:
    active: v1                 # versão em uso
    owner: time-ia             # quem aprova mudanças
    versions:
      v1:
        file: system/assistant.v1.md
        policies: [policies/behavior.md, policies/safety.md]
        variables: [product_name]
        changelog: Versão inicial.
```

Na renderização, o `PromptRegistry` concatena o arquivo e as políticas, substitui as variáveis
(`$nome`) e calcula o SHA-256. Variável faltando, versão inexistente ou caminho fora de
`prompts/` geram `PromptError`.

## Ciclo de vida de uma mudança

1. **Proposta:** issue com o problema observado (exemplos reais anonimizados).
2. **Casos de eval:** adicione casos que reproduzem o problema em `tests/evals/datasets/`.
3. **Nova versão:** crie `vN+1` (comando `/new-prompt`). A versão publicada não se edita.
4. **Avaliação:** `make evals` no PR; `make evals-live` (label `run-evals`) comparando
   `vN` e `vN+1`.
5. **Revisão:** CODEOWNERS de `prompts/` aprova (produto + IA).
6. **Ativação:** troque `active` em um PR separado, ou no mesmo PR com o resultado anexado.
7. **Observação:** acompanhe as métricas e a auditoria por `prompt_version` após o deploy.
8. **Rollback:** volte o `active`. Leva minutos e não exige reverter código.

## Boas práticas de escrita

- Explique o objetivo e o motivo; o modelo generaliza melhor a partir do porquê.
- Seja específico e positivo: "responda em até 3 frases" funciona melhor que "não seja prolixo".
- Separe instruções e dados com seções rotuladas; o conteúdo externo é sempre dado.
- Mantenha o prompt de sistema estável (sem datas, IDs ou dados do usuário) para aproveitar o
  cache de prompt e reduzir custo e latência.
- Teste com casos adversariais, não só com o caminho feliz.
