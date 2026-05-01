# DB Schema Raw

## Resumo do que foi analisado
- Entidades/tabelas mapeadas: orders
- Fonte primária predominante: migration

## Fontes e evidências
- Migrations/DDL: prisma/migrations/20260401_orders.sql
- Schemas ORM: schema.prisma
- Types/models auxiliares: nenhum

## Conteúdo extraído
### orders
| campo | tipo | nullable | default | constraints | origem | confiança |
| id | uuid | não | gen_random_uuid() | pk | migration | Alta |
| customer_email | text | não | | | migration | Alta |
| phone | text | sim | | | migration | Alta |

## Itens inferidos e não verificados
- Nenhum

## Conflitos, bloqueios e perguntas abertas
- Nenhum
