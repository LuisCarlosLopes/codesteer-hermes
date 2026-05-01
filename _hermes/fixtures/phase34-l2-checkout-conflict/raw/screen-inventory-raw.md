# Screen Inventory Raw

## Resumo do que foi analisado
- Target: checkout
- Nível: L2
- Modo de exploração: estático
- Cobertura: cart, checkout, confirmation

## Fontes e evidências
- Rotas/arquivos lidos: app/cart/page.tsx, app/checkout/page.tsx, app/confirmation/page.tsx
- Runtime usado: não
- Screenshots gerados: nenhum

## Conteúdo extraído
| screen_id | rota_ou_entrypoint | marcador_visual | propósito | evidência | confiança | screenshot |
| checkout | /checkout | "Finalizar compra" | coletar dados e concluir pedido | route:/checkout | Alta | |
| confirmation | /confirmation | "Pedido confirmado" | confirmar conclusão | route:/confirmation | Alta | |

## Itens inferidos e não verificados
- O checkout parece dividido em endereço e pagamento.

## Conflitos, bloqueios e perguntas abertas
- Nenhum
