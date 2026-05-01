# Screen Inventory Raw

## Resumo do que foi analisado
- Target: auth/profile
- Nível: L3
- Modo de exploração: estático
- Cobertura: login, profile

## Fontes e evidências
- Rotas/arquivos lidos: app/login/page.tsx, app/profile/page.tsx
- Runtime usado: não
- Screenshots gerados: nenhum

## Conteúdo extraído
| screen_id | rota_ou_entrypoint | marcador_visual | propósito | evidência | confiança | screenshot |
| login | /login | "Entrar" | autenticar usuário | route:/login | Alta | |
| profile | /profile | "Meu perfil" | exibir dados do usuário | route:/profile | Alta | |

## Itens inferidos e não verificados
- Nenhum

## Conflitos, bloqueios e perguntas abertas
- Nenhum
