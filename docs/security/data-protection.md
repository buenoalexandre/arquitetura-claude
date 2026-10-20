# Proteção de dados (LGPD)

## Princípios aplicados

| Princípio | Como o template aplica |
|---|---|
| Finalidade e necessidade | Só a mensagem atual, a janela de histórico e a memória relevante vão ao modelo |
| Minimização | PII é redigida antes de persistir; a auditoria guarda hashes, não conteúdo |
| Retenção limitada | TTL na memória de longo prazo (30 dias em produção) |
| Direitos do titular | `DELETE /v1/memory` apaga a memória curta e a longa do usuário |
| Segurança | Autenticação, RBAC, segredos em cofre, TLS na borda |
| Responsabilização | Auditoria, ADRs e checklist de validação |

## Fluxo de dados pessoais

1. **Entrada:** a mensagem do usuário é analisada pelos guardrails (PII sinalizada).
2. **Provedor LLM:** a mensagem original vai ao provedor. Confirme no contrato a retenção, o
   uso para treinamento e a região. Para dados sensíveis, redija antes de enviar ou use
   implantação regional ou dedicada.
3. **Histórico:** é guardado com a PII redigida.
4. **Logs:** não há conteúdo de mensagens; os campos sensíveis são mascarados.
5. **Auditoria:** hash e tamanho do conteúdo, ator, ação e versão do prompt.

## Classificação

| Classe | Exemplos | Pode ir ao LLM? |
|---|---|---|
| Pública | Documentação do produto | Sim |
| Interna | Dados operacionais | Sim, com contrato adequado |
| Pessoal | Nome, e-mail, CPF | Só o necessário; redigido na persistência |
| Sensível (art. 5º, II) | Saúde, biometria, religião | Só com base legal específica e avaliação de impacto (RIPD) |
| Segredos | Senhas, chaves | Nunca |

## Ambientes não produtivos

Não use dados reais de clientes em desenvolvimento, testes ou evals. Datasets de eval vindos de
produção precisam ser anonimizados e revisados antes do commit.
