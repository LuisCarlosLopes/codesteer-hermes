---
name: skill-sdd-template
description: >
  HERMES / SDD-Writer: orientação para transformar artefatos consolidados em documentos finais usando os
  templates por nível, mantendo rastreabilidade, seções obrigatórias e marcação explícita de itens que ainda
  requerem validação. Use quando precisar gerar o SDD final a partir da saída do Synthesizer e Validator.
---

# skill-sdd-template

## Quando Carregar Esta Skill

Carregue esta skill quando:

- o agente ativo for o `SDD-Writer`
- houver artefatos consolidados e `validation-report.md`
- a tarefa for compor documentação final a partir de templates

## Regras Base

- leia `session.yaml` antes de escolher templates
- use apenas artefatos consolidados da raiz de `_hermes/{scope-slug}/`
- não consuma `raw/` diretamente
- marque itens de baixa certeza com `REQUER VALIDAÇÃO`

## Mapeamento por Nível

### L1

Gere:

- `architecture-overview.md`
- `screen-inventory.md`
- `db-schema-outline.md`
- `main-flows.md`
- `tech-stack.md`

### L2

Além de `L1`, gere:

- `component-map.md`
- `business-rules.md`
- `api-contracts.md`
- `state-map.md`
- `design-overview.md`

### L3

Além de `L2`, gere:

- `design-tokens.md`
- `db-complete.md`
- `security-model.md`
- `error-catalog.md`
- `performance-notes.md`
- `test-strategy.md`
- `sdd-index.md`

## Estratégia de Escrita

1. usar o template do nível
2. preencher apenas com evidência consolidada
3. inserir cross-references entre telas, BRs, entidades e endpoints
4. se faltar dado, explicitar insuficiência e apontar para `gaps.md`

## Anti-padrões

- usar linguagem especulativa
- puxar dado diretamente de `raw/`
- omitir lacuna para "fechar" a seção
