# Regras para prompts

Vale para `prompts/**`. O processo completo está em `docs/ai/prompt-management.md`.

- Todo prompt é declarado em `prompts/registry.yaml`, com dono, variáveis e changelog.
- Versões publicadas são **imutáveis**. Para mudar, crie `nome.vN+1.md`, registre-o e só depois
  troque `active`.
- A troca de `active` exige, no mesmo PR, evals passando e o resultado comparado com a versão
  anterior.
- Variáveis usam a sintaxe `$nome` (`string.Template`). Para um `$` literal, escreva `$$`.
- As políticas (`prompts/policies/`) são compostas, não copiadas: referencie-as no registro.
- Escreva instruções positivas e específicas, explicando o objetivo e o motivo. Evite CAIXA
  ALTA e ameaças ("NUNCA", "OBRIGATÓRIO"); modelos atuais seguem bem instruções calmas.
- Não coloque dados variáveis (data, ID de requisição) no prompt de sistema: isso quebra o
  cache de prompt.
