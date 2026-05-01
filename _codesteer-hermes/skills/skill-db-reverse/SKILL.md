---
name: skill-db-reverse
description: >
  HERMES / Data-Scout: recipes para engenharia reversa de schema e persistência a partir de migrations,
  ORMs, entities, models e tipos auxiliares. Use quando precisar mapear tabelas, campos, constraints,
  relações, enums e seeds sem acessar banco em runtime, preservando a hierarquia formal de evidência.
---

# skill-db-reverse

## Quando Carregar Esta Skill

Carregue esta skill quando:
- o agente ativo for o `Data-Scout`
- houver schema, migrations, entities, models ou tipos persistidos no escopo
- você precisar distinguir fonte formal de inferência

Não carregue esta skill quando:
- o trabalho for apenas UI ou contratos de API sem persistência

---

## Hierarquia de Evidência

Use sempre esta ordem:
1. migrations / DDL
2. schema ORM
3. entities / models
4. types / interfaces / enums
5. inferência documentada

Se fontes divergirem, registre conflito. Não escolha silenciosamente.

---

## Recipes por Tecnologia

### Prisma

Procure:
- `schema.prisma`
- diretório `prisma/migrations`
- seeds e enums

### Drizzle

Procure:
- definições de schema
- migrations SQL/TS
- relações definidas no código

### TypeORM / Sequelize

Procure:
- entities/models
- decorators/metadata
- migrations

### Django

Procure:
- `models.py`
- pasta `migrations/`
- choices/enums e relacionamentos

### Laravel

Procure:
- `database/migrations`
- `app/Models`
- casts, guarded/fillable, relations

---

## Heurísticas de Extração

Para cada entidade/tabela, capture:
- nome
- origem
- campos
- tipo
- nulabilidade
- default
- constraints e índices conhecidos

Para relações:
- direção
- cardinalidade
- evidência concreta

Para tipos de domínio:
- enums
- catálogos
- seeds de referência

---

## Convenções de Saída

### `db-schema-raw.md`

Cada tabela/entidade deve indicar:
- campo
- tipo
- nullable
- default
- constraints
- origem
- confiança

### `db-relations.md`

Inclua:
- diagrama Mermaid ER
- tabela resumindo relação, evidência e confiança

### `data-types.md`

Inclua:
- tipo
- valores ou formato
- origem
- confiança

---

## Fallbacks e Bloqueios

Se não houver fonte formal:
- use types/interfaces com rotulagem `inferido, não verificado`
- documente a ausência de migration/schema
- não invente constraints implícitas
