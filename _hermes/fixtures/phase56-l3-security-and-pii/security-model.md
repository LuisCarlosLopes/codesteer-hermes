# Security Model

## Escopo consolidado
- autenticação, autorização e PII

## Evidências consolidadas
- request:POST /api/auth/login
- request:GET /api/profile

## Conteúdo reconciliado
- autenticação por JWT
- perfil protegido por token válido
- PII em nome, email e telefone

## Itens pendentes de validação
- MFA para contas de risco `⚠️ REQUER VALIDAÇÃO`

## Conflitos e gaps relacionados
- GAP-021
