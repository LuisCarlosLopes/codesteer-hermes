# HERMES — Hierarchical Engineering Reverse-Map & Extraction Squad
**Proposta de Squad Agentic: Engenharia Reversa → SDD**
**Versão 2.0 — Documento Unificado**

> *"Se um humano precisa inferir o que o sistema faz, o agente falhou antes de começar."*

---

## 1. Sumário Executivo

HERMES é uma squad de agentes especializados para realizar engenharia reversa de artefatos de software — módulo, tela ou aplicação completa — e produzir documentos SDD (Software Design Document) prontos para recriação. A squad opera em **seis fases sequenciais**, com **fan-out paralelo exclusivamente em fases read-only** de exploração e análise, e **agente único sequencial** nas fases de síntese e escrita do SDD — evitando o *Flappy Bird effect* de saídas inconsistentes geradas em paralelo.

O princípio cardinal é **zero inferência**: nenhum agente assume ou supõe. Todo gap de informação dispara uma pergunta estruturada ao usuário antes de qualquer exploração onerosa.

Dois pilares de infraestrutura sustentam a operação:

- **`_codesteer/`** — repositório canônico de toda a squad. Agents, skills e templates existem aqui como source of truth. IDEs são destinos de deploy gerados por um script Python, nunca fontes.
- **`_hermes/{scope-slug}/`** — isolamento total por sessão. Cada análise gera um slug determinístico e legível, garantindo que múltiplas sessões paralelas coexistam sem conflito e que o histórico seja auditável no git.

**Compatibilidade:** Claude Code (nativa, máximo aproveitamento de hooks), Kiro, Cursor, GitHub Copilot Coding Agent.

---

## 2. Princípios Arquiteturais

| Princípio | Aplicação na HERMES |
|---|---|
| **Zero Inferência** | Clarifier bloqueia o pipeline até toda ambiguidade ser resolvida. Nenhum agente downstream recebe contexto incompleto. |
| **Fan-out só em read-only** | Fases 2 e 3 são paralelas e read-only sobre o artefato-alvo. Fases 4, 5 e 6 são sempre agente único sequencial. |
| **Isolamento por sessão** | `_hermes/{scope-slug}/` garante coexistência de múltiplas sessões sem conflito de arquivos. O slug é determinístico e legível por humano. |
| **Fonte canônica única** | `_codesteer/` é o único lugar onde agents, skills e templates existem como source of truth. IDEs são destinos de deploy, nunca fontes. |
| **Frontmatter como configuração** | O corpo do agente é separado do frontmatter IDE-específico. Atualizar instruções não exige conhecer o formato de cada IDE. |
| **Symlink para skills** | Skills não têm variação IDE-específica; symlinks diretos evitam qualquer duplicação. |
| **Deploy determinístico** | `deploy.py` é idempotente, auditável via log, e detecta edições manuais nos arquivos de destino. |
| **Arquivos como memória compartilhada** | `_hermes/{scope-slug}/` é agnóstico a LLM, revisável por humano e sobrevive à compactação de contexto. |
| **Envelope de contexto mínimo** | Cada agente recebe apenas o subconjunto de `_hermes/{scope-slug}/` relevante à sua missão, definido pelo Conductor no handoff. |
| **Progressive disclosure de Skills** | Apenas `name` + `description` de cada skill são pré-carregados. O corpo completo é carregado só quando o agente detecta relevância. |
| **HITL em toda transição de fase** | O usuário aprova o output de cada fase antes do avanço. Checkpoints explícitos, nunca implícitos. |
| **Nível de detalhe como roteamento** | L1/L2/L3 determina quais workers o Conductor ativa. Agentes inativos não consomem tokens. |

---

## 3. Níveis de Detalhe (Parâmetro Global)

O usuário escolhe o nível no início da sessão, na Fase 1. O Conductor usa essa escolha para montar o grafo de execução ativo para toda a sessão.

### L1 — Macro View (Visão de Altitude)

**Quando usar:** Avaliação rápida, onboarding de novo membro, due diligence técnica.

**Agentes ativos:** Conductor, Clarifier, UI-Scout (modo básico), Code-Scout, Data-Scout, Synthesizer, Validator, SDD-Writer.

**Artefatos gerados:**
- `architecture-overview.md` — Stack, camadas, dependências críticas
- `screen-inventory.md` — Lista de telas com descrição de propósito
- `db-schema-outline.md` — Tabelas principais e relações essenciais
- `main-flows.md` — Fluxos felizes dos 3–5 casos de uso core
- `tech-stack.md` — Versões, frameworks, libs

**Estimativa de consumo:** ~40–80k tokens por sessão completa.

---

### L2 — Functional View (Visão Funcional)

**Quando usar:** Recriação de funcionalidade específica, handoff entre times, documentação de produto legado.

**Agentes ativos:** Todos do L1 + API-Scout, Business-Rules Analyst, Design Analyst, State Analyst.

**Artefatos adicionais sobre L1:**
- `component-map.md` — Árvore de componentes por tela, props, dependências
- `business-rules.md` — BRs em formato EARS-notation por domínio
- `api-contracts.md` — Endpoints, request/response schemas, auth
- `state-map.md` — Stores, slices, queries, fluxo de dados
- `design-overview.md` — Sistema de design em alto nível, padrões visuais

**Estimativa de consumo:** ~150–300k tokens por sessão completa.

---

### L3 — Complete SDD (Documento Completo)

**Quando usar:** Recriação total de um app, auditoria completa, migração de plataforma.

**Agentes ativos:** Todos do L2 + Security Analyst + UI-Scout em modo Playwright profundo.

**Artefatos adicionais sobre L2:**
- `design-tokens.md` — Cores, tipografia, espaçamento, breakpoints completos
- `db-complete.md` — Migrations, índices, constraints, triggers, seeds
- `security-model.md` — Auth flows, permissões, roles, dados sensíveis
- `error-catalog.md` — Estados de erro por tela e por operação
- `performance-notes.md` — Pontos críticos de performance identificados
- `test-strategy.md` — Cobertura existente, gaps, estratégia sugerida
- `sdd-index.md` — Índice mestre com referências cruzadas entre todos os artefatos

**Estimativa de consumo:** ~400–800k tokens por sessão completa.

---

## 4. Catálogo de Agentes

### FASE 0 — ORQUESTRAÇÃO CONTÍNUA

---

#### 🎼 Conductor
**Tipo:** Supervisor (ativo durante toda a sessão)
**Single Responsibility:** Gerenciar o grafo de estado da squad, gerar o scope slug, rotear entre fases, aplicar HITL gates e ajustar o plano de execução com base no nível de detalhe.

