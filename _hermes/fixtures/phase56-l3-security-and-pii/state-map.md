# State Map

## Escopo consolidado
- estado de sessão autenticada

## Evidências consolidadas
- request:POST /api/auth/login
- request:GET /api/profile

## Conteúdo reconciliado
- sessão autenticada em store global
- refresh token gerenciado em camada de auth

## Itens pendentes de validação
- estratégia offline não confirmada

## Conflitos e gaps relacionados
- GAP-021
