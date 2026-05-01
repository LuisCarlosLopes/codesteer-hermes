# Fixtures HERMES — FASES 3 e 4

Este diretório contém fixtures sintéticos para validar a implementação documental das FASES 3 e 4 sem depender
de um projeto real.

## Fixtures disponíveis

- `phase34-l2-checkout-conflict/`
  - cenário L2
  - inclui regra de baixa certeza
  - inclui conflito entre UI e DB
- `phase34-l3-auth-pii/`
  - cenário L3
  - inclui auth, roles e PII

## Como usar

1. trate cada pasta como uma sessão `_hermes/{scope-slug}/`
2. leia `scope.md`, `session.yaml` e o conteúdo de `raw/`
3. valide se um `Synthesizer` seguindo os contratos:
   - gera os arquivos consolidados esperados
   - registra `gaps.md`
   - emite `remediation-requests.md` apenas quando cabível
4. valide se um `Validator`:
   - aprova itens presentes e rastreáveis
   - falha quando a cobertura ou reconciliação estiverem insuficientes

Esses fixtures são intencionalmente pequenos. O objetivo é testar contrato e raciocínio, não volume.
