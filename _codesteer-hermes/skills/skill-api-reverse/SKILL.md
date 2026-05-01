---
name: skill-api-reverse
description: >
  HERMES / API-Scout: recipes para extrair contratos de API a partir de specs formais, rotas backend,
  clients frontend e mocks de teste. Use quando precisar mapear endpoints, operações GraphQL, autenticação,
  headers, requests, responses e erros sem fazer chamadas reais durante a análise.
---

# skill-api-reverse

## Quando Carregar Esta Skill

Carregue esta skill quando:
- o agente ativo for o `API-Scout`
- houver backend, spec formal, clients frontend ou mocks
- você precisar decidir entre contrato formal, rota real ou inferência de consumo

Não carregue esta skill quando:
- o trabalho for puramente UI ou schema de banco sem integrações

---

## Prioridade de Fontes

Use sempre esta ordem:
1. `OpenAPI` / `Swagger`
2. `GraphQL schema`
3. rotas/controladores backend
4. clients/services/repositories frontend
5. mocks e fixtures

Fonte mais fraca nunca sobrescreve fonte mais forte sem conflito explícito.

---

## Recipes por Tecnologia

### OpenAPI / Swagger

Procure:
- `openapi.yaml`
- `openapi.json`
- `swagger.json`

Extraia:
- métodos
- paths
- params
- bodies
- responses
- auth schemes

### GraphQL

Procure:
- `schema.graphql`
- SDLs e codegen configs
- resolvers quando necessário para confirmar operação

### Express / NestJS

Procure:
- controllers
- decorators de rota
- routers e middlewares
- interceptors/guards

### FastAPI / Django / Laravel

Procure:
- registradores de rota
- serializers/schemas
- middleware/auth

### Frontend Clients

Procure:
- `*.service.*`
- `*.api.*`
- `client`, `repository`, `sdk`
- interceptors
- mocks de teste

---

## Convenções de Saída

### `api-contracts-raw.md`

Campos mínimos:
- método
- path ou operação
- request
- response
- auth
- origem
- confiança

### `auth-patterns.md`

Campos mínimos:
- fluxo
- mecanismo
- evidência
- confiança

---

## Heurísticas de Confiança

- `Alta`: spec formal ou rota backend claramente definida
- `Média`: client/service confirmado por múltiplos usos
- `Baixa`: mock isolado ou inferência parcial

Use `inferido de consumo` quando o contrato vier apenas do frontend.

---

## Fallbacks e Bloqueios

Se não houver spec formal:
- use backend como fonte principal
- se não houver backend, use clients/mocks
- marque toda limitação explicitamente

Nunca faça request real para “confirmar” contrato.
