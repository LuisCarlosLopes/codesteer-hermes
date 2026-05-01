# HERMES Artifact Contracts

## Objetivo

Este documento define o contrato canonico dos artefatos produzidos nas FASES 2, 3, 4, 5 e 6 da HERMES.
Ele existe para evitar que cada agente escreva em um formato diferente e para permitir que `Synthesizer`,
`Validator` e `SDD-Writer` operem sobre arquivos previsiveis.

Regra geral:

- FASE 2 escreve somente em `_hermes/{scope-slug}/raw/`
- FASE 3 escreve somente em `_hermes/{scope-slug}/raw/`
- FASE 4 escreve somente em `_hermes/{scope-slug}/`
- FASE 5 escreve somente em `_hermes/{scope-slug}/`
- FASE 6 escreve somente em `_hermes/{scope-slug}/sdd/`
- nenhum agente altera o codebase original do usuario

## 1. Secoes obrigatorias

Todo arquivo `raw/` deve conter exatamente estas secoes, nesta ordem:

1. `## Resumo do que foi analisado`
2. `## Fontes e evidências`
3. `## Conteúdo extraído`
4. `## Itens inferidos e não verificados`
5. `## Conflitos, bloqueios e perguntas abertas`

Arquivos consolidados da FASE 4 devem conter, no minimo:

1. `## Escopo consolidado`
2. `## Evidências consolidadas`
3. `## Conteúdo reconciliado`
4. `## Itens pendentes de validação`
5. `## Conflitos e gaps relacionados`

Excecoes permitidas:

- `gaps.md`
- `synthesis-report.md`
- `remediation-requests.md`
- `validation-report.md`
- `user-confirmation.md`

Esses cinco artefatos tem estrutura propria definida ao final deste documento.

## 2. Convencoes de evidência

Use sempre referencias localizaveis. Formatos aceitos:

- `path/to/file.ext:123`
- `path/to/file.ext:123-145`
- `screen:<screen_id>`
- `route:/checkout`
- `request:POST /api/orders`
- `migration:202604010945_create_orders`

Nunca cite apenas "no código", "na UI" ou "na API" sem localizacao.

## 3. Convencoes de confiança

Valores permitidos:

- `Alta`
- `Média`
- `Baixa`

Interpretação:

- `Alta`: fonte formal ou observação direta
- `Média`: duas ou mais evidências convergentes
- `Baixa`: hipótese sustentada por um único sinal fraco ou evidência parcial

Itens `Baixa` nunca devem ser promovidos silenciosamente para verdade consolidada. Eles precisam:

- permanecer rotulados
- ir para `open-questions-br.md`, `gaps.md` ou `Itens pendentes de validação`

## 4. Mapeamento raw -> consolidado

Quando o `Synthesizer` promover um artefato, ele deve usar o nome abaixo:

| Raw | Consolidado |
|---|---|
| `screen-inventory-raw.md` | `screen-inventory.md` |
| `navigation-graph.md` | `navigation-graph.md` |
| `ui-states-catalog.md` | `ui-states-catalog.md` |
| `tech-stack.md` | `tech-stack.md` |
| `code-structure.md` | `code-structure.md` |
| `architecture-patterns.md` | `architecture-patterns.md` |
| `tech-debt.md` | `tech-debt.md` |
| `db-schema-raw.md` | `db-schema.md` |
| `db-relations.md` | `db-relations.md` |
| `data-types.md` | `data-types.md` |
| `api-contracts-raw.md` | `api-contracts.md` |
| `auth-patterns.md` | `auth-patterns.md` |
| `business-rules.md` | `business-rules.md` |
| `open-questions-br.md` | `open-questions-br.md` |
| `design-overview.md` | `design-overview.md` |
| `design-tokens.md` | `design-tokens.md` |
| `component-map.md` | `component-map.md` |
| `state-map.md` | `state-map.md` |
| `data-flow.md` | `data-flow.md` |
| `security-model.md` | `security-model.md` |
| `pii-map.md` | `pii-map.md` |

`Synthesizer` pode deixar de gerar um artefato apenas quando:

- o nivel nao exige aquele arquivo
- a fase anterior registrou explicitamente "não aplicável"

## 5. Definição de gap

Um gap e qualquer uma destas situacoes:

- evidencia ausente para uma afirmacao esperada
- conflito entre duas fontes
- cobertura parcial de um fluxo, tela, endpoint ou entidade
- dependencia de resposta do usuario
- dependencia de rodada adicional de exploracao

Todo gap deve ter:

- `gap_id`
- `tipo`
- `descrição`
- `impacto`
- `arquivos_afetados`
- `ação_recomendada`
- `responsável_sugerido`
- `status`

## 6. Definição de remediação

Quando um gap puder ser atacado sem perguntar ao usuario, o `Synthesizer` deve registrar um pedido em
`remediation-requests.md`. Esse arquivo nao dispara subagentes diretamente. Ele serve para o `Conductor`
decidir se reabre exploracao.

Campos obrigatorios por pedido:

