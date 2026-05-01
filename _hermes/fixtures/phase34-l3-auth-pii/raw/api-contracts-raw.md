# API Contracts Raw

## Resumo do que foi analisado
- Operações documentadas: 3
- Fonte primária predominante: backend route/controller

## Fontes e evidências
- Specs formais: nenhuma
- Rotas/backend: src/api/auth/login.ts, src/api/auth/refresh.ts, src/api/profile/me.ts
- Clients/mocks: nenhum

## Conteúdo extraído
| método | path_ou_operação | request | response | auth | origem | confiança |
| POST | /api/auth/login | email, password | accessToken | pública | backend route/controller | Alta |
| POST | /api/auth/refresh | refresh cookie | accessToken | refresh cookie | backend route/controller | Alta |
| GET | /api/profile/me | none | user profile | bearer token | backend route/controller | Alta |

## Itens inferidos e não verificados
- Nenhum

## Conflitos, bloqueios e perguntas abertas
- Nenhum
