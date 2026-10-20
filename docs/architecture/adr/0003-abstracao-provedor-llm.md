# 0003. Abstração própria de provedor, sem framework de orquestração

- **Status:** Aceito
- **Data:** 2026-10-20

## Contexto

A aplicação precisa trocar de modelo ou provedor sem reescrever regras de negócio, testar
offline e controlar retentativas, custo e auditoria em um único ponto. Frameworks de
orquestração (LangChain, LlamaIndex, CrewAI) oferecem abstrações prontas, mas trazem muitas
dependências, mudam a API com frequência e escondem detalhes como erros e uso de tokens.

## Decisão

- Um contrato mínimo `LLMProvider.complete(LLMRequest) -> LLMResponse` em `src/app/llm/`.
- Implementação de referência com o **SDK oficial da Anthropic**, com retentativas do SDK
  desligadas (`max_retries=0`) porque a política de retentativa fica em `ResilientLLMClient`.
- Fallback **no servidor** para recusas (`fallbacks: "default"`) e fallback **local** de modelo
  para indisponibilidade.
- `FakeProvider` determinístico para desenvolvimento, CI e testes de falha.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Contrato próprio + SDK oficial (escolhida) | Controle total, poucas dependências, erros tipados | Precisamos escrever cada adaptador |
| LiteLLM | Uma API para mais de 100 provedores | Mais uma camada entre nós e o provedor; recursos específicos ficam atrás de opções genéricas |
| LangChain / LangGraph | Ecossistema grande, agentes e RAG prontos | Muitas dependências, API instável, difícil de depurar |
| Chamar o SDK direto nos serviços | Simples no início | Acopla o domínio ao provedor; difícil de testar |

## Consequências

- Recursos avançados (tool use, streaming, cache de prompt) são adicionados ao contrato quando
  houver necessidade real.
- Frameworks de agentes podem ser usados **dentro** de um adaptador ou de um serviço específico,
  sem vazar para o domínio, com um ADR próprio.

## Critérios de revisão

Se o projeto precisar de mais de três provedores simultâneos, reavalie o uso de LiteLLM ou de
um gateway (por exemplo, um AI Gateway gerenciado).
