# Fixture Negativo — Artefato Obrigatório Ausente

## Intenção

Este fixture força o `Validator` a produzir `FALHA` porque um artefato consolidado obrigatório de `L1` foi omitido.

## O que validar

- `db-schema.md` está ausente
- a ausência não pode ser rebaixada para `ALERTA`
- a recomendação final deve ser revisar antes do checkpoint