**Missão:**
O Conductor é o único agente com visão completa do pipeline. Não analisa nem escreve conteúdo — gerencia transições. Seu primeiro ato após o Clarifier fechar `scope.md` é gerar o scope slug e criar `_hermes/{scope-slug}/session.yaml`. A partir daí, propaga o caminho `_hermes/{scope-slug}/` para todos os agentes como parte do envelope de contexto. Lê o nível (L1/L2/L3) e monta o conjunto de workers ativos. Ao final de cada fase, consolida outputs e apresenta um **resumo de checkpoint** ao usuário antes de avançar.

**Scope slug — geração:**

O slug segue o formato `{target-type}-{sanitized-name}-{YYYYMMDD}`:

- `target-type`: um de `app`, `module`, `screen`, `api`, `flow` — extraído da classificação do Clarifier
- `sanitized-name`: lowercase, hífens, máximo 24 caracteres, sem caracteres especiais
- `YYYYMMDD`: data de início da sessão
- Sufixo `--N` em caso de colisão no mesmo dia

Exemplos: `app-ecommerce-checkout-20260501`, `module-user-auth-20260501`, `screen-product-detail-20260501`.

**Inputs recebidos:**
- Sessão iniciada com `target`, `level` (L1/L2/L3) e `source` (código-fonte, URL, APK, combinação)
- `_hermes/{scope-slug}/scope.md` aprovado pelo Clarifier
- Referências de arquivo dos outputs de cada fase (não conteúdo completo)

**Outputs produzidos:**
- `_hermes/{scope-slug}/session.yaml` — manifesto completo da sessão
- `_hermes/.sessions-index.yaml` — registro global de todas as sessões (slug, target, data, status)
- Envelopes de contexto para cada agente (subconjunto mínimo de `_hermes/{scope-slug}/`)
- Mensagens de checkpoint estruturadas para o usuário

**`session.yaml` — estrutura:**
```yaml
scope_slug: app-ecommerce-checkout-20260501
target: "App de e-commerce — módulo de checkout completo"
target_type: app
level: L2
source:
  type: source_code
  path: ../projects/ecommerce-app
created_at: 2026-05-01T14:32:00Z
agents_active:
  - conductor
  - clarifier
  - ui-scout
  - code-scout
  - data-scout
  - api-scout
  - br-analyst
  - design-analyst
  - state-analyst
  - synthesizer
  - validator
  - sdd-writer
phases_completed: []
current_phase: intake
hermes_root: _hermes/app-ecommerce-checkout-20260501
```

**Guardrails:**
- Nunca avança de fase sem confirmação explícita do usuário
- Detecta loops (mesma pergunta ao usuário por 3+ vezes) e escalona com meta-pergunta
- Limita fan-out máximo a 4 workers paralelos simultâneos
- Compacta contexto ao atingir 70% do limite da janela, preservando `_hermes/{scope-slug}/` como âncora

**Compatibilidade IDE:**
- Claude Code: Hook `UserPromptSubmit` para captura de `target` e `level`; `SubagentStop` para consolidação de fase
- Kiro: `postSpecTask` hook para HITL gates
- Cursor/Copilot: MCP server como ponto único de controle de estado

---

### FASE 1 — INTAKE & SCOPING

---

#### 🔍 Clarifier
**Tipo:** Worker sequencial (bloqueante — nada avança sem sua conclusão)
**Single Responsibility:** Eliminar toda ambiguidade de escopo antes de qualquer exploração onerosa.

**Missão:**
O Clarifier é o guardião da fronteira entre o usuário e o pipeline. Nunca assume. Sua única função é transformar um input vago em um manifesto de escopo preciso aprovado pelo usuário. Emite perguntas em lotes — máximo 5 por rodada, nunca uma a uma — para eficiência de turnos.

**Protocolo de perguntas:**

*Rodada 1 — Escopo e Target:*
1. O que exatamente deve ser analisado? (tela específica / módulo / app completo)
2. Qual o objetivo do SDD? (recriar do zero / documentar para handoff / auditoria)
3. Há partes que devem ser **excluídas** da análise?

*Rodada 2 — Acesso ao Artefato:*
4. Como a squad acessa o artefato? (código-fonte no repo / URL de aplicação web rodando / APK/IPA / combinação)
5. Há credenciais, variáveis de ambiente ou dados de teste necessários para explorar a aplicação rodando?

*Rodada 3 — Restrições:*
6. Há informações confidenciais que **não** devem ser incluídas no SDD?
7. Há tecnologias específicas que o SDD deve assumir para a recriação?

**Outputs produzidos:**
- `_hermes/{scope-slug}/scope.md` — Target, objetivo, exclusões, nível, fonte de acesso, restrições
- `_hermes/{scope-slug}/glossary.md` — Termos de domínio identificados durante o intake

**Guardrails:**
- Nunca interpreta o input do usuário — reflete de volta para confirmação
- Se a resposta for ambígua, parafraseia e pergunta "Entendi corretamente que...?"
- Máximo de 3 rodadas; se ainda houver ambiguidade, documenta como "item aberto" no `scope.md` e avança com o que foi clarificado

**Skill associada:** `skill-clarifier`

---

### FASE 2 — EXPLORAÇÃO (Fan-out Paralelo / Read-only)

*Todos os workers desta fase são read-only. Não escrevem no codebase original. Escrevem apenas em `_hermes/{scope-slug}/raw/`.*

---

#### 🗺️ UI-Scout
**Tipo:** Worker paralelo (ativo em L1/L2/L3)
**Single Responsibility:** Mapear todas as telas, estados visuais e fluxos de navegação do artefato.

**Missão:**
UI-Scout explora a interface do artefato e produz um inventário visual e estrutural. Em **modo básico (L1)**, lista telas e descreve propósito via leitura de estrutura de rotas. Em **modo profundo (L2/L3)**, usa Playwright-CLI para navegar, capturar screenshots, mapear interações e identificar estados por tela.

**Protocolo de exploração:**

*Modo Básico (L1) — sem execução da aplicação:*
- Lê estrutura de arquivos de rotas (Next.js `pages/` / `app/`, expo-router `app/`, React Router)
- Infere inventário de telas a partir da estrutura de diretórios
- Lê componentes de nível de página para descrever propósito

