# DB Schema

## Escopo consolidado
- persistência de clientes e sessões

## Evidências consolidadas
- migration:202604031000_create_customers
- migration:202604031030_create_refresh_tokens

## Conteúdo reconciliado
- `customers`
- `refresh_tokens`
- `password_reset_tokens`

## Itens pendentes de validação
- colunas de auditoria de IP não confirmadas

## Conflitos e gaps relacionados
- GAP-021
