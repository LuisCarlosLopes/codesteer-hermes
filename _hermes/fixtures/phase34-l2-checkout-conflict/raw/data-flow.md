# Data Flow

## Resumo do que foi analisado
- Fluxos documentados: 1
- Fronteiras de estado: store -> API

## Fontes e evidências
- Artefatos usados: state-map.md, api-contracts-raw.md, navigation-graph.md

## Conteúdo extraído
| fluxo | origem | transformação | destino | evidência | confiança |
| checkout-submit | checkout-store | serialização do payload | POST /api/orders | request:POST /api/orders | Alta |

## Itens inferidos e não verificados
- Nenhum

## Conflitos, bloqueios e perguntas abertas
- Nenhum
