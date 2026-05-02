---
name: hermes-help
description: >
  HERMES / Guia de fluxo e onboarding: explique como a squad funciona — fases 1–6, HITL, níveis L1/L2/L3,
  papel de cada agente, qual skill usar com qual worker, onde ficam raw/ consolidados e sdd/ em
  `_hermes/{scope-slug}/`, scope slug, intake, primeira sessão, comandos `npx codesteer-hermes`, e remissões
  aos contratos. Use sempre que o usuário (ou você) perguntar "como funciona", "em que estou",
  "o que vem depois", "posso pular Clarifier?", "onde o Synthesizer grava?", "dif L1 vs L3",
  Security Analyst, paralelismo, gaps, Validator, estrutura de pastas `_codesteer-hermes/` vs deploy na IDE —
  mesmo sem citar HERMES. Não substitua skills técnicas: pedidos de recipes (Express, Prisma,
  Playwright, EARS…) vão ao worker + skill especializada correspondente.
---

# hermes-help

## Para que serve

Orientação sobre **processo, papéis e layout de arquivos** da squad HERMES. O detalhe normativo de nomes de artefatos e seções está em [`_codesteer-hermes/contracts/artifact-contracts.md`](../../contracts/artifact-contracts.md).

---

## Quando carregar esta skill

Carregue quando a dúvida for sobre **fluxo, conceitos ou navegação** no pipeline.

**Não** use apenas esta skill quando o objetivo for **executar** trabalho técnico de worker (extrair APIs, BRs, schema, UI, templates SDD linha a linha). Nesses casos, carregue a skill especializada correspondente (`hermes-api-reverse`, `hermes-br-extraction`, etc.) conforme [`_codesteer-hermes/docs/HERMES.md`](../../docs/HERMES.md) — seção *Skills Library*.

---

## Documentos canônicos (ler antes de inventar nomes)

| Necessidade | Arquivo |
|-------------|---------|
| Operar primeira sessão, IDEs, boas práticas | `_codesteer-hermes/docs/onboarding-hermes.md` |
| Spec completa: níveis, agentes, deploy, filosofia | `_codesteer-hermes/docs/HERMES.md` |
| Formato obrigatório de `raw/`, consolidados, `sdd/`, gaps | `_codesteer-hermes/contracts/artifact-contracts.md` |

Se não tiver evidência normativa sob mão, **aponte uma dessas referências** em vez de adivinhar nomes ou seções.

---

## Pilares (resumo)

- **Zero inferência:** falta de evidência vira gap, pergunta aberta ou pendência explícita.
- **Código/arquivo sob análise:** somente leitura; saídas em **`_hermes/{scope-slug}/`** (e intake provisório).
- **Fonte canônica:** agentes, skills e templates moram em **`_codesteer-hermes/`**; pastas de IDE são **deploy**, não verdade paralela.

---

## Fases e paralelismo

| Fase | Nome | Notas |
|:----:|------|-------|
| 1 | Clarifier | **Sequencial**; intake e escopo antes de exploração cara. |
| 2 | Exploração | **Paralela** entre scouts; só escrita sob `raw/`; read-only no alvo. |
| 3 | Análise | **Paralela** sobre `raw/` (**L2 e L3**; L1 não entra aqui na prática habitual). |
| 4 | Synthesizer | **Sequencial**; consolida na raiz do slug. |
| 5 | Validator | **Sequencial**; checklist + checkpoint com usuário (HITL). |
| 6 | SDD-Writer | **Sequencial**; gera `sdd/` a partir de consolidados + templates. |

Fluxo alto nível:

```text
Conductor → F1 Clarifier → F2 Exploração (paralelo)
→ (L1?) pular F3 : F3 Análise (paralelo) → F4 Synthesizer → F5 Validator → F6 SDD-Writer → sdd/
```

Transições de fase esperam **aprovação explícita** humana onde o playbook pedir checkpoint.

---

## Níveis L1, L2 e L3

| Nível | Ideia rápida | Fase 3 (análises paralelas sobre raw/) |
|-------|----------------|----------------------------------------|
| **L1** | Visão macro, DD rápida | Tipicamente **não aplicável** → após exploração, segue ao Synthesizer. |
| **L2** | Handoff funcional | API-Scout, BR Analyst, Design, State Analyst, etc., conforme spec. |
| **L3** | SDD pesado / auditoria / migração | L2 **+ Security Analyst**; maior profundidade (UI, segurança, tokens…). |

Listas por nível: `_codesteer-hermes/docs/HERMES.md` (*Níveis de Detalhe*).

---

## Agentes — uma frase cada

