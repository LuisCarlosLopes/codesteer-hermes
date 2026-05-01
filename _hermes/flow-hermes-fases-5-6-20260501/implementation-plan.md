# Plano de Implementacao — HERMES FASE 5 e FASE 6

Data: 2026-05-01
Escopo: planejar a implementacao da FASE 5 (Validacao), FASE 6 (Documentacao SDD) e registrar uma validacao geral do escopo atual descrito em `HERMES.md`
Status atual: planejamento

## 1. Diagnostico atual

O repositorio ja saiu do estado inicial das FASES 3 e 4: hoje existem contrato canonico de artefatos, agentes de analise preenchidos, `Synthesizer` especificado e `Validator` com protocolo proprio.

Para FASE 5 e FASE 6, o quadro atual e este:

- `Validator` ja possui corpo canonico utilizavel em `_codesteer-hermes/agents/validator.md`
- o contrato de `validation-report.md` e `user-confirmation.md` ja existe em `_codesteer-hermes/contracts/artifact-contracts.md`
- `skill-sdd-template` ja existe e define regras-base de escrita
- os templates por nivel existem em `_codesteer-hermes/templates/l1`, `l2` e `l3`
- o agente canonico `SDD-Writer` ainda nao existe de fato: `_codesteer-hermes/agents/sdd-writer.md` esta em placeholder circular

Conclusao: a FASE 5 esta parcialmente especificada e proxima de ficar operacional. A FASE 6 ainda esta estruturalmente incompleta porque falta o agente principal que transforma os artefatos validados em entrega final.

## 2. Validacao geral do escopo

O escopo geral da HERMES esta coerente em alto nivel: intake -> exploracao -> analise -> sintese -> validacao -> documentacao final. O problema nao esta no fluxo macro. O problema esta nas fronteiras operacionais entre FASE 5, FASE 6, contratos e templates.

### 2.1 Pontos consistentes

- o principio de "fan-out so em read-only" esta preservado
- a separacao entre `raw/`, consolidado e artefato final esta conceitualmente correta
- o `Conductor` ja modela gates HITL por fase
- o contrato canonico de artefatos reduz bastante a ambiguidade entre FASE 4 e FASE 5
- os templates por nivel cobrem a maior parte dos artefatos finais esperados

### 2.2 Inconsistencias e lacunas de escopo

#### A. FASE 6 sem agente canonico real

Hoje a maior lacuna do escopo e objetiva:

- `_codesteer-hermes/agents/sdd-writer.md` nao contem protocolo
- o arquivo manda "ler o proprio arquivo canonico", mas ele ja e o arquivo canonico

Impacto:

- a FASE 6 nao e executavel
- nao ha definicao operacional de inputs, outputs, guardrails e criterio de encerramento

#### B. Ambiguidade entre "artefato consolidado" e "artefato final SDD"

`HERMES.md` diz que:

- o `Synthesizer` gera versoes consolidadas na raiz de `_hermes/{scope-slug}/`
- o `SDD-Writer` escreve o resultado final em `_hermes/{scope-slug}/sdd/`

Isso esta correto como conceito, mas falta uma regra explicita para:

- quais arquivos sao "base consolidada"
- quais arquivos sao "documentacao final"
- quando o nome do arquivo muda entre consolidado e SDD

Impacto:

- risco de o `SDD-Writer` apenas copiar artefatos consolidados para `sdd/`
- risco de o `Validator` validar um nome e o template final usar outro

#### C. Inconsistencia de nomenclatura do schema de banco

Hoje coexistem tres nomes/logicas:

- em L1, o template final esperado e `db-schema-outline.md`
- no contrato consolidado da FASE 4, o nome e `db-schema.md`
- na checklist do `Validator`, o arquivo exigido tambem e `db-schema.md`

Impacto:

- a passagem FASE 5 -> FASE 6 fica ambigua
- nao esta claro se `db-schema.md` e base consolidada intermediaria para alimentar `db-schema-outline.md` e `db-complete.md`, ou se o nome final deveria ser outro

#### D. Ambiguidade sobre `sdd-index.md`

`HERMES.md` afirma no texto da FASE 6 que o `SDD-Writer` gera `sdd-index.md` como parte do protocolo geral. Mas:

- o mapeamento por nivel da `skill-sdd-template` lista `sdd-index.md` apenas em `L3`
- o sumario de L3 em `HERMES.md` tambem coloca `sdd-index.md` como artefato adicional de `L3`

Impacto:

- falta decidir se `sdd-index.md` e obrigatorio em todos os niveis ou apenas em `L3`

#### E. Checklist da FASE 5 mistura cobertura funcional com cobertura de UI

O item:

- "Todo endpoint em `api-contracts.md` aparece em ao menos um fluxo de tela"

e forte demais para alguns escopos, por exemplo:

- endpoints internos sem tela direta
- endpoints de suporte administrativo fora do fluxo principal
- escopos tipo `api` ou `module` sem UI proporcional

Impacto:

- o `Validator` pode reprovar artefatos corretos por uma regra excessivamente rigida

