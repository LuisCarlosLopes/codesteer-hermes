---
name: hermes-code-static-analysis
description: >
  HERMES / Code-Scout: recipes de análise estática em camadas para mapear stack, estrutura de código,
  entrypoints, padrões arquiteturais e dívida técnica com leitura mínima necessária. Use quando precisar
  explorar codebases sem execução, priorizando manifests, configs, árvores de diretório e evidência estrutural.
---

# hermes-code-static-analysis

## Quando Carregar Esta Skill

Carregue esta skill quando:
- o agente ativo for o `Code-Scout`
- houver necessidade de mapear stack, módulos, entrypoints ou arquitetura
- você quiser reduzir leitura extensa usando busca estrutural primeiro

Não carregue esta skill quando:
- a tarefa for focada apenas em banco, API ou UI runtime

---

## Estratégia Base

Trabalhe em camadas:
1. manifests e locks
2. árvore de diretórios
3. configs centrais
4. entrypoints e registradores
5. padrões recorrentes
6. dívida técnica explícita

Nunca leia arquivos grandes por completo sem motivo.

---

## Recipes por Stack

### JavaScript / TypeScript

Procure:
- `package.json`
- `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`
- `tsconfig.json`
- configs de framework e bundler

Buscas úteis:
- entrypoints: `main`, `index`, `bootstrap`, `render`, `createRoot`
- rotas: `Route`, `router`, `pages`, `app`
- estado: `redux`, `zustand`, `jotai`, `queryClient`, `context`

### Python

Procure:
- `pyproject.toml`, `requirements.txt`, `poetry.lock`
- `manage.py`, `asgi.py`, `wsgi.py`, `main.py`
- diretórios `app`, `api`, `services`, `models`

### Flutter / Dart

Procure:
- `pubspec.yaml`
- `lib/main.dart`
- `lib/screens`, `lib/pages`, `lib/features`

### JVM / Android

Procure:
- `build.gradle`, `settings.gradle`, `pom.xml`
- `src/main`
- módulos por feature ou camada

---

## Heurísticas Arquiteturais

Só registre padrão com pelo menos duas evidências.

Exemplos:
- `feature-based`: `features/*`, código vertical por domínio
- `layer-based`: `controllers`, `services`, `repositories`, `models`
- `atomic/component-driven`: `atoms`, `molecules`, `organisms`
- `clean/onion/hexagonal`: portas/adapters/use-cases claros, não apenas nomes aspiracionais

---

## Convenções de Saída

### `tech-stack.md`

Inclua:
- camada
- tecnologia
- versão
- evidência
- confiança

### `code-structure.md`

Inclua:
- árvore anotada curta
- tabela de módulos/path
- papel aparente
- evidência
- confiança

### `architecture-patterns.md`

Inclua:
- padrão
- descrição
- evidências
- confiança

### `tech-debt.md`

Inclua:
- tipo
- path
- trecho ou sinal
- impacto aparente
- confiança

---

## Regras de Leitura

- prefira `rg` e leitura parcial
- arquivos >500 linhas: comece por imports, exports, assinaturas e blocos estruturais
- comentários antigos exigem corroborar com código vivo

---

## Fallbacks e Bloqueios

Se o repo estiver incompleto ou fragmentado:
- catalogue apenas o que é visível
- marque lacunas como bloqueio
- não extrapole arquitetura total a partir de um subdiretório isolado