*Modo Profundo (L2/L3 — Playwright-CLI):*
1. Captura screenshot da tela inicial
2. Mapeia todos os elementos clicáveis (links, botões, formulários)
3. Navega para cada rota identificada no modo básico
4. Por tela: captura screenshot, identifica título/heading principal, lista elementos de formulário, identifica chamadas de rede disparadas
5. Força estados de erro (campo vazio, input inválido) quando detecta formulários
6. Documenta fluxos de navegação como grafo: `Tela A → [ação] → Tela B`

**Inputs recebidos (envelope mínimo):**
- `_hermes/{scope-slug}/scope.md`
- Estrutura de diretório de rotas (não codebase completo)

**Outputs produzidos:**
- `_hermes/{scope-slug}/raw/screen-inventory-raw.md` — lista de telas com paths de screenshot e propósito inferido
- `_hermes/{scope-slug}/raw/navigation-graph.md` — grafo de navegação em formato de lista adjacente
- `_hermes/{scope-slug}/raw/ui-states-catalog.md` — estados visuais por tela (L2/L3 apenas)

**Guardrails:**
- Nunca interage com dados reais de produção — usa dados de teste ou modo demo
- Se Playwright-CLI falhar em uma rota, documenta o erro e continua — não para o pipeline
- Não tenta adivinhar o propósito de telas sem pelo menos um elemento identificador

**Skill associada:** `skill-ui-exploration`

---

#### 🔬 Code-Scout
**Tipo:** Worker paralelo (ativo em L1/L2/L3)
**Single Responsibility:** Mapear estrutura de código, stack tecnológica, dependências e padrões arquiteturais.

**Missão:**
Code-Scout realiza análise estática do código-fonte. Nunca executa código. Opera em camadas progressivas: estrutura de diretórios → package manifests → arquivos de configuração → módulos core → padrões de código. Usa grep/ast-grep antes de ler arquivos completos — eficiência de tokens.

**Protocolo de análise:**
1. Lê `package.json` / `pubspec.yaml` / `build.gradle` / `requirements.txt` para identificar stack e versões
2. Mapeia estrutura de diretórios (2 níveis de profundidade)
3. Lê arquivos de configuração (`tsconfig.json`, `babel.config.js`, `metro.config.js`, `.env.example`)
4. Identifica padrão arquitetural (feature-based, layer-based, atomic design)
5. Mapeia entry points e módulos principais
6. Identifica padrões recorrentes (custom hooks, HOCs, contexts, stores)
7. Documenta comentários `// TODO`, `// FIXME`, `// HACK` como dívida técnica

**Inputs recebidos (envelope mínimo):**
- `_hermes/{scope-slug}/scope.md`
- Raiz do repositório (acesso de leitura)

**Outputs produzidos:**
- `_hermes/{scope-slug}/raw/tech-stack.md` — stack com versões exatas
- `_hermes/{scope-slug}/raw/code-structure.md` — árvore de diretórios anotada
- `_hermes/{scope-slug}/raw/architecture-patterns.md` — padrões identificados com exemplos de arquivo
- `_hermes/{scope-slug}/raw/tech-debt.md` — TODOs, FIXMEs, código comentado

**Guardrails:**
- Lê o mínimo de linhas necessário por arquivo (usa ranges, não lê arquivos completos desnecessariamente)
- Arquivos >500 linhas: lê apenas as primeiras 80 (imports + estrutura principal) e registra para análise posterior se necessário
- Não infere propósito de módulo sem pelo menos 2 evidências no código

**Skill associada:** `skill-code-static-analysis`

---

#### 🗄️ Data-Scout
**Tipo:** Worker paralelo (ativo em L1/L2/L3)
**Single Responsibility:** Mapear esquema de banco de dados, modelos de dados, relacionamentos e padrões de persistência.

**Missão:**
Data-Scout extrai o modelo de dados da aplicação a partir de múltiplas fontes: arquivos de migration, ORM models, schemas GraphQL, type definitions e comentários de banco. Prioriza fontes formais (migrations) sobre fontes inferidas (models).

**Protocolo de análise:**
1. Localiza migrations (Prisma, Drizzle, Knex, Django, Laravel, Alembic, Flyway)
2. Lê schemas ORM (Prisma schema, Sequelize models, TypeORM entities)
3. Mapeia relacionamentos (1:1, 1:N, N:N)
4. Identifica índices e constraints documentados
5. Localiza seeds e dados de referência
6. Mapeia enums e tipos de domínio
7. Se não houver migration: infere schema a partir de types/interfaces TypeScript e documenta como "inferido, não verificado"

**Inputs recebidos (envelope mínimo):**
- `_hermes/{scope-slug}/scope.md`
- Diretório de migrations e models

**Outputs produzidos:**
- `_hermes/{scope-slug}/raw/db-schema-raw.md` — tabelas, colunas, tipos, constraints
- `_hermes/{scope-slug}/raw/db-relations.md` — diagrama de relacionamentos (formato Mermaid ER)
- `_hermes/{scope-slug}/raw/data-types.md` — enums, tipos de domínio, valores válidos

**Guardrails:**
- Distingue explicitamente "extraído de migration" vs "inferido de model/type" em cada campo
- Nunca acessa banco de dados em produção — apenas arquivos de schema
- Se dois arquivos conflitam (model desatualizado vs migration), documenta o conflito e pergunta ao usuário antes de avançar

**Skill associada:** `skill-db-reverse`

---

#### 🔌 API-Scout
**Tipo:** Worker paralelo (ativo em L2/L3 apenas)
**Single Responsibility:** Mapear contratos de API — endpoints, request/response schemas, autenticação e padrões de integração.

**Missão:**
API-Scout extrai contratos de API a partir de múltiplas fontes: arquivos OpenAPI/Swagger, definições GraphQL, arquivos de rotas de backend, interceptors de HTTP no frontend e mocks de teste. Nunca faz chamadas reais à API.

**Protocolo de análise:**
1. Localiza `openapi.yaml`, `swagger.json`, `schema.graphql`
2. Se não houver spec formal: lê arquivos de rotas do backend (Express, FastAPI, Laravel, NestJS)
3. Lê camada de serviço/repository no frontend (`*.service.ts`, `*.api.ts`, `api/`)
4. Identifica baseURL, headers padrão, autenticação (JWT, OAuth, API Key)
5. Mapeia cada endpoint: método, path, params, body, response schema, códigos de erro

**Outputs produzidos:**
- `_hermes/{scope-slug}/raw/api-contracts-raw.md` — endpoints documentados
- `_hermes/{scope-slug}/raw/auth-patterns.md` — fluxo de autenticação e autorização

**Guardrails:**
- Read-only de código — nunca faz chamadas reais à API durante a análise
- Documenta endpoints sem spec formal como "inferido de código — requer validação"

