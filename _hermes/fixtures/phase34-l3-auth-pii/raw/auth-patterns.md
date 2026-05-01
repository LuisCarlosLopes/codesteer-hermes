# Auth Patterns

## Resumo do que foi analisado
- Fluxos de auth identificados: login, refresh

## Fontes e evidências
- Arquivos usados: src/api/auth/login.ts, src/api/auth/refresh.ts

## Conteúdo extraído
| fluxo | mecanismo | evidência | confiança |
| login | JWT com cookie httpOnly | src/api/auth/login.ts:18 | Alta |
| refresh | refresh token por cookie | src/api/auth/refresh.ts:11 | Alta |

## Itens inferidos e não verificados
- A duração do refresh token não está explícita.

## Conflitos, bloqueios e perguntas abertas
- Não há evidência clara de revogação.
