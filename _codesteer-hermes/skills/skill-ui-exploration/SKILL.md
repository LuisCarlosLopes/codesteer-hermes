---
name: skill-ui-exploration
description: >
  HERMES / UI-Scout: recipes de exploração de UI por framework, combinando descoberta estática de rotas
  com navegação em runtime quando disponível. Use quando precisar mapear telas, fluxos, estados visuais,
  screenshots e grafos de navegação para web ou mobile baseado em código-fonte, URL local ou ambiente demo.
---

# skill-ui-exploration

## Quando Carregar Esta Skill

Carregue esta skill quando:
- o agente ativo for o `UI-Scout`
- houver necessidade de descobrir telas, rotas ou fluxos navegáveis
- você precisar decidir entre exploração estática e runtime
- houver screenshots, formulários ou estados visuais no escopo

Não carregue esta skill quando:
- o trabalho for puramente estrutural de código sem foco em interface
- o alvo for somente backend/API sem superfície visual

---

## Estratégia Base

Sempre siga esta ordem:
1. Descoberta estática de rotas e entrypoints
2. Lista inicial de telas candidatas
3. Exploração runtime, se disponível
4. Consolidação em `screen-inventory-raw.md`, `navigation-graph.md` e `ui-states-catalog.md`

Nunca comece pelo runtime sem antes entender a estrutura de navegação em código.

---

## Recipes por Framework

### Next.js `app/`

Procure:
- `app/**/page.*`
- `app/**/layout.*`
- `app/**/loading.*`
- `app/**/error.*`
- route groups e segmentos dinâmicos

Heurísticas:
- `page.*` sugere tela navegável
- `loading.*` e `error.*` revelam estados explícitos
- `layout.*` ajuda a identificar shell compartilhado e navegação persistente

### Next.js `pages/`

Procure:
- `pages/**/*.tsx|jsx|js`
- `_app.*`, `_document.*`
- API routes para excluir quando o foco for UI

Heurísticas:
- cada arquivo em `pages/` tende a mapear uma rota
- `index.*` costuma ser landing ou dashboard do segmento

### React Router

Procure:
- `createBrowserRouter`
- `Routes`, `Route`
- arquivos `router.*`, `routes.*`

Heurísticas:
- rotas aninhadas devem virar telas distintas se tiverem conteúdo próprio
- loaders/actions podem indicar formulários e transições relevantes

### Expo Router

Procure:
- `app/` do router
- `_layout.*`
- grupos `(group)` e segmentos dinâmicos

Heurísticas:
- tabs e stacks ficam evidentes em `_layout.*`
- modais e flows paralelos costumam aparecer na estrutura de pastas

### Angular

Procure:
- `app-routing.module.*`
- `*.routes.*`
- `RouterModule.forRoot/forChild`

Heurísticas:
- cada route config aponta para component/page alvo
- guards resolvem telas protegidas versus acessos bloqueados

---

## Heurísticas de Runtime

Quando houver aplicação navegável:
- capture sempre a tela inicial primeiro
- priorize headings, breadcrumbs, labels de CTA e placeholders como marcadores visuais
- em formulários, teste apenas validações não destrutivas
- use credenciais ou dados de teste; nunca use produção

Quando não houver runtime:
- registre a limitação explicitamente
- não invente screenshots
- não force `ui-states-catalog.md`; apenas marque indisponibilidade

---

## Convenções de Saída

### `screen-inventory-raw.md`

Campos mínimos por tela:
- `screen_id`
- `rota_ou_entrypoint`
- `marcador_visual`
- `propósito`
- `evidência`
- `confiança`
- `screenshot`

### `navigation-graph.md`

Use formato adjacente:
- `origem --[ação]--> destino`

Inclua:
- transições observadas
- transições estáticas não verificadas
- rotas sem caminho claro a partir do escopo explorado

### `ui-states-catalog.md`

Campos mínimos:
- `screen_id`
- `state`
- `trigger`
- `mudança_visível`
- `evidência`
- `confiança`
- `screenshot`

---

## Regras de Confiança

- `Alta`: tela/estado observado diretamente ou rota formal confirmada
- `Média`: combinação de rota, componente e marcador visual
- `Baixa`: inferência por nomenclatura ou estrutura parcial

Não registre propósito com `Alta` sem evidência direta.

---

## Fallbacks e Bloqueios

Se houver bloqueio:
- autenticação ausente
- ambiente indisponível
- rota quebrada
- erro de build ou runtime

Então:
- documente o bloqueio no arquivo correspondente
- continue com o restante da cobertura possível
- preserve o máximo de mapeamento estático