**Skill associada:** `skill-api-reverse`

---

### FASE 3 — ANÁLISE (Fan-out Paralelo / Read-only sobre `_hermes/{scope-slug}/raw/`)

*Workers desta fase leem apenas os arquivos produzidos na Fase 2. Não tocam no codebase original.*

---

#### 📋 Business-Rules Analyst
**Tipo:** Worker paralelo (ativo em L2/L3)
**Single Responsibility:** Extrair e documentar regras de negócio em formato estruturado a partir dos artefatos de exploração.

**Missão:**
Sintetiza regras de negócio a partir de múltiplas fontes de evidência: validações de formulário (UI-Scout), constraints de banco (Data-Scout), lógica de API (API-Scout) e comentários de código (Code-Scout). Não infere regras sem evidência; documenta a fonte de cada regra.

**Formato de saída (EARS-notation adaptada):**
```
BR-001: [Domínio] [Condição] → [Ação/Restrição]
Evidência: [arquivo:linha ou tela identificada]
Certeza: Alta (extraído de código) | Média (inferido de validação UI) | Baixa (inferido de nomenclatura)
```

**Outputs produzidos:**
- `_hermes/{scope-slug}/raw/business-rules.md` — BRs organizadas por domínio, com evidência e certeza
- `_hermes/{scope-slug}/raw/open-questions-br.md` — regras que precisam de confirmação do usuário (certeza Baixa)

**Guardrails:**
- Toda regra de certeza "Baixa" vai para `open-questions-br.md` — não entra no SDD sem validação do usuário
- Máximo de 10 perguntas abertas ao usuário por rodada de validação

**Skill associada:** `skill-br-extraction`

---

#### 🎨 Design Analyst
**Tipo:** Worker paralelo (ativo em L2/L3)
**Single Responsibility:** Extrair sistema de design, padrões visuais e inventário de componentes.

**Missão:**
Analisa os screenshots capturados pelo UI-Scout e os arquivos de estilo do Code-Scout para produzir documentação do sistema de design. Em L2 foca em padrões; em L3 extrai tokens específicos com valores exatos.

**Protocolo:**
1. Lê arquivos de tema (`theme.ts`, `tailwind.config.js`, `design-tokens.json`, `tokens.css`)
2. Analisa screenshots para identificar padrões visuais (L3)
3. Inventaria componentes UI reutilizáveis identificados pelo Code-Scout
4. Mapeia variantes de componentes (estados: default, hover, disabled, loading, error)

**Outputs produzidos:**
- `_hermes/{scope-slug}/raw/design-overview.md` — padrões visuais, biblioteca de componentes (L2)
- `_hermes/{scope-slug}/raw/design-tokens.md` — cores, tipografia, espaçamento, sombras com valores (L3)
- `_hermes/{scope-slug}/raw/component-map.md` — árvore de componentes com props inferidas

**Skill associada:** `skill-design-audit`

---

#### 🔄 State Analyst
**Tipo:** Worker paralelo (ativo em L2/L3)
**Single Responsibility:** Mapear gerenciamento de estado — stores, queries, contextos e fluxo de dados.

**Missão:**
Lê os artefatos do Code-Scout focados em gerenciamento de estado (Redux, Zustand, Jotai, Context API, TanStack Query, SWR, Apollo) e produz um mapa do fluxo de dados da aplicação.

**Outputs produzidos:**
- `_hermes/{scope-slug}/raw/state-map.md` — stores, slices, atoms, contextos com responsabilidades
- `_hermes/{scope-slug}/raw/data-flow.md` — quem produz, quem consome cada estado

**Skill associada:** `skill-state-reverse`

---

#### 🔐 Security Analyst
**Tipo:** Worker paralelo (ativo em L3 apenas)
**Single Responsibility:** Mapear modelo de segurança — autenticação, autorização, dados sensíveis e superfície de ataque.

**Missão:**
Analisa fluxos de auth (API-Scout), permissões (Business-Rules Analyst) e dados sensíveis (Data-Scout) para produzir um mapa de segurança do sistema. Identifica mas **não explora** vulnerabilidades.

**Outputs produzidos:**
- `_hermes/{scope-slug}/raw/security-model.md` — roles, permissões, dados sensíveis, flows de auth
- `_hermes/{scope-slug}/raw/pii-map.md` — campos que contêm dados pessoais identificáveis

---

### FASE 4 — SÍNTESE (Agente Único Sequencial)

---

#### 🧬 Synthesizer
**Tipo:** Agente único sequencial (não paralelizável)
**Single Responsibility:** Consolidar todos os artefatos `raw/` em uma visão coerente, resolver conflitos e identificar gaps.

**Missão:**
O Synthesizer é o único agente que lê **todos** os arquivos `_hermes/{scope-slug}/raw/` de uma vez. Detecta inconsistências entre os outputs dos workers — por exemplo, UI-Scout identificou uma tela de "Pagamentos" mas Data-Scout não encontrou tabela de transações — e produz uma lista de gaps que precisam de resolução.

**Protocolo:**
1. Lê todos os arquivos `_hermes/{scope-slug}/raw/`
2. Cruza referências: cada tela do UI-Scout deve ter ao menos uma BR correspondente (L2+); cada entidade do DB deve aparecer em ao menos um model do Code-Scout
3. Lista inconsistências e gaps
4. Para cada gap: determina se pode ser resolvido com exploração adicional (dispara mini-task para worker específico) ou precisa de pergunta ao usuário
5. Produz versão consolidada dos arquivos reconciliados (escreve em `_hermes/{scope-slug}/`, sem sufixo `-raw`)

**Outputs produzidos:**
- `_hermes/{scope-slug}/gaps.md` — inconsistências e itens não resolvidos
- `_hermes/{scope-slug}/synthesis-report.md` — resumo executivo para checkpoint HITL
- Versões consolidadas de todos os arquivos raw (sem sufixo `-raw`)

**Guardrails:**
- Máximo de 2 rodadas de exploração adicional — se o gap persiste, vai para o usuário
- Não preenche gaps com suposições; documenta como "não determinado"

---

### FASE 5 — VALIDAÇÃO (Checkpoint HITL)

---

#### ✅ Validator
**Tipo:** Worker sequencial (bloqueante para fase seguinte)
**Single Responsibility:** Verificar consistência interna dos artefatos sintetizados e conduzir o checkpoint formal com o usuário.

**Missão:**
Aplica uma checklist determinística sobre os artefatos do Synthesizer antes de apresentar ao usuário. Garante que o SDD será construído sobre uma base consistente.

