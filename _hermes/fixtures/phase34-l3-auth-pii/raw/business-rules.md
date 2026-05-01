# Business Rules

## Resumo do que foi analisado
- Domínios cobertos: auth, profile
- Regras extraídas: 2
- Distribuição de certeza: Alta 2

## Fontes e evidências
- Arquivos raw usados: api-contracts-raw.md, db-schema-raw.md

## Conteúdo extraído
### auth
| rule_id | regra_ears | evidência | certeza |
| BR-001 | [Auth] Quando as credenciais forem válidas -> o sistema deve emitir sessão autenticada | request:POST /api/auth/login | Alta |
| BR-002 | [Profile] Quando o usuário não estiver autenticado -> o endpoint de perfil não deve responder dados pessoais | request:GET /api/profile/me | Alta |

## Itens inferidos e não verificados
- Nenhum

## Conflitos, bloqueios e perguntas abertas
- Nenhum
