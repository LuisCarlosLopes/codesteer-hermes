# Plano de Implementacao — HERMES FASE 3 e FASE 4

Data: 2026-05-01
Escopo: implementar a camada de analise (FASE 3) e sintese (FASE 4) descritas em `HERMES.md`
Status atual: planejamento

## 1. Diagnostico atual

O desenho funcional das FASES 3 e 4 esta relativamente bem definido em `HERMES.md`, mas a implementacao canônica ainda nao existe de fato:

- Os agentes canônicos abaixo ainda estao em placeholder:
  - `_codesteer-hermes/agents/br-analyst.md`
  - `_codesteer-hermes/agents/design-analyst.md`
  - `_codesteer-hermes/agents/state-analyst.md`
  - `_codesteer-hermes/agents/security-analyst.md`
  - `_codesteer-hermes/agents/synthesizer.md`
  - `_codesteer-hermes/agents/validator.md`
- As skills de suporte das FASES 3 e 4 tambem estao praticamente vazias:
  - `_codesteer-hermes/skills/skill-br-extraction/SKILL.md`
  - `_codesteer-hermes/skills/skill-design-audit/SKILL.md`
  - `_codesteer-hermes/skills/skill-state-reverse/SKILL.md`
  - `_codesteer-hermes/skills/skill-sdd-template/SKILL.md`
- O `Conductor` ja descreve os gates e envelopes, mas ainda falta um contrato operacional claro para:
  - entrada minima por analyst
  - formato consistente dos outputs `raw/`
  - resolucao de gaps da FASE 4 sem violar a responsabilidade unica do Conductor

Conclusao: o gap principal nao e "falta de wiring". O gap principal e falta de especificacao executavel dos agentes, skills e contratos de arquivo.

## 2. Objetivo da implementacao

Entregar uma FASE 3 e uma FASE 4 que sejam:

- deterministicas
- read-only sobre o artefato original
- baseadas em arquivos em `_hermes/{scope-slug}/`
- compatíveis com o principio de zero inferencia
- suficientemente estruturadas para sustentar a FASE 5 e a FASE 6 sem ambiguidade

## 3. Decisoes arquiteturais que devem guiar a implementacao

### 3.1 FASE 3 so le `raw/`

Os analysts nao devem reler o codebase original. Toda a FASE 3 deve operar exclusivamente sobre os artefatos gerados na FASE 2. Isso precisa virar regra explicita nos agentes e nas skills.

### 3.2 Contrato de arquivo antes de prompt

Antes de escrever o corpo final dos agentes, definir uma tabela canonica de I/O para cada worker:

- entradas obrigatorias
- entradas opcionais
- arquivos de saida
- campos obrigatorios em cada arquivo
- como marcar certeza, evidencia, conflito e item aberto

Sem isso, cada agente vai escrever em formato diferente e o Synthesizer vira um parser informal.

### 3.3 O Synthesizer identifica a remedicao; o Conductor executa

`HERMES.md` diz que o Synthesizer pode disparar mini-task para exploracao adicional. Para preservar a responsabilidade do Conductor como unico orquestrador, a implementacao deve funcionar assim:

1. `Synthesizer` identifica o gap
2. `Synthesizer` grava um artefato estruturado de remedicao
3. `Conductor` decide se abre rodada adicional com worker da FASE 2 ou 3
4. `Conductor` reapresenta checkpoint

Isso evita dois agentes controlando fluxo de sessao ao mesmo tempo.

### 3.4 Security Analyst e um ponto de decisao

Hoje existe agente de seguranca em `HERMES.md`, mas nao existe skill dedicada. Ha duas opcoes:

- Opcao A: manter o `security-analyst` autocontido no proprio agente
- Opcao B: criar `skill-security-audit`

Recomendacao: comecar com a Opcao A para reduzir superficie. Se a heuristica ficar grande demais, extrair skill depois usando `skill-creator`.

## 4. Backlog de implementacao

### Etapa 1 — Contratos canonicos de FASE 3 e 4

Objetivo: definir o protocolo de arquivos que todos os agentes vao obedecer.

