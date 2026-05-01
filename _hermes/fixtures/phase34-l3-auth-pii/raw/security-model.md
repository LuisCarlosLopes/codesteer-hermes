# Security Model

## Resumo do que foi analisado
- Fluxos de auth: login, refresh
- Controles de acesso identificados: token para /profile/me
- Superfícies sensíveis: cookies, perfil do usuário

## Fontes e evidências
- Artefatos raw usados: auth-patterns.md, api-contracts-raw.md, db-schema-raw.md, business-rules.md

## Conteúdo extraído
| categoria | item | descrição | evidência | confiança |
| auth | login session | login emite token de acesso | src/api/auth/login.ts:18 | Alta |
| auth | refresh flow | refresh usa cookie dedicado | src/api/auth/refresh.ts:11 | Alta |
| access | profile protection | endpoint de perfil exige autenticação | request:GET /api/profile/me | Alta |

## Itens inferidos e não verificados
- Política de expiração não está visível.

## Conflitos, bloqueios e perguntas abertas
- Não há evidência de revogação de sessão.
