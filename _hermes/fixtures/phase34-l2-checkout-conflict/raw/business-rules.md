# Business Rules

## Resumo do que foi analisado
- Domínios cobertos: checkout
- Regras extraídas: 2
- Distribuição de certeza: Alta 1, Baixa 1

## Fontes e evidências
- Arquivos raw usados: screen-inventory-raw.md, db-schema-raw.md, api-contracts-raw.md

## Conteúdo extraído
### checkout
| rule_id | regra_ears | evidência | certeza |
| BR-001 | [Checkout] Quando o e-mail do cliente estiver ausente -> o pedido não deve ser criado | prisma/migrations/20260401_orders.sql:12 | Alta |
| BR-002 | [Checkout] Quando o telefone não for informado -> o usuário não pode concluir o checkout | screen:checkout | Baixa |

## Itens inferidos e não verificados
- A obrigatoriedade do telefone foi inferida do formulário.

## Conflitos, bloqueios e perguntas abertas
- O DB marca `phone` como nullable.