#### F. Templates finais ainda estao praticamente vazios

Os arquivos em `_codesteer-hermes/templates/` hoje sao basicamente placeholders de titulo.

Impacto:

- mesmo com `SDD-Writer` implementado, a FASE 6 ainda nao entrega padrao editorial consistente
- faltam secoes obrigatorias por template, cross-references esperadas e criterios de minimo aceitavel

#### G. Falta fixture dedicada para FASE 5 e 6

Hoje existem fixtures que cobrem essencialmente o terreno de FASE 3/4. Nao existe, pelo menos no repositorio atual, fixture clara para:

- validacao feliz de FASE 5
- falha por artefato obrigatorio ausente
- aprovacao com alerta
- geracao completa de `sdd/` em L1, L2 e L3

Impacto:

- alta chance de regressao silenciosa na fase final do pipeline

## 3. Objetivo da implementacao

Entregar uma FASE 5 e uma FASE 6 que sejam:

- deterministicas
- alinhadas ao contrato canonico
- rastreaveis de ponta a ponta
- compatíveis com os gates HITL do `Conductor`
- capazes de produzir um pacote `sdd/` previsivel por nivel

## 4. Decisoes arquiteturais necessarias antes de codificar

### 4.1 Consolidado nao e entrega final

Recomendacao:

- raiz de `_hermes/{scope-slug}/` = base reconciliada e auditavel
- `_hermes/{scope-slug}/sdd/` = pacote final de leitura humana

Regra pratica:

- `Synthesizer` nunca escreve em `sdd/`
- `Validator` nunca valida o conteudo editorial de `sdd/`; valida a base consolidada
- `SDD-Writer` le apenas a base consolidada e gera a camada editorial final

### 4.2 `db-schema.md` deve ser tratado como artefato intermediario

Recomendacao:

- manter `db-schema.md` como consolidado canonico da FASE 4
- `SDD-Writer` transforma isso em:
  - `db-schema-outline.md` no `L1`
  - `db-complete.md` no `L3`

Isso remove a colisao entre contrato tecnico e formato final de documento.

### 4.3 `sdd-index.md` deve existir em todos os niveis

Recomendacao:

- promover `sdd-index.md` para artefato final universal de `L1`, `L2` e `L3`

Motivo:

- simplifica navegacao
- padroniza a entrega final
- reduz branching condicional no `SDD-Writer`

Se isso nao for desejado, entao o texto da FASE 6 precisa ser reduzido para explicitar "apenas L3".

### 4.4 O `Validator` deve validar cobertura por escopo, nao por dogma

Recomendacao:

- trocar "todo endpoint aparece em fluxo de tela" por "todo endpoint aparece em fluxo, regra, tela ou contexto explicito do escopo"

Isso ja esta mais proximo do que o proprio `validator.md` canônico descreve do que do texto resumido em `HERMES.md`.

### 4.5 Templates precisam virar contrato editorial minimo

Recomendacao:

- cada template deve ter estrutura minima obrigatoria
- o `SDD-Writer` nao deve improvisar secoes
- `skill-sdd-template` deve refletir os templates reais e nao compensar a falta deles

## 5. Backlog de implementacao

### Etapa 1 — Fechar as decisoes de escopo da FASE 5/6

Objetivo: eliminar ambiguidades antes de detalhar agente e templates.

Decisoes que precisam ser congeladas:

- `sdd-index.md` e universal ou so `L3`
- `db-schema.md` e intermediario oficial da base consolidada
- quais artefatos finais vivem apenas em `sdd/`
- quais checks do `Validator` sao universais e quais sao condicionais ao tipo de alvo

Criterio de aceite:

- `HERMES.md`, `validator.md`, `artifact-contracts.md` e `skill-sdd-template` deixam de se contradizer

### Etapa 2 — Implementar de fato o agente canonico `SDD-Writer`

Objetivo: remover o maior bloqueio atual da FASE 6.

Arquivo alvo:

- `_codesteer-hermes/agents/sdd-writer.md`

Conteudo minimo esperado:

- identidade e responsabilidade unica
- pre-condicoes explicitas
- envelope minimo de contexto
- mapeamento consolidado -> template -> artefato final
- regras de cross-reference
- tratamento de lacunas e itens `Baixa`
- protocolo de escrita do `sdd-index.md`
- criterio de encerramento

Criterio de aceite:

- o agente pode operar sem depender do texto descritivo de `HERMES.md`

### Etapa 3 — Endurecer a FASE 5

Objetivo: transformar o `Validator` em gate realmente deterministico.

Arquivos alvo:

- `_codesteer-hermes/agents/validator.md`
- `_codesteer-hermes/contracts/artifact-contracts.md`
- `_codesteer-hermes/agents/conductor.md`

Ajustes recomendados:

- alinhar checklist resumida de `HERMES.md` com a checklist operacional de `validator.md`
- tornar alguns checks condicionais a `target_type` e `level`
- definir como o `Conductor` persiste a resposta do usuario em `user-confirmation.md`
- definir quando `ALERTA` permite avancar e quando exige bloqueio

