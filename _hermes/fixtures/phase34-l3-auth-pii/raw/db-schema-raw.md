# DB Schema Raw

## Resumo do que foi analisado
- Entidades/tabelas mapeadas: users, sessions
- Fonte primária predominante: schema ORM

## Fontes e evidências
- Migrations/DDL: nenhuma
- Schemas ORM: prisma/schema.prisma
- Types/models auxiliares: nenhum

## Conteúdo extraído
### users
| campo | tipo | nullable | default | constraints | origem | confiança |
| id | uuid | não | uuid() | pk | schema ORM | Alta |
| email | text | não | | unique | schema ORM | Alta |
| full_name | text | não | | | schema ORM | Alta |
| cpf | text | sim | | | schema ORM | Alta |

### sessions
| campo | tipo | nullable | default | constraints | origem | confiança |
| id | uuid | não | uuid() | pk | schema ORM | Alta |
| user_id | uuid | não | | fk -> users.id | schema ORM | Alta |
| refresh_token_hash | text | não | | | schema ORM | Alta |

## Itens inferidos e não verificados
- Nenhum

## Conflitos, bloqueios e perguntas abertas
- Nenhum