Entregas:

- Criar uma secao canônica de contratos em um dos dois formatos:
  - opcao preferida: documento novo em `_codesteer-hermes/` dedicado a contratos de artefatos
  - opcao minima: incorporar os contratos diretamente nos agentes e skills
- Definir o esquema minimo para:
  - `raw/business-rules.md`
  - `raw/open-questions-br.md`
  - `raw/design-overview.md`
  - `raw/design-tokens.md`
  - `raw/component-map.md`
  - `raw/state-map.md`
  - `raw/data-flow.md`
  - `raw/security-model.md`
  - `raw/pii-map.md`
  - `gaps.md`
  - `synthesis-report.md`
- Padronizar metadados obrigatorios em todos os arquivos:
  - resumo
  - fontes/evidencias
  - conteudo extraido
  - itens inferidos e nao verificados
  - conflitos/bloqueios/perguntas abertas

Criterio de aceite:

- um humano consegue prever exatamente quais arquivos a FASE 3 e 4 vao produzir
- o Validator consegue validar sem interpretacao ad hoc

### Etapa 2 — Implementar os agentes canônicos da FASE 3

Objetivo: trocar placeholders por instrucoes operacionais executaveis.

Arquivos alvo:

- `_codesteer-hermes/agents/br-analyst.md`
- `_codesteer-hermes/agents/design-analyst.md`
- `_codesteer-hermes/agents/state-analyst.md`
- `_codesteer-hermes/agents/security-analyst.md`

Cada agente deve incluir:

- identidade e responsabilidade unica
- pre-condicoes explicitas
- envelope minimo de contexto
- protocolo passo a passo
- formato de output
- guardrails
- criterio de encerramento da tarefa
- regra de escalonamento quando faltar evidencia

Pontos especificos:

- `br-analyst` precisa classificar certeza por regra e expulsar certeza baixa para `open-questions-br.md`
- `design-analyst` precisa separar claramente L2 de L3
- `state-analyst` precisa mapear produtor, consumidor e fronteira do estado
- `security-analyst` precisa distinguir fato observado de risco potencial sem virar pentest

Criterio de aceite:

- cada agente consegue ser usado isoladamente sem depender de interpretacao externa do `HERMES.md`

### Etapa 3 — Implementar as skills da FASE 3

Objetivo: dar repertorio operacional aos analysts sem inflar o prompt-base.

Arquivos alvo:

- `_codesteer-hermes/skills/skill-br-extraction/SKILL.md`
- `_codesteer-hermes/skills/skill-design-audit/SKILL.md`
- `_codesteer-hermes/skills/skill-state-reverse/SKILL.md`

Conteudo esperado:

- heuristicas por stack
- sinais fortes vs sinais fracos
- estrategia de evidencia
- formato de citacao para arquivos `raw/`
- exemplos de saida boa e saida ruim

Decisao adicional:

- avaliar se `security-analyst` precisa de skill propria depois da primeira rodada funcional

Criterio de aceite:

- o agente consegue carregar a skill e executar o protocolo sem reinstrucoes manuais

### Etapa 4 — Implementar o Synthesizer

Objetivo: transformar os `raw/` em uma base reconciliada e auditavel.

Arquivos alvo:

- `_codesteer-hermes/agents/synthesizer.md`

Capacidades obrigatorias:

- ler todos os arquivos `raw/`
- cruzar entidades entre dominios
- detectar inconsistencias
- classificar cada gap por tipo:
  - faltou evidencia
  - conflito entre fontes
  - cobertura parcial
  - dependencia de resposta do usuario
- produzir saidas consolidadas sem sufixo `-raw`
- produzir `gaps.md`
- produzir `synthesis-report.md`
- produzir, se necessario, um artefato de pedido de remedicao para o Conductor

Recomendacao de implementacao:

- definir uma matriz de reconciliacao minima:
  - tela -> fluxo -> BR
  - endpoint -> tela ou fluxo
  - entidade de dados -> model ou modulo
  - permissao/role -> endpoint ou tela protegida

