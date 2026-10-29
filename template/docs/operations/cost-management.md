# Gestão de custos

## Como o custo é medido

`llm/cost.py` estima o custo de cada chamada (tokens × preço por milhão). O valor vai para a
resposta (`usage.cost_usd`), para a métrica `llm_cost_usd_total` e para a auditoria. A tabela de
preços é de referência: revise-a a cada troca de modelo e confira o faturamento real no console
do provedor.

## Alavancas, em ordem de prioridade

1. **Cache de prompt:** mantenha o prompt de sistema e as políticas estáveis e no início. Leituras
   de cache custam uma fração do preço normal.
2. **Contexto menor:** ajuste `memory.short_term_max_tokens` e `long_term_recall_limit`; recupere
   menos e melhor.
3. **Saída menor:** instruções de formato e `max_tokens` adequados por rota.
4. **Esforço por rota:** `llm.effort` mais baixo (`low`/`medium`) em tarefas simples; mais alto só
   onde os evals mostram ganho.
5. **Batch:** cargas assíncronas pela API de batch (cerca de 50% mais barata).
6. **Modelo:** trocar para um modelo menor só depois de evals comparativos. Meça o custo por
   tarefa concluída, não por requisição: um modelo barato que exige retentativas pode sair mais
   caro.

## Controles

- Limite de gasto mensal no console do provedor, por chave e por ambiente.
- Alerta de custo diário (ver [observabilidade](observability.md)).
- Evals live com `effort=low` e execução agendada, não em todo PR.
- Orçamento por tenant em produtos multicliente.