- `remediation_id`
- `worker_sugerido`
- `objetivo`
- `arquivos_de_entrada`
- `evidência_esperada`
- `prioridade`
- `status`

## 7. Estrutura de `gaps.md`

```markdown
# Gaps

## Resumo
- Gaps totais:
- Gaps bloqueantes:
- Gaps que dependem do usuário:
- Gaps elegíveis para remediação:

## Lista de gaps
### GAP-001
- Tipo:
- Descrição:
- Impacto:
- Arquivos afetados:
- Ação recomendada:
- Responsável sugerido:
- Status:

## Decisões de consolidação impactadas
- ...
```

## 8. Estrutura de `synthesis-report.md`

```markdown
# Synthesis Report

## Resumo executivo
- Nível:
- Arquivos raw lidos:
- Artefatos consolidados:
- Conflitos resolvidos:
- Gaps remanescentes:

## Cobertura consolidada por domínio
| domínio | status | observações |

## Conflitos reconciliados
| item | fontes | decisão | justificativa |

## Pendências para checkpoint HITL
- ...
```

## 9. Estrutura de `remediation-requests.md`

```markdown
# Remediation Requests

## Resumo
- Pedidos emitidos:
- Rodada de remediação:

## Pedidos
| remediation_id | worker_sugerido | objetivo | arquivos_de_entrada | evidência_esperada | prioridade | status |
```

Valores de `status`:

- `pending`
- `approved_by_conductor`
- `completed`
- `discarded`

## 10. Estrutura de `validation-report.md`

```markdown
# Validation Report

## Resumo
- Nível:
- Arquivos consolidados verificados:
- Checklist total:
- Itens aprovados:
- Alertas:
- Falhas:

## Checklist por categoria
| categoria | item | status | evidência | observação |

## Riscos residuais
- ...

## Recomendação do Validator
- Prosseguir para checkpoint HITL
- Revisar gaps antes do checkpoint
```

Valores de `status`:

- `OK`
- `ALERTA`
- `FALHA`
- `NÃO APLICÁVEL`

## 11. Estrutura de `user-confirmation.md`

```markdown
# User Confirmation

## Estado
- Status: pending | approved | needs_revision
- Fase: validation

## Checkpoint apresentado
{mensagem exata apresentada ao usuário}

## Resposta do usuário
{texto do usuário ou "pendente"}

## Próxima ação
- ...
```

O `Validator` pode criar o arquivo com `Status: pending`. O `Conductor` e quem atualiza a resposta real do usuario.

## 12. Camada final `sdd/`

A raiz de `_hermes/{scope-slug}/` e a base consolidada e auditavel da sessao.
O diretorio `_hermes/{scope-slug}/sdd/` e a camada editorial final entregue ao usuario.

Regras:

- o `Synthesizer` nunca escreve em `sdd/`
- o `Validator` valida a base consolidada, nao a redacao final do `sdd/`
- o `SDD-Writer` le apenas a base consolidada e gera o pacote final

## 13. Artefatos finais por nível

Todo pacote final em `sdd/` deve conter:

- `sdd-index.md`

### L1

- `architecture-overview.md`
- `screen-inventory.md`
- `db-schema-outline.md`
- `main-flows.md`
- `tech-stack.md`

### L2

Além de `L1`:

- `component-map.md`
- `business-rules.md`
- `api-contracts.md`
- `state-map.md`
- `design-overview.md`

### L3

Além de `L2`:

- `design-tokens.md`
- `db-complete.md`
- `security-model.md`
- `error-catalog.md`
- `performance-notes.md`
- `test-strategy.md`

## 14. Mapeamento consolidado -> pacote final

| Consolidado | Documento final |
|---|---|
| `architecture-patterns.md` + `code-structure.md` + `tech-stack.md` | `architecture-overview.md` |
| `screen-inventory.md` | `screen-inventory.md` |
| `navigation-graph.md` + `business-rules.md` + `api-contracts.md` | `main-flows.md` |
| `db-schema.md` + `db-relations.md` | `db-schema-outline.md` |
| `db-schema.md` + `db-relations.md` + `data-types.md` | `db-complete.md` |
| `tech-stack.md` | `tech-stack.md` |
| `component-map.md` | `component-map.md` |
| `business-rules.md` + `open-questions-br.md` | `business-rules.md` |
| `api-contracts.md` + `auth-patterns.md` | `api-contracts.md` |
| `state-map.md` + `data-flow.md` | `state-map.md` |
| `design-overview.md` | `design-overview.md` |
| `design-tokens.md` | `design-tokens.md` |
| `security-model.md` + `pii-map.md` + `auth-patterns.md` | `security-model.md` |
| `ui-states-catalog.md` + `gaps.md` | `error-catalog.md` |
| `tech-stack.md` + `tech-debt.md` + `gaps.md` | `performance-notes.md` |
| `validation-report.md` + `gaps.md` + artefatos consolidados | `test-strategy.md` |

O `SDD-Writer` pode combinar mais fontes do que as listadas acima, mas nunca pode ignorar a base consolidada
obrigatoria de cada documento.
