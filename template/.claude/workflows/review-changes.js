export const meta = {
  name: 'review-changes',
  description: 'Revisa o diff em várias dimensões e verifica cada achado de forma adversarial',
  whenToUse: 'Antes de abrir ou aprovar um PR grande ou sensível (segurança, prompts, memória). Uso: args = { base: "main" }',
  phases: [
    { title: 'Revisar', detail: 'um revisor por dimensão: correção, segurança de IA, arquitetura e testes' },
    { title: 'Verificar', detail: 'três céticos independentes tentam refutar cada achado' },
  ],
}

// Script de orquestração multiagente: só roda quando o usuário pede explicitamente
// (ex.: "rode o workflow review-changes"). Para revisões do dia a dia, use /review.

const base = (args && args.base) || 'main'

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'integer' },
          severity: { type: 'string', enum: ['critico', 'alto', 'medio', 'baixo'] },
          summary: { type: 'string' },
          scenario: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['file', 'line', 'severity', 'summary', 'scenario'],
      },
    },
  },
  required: ['findings'],
}

const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
  },
  required: ['refuted', 'reason'],
}

const DIMENSIONS = [
  {
    key: 'correcao',
    agentType: 'code-reviewer',
    focus: 'bugs de lógica, condições de corrida, erros não tratados, quebra de contrato da API',
  },
  {
    key: 'seguranca-ia',
    agentType: 'security-auditor',
    focus: 'injeção de prompt, vazamento de dados entre usuários, segredos, guardrails e RBAC',
  },
  {
    key: 'arquitetura-testes',
    agentType: 'code-reviewer',
    focus: 'regra de dependência entre camadas, prompts fora do registro, testes ausentes ou fracos',
  },
]

const results = await pipeline(
  DIMENSIONS,
  d =>
    agent(
      `Revise o diff de \`git diff ${base}...HEAD\` com foco em: ${d.focus}. ` +
        'Leia os arquivos completos envolvidos. Reporte só problemas com cenário concreto de falha.',
      { label: `revisar:${d.key}`, phase: 'Revisar', schema: FINDINGS, agentType: d.agentType },
    ),
  (review, d) =>
    parallel(
      (review ? review.findings : []).map(f => () =>
        parallel(
          [0, 1, 2].map(i => () =>
            agent(
              `Cético ${i + 1}: tente REFUTAR este achado de revisão (dimensão ${d.key}). ` +
                `Arquivo ${f.file}:${f.line}. Achado: ${f.summary}. Cenário: ${f.scenario}. ` +
                'Leia o código. Se não conseguir reproduzir o cenário pela leitura, refuted=true.',
              { label: `verificar:${f.file}:${f.line}#${i + 1}`, phase: 'Verificar', schema: VERDICT },
            ),
          ),
        ).then(votes => ({
          ...f,
          dimension: d.key,
          confirmed: votes.filter(Boolean).filter(v => !v.refuted).length >= 2,
        })),
      ),
    ),
)

const all = results.filter(Boolean).flat().filter(Boolean)
const confirmed = all.filter(f => f.confirmed)
log(`${confirmed.length} de ${all.length} achados sobreviveram à verificação`)
const order = { critico: 0, alto: 1, medio: 2, baixo: 3 }
return confirmed.sort((a, b) => order[a.severity] - order[b.severity])