**Checklist de consistência (automatizada):**
- [ ] Toda tela do `screen-inventory.md` tem pelo menos um item em `navigation-graph.md`
- [ ] Toda BR de certeza "Alta" tem evidência referenciada
- [ ] Todo endpoint em `api-contracts.md` aparece em ao menos um fluxo de tela
- [ ] Toda tabela em `db-schema.md` tem ao menos um model no `code-structure.md`
- [ ] `open-questions-br.md` está vazio ou foi revisado pelo usuário

**Checkpoint apresentado ao usuário:**
```
CHECKPOINT HERMES — Fase de Síntese Concluída
Sessão: app-ecommerce-checkout-20260501  |  Nível: L2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Telas mapeadas: N
✅ Regras de negócio extraídas: N (Alta: X | Média: Y | Baixa: Z)
✅ Endpoints documentados: N
✅ Tabelas mapeadas: N
⚠️  Gaps não resolvidos: N  →  _hermes/{scope-slug}/gaps.md
⚠️  Perguntas abertas ao usuário: N

→ Deseja prosseguir para geração do SDD? [Sim / Revisar gaps primeiro]
```

**Outputs produzidos:**
- `_hermes/{scope-slug}/validation-report.md` — checklist com resultados
- `_hermes/{scope-slug}/user-confirmation.md` — resposta do usuário ao checkpoint

---

### FASE 6 — DOCUMENTAÇÃO SDD (Agente Único Sequencial)

---

#### 📄 SDD-Writer
**Tipo:** Agente único sequencial (não paralelizável)
**Single Responsibility:** Transformar os artefatos validados em documentos SDD formatados, organizados e referenciados cruzadamente, conforme o nível selecionado.

**Missão:**
SDD-Writer é o único agente que produz os artefatos finais entregues ao usuário. Lê exclusivamente os arquivos consolidados do Synthesizer — nunca os arquivos `raw/`. Segue os templates de `_codesteer/templates/{l1|l2|l3}/` para garantir consistência de formato entre sessões. Gera um `sdd-index.md` com referências cruzadas entre todos os documentos.

**Protocolo de escrita:**
1. Lê `_hermes/{scope-slug}/session.yaml` para confirmar nível e artefatos esperados
2. Para cada artefato do nível: lê fonte(s) correspondente(s), aplica template de `_codesteer/templates/`, escreve documento final em `_hermes/{scope-slug}/sdd/`
3. Insere referências cruzadas (ex: BR-042 referencia Tabela `orders`, Tela `checkout`)
4. Gera `sdd-index.md` com sumário de todos os documentos, número de itens por seção e links
5. Apresenta ao usuário o índice completo para aprovação final

**Guardrails:**
- Nunca escreve "assume-se que", "provavelmente", "possivelmente" — toda afirmação tem referência ao arquivo `_hermes/{scope-slug}/` de origem
- Itens com certeza "Baixa" são marcados com `⚠️ REQUER VALIDAÇÃO` no SDD
- Se um artefato esperado não tem dados suficientes, escreve seção vazia com nota "Dados insuficientes — ver `gaps.md#item-X`"

**Skill associada:** `skill-sdd-template`

---

## 5. Skills Library

Todas as skills residem canonicamente em `_codesteer/skills/` e são distribuídas para as IDEs via symlink pelo `deploy.py`. O formato segue o standard agentskills.io: cada skill é uma pasta com um `SKILL.md` obrigatório.

| Skill | Agente Principal | Conteúdo Central |
|---|---|---|
| `skill-clarifier` | Clarifier | Templates de perguntas por domínio (web, mobile, backend, monolito) |
| `skill-ui-exploration` | UI-Scout | Padrões Playwright-CLI por framework (Next.js, Expo, React, Angular) |
| `skill-code-static-analysis` | Code-Scout | Padrões de leitura eficiente por stack (grepping patterns, ast-grep queries) |
| `skill-db-reverse` | Data-Scout | Extração por ORM (Prisma, Drizzle, Django, Laravel, TypeORM) |
| `skill-api-reverse` | API-Scout | Leitura de rotas por framework (Express, FastAPI, NestJS, Laravel) |
| `skill-br-extraction` | BR Analyst | EARS-notation, heurísticas de extração de BR a partir de código |
| `skill-design-audit` | Design Analyst | Leitura de tokens por sistema (Tailwind, styled-components, NativeWind) |
| `skill-state-reverse` | State Analyst | Padrões por biblioteca (Zustand, Redux, Jotai, TanStack Query) |
| `skill-sdd-template` | SDD-Writer | Templates de artefato por nível (L1/L2/L3) com seções obrigatórias |

**Princípio de carregamento (progressive disclosure):** Apenas `name` + `description` de cada skill (~100 tokens) são pré-carregados no contexto do agente. O corpo completo (~2–3k tokens) é carregado somente quando o agente detecta relevância — reduz custo de tokens em sessões onde um worker encontra uma stack não-contemplada.

---

## 6. Fonte Canônica: `_codesteer/`

### 6.1 Estrutura de Diretórios

`_codesteer/` é o repositório canônico de toda a squad HERMES. Nenhum agente, skill ou template existe em outro lugar sem ser gerado a partir daqui. As IDEs nunca são a fonte — são destinos de deploy.

