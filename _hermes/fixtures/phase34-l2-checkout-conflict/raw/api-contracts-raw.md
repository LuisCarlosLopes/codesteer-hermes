# API Contracts Raw

## Resumo do que foi analisado
- Operações documentadas: 1
- Fonte primária predominante: backend route/controller

## Fontes e evidências
- Specs formais: nenhuma
- Rotas/backend: src/app/api/orders/route.ts
- Clients/mocks: src/features/checkout/api.ts

## Conteúdo extraído
| método | path_ou_operação | request | response | auth | origem | confiança |
| POST | /api/orders | email, address, phone? | orderId | opcional | backend route/controller | Alta |

## Itens inferidos e não verificados
- O campo `phone` parece opcional pela assinatura.

## Conflitos, bloqueios e perguntas abertas
- Nenhum