Criterio de aceite:

- o Synthesizer consegue explicar por que consolidou ou marcou conflito em cada item importante

### Etapa 5 — Ajustar Conductor e Validator para acomodar a FASE 4 real

Objetivo: garantir que a sintese implementada encaixe no pipeline existente.

Arquivos provaveis:

- `_codesteer-hermes/agents/conductor.md`
- `_codesteer-hermes/agents/validator.md`

Ajustes necessarios:

- formalizar como o Conductor consome pedidos de remedicao emitidos pelo Synthesizer
- limitar a duas rodadas extras de exploracao, como definido no `HERMES.md`
- explicitar o que conta como "arquivo consolidado"
- alinhar checklist do Validator com os nomes reais de arquivo

Criterio de aceite:

- nao existe ambiguidade sobre quem decide nova rodada de exploracao

### Etapa 6 — Validacao por fixtures

Objetivo: testar o desenho sem depender de um projeto real grande.

Abordagem recomendada:

- criar um fixture pequeno em `_hermes/` com `raw/` sintetico
- executar mentalmente ou por roteiro:
  - caso feliz L2
  - caso com BR de baixa certeza
  - caso com conflito entre UI e DB
  - caso L3 com PII e auth

Se fizer sentido automatizar depois:

- adicionar um verificador simples de presenca de arquivos obrigatorios e secoes minimas

Criterio de aceite:

- os artefatos finais da FASE 4 sao previsiveis e revisaveis sem depender do historico da conversa

## 5. Ordem recomendada de execucao

1. Definir contratos de I/O
2. Implementar `synthesizer.md` e `validator.md` em paralelo conceitual
3. Implementar os quatro analysts da FASE 3
4. Implementar as tres skills de FASE 3
5. Ajustar `conductor.md` para o loop de remedicao
6. Rodar fixture de validacao
7. So depois disso refinar SDD-Writer, se necessario

Motivo: se os contratos de sintese vierem por ultimo, os analysts vao nascer com formatos desalinhados.

## 6. Divisao em milestones

### Milestone A — Base estrutural

- contratos de artefato definidos
- Synthesizer especificado
- Validator alinhado

Resultado esperado:

- pipeline FASE 3 -> FASE 4 deixa de ser conceitual e passa a ser implementavel

### Milestone B — Workers de analise

- quatro agentes da FASE 3 completos
- tres skills da FASE 3 completas

Resultado esperado:

- HERMES consegue produzir analise estruturada a partir dos scouts

### Milestone C — Integracao

- Conductor ajustado para loop de remedicao
- fixture validado
- gaps e checkpoint revisados

Resultado esperado:

- HERMES consegue atravessar FASE 3 e 4 de ponta a ponta com criterios claros

## 7. Riscos e decisoes em aberto

- `HERMES.md` mistura, em alguns pontos, responsabilidade de orquestracao do Conductor com acao operacional do Synthesizer
- nao ha hoje um schema formal para os arquivos `raw/`; sem isso, o custo de manutencao cresce rapido
- `security-analyst` pode ficar subespecificado se tentar operar sem skill e sem exemplos
- o `skill-sdd-template` esta vazio, mas o impacto principal dele aparece na FASE 6; nao deve bloquear a FASE 3/4

## 8. Definicao de pronto

Considerar FASE 3 e FASE 4 implementadas quando:

- todos os agentes canônicos envolvidos deixarem de ser placeholders
- os arquivos produzidos por cada agent tiverem formato previsivel
- o Synthesizer gerar consolidado, gaps e resumo executivo
- o Conductor conseguir governar rodada extra sem conflito de responsabilidade
- o Validator conseguir rodar checklist contra nomes reais de arquivos
- existir pelo menos um fixture demonstrando o fluxo completo

## 9. Recomendacao pratica

Se o objetivo for maximizar velocidade com baixo retrabalho, iniciar pela Milestone A e nao pelos analysts. O erro mais caro aqui seria escrever prompts ricos para a FASE 3 antes de fixar o formato que a FASE 4 precisa consumir.