```
_codesteer/
├── agents/                         ← corpos canônicos dos agentes (sem frontmatter)
│   ├── conductor.md
│   ├── clarifier.md
│   ├── ui-scout.md
│   ├── code-scout.md
│   ├── data-scout.md
│   ├── api-scout.md
│   ├── br-analyst.md
│   ├── design-analyst.md
│   ├── state-analyst.md
│   ├── security-analyst.md
│   ├── synthesizer.md
│   ├── validator.md
│   └── sdd-writer.md
│
├── skills/                         ← estrutura padrão agentskills.io
│   ├── skill-clarifier/
│   │   └── SKILL.md
│   ├── skill-ui-exploration/
│   │   └── SKILL.md
│   ├── skill-code-static-analysis/
│   │   └── SKILL.md
│   ├── skill-db-reverse/
│   │   └── SKILL.md
│   ├── skill-api-reverse/
│   │   └── SKILL.md
│   ├── skill-br-extraction/
│   │   └── SKILL.md
│   ├── skill-design-audit/
│   │   └── SKILL.md
│   ├── skill-state-reverse/
│   │   └── SKILL.md
│   └── skill-sdd-template/
│       └── SKILL.md
│
├── templates/                      ← templates SDD por nível de detalhe
│   ├── l1/
│   │   ├── architecture-overview.md
│   │   ├── screen-inventory.md
│   │   ├── db-schema-outline.md
│   │   ├── main-flows.md
│   │   └── tech-stack.md
│   ├── l2/
│   │   └── [artefatos L1 + component-map, business-rules, api-contracts, state-map, design-overview]
│   └── l3/
│       └── [artefatos L2 + design-tokens, db-complete, security-model, error-catalog, performance-notes, test-strategy, sdd-index]
│
├── ide-configs/                    ← frontmatter configurável por IDE × agente
│   ├── claude-code/
│   │   ├── _defaults.yaml          ← defaults para todos os agents nesta IDE
│   │   ├── conductor.yaml
│   │   ├── clarifier.yaml
│   │   ├── ui-scout.yaml
│   │   └── [demais agentes]
│   ├── kiro/
│   │   ├── _defaults.yaml
│   │   └── [configs por agente]
│   ├── cursor/
│   │   ├── _defaults.yaml
│   │   └── [configs por agente]
│   └── copilot/
│       ├── _defaults.yaml
│       └── [configs por agente]
│
├── deploy/
│   ├── deploy.py                   ← entry point do script de deploy
│   ├── config.yaml                 ← targets habilitados, caminhos, flags
│   └── adapters/
│       ├── claude_code.py
│       ├── kiro.py
│       ├── cursor.py
│       └── copilot.py
│
└── AGENTS.md                       ← contexto canônico da squad (carregado a cada turno)
```

**Invariante garantida:** qualquer arquivo fora de `_codesteer/` que pertença à squad HERMES é um artefato gerado — nunca editado manualmente. O `deploy.py` detecta edições manuais nos arquivos de destino via hash check e emite `⚠️ arquivo modificado fora do deploy script`.

---

### 6.2 Formato dos IDE Config YAMLs

**Conceito:** cada arquivo `ide-configs/{ide}/{agent}.yaml` define **apenas o frontmatter IDE-específico**. O corpo do agente — missão, protocolo, guardrails — permanece exclusivamente em `_codesteer/agents/{agent}.md`. O deploy script combina `frontmatter (do YAML) + corpo (do canonical .md)` e escreve o arquivo final na localização esperada pela IDE.

#### `_defaults.yaml` — defaults por IDE

**`ide-configs/claude-code/_defaults.yaml`**
```yaml
ide: claude-code
model: claude-sonnet-4-5
tools_default:
  - Read
  - Glob
  - Grep
  - Write
```

**`ide-configs/cursor/_defaults.yaml`**
```yaml
ide: cursor
rule_type: Agent Requested
always_apply: false
```

**`ide-configs/kiro/_defaults.yaml`**
```yaml
ide: kiro
trigger_type: manual
```

**`ide-configs/copilot/_defaults.yaml`**
```yaml
ide: copilot
apply_to: "**"
```

#### Exemplo completo: agente `clarifier` em todas as IDEs

**`ide-configs/claude-code/clarifier.yaml`**
```yaml
name: "HERMES — Clarifier"
description: >
  Elimina ambiguidades de escopo antes de qualquer exploração onerosa.
  Ative com /hermes-clarify ao iniciar uma sessão de engenharia reversa.
tools:
  - Read
  - Write
allowed_paths:
  - "_hermes/*/scope.md"
  - "_hermes/*/glossary.md"
  - "_hermes/.sessions-index.yaml"
disallowed_tools:
  - Bash
  - WebSearch
```

*Arquivo gerado em `.claude/agents/clarifier.md`:* frontmatter acima + corpo de `_codesteer/agents/clarifier.md`.

---

**`ide-configs/cursor/clarifier.yaml`**
```yaml
description: >
  HERMES Clarifier — elimina ambiguidades de escopo antes de exploração.
  Use @hermes-clarifier ao iniciar análise de engenharia reversa.
globs: []
```

*Arquivo gerado em `.cursor/rules/hermes-clarifier.mdc`:* frontmatter acima + corpo canônico.

---

**`ide-configs/kiro/clarifier.yaml`**
```yaml
name: "HERMES — Clarifier"
description: "Elimina ambiguidades de escopo antes de exploração."
triggers:
  - type: preSpecTask
    condition: "task contains 'hermes' or 'reverse'"
  - type: manual
    command: "/hermes-clarify"
```

*Arquivo gerado em `.kiro/steering/hermes-clarifier.md`:* frontmatter acima + corpo canônico.

---

**`ide-configs/copilot/clarifier.yaml`**
```yaml
name: hermes-clarifier
description: "HERMES Clarifier: elimina ambiguidades de escopo antes de exploração de engenharia reversa."
tools: []
apply_to: "**"
```

*Arquivo gerado em `.github/agents/hermes-clarifier.agent.md`:* frontmatter acima + corpo canônico.

---

### 6.3 Estratégia de Symlinks para Skills

Skills não têm frontmatter IDE-específico — o `SKILL.md` é auto-contido. A estratégia é symlink direto, não template generation.

| IDE | Symlink destino |
|---|---|
| Claude Code | `skillsPath` no `settings.json` aponta para `_codesteer/skills/` |
| Kiro | `_codesteer/skills/{skill}/SKILL.md` → `.kiro/steering/hermes-{skill}.md` |
| Cursor | `_codesteer/skills/{skill}/SKILL.md` → `.cursor/rules/hermes-{skill}.mdc` |
| Copilot | `_codesteer/skills/{skill}/SKILL.md` → `.github/instructions/hermes-{skill}.instructions.md` |

**`AGENTS.md` e `CLAUDE.md`:**
```
[raiz do repo]
├── AGENTS.md  →  symlink para _codesteer/AGENTS.md
└── CLAUDE.md  →  symlink para AGENTS.md
```

Regra de mão única: edita-se `_codesteer/AGENTS.md`, nunca `AGENTS.md` ou `CLAUDE.md` diretamente.

---

### 6.4 Arquitetura do Deploy Script

O `deploy.py` é o único ponto de mutação do sistema de configuração. Reside em `_codesteer/deploy/`.

