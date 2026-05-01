---
name: skill-clarifier
description: >
  HERMES / Squad Clarifier: templates de perguntas por domínio (web, mobile, API/backend, monolito, full-stack)
  e por rodada de intake (1, 2, 3), além de frases de confirmação pós-rodada. Use sempre que você for o Clarifier
  ou estiver preparando esclarecimentos antes do SDD: escopo vago, target ambíguo, precisa classificar domínio,
  escolher o bloco certo de perguntas, ou conduzir Rodada 1/2/3 com variações por tipo de alvo. Use também quando
  o usuário pedir clarificação de escopo, intake HERMES, perguntas estruturadas ao cliente, ou "o que perguntar
  antes de engenharia reversa" — mesmo sem citar HERMES ou Clarifier.
---

# skill-clarifier

## Descrição

Templates de perguntas estruturadas por domínio e por target-type para guiar o Clarifier nas Rodadas 1, 2 e 3 do intake. Use esta skill para selecionar o conjunto de perguntas mais relevante antes de cada rodada.

---

## Quando Carregar Esta Skill

Carregue o corpo desta skill quando:
- Precisar de variações de perguntas adaptadas ao domínio do target
- O target for ambíguo e você quiser identificar qual template se aplica
- Precisar de frases de confirmação/paráfrase para a reflexão pós-rodada

---

## Passo 1 — Identificar Domínio

Antes de formular perguntas, classifique o domínio a partir do `target` e `source` fornecidos pelo Conductor:

| Palavras-chave no target/source | Domínio |
|---------------------------------|---------|
| "app mobile", "React Native", "Flutter", "Expo", "iOS", "Android", ".apk", ".ipa" | **Mobile** |
| "web app", "Next.js", "React", "Vue", "Angular", "SPA", "PWA", URL HTTP/HTTPS | **Web** |
| "API", "REST", "GraphQL", "endpoint", "backend", "serviço", "microserviço", "NestJS", "FastAPI", "Express", "Laravel", "Django" | **Backend API** |
| "monolito", "Rails", "Django full-stack", "Laravel full-stack", "PHP", "Java Spring MVC" | **Monolito** |
| Combinação de múltiplos acima | **Full-stack** |

---

## Templates por Domínio

### Domínio: Web App

**Rodada 1 — Questões adicionais relevantes:**
- A aplicação usa SSR (Server-Side Rendering), SSG (Static Site Generation) ou é uma SPA pura?
- Há múltiplos perfis de usuário com acessos diferentes (ex: admin, usuário comum, guest)?
- O foco é o frontend, o backend (API), ou ambos juntos?

**Rodada 2 — Acesso:**
- A aplicação está acessível em um ambiente local (localhost) ou em uma URL de staging/produção?
- O login requer credenciais específicas? (informe usuário e senha de teste, ou como obtê-los)

**Rodada 3 — Restrições:**
- O SDD deve assumir algum framework específico para a recriação (ex: "manter Next.js 14" vs. "livre escolha")?

---

### Domínio: Mobile App

**Rodada 1 — Questões adicionais relevantes:**
- O app é para iOS, Android ou ambas as plataformas?
- O app usa navegação nativa (React Navigation, Expo Router) ou WebView embutido?
- Há fluxos offline que devem ser documentados?

**Rodada 2 — Acesso:**
- O código-fonte está disponível? Se sim, qual o path do diretório raiz?
- Há um APK/IPA para análise de comportamento em runtime? Se sim, qual o path?
- Para exploração com Playwright-CLI, a aplicação pode rodar em emulador/simulador local?

**Rodada 3 — Restrições:**
- O SDD deve assumir alguma plataforma-alvo específica para recriação (ex: "manter React Native com Expo" vs. "Flutter")?

---

### Domínio: Backend API

**Rodada 1 — Questões adicionais relevantes:**
- A API tem spec formal (OpenAPI/Swagger, GraphQL schema)? Se sim, onde está o arquivo?
- Quais domínios/resources da API devem ser cobertos (ex: "apenas /users e /orders", "toda a API")?
- A API tem múltiplos ambientes (dev, staging, prod)? Qual deve ser analisado?

**Rodada 2 — Acesso:**
- A API está rodando e acessível? Se sim, qual a base URL?
- A autenticação requer token/API key? Como obtê-lo para testes?
- O código-fonte do backend está disponível? Se sim, qual o path?

**Rodada 3 — Restrições:**
- O SDD deve documentar apenas os contratos (request/response) ou também a implementação interna (banco, lógica de negócio)?

