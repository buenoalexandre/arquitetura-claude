# Guardrails

Guardrails são verificações determinísticas antes e depois do modelo. Eles são uma camada de
defesa em profundidade e **não substituem** o controle de acesso: o modelo nunca deve ter
acesso a dados ou ferramentas que o usuário não poderia acessar diretamente.

## Entrada (`guardrails/input.py`)

| Verificação | Ação padrão | Configuração |
|---|---|---|
| Tamanho máximo | Rejeita (400) | `guardrails.max_input_chars` |
| Injeção de prompt (heurísticas PT/EN) | Rejeita (400) ou só sinaliza | `guardrails.block_prompt_injection` |
| PII (e-mail, CPF, cartão, telefone) | Sinaliza; redige antes de persistir | `memory.redact_pii` |

## Saída (`guardrails/output.py`)

| Verificação | Ação |
|---|---|
| Vazamento do prompt de sistema (trechos literais longos) | Substitui a resposta por uma recusa padrão |
| PII que o usuário não forneceu | Redige o trecho e sinaliza |

Os sinalizadores (`guardrail_flags`) vão na resposta da API e no evento de auditoria. Isso
permite medir falsos positivos e encontrar novos padrões de ataque.

## Limitações conhecidas

- Heurísticas de injeção têm falsos negativos (paráfrases, outros idiomas, codificações).
  Para ameaças maiores, adicione um classificador dedicado: Prompt Guard, Lakera Guard,
  NVIDIA NeMo Guardrails, Azure AI Content Safety ou AWS Bedrock Guardrails.
- Regex de PII tem falsos positivos (números parecidos com CPF). Microsoft Presidio é a
  alternativa mais robusta para detecção e anonimização.
- Injeção indireta (em documentos de RAG ou resultados de ferramentas) exige rotular e
  delimitar esse conteúdo como dado e restringir o que o modelo pode fazer depois de lê-lo.

## Como evoluir

1. Novo padrão encontrado → caso em `tests/security/injection_payloads.json` (em `blocked`).
2. Falso positivo encontrado → caso em `allowed`.
3. Ajuste a heurística ou o classificador até ambos passarem.