**`config.yaml` — controle de targets:**
```yaml
targets:
  claude-code:
    enabled: true
    root: "../../"
    agents_dir: ".claude/agents"
    skills_strategy: settings_json
    settings_json_path: ".claude/settings.json"

  kiro:
    enabled: true
    root: "../../"
    agents_dir: ".kiro/steering"
    skills_dir: ".kiro/steering"
    skill_prefix: "hermes-"
    skill_suffix: ".md"

  cursor:
    enabled: true
    root: "../../"
    agents_dir: ".cursor/rules"
    skills_dir: ".cursor/rules"
    skill_prefix: "hermes-"
    skill_suffix: ".mdc"

  copilot:
    enabled: false
    root: "../../"
    agents_dir: ".github/agents"
    skills_dir: ".github/instructions"
    skill_prefix: "hermes-"
    skill_suffix: ".instructions.md"

agents_canonical_dir: "../agents"
skills_canonical_dir: "../skills"
templates_canonical_dir: "../templates"
ide_configs_dir: "../ide-configs"
```

**Responsabilidades de `deploy.py` e adapters:**

`deploy.py` (entry point):
- Lê `config.yaml` e instancia o adapter de cada IDE habilitada
- Executa na ordem: `validate → deploy_agents → deploy_skills → create_symlinks`
- Suporta flags: `--dry-run` (mostra o que seria feito sem escrever nada), `--ide claude-code` (deploy seletivo), `--force` (sobrescreve mesmo se idêntico), `--validate` (hash check sem deploy)
- Gera log de cada execução em `_codesteer/deploy/.deploy-log.yaml`

Cada `adapters/{ide}.py`:
1. `validate()` — verifica que canonical files existem e são válidos; aborta se não
2. `deploy_agent(agent_name)` — merge de `_defaults.yaml` + `{agent}.yaml` → frontmatter → concatena com `agents/{agent}.md` → escreve no destino
3. `deploy_skill(skill_name)` — cria ou atualiza symlink de `skills/{skill}/SKILL.md` para o destino IDE
4. `create_main_symlinks()` — `AGENTS.md → _codesteer/AGENTS.md`; `CLAUDE.md → AGENTS.md`
5. `update_settings()` — para Claude Code: atualiza `.claude/settings.json` com `skillsPath` e lista de agents

**Ciclo de atualização:**
```
1. Editar _codesteer/agents/{agent}.md
2. Rodar: python _codesteer/deploy/deploy.py --ide claude-code --ide cursor
3. Deploy script regenera os arquivos IDE com o corpo atualizado
4. git commit: "feat(hermes): update {agent} — descrição da mudança"
   → mudança rastreável em _codesteer/agents/ (fonte)
   → arquivos IDE são derivados, versionados como evidência
```

---

## 7. Compatibilidade por IDE

| Capacidade | Claude Code | Kiro | Cursor | Copilot |
|---|---|---|---|---|
| **Agents canônicos** | `.claude/agents/` (gerado por deploy.py) | `.kiro/steering/` (gerado) | `.cursor/rules/` (gerado) | `.github/agents/` (gerado) |
| **Skills** | `skillsPath` → `_codesteer/skills/` | Symlinks em `.kiro/steering/` | Symlinks em `.cursor/rules/` | Symlinks em `.github/instructions/` |
| **Conductor como StateGraph** | Hooks nativos (13 eventos) | `postSpecTask` hooks | MCP server proxy | MCP server proxy |
| **Fan-out de workers** | Subagents nativos | Tasks paralelas | Background Agents | Custom agents |
| **HITL Gates** | `Stop` hook + prompt | `preSpecTask` hook | Rules + pausa manual | PR review gate |
| **Contexto compartilhado** | `_hermes/{slug}/` filesystem | `_hermes/{slug}/` filesystem | `_hermes/{slug}/` filesystem | `_hermes/{slug}/` filesystem |
| **Playwright-CLI** | MCP tool (Playwright MCP) | MCP tool | MCP tool | GitHub Actions |
| **Hooks determinísticos** | 13 eventos de ciclo de vida | `preToolUse`, `postToolUse` | Nenhum (só rules) | Nenhum in-IDE |

**Recomendação:** Claude Code oferece a implementação mais completa — hooks determinísticos, subagents de primeira classe e `skillsPath` nativo que aponta diretamente para `_codesteer/skills/`. Kiro é segunda opção. Cursor e Copilot operam com degradação graceful via MCP como ponto de gating.

---

## 8. Estratégia de Eficiência de Tokens

Engenharia reversa é intrinsecamente custosa em tokens — o artefato inteiro precisa ser lido. A estratégia HERMES minimiza o custo em sete camadas:

1. **Clarifier front-loads tudo.** Toda ambiguidade é resolvida antes de qualquer leitura de código. Uma re-execução por escopo errado custa 10× mais tokens do que 5 perguntas de intake.

2. **Leitura em camadas.** Code-Scout e Data-Scout usam grep/estrutura antes de ler conteúdo. Arquivos >500 linhas são lidos em ranges, não na íntegra.

3. **Envelope mínimo por agente.** Cada worker recebe apenas a porção de `_hermes/{scope-slug}/` relevante à sua missão — nunca o conjunto completo.

4. **Fan-out paralelo elimina espera sequencial.** 4 Scouts em paralelo custam os mesmos tokens mas 4× menos wall-clock que sequencial.

5. **Arquivos como memória.** Synthesizer e SDD-Writer leem arquivos de `_hermes/{scope-slug}/`, não o histórico de conversa. Compactação de contexto não destrói o estado da sessão.

6. **Skills com progressive disclosure.** ~100 tokens de descrição por skill no system prompt; corpo completo (~2–3k tokens) carregado só quando necessário.

7. **Checkpoints como poda.** O HITL na Fase 5 pode redirecionar ou encerrar antes do SDD-Writer — evita o custo de geração de documentação que seria descartada.

---

## 9. Estrutura Completa de Arquivos

### `_codesteer/` — fonte canônica

```
_codesteer/
├── AGENTS.md                         ← contexto canônico; symlinked ← raiz/AGENTS.md ← raiz/CLAUDE.md
├── agents/                           ← 13 corpos canônicos de agente
├── skills/                           ← 9 skill folders (agentskills.io standard)
├── templates/l1|l2|l3/               ← templates SDD por nível
├── ide-configs/claude-code|kiro|cursor|copilot/   ← frontmatter por IDE × agente
└── deploy/
    ├── deploy.py
    ├── config.yaml
    ├── .deploy-log.yaml
    └── adapters/claude_code.py|kiro.py|cursor.py|copilot.py
```

### `_hermes/` — memória de sessões

