# PII Map

## Resumo do que foi analisado
- Campos PII identificados: email, full_name, cpf
- Entidades ou fluxos sensíveis: users, profile

## Fontes e evidências
- Artefatos usados: db-schema-raw.md, api-contracts-raw.md

## Conteúdo extraído
| entidade_ou_fluxo | campo_ou_dado | classificação | evidência | confiança |
| users | email | PII direta | prisma/schema.prisma:12 | Alta |
| users | full_name | PII direta | prisma/schema.prisma:13 | Alta |
| users | cpf | PII direta | prisma/schema.prisma:14 | Alta |
| sessions | refresh_token_hash | credencial | prisma/schema.prisma:22 | Alta |

## Itens inferidos e não verificados
- Nenhum

## Conflitos, bloqueios e perguntas abertas
- Nenhum
