---
name: skill-state-reverse
description: >
  HERMES / State Analyst: heurísticas para mapear estado global, local e remoto, identificando stores,
  providers, caches, queries, produtores e consumidores a partir de artefatos de estrutura e navegação.
  Use quando precisar documentar fluxo de dados sem reler o codebase original.
---

# skill-state-reverse

## Quando Carregar Esta Skill

Carregue esta skill quando:

- o agente ativo for o `State Analyst`
- houver pistas de bibliotecas de estado, providers, queries ou hooks em `raw/`
- você precisar distinguir onde o dado nasce, trafega e termina

## Taxonomia Base

Classifique cada item como um destes tipos:

- `global store`
- `feature store`
- `context/provider`
- `remote cache/query`
- `local UI state`
- `derived/computed state`

## Recipes por Biblioteca

### Redux

Procure sinais de:

- `store`
- `slice`
- `reducer`
- `dispatch`
- selectors

Interprete:

- produtor: action, thunk, mutation
- consumidor: componente conectado, hook ou selector

### Zustand

Procure sinais de:

- `create(...)`
- hooks com `useXStore`
- setters e slices

### Context API

Procure sinais de:

- `createContext`
- provider
- `useContext`

### TanStack Query / SWR / Apollo

Procure sinais de:

- query keys
- mutation handlers
- cache invalidation
- loading/error/success states

## Heurística de Fluxo

Para cada fluxo relevante, tente responder:

1. qual evento inicia o dado
2. em qual container ele entra
3. se sofre transformação
4. quem consome
5. se persiste entre telas

## Sinais Fortes

- store explicitamente nomeado
- provider mapeado
- query client com key identificável
- fluxo de tela que depende daquele estado

## Sinais Fracos

- pasta chamada `state`
- hook com nome genérico sem uso rastreável
- props locais sem relação com navegação ou compartilhamento

## Anti-padrões

- tratar estado remoto e cache como a mesma coisa sem explicação
- chamar qualquer `useState` de arquitetura de estado
- ignorar coexistência de múltiplos mecanismos