```
_hermes/
├── .sessions-index.yaml              ← registro global de todas as sessões
│
└── {scope-slug}/                     ← isolamento total por sessão
    ├── session.yaml                  ← manifesto: target, level, agentes, fases, hermes_root
    ├── scope.md                      ← Clarifier: target, objetivo, exclusões, restrições
    ├── glossary.md                   ← Clarifier: termos de domínio
    │
    ├── raw/                          ← outputs brutos dos Scouts e Analysts
    │   ├── screen-inventory-raw.md
    │   ├── navigation-graph.md
    │   ├── ui-states-catalog.md      ← L2/L3
    │   ├── tech-stack.md
    │   ├── code-structure.md
    │   ├── architecture-patterns.md
    │   ├── tech-debt.md
    │   ├── db-schema-raw.md
    │   ├── db-relations.md           ← Mermaid ER
    │   ├── data-types.md
    │   ├── api-contracts-raw.md      ← L2/L3
    │   ├── auth-patterns.md          ← L2/L3
    │   ├── business-rules.md         ← L2/L3
    │   ├── open-questions-br.md      ← L2/L3
    │   ├── design-overview.md        ← L2/L3
    │   ├── design-tokens.md          ← L3
    │   ├── component-map.md          ← L2/L3
    │   ├── state-map.md              ← L2/L3
    │   ├── data-flow.md              ← L2/L3
    │   ├── security-model.md         ← L3
    │   └── pii-map.md                ← L3
    │
    ├── [arquivos consolidados]       ← Synthesizer: versões sem sufixo -raw
    ├── synthesis-report.md           ← Synthesizer: visão consolidada
    ├── gaps.md                       ← Synthesizer: inconsistências e itens abertos
    ├── validation-report.md          ← Validator: checklist de consistência
    ├── user-confirmation.md          ← resposta do usuário ao checkpoint
    │
    └── sdd/                          ← artefatos SDD finais
        ├── sdd-index.md              ← índice mestre com referências cruzadas (L3)
        ├── architecture-overview.md
        ├── screen-inventory.md
        ├── db-schema.md
        ├── main-flows.md
        ├── tech-stack.md
        └── [demais artefatos conforme nível]
```

---

## 10. Fluxo de Setup e Onboarding

Sequência para onboarding de um novo repositório na squad HERMES:

```
1. Adicionar _codesteer/ à raiz do repo (clone direto ou git submodule)

2. Editar _codesteer/deploy/config.yaml
   → habilitar apenas as IDEs usadas no projeto
   → confirmar caminhos de root relativos

3. Simular o deploy
   python _codesteer/deploy/deploy.py --dry-run
   → revisar o que será criado antes de qualquer escrita

4. Executar o deploy
   python _codesteer/deploy/deploy.py
   → cria estrutura em .claude/, .cursor/, .kiro/, .github/ (IDEs habilitadas)
   → cria AGENTS.md e CLAUDE.md como symlinks
   → atualiza .claude/settings.json com skillsPath e lista de agents

5. Commitar no git
   git add _codesteer/ AGENTS.md CLAUDE.md .claude/ .cursor/ .kiro/ .github/
   git commit -m "feat: setup HERMES squad v2"

6. Primeira sessão
   → Abrir a IDE escolhida
   → Chamar o Conductor ou usar /hermes-clarify
   → Conductor solicita: target, level (L1/L2/L3), source
   → Clarifier conduz intake
   → Conductor gera scope slug e cria _hermes/{scope-slug}/session.yaml
   → Pipeline inicia
```

**Referência rápida de comandos do deploy:**

| Ação | Comando |
|---|---|
| Deploy completo em todas as IDEs | `python _codesteer/deploy/deploy.py` |
| Deploy seletivo para uma IDE | `python _codesteer/deploy/deploy.py --ide claude-code` |
| Simular sem escrever nada | `python _codesteer/deploy/deploy.py --dry-run` |
| Forçar sobrescrita | `python _codesteer/deploy/deploy.py --force` |
| Verificar integridade (hash check) | `python _codesteer/deploy/deploy.py --validate` |
| Atualizar instrução de um agente | Editar `_codesteer/agents/{agent}.md` → deploy |
| Atualizar frontmatter de um IDE | Editar `_codesteer/ide-configs/{ide}/{agent}.yaml` → deploy |
| Adicionar novo agente em todas as IDEs | Criar `agents/{agent}.md` + configs por IDE → deploy |

---

## 11. Resumo de Responsabilidades

| Agente | Fase | Paralelizável | Bloqueante | Toca codebase original |
|---|---|---|---|---|
| Conductor | 0 — contínua | — | Sim (HITL gates) | Não |
| Clarifier | 1 — intake | Não | Sim | Não |
| UI-Scout | 2 — exploração | Sim | Não | Leitura + Playwright |
| Code-Scout | 2 — exploração | Sim | Não | Leitura |
| Data-Scout | 2 — exploração | Sim | Não | Leitura |
| API-Scout | 2 — exploração | Sim | Não | Leitura |
| BR Analyst | 3 — análise | Sim | Não | Não (`raw/` apenas) |
| Design Analyst | 3 — análise | Sim | Não | Não (`raw/` apenas) |
| State Analyst | 3 — análise | Sim | Não | Não (`raw/` apenas) |
| Security Analyst | 3 — análise | Sim | Não | Não (`raw/` apenas) |
| Synthesizer | 4 — síntese | Não | Não | Não (`_hermes/{slug}/` apenas) |
| Validator | 5 — validação | Não | Sim (HITL) | Não |
| SDD-Writer | 6 — documentação | Não | Não | Não (`_hermes/{slug}/` apenas) |

---

## Apêndice — Diagrama de Relações `_codesteer/` × IDEs

```
_codesteer/agents/{agent}.md  ─────────────────────────────────────────┐
                                                                        │ corpo canônico
_codesteer/ide-configs/                                                 │
  claude-code/{agent}.yaml  ──┐                                        │
  kiro/{agent}.yaml          ─┤── deploy.py (frontmatter + corpo) ────>├── .claude/agents/{agent}.md
  cursor/{agent}.yaml        ─┤                                        ├── .kiro/steering/hermes-{agent}.md
  copilot/{agent}.yaml       ─┘                                        ├── .cursor/rules/hermes-{agent}.mdc
                                                                        └── .github/agents/hermes-{agent}.agent.md

_codesteer/skills/{skill}/SKILL.md ── symlink ──> .claude/ (via settings.json)
                                   ── symlink ──> .kiro/steering/hermes-{skill}.md
                                   ── symlink ──> .cursor/rules/hermes-{skill}.mdc
                                   ── symlink ──> .github/instructions/hermes-{skill}.instructions.md

_codesteer/AGENTS.md ── symlink ──> [raiz]/AGENTS.md ── symlink ──> [raiz]/CLAUDE.md
```