Criterio de aceite:

- nao existe duvida sobre quando a FASE 5 aprova, alerta ou barra a sessao

### Etapa 4 — Transformar templates em estrutura editorial utilizavel

Objetivo: fazer a FASE 6 ter destino real.

Arquivos alvo:

- todos os templates em `_codesteer-hermes/templates/l1`
- todos os templates em `_codesteer-hermes/templates/l2`
- todos os templates em `_codesteer-hermes/templates/l3`

Cada template deve definir:

- objetivo do documento
- secoes obrigatorias
- lista minima de evidencias/cross-references
- como marcar `REQUER VALIDAÇÃO`
- o que fazer quando houver dados insuficientes

Criterio de aceite:

- duas sessoes diferentes produzem documentos com forma semelhante e qualidade editorial previsivel

### Etapa 5 — Ajustar `skill-sdd-template`

Objetivo: alinhar a skill ao agente real e aos templates reais.

Arquivo alvo:

- `_codesteer-hermes/skills/skill-sdd-template/SKILL.md`

A skill deve passar a conter:

- estrategia de composicao por nivel
- regra de naming final no diretorio `sdd/`
- exemplos de cross-reference boa
- exemplos de marcacao de lacuna
- anti-padroes especificos de duplicacao entre consolidado e SDD final

Criterio de aceite:

- o `SDD-Writer` recebe reforco util, e nao apenas lembretes genericos

### Etapa 6 — Fixtures e validacao de ponta a ponta

Objetivo: provar que FASE 5 e 6 funcionam sem depender de um projeto real grande.

Fixtures recomendadas:

- `phase56-l1-happy-path`
- `phase56-l2-open-questions-reviewed`
- `phase56-l2-endpoint-without-screen`
- `phase56-l3-security-and-pii`
- `phase56-missing-required-artifact`

Cada fixture deve permitir validar:

- checklist do `Validator`
- comportamento de bloqueio vs alerta
- escrita do `user-confirmation.md`
- geracao do pacote `sdd/`
- coerencia do `sdd-index.md`

Criterio de aceite:

- a camada final da HERMES pode ser revisada sem depender do historico da conversa

## 6. Ordem recomendada de execucao

1. Congelar as decisoes de escopo listadas na Etapa 1
2. Implementar `sdd-writer.md`
3. Ajustar `artifact-contracts.md`, `validator.md` e `conductor.md`
4. Estruturar os templates `l1`, `l2`, `l3`
5. Refinar `skill-sdd-template`
6. Criar fixtures de FASE 5/6
7. Rodar validacao final de consistencia do fluxo FASE 4 -> 5 -> 6

Motivo:

- hoje o gargalo principal nao e o `Validator`; e a ausencia do contrato operacional do `SDD-Writer`
- preencher templates antes de congelar o agente tambem tende a gerar retrabalho

## 7. Milestones sugeridas

### Milestone A — Fechamento de escopo

- decisoes de naming e obrigatoriedade resolvidas
- textos centrais sem contradicoes

Resultado esperado:

- a FASE 5/6 deixa de ter conflitos de especificacao

### Milestone B — Execucao da FASE 6

- `sdd-writer.md` implementado
- `skill-sdd-template` alinhada

Resultado esperado:

- HERMES passa a conseguir gerar entrega final, ainda que com templates simples

### Milestone C — Qualidade editorial e gate

- templates preenchidos
- `Validator` endurecido
- `Conductor` alinhado ao gate final

Resultado esperado:

- pipeline final fica revisavel e previsivel

### Milestone D — Prova por fixtures

- fixtures criadas
- cenarios felizes e de falha cobertos

Resultado esperado:

- validacao objetiva das fases finais sem depender de julgamento informal

## 8. Riscos principais

- implementar o `SDD-Writer` antes de resolver naming e fronteira consolidado/final
- endurecer demais o `Validator` e reprovar escopos validos sem UI direta
- deixar os templates vazios e empurrar toda a estrutura para o prompt do agente
- manter `sdd-index.md` ambíguo por nivel e gerar bifurcacao desnecessaria

## 9. Definicao de pronto

Considerar FASE 5 e FASE 6 prontas quando:

- `_codesteer-hermes/agents/sdd-writer.md` deixar de ser placeholder
- `Validator`, contrato e `HERMES.md` estiverem semanticamente alinhados
- os templates tiverem secoes obrigatorias reais
- o pacote final `_hermes/{scope-slug}/sdd/` tiver naming previsivel por nivel
- existir fixture cobrindo aprovacao, alerta e bloqueio
- o fluxo FASE 4 -> FASE 5 -> FASE 6 puder ser revisado sem inferencia adicional

## 10. Recomendacao pratica

Se o objetivo for velocidade com baixo retrabalho, a primeira acao correta nao e "começar pelos templates" e nem "apertar o Validator". A primeira acao correta e escrever o agente canônico do `SDD-Writer` e, ao mesmo tempo, congelar as decisoes de naming e obrigatoriedade que hoje ainda estao contraditorias no escopo.
