# Fixture L2 — Endpoint por Contexto Explícito

## Intenção

Este fixture existe para validar a regra nova do `Validator`: um endpoint pode ser aceito sem ligação direta com tela quando aparecer em regra, fluxo ou contexto explícito do escopo.

## O que validar

- `api-contracts.md` contém endpoint de exportação
- a exportação não tem tela própria no fluxo principal
- `business-rules.md` e `state-map.md` dão contexto suficiente para aprovação
