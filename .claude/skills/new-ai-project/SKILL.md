---
name: new-ai-project
description: Cria um novo projeto de IA a partir deste template e valida se ele atende ao padrão organizacional. Use quando o usuário pedir para iniciar, gerar ou "scaffoldar" um projeto com IA, ou para verificar se um projeto existente segue o template.
---

# Novo projeto de IA a partir do template

Esta skill gera um projeto novo a partir deste repositório e conduz as adaptações mínimas.
Ela também audita projetos que já existem.

## Modo 1: criar um projeto

1. Pergunte, se ainda não souber: nome do projeto (kebab-case), pasta de destino, provedor de
   LLM (`anthropic` ou outro) e se o projeto terá RAG, ferramentas (tool use) ou só chat.
2. Gere a cópia:
   ```bash
   python scripts/new_project.py <destino> --name <nome-do-projeto>
   ```
   O script copia o template sem `.git`, `.venv` nem caches, renomeia o pacote no
   `pyproject.toml`, `config/base.yaml` e `README.md`, e reinicia o `CHANGELOG.md`.
3. No projeto novo:
   - Ajuste a seção "Projeto" do `CLAUDE.md` com o domínio real.
   - Troque `owner` em `prompts/registry.yaml` e os times em `.github/CODEOWNERS`.
   - Escreva o primeiro prompt real com `/new-prompt` e pelo menos 5 casos de eval.
   - Remova o que não se aplica (por exemplo, `memory/` da aplicação em um serviço sem estado)
     e registre essa escolha em um ADR com `/adr`.
4. Rode `make install && make check` e, por fim, o checklist (Modo 2).
5. Só inicialize o git e faça o primeiro commit quando o usuário pedir.

## Modo 2: validar um projeto

1. Rode `python scripts/check_template.py` na raiz do projeto. Ele verifica automaticamente
   os itens estruturais.
2. Percorra `checklist.md` (nesta pasta). Para cada item que não for automático, procure a
   evidência no repositório (arquivo, teste, workflow) e marque ✅, ⚠️ (parcial) ou ❌.
3. Entregue uma tabela por seção, com a evidência de cada item, e a lista priorizada de
   lacunas: primeiro segurança, depois testes e evals, depois o resto.

## Princípios

- O template é o ponto de partida, não uma camisa de força. Desvios são permitidos quando
  documentados em ADR.
- Não copie segredos, `.env` ou dados do projeto de origem.
- Prefira remover um componente não usado a deixá-lo desatualizado.
