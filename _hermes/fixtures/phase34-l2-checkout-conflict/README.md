# Fixture L2 — Checkout Conflict

## Intenção

Este fixture deve forçar o `Synthesizer` a detectar:

- cobertura funcional razoável de checkout
- uma BR de baixa certeza
- conflito entre UI e DB sobre telefone obrigatório

## Resultado esperado

- `gaps.md` com pelo menos um gap de `conflito entre fontes`
- consolidação de `business-rules.md` preservando a dúvida
- `open-questions-br.md` ou `Itens pendentes de validação` com a pergunta sobre telefone