| Agente | Função |
|--------|--------|
| **HERMES (Conductor)** | Orquestra fases, slug, checkpoints; não faz análise de negócio. |
| **Clarifier** | Intake estruturado; `scope.md` / glossário antes de ler o mundo. |
| **UI-Scout** | Telas, rotas, estados visuais; runtime quando aplicável. |
| **Code-Scout** | Stack, estrutura, padrões, dívida técnica (estático). |
| **Data-Scout** | Persistência, ORM/migrations/schema. |
| **API-Scout** | Contratos HTTP/GraphQL/etc. sem “chamar produção”. |
| **BR Analyst** | Regras de negócio com evidência e notação EARS-style. |
| **Design Analyst** | Design system, componentes; tokens forte em L3. |
| **State Analyst** | Estado global/remoto/cache e fluxo de dados. |
| **Security Analyst** | Modelo de ameaça / superfície (tipicamente **L3**). |
| **Synthesizer** | Reconcilia `raw/` → consolidados na raiz do slug. |
| **Validator** | Formaliza qualidade antes do pacote SDD final. |
| **SDD-Writer** | Monta **`sdd/`** com templates L1/L2/L3. |

---

## Skills ↔ agentes (somente vínculo; detalhes nas skills próprias)

| Skill | Agente principal |
|-------|------------------|
| `hermes-clarifier` | Clarifier |
| `hermes-ui-exploration` | UI-Scout |
| `hermes-code-static-analysis` | Code-Scout |
| `hermes-db-reverse` | Data-Scout |
| `hermes-api-reverse` | API-Scout |
| `hermes-br-extraction` | BR Analyst |
| `hermes-design-audit` | Design Analyst |
| `hermes-state-reverse` | State Analyst |
| `hermes-sdd-template` | SDD-Writer |
| `hermes-help` | **Qualquer** — explica **processo** (esta skill) |
| `playwright-cli` | UI-Scout (exploração assistida por browser) |

**Progressive disclosure:** no contexto do agente entram primeiro `name` + `description` de cada skill; o corpo completo só quando houver relevância.

**Deploy IDE:** pastas canônicas em `_codesteer-hermes/skills/` usam o mesmo nome que `name` em `SKILL.md` (ex.: `hermes-api-reverse/`, `hermes-help/`). O deploy cria symlinks com prefixo `hermes-` quando o nome da pasta ainda não o tem; skills listadas em `skills_without_prefix` (ex.: `playwright-cli`) mantêm o nome sem prefixo extra.

---

## Onde cada coisa mora (`_hermes/`)

- **`.sessions-index.yaml`** — índice global de sessões.
- **`_intake/{intake-id}/`** — rascunho antes do slug final (Clarifier).
- **`{scope-slug}/`** — sessão ativa:
  - `session.yaml`, `scope.md`, `glossary.md`
  - **`raw/`** — Fases 2 e 3 (artefatos brutos / analíticos conforme contrato)
  - Raiz do slug — consolidados pós-Synthesizer, relatórios de validação, etc.
  - **`sdd/`** — Fase 6 (pacote SDD)

**Scope slug** (formato típico): `{target-type}-{nome-sanitizado}-{YYYYMMDD}` com sufixo `--N` se colidir. Detalhes: Conductor + onboarding.

---

## Escrita por fase (contrato)

Regra geral:

- Fases **2 e 3** → principalmente `_hermes/{scope-slug}/raw/`
- Fase **4** → raiz do slug (consolidados)
- Fases **5 e 6** → raiz e `sdd/` conforme `artifact-contracts.md`

Exceções e nomes exatos de arquivos: **sempre** `artifact-contracts.md`.

---

## CLI `codesteer-hermes` (consumidor)

| Comando | Uso |
|---------|-----|
| `npx codesteer-hermes install` | Instala agentes/skills nas IDEs configuradas. |
| `npx codesteer-hermes@latest update` | Atualiza instalação. |
| `npx codesteer-hermes remove --yes` | Remove artefatos gerenciados. |
| `npx codesteer-hermes validate` | Valida instalação. |

Após `install`, o comando slash para **iniciar sessão** depende da IDE (ex.: `/hermes`, `/hermes-start`). **Siga o que a sua IDE listar** após o deploy — não discuta qual doc está “certo”.

---

## Como responder ao usuário

1. Responda na linguagem do usuário, de forma **curta e ordenada** (fase → quem age → onde grava).
2. Se precisar de **lista normativa** de arquivos ou seções, cite `artifact-contracts.md` ou `HERMES.md` e, se possível, a subseção.
3. Se a pergunta for “como faço X no código / framework Y”, indique **qual agente + qual skill técnica** devem liderar.

---

## Anti-padrões

- Inventar nomes de artefato que não estão no contrato.
- Responder “pode pular Clarifier” sem deixar claro o **risco de retrabalho** e a política de zero inferência.
- Usar esta skill no lugar de `hermes-api-reverse`, `hermes-db-reverse`, etc., quando o pedido é claramente técnico-instrumental.