---

### Domínio: Monolito

**Rodada 1 — Questões adicionais relevantes:**
- O monolito tem frontend embutido (views/templates) ou é separado?
- Qual a parte do monolito em foco: models/entidades, controllers/rotas, views/templates, jobs/workers, ou tudo?
- O sistema tem módulos bem delimitados dentro do monolito ou é uma codebase acoplada?

**Rodada 2 — Acesso:**
- O código-fonte está disponível? Se sim, qual o path da raiz do projeto?
- O sistema pode ser rodado localmente para exploração? Quais são os pré-requisitos?

**Rodada 3 — Restrições:**
- Há migrations de banco que devem ser incluídas na análise ou apenas o schema atual?

---

### Domínio: Full-stack (combinação)

Use as questões dos domínios Web + Backend API, mas priorize:

**Rodada 1 — Delimitação crítica:**
- O SDD deve cobrir o sistema completo (frontend + backend + banco) ou apenas uma das camadas?
- Se apenas uma camada: qual é o foco principal?
- Há fronteiras claras entre os serviços (ex: o frontend consome uma API REST separada)?

---

## Templates por Target-Type

### Target-type: `app` (aplicação completa)

Questões de foco para Rodada 1:
- Quais são os 3-5 fluxos mais críticos do app? (para priorizar o nível de detalhe)
- Há módulos que são claramente fora do escopo (ex: área administrativa, módulo legado)?

### Target-type: `module` (módulo isolado)

Questões de foco para Rodada 1:
- Quais são as fronteiras desse módulo? (onde começa e onde termina)
- O módulo se integra com outros módulos? Quais integrações devem ser documentadas?
- Há um ponto de entrada claro (rota, tela, endpoint) que delimita o módulo?

### Target-type: `screen` (tela ou página)

Questões de foco para Rodada 1:
- Qual o nome ou identificador da tela? (ex: nome da rota, título visível)
- Quais são os estados visuais desta tela que devem ser capturados? (default, loading, vazio, erro, preenchido)
- A tela tem variações por perfil de usuário (ex: admin vê campos adicionais)?

### Target-type: `api` (API ou endpoints)

Questões de foco para Rodada 1:
- Quais recursos/endpoints especificamente? (ex: "todos os /payments", "apenas POST /checkout")
- O SDD deve incluir apenas os contratos ou também a lógica de negócio por trás?
- Há versões diferentes da API que devem ser diferenciadas?

### Target-type: `flow` (fluxo de usuário)

Questões de foco para Rodada 1:
- Qual é o evento que inicia o fluxo? (ex: "usuário clica em 'Comprar'")
- Qual é o estado final esperado do fluxo? (ex: "pedido confirmado e email enviado")
- O fluxo tem branches (caminhos alternativos)? Quais devem ser documentados?

---

## Frases de Confirmação (Protocolo de Reflexão)

Use estas estruturas para parafrasear respostas e confirmar entendimento:

### Confirmação de Target
> "Entendi que o target é **{descrição}** — especificamente **{parte delimitada}**, excluindo **{exclusões}**. Correto?"

### Confirmação de Objetivo
> "O objetivo é **{recriar do zero | documentar para handoff | auditar}** — o SDD resultante deve permitir que **{quem}** possa **{fazer o quê}**. Correto?"

### Confirmação de Acesso
> "A squad acessará o artefato via **{tipo}** em **{localização}**. As credenciais necessárias são **{credenciais ou 'nenhuma'}**. Correto?"

### Confirmação de Restrições
> "As restrições são: informações confidenciais a omitir = **{lista ou 'nenhuma'}**; tecnologias assumidas para recriação = **{lista ou 'nenhuma definida'}**. Correto?"

### Quando a resposta for ambígua
> "Entendi corretamente que você quer **[interpretação A]**? Ou você quis dizer **[interpretação B]**?"

---

## Heurísticas de Identificação de Termos de Domínio

Extraia para o `glossary.md` qualquer termo que:
- Seja específico do negócio e não trivialmente óbvio (ex: "SKU", "chargeback", "MRR", "sprint", "workflow de aprovação")
- Seja um nome de módulo, entidade ou sistema interno mencionado pelo usuário (ex: "módulo Fênix", "tabela de contas correntes", "serviço de antifraude")
- Tenha uma definição que pode variar por contexto (ex: "cliente" pode ser pessoa física ou empresa dependendo do sistema)

Não extraia termos genéricos de tecnologia (ex: "componente", "endpoint", "banco de dados").
