# Fixture L3 — Auth and PII

## Intenção

Este fixture deve validar se a implementação de `Security Analyst`, `Synthesizer` e `Validator` consegue:

- mapear roles e autenticação
- identificar PII direta e credenciais
- manter lacunas explícitas quando a política de expiração de sessão não estiver clara

## Resultado esperado

- `security-model.md` consolidado com auth, roles e superfícies protegidas
- `pii-map.md` consolidado
- pelo menos um gap de `evidência ausente` sobre expiração ou revogação de sessão
