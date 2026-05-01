# Business Rules

## Escopo consolidado
- regras de autenticação e perfil

## Evidências consolidadas
- request:POST /api/auth/login
- request:POST /api/auth/forgot-password

## Conteúdo reconciliado
- `BR-101`: login exige credenciais válidas
- `BR-102`: token de reset expira em 30 minutos
- `BR-103`: perfil só é acessível por usuário autenticado

## Itens pendentes de validação
- `BR-104`: MFA para perfis de risco `⚠️ REQUER VALIDAÇÃO`

## Conflitos e gaps relacionados
- GAP-021
