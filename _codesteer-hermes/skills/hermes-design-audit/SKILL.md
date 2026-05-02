---
name: hermes-design-audit
description: >
  HERMES / Design Analyst: heurísticas para identificar padrões visuais, tokens, variantes e composição
  de componentes a partir de screenshots e pistas estruturais já extraídas. Use quando precisar documentar
  design system observável sem reler o codebase original.
---

# hermes-design-audit

## Quando Carregar Esta Skill

Carregue esta skill quando:

- o agente ativo for o `Design Analyst`
- houver screenshots, estados de UI e pistas de componentes em `raw/`
- você precisar separar `L2` e `L3` com rigor

Não carregue esta skill quando:

- não houver evidência visual suficiente
- a tarefa for apenas estado, regras ou segurança

## Estratégia por Nível

### L2

Foque em padrões:

- hierarquia tipográfica aparente
- densidade e espaçamento relativo
- família de componentes recorrentes
- composição de layouts
- estados de componentes observados

Não force valores exatos.

### L3

Além dos padrões, capture valores quando houver evidência:

- nomes ou valores de tokens
- cores específicas
- famílias tipográficas explícitas
- breakpoints documentados
- sombras, raios e spacing quando observáveis

## Sinais Fortes

- repetição do mesmo padrão em múltiplas telas
- componente nomeado explicitamente em artefato estrutural
- estado visual observado em screenshot ou catalogado pela UI
- arquivo de tema citado pelo `Code-Scout`

## Sinais Fracos

- um único screenshot isolado
- dedução de cor sem contexto
- suposição de design system só porque há muitos componentes

## Como Montar `component-map.md`

Para cada item, responda:

- em qual tela ele aparece
- qual seu papel aparente
- quais variantes foram observadas
- se o item parece reusable ou pontual

Tipos comuns:

- `layout shell`
- `navigation`
- `form field`
- `feedback`
- `data display`
- `action`

## Como Montar `design-tokens.md`

Só registre token quando houver evidência concreta. Bons exemplos:

- `color.primary = #0F172A`
- `spacing.4 = 16px`
- `font.heading = "Söhne"`

Exemplos ruins:

- `provavelmente usa azul escuro`
- `deve ter uma escala de spacing`

## Anti-padrões

- converter observação visual vaga em token formal
- chamar elemento único de componente base
- misturar conclusão de UX com descrição de design system
