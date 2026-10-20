# Runbook de incidentes

## Severidades

| Sev | Exemplo | Resposta |
|---|---|---|
| 1 | Vazamento de dados, serviço fora do ar | Imediata, com comunicação ao jurídico/DPO |
| 2 | LLM indisponível, qualidade muito degradada | Até 30 min |
| 3 | Latência alta, custo anômalo | Mesmo dia |

## Cenários

### Provedor de LLM indisponível (503 `llm_unavailable`, circuit breaker aberto)

1. Confira a página de status do provedor.
2. Veja `llm_requests_total` por `status`: é timeout, 5xx ou rate limit?
3. Se o fallback também falhou, troque `APP_LLM__MODEL` ou `APP_LLM__FALLBACK_MODEL` por
   variável de ambiente e reinicie.
4. Comunique a degradação aos usuários.

### Rate limit do provedor (aumento de `transient_error` com 429)

1. Reduza `requests_per_minute` para ficar abaixo da cota.
2. Mova cargas não interativas para batch.
3. Peça aumento de cota ao provedor, se for um crescimento legítimo.

### Qualidade degradada (reclamações ou evals agendados falhando)

1. Identifique o `prompt_version` e o `model` das respostas ruins pela auditoria.
2. Houve deploy recente de prompt ou modelo? Volte o `active` ou o modelo.
3. Transforme os exemplos ruins (anonimizados) em casos de eval antes de corrigir.

### Suspeita de injeção de prompt ou vazamento

1. Filtre a auditoria por `flags` contendo `injection:` ou `output:`.
2. Se houve vazamento confirmado: Sev 1, preserve as evidências, envolva segurança e DPO.
3. Ative o bloqueio (`guardrails.block_prompt_injection=true`) se estiver desligado.
4. Adicione os payloads aos testes de segurança e corrija a mitigação.

### Custo anômalo

1. Veja `llm_cost_usd_total` e `llm_tokens_total` por modelo: o pico é de entrada (contexto) ou
   de saída?
2. Procure um usuário ou chave com volume fora do padrão (possível abuso).
3. Reduza os limites ou revogue a chave; revise `max_tokens` e o tamanho da janela de memória.

## Pós-incidente

Registre em até 5 dias úteis: linha do tempo, causa raiz, impacto, ações corretivas (com
responsável e prazo) e o que vai virar teste, eval ou alerta.
