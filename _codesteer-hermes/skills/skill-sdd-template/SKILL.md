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
- confirme em `validation-report.md` que a recomendação permite seguir
- confirme em `user-confirmation.md` que o usuário aprovou a transição para FASE 6
- use apenas artefatos consolidados da raiz de `_hermes/{scope-slug}/`
- não consuma `raw/` diretamente
- marque itens de baixa certeza com `REQUER VALIDAÇÃO`
- escreva apenas em `_hermes/{scope-slug}/sdd/`
- trate `db-schema.md` como base intermediária para `db-schema-outline.md` e `db-complete.md`

## Mapeamento por Nível

### Universal

Sempre gere:

- `sdd-index.md`

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

## Estratégia de Escrita

1. usar o template do nível e preservar sua estrutura mínima
2. preencher apenas com evidência consolidada
3. inserir cross-references entre telas, BRs, entidades, endpoints, componentes e controles de segurança quando houver base
4. se faltar dado, explicitar insuficiência e apontar para `gaps.md`, `open-questions-br.md` ou `validation-report.md`
5. gerar `sdd-index.md` por último, após o pacote final estar completo

## Convenções de Composição

- o pacote `sdd/` é editorial: pode reorganizar e resumir, mas não pode contradizer a base consolidada
- preserve IDs e nomes de referência já consolidados, como `BR-001`, nomes de telas, rotas e entidades
- não replique arquivos consolidados linha a linha quando uma síntese rastreável for suficiente
- quando um documento final derivar de múltiplas fontes, explicite isso em uma seção de rastreabilidade

## Cross-References Mínimos

- cada fluxo principal deve apontar para telas, regras e integrações envolvidas
- cada regra de negócio deve apontar para pelo menos uma tela, endpoint ou entidade quando houver evidência
- cada documento de segurança deve apontar para roles, endpoints e dados sensíveis relacionados
- cada documento final deve indicar de quais artefatos consolidados se origina

## Anti-padrões

- usar linguagem especulativa
- puxar dado diretamente de `raw/`
- omitir lacuna para "fechar" a seção
- copiar artefatos consolidados para `sdd/` sem transformação editorial
