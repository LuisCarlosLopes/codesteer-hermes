# Fixtures HERMES — FASES 3 a 6

Este diretório contém fixtures sintéticos para validar a implementação documental das FASES 3 a 6 sem depender
de um projeto real.

## Fixtures disponíveis

- `phase34-l2-checkout-conflict/`
  - cenário L2
  - inclui regra de baixa certeza
  - inclui conflito entre UI e DB
- `phase34-l3-auth-pii/`
  - cenário L3
  - inclui auth, roles e PII
- `phase56-l1-happy-path/`
  - cenário L1 pós-validação
  - pronto para entrada do `SDD-Writer`
- `phase56-l2-endpoint-context/`
  - cenário L2 pré-validação
  - garante que endpoint sem tela direta ainda possa ser aceito por contexto explícito
- `phase56-l3-security-and-pii/`
  - cenário L3 pós-validação
  - pronto para entrada do `SDD-Writer` com segurança e PII
- `phase56-missing-required-artifact/`
  - cenário negativo para `Validator`
  - falta artefato obrigatório consolidado

## Como usar

1. trate cada pasta como uma sessão `_hermes/{scope-slug}/`
2. leia `scope.md`, `session.yaml` e os artefatos existentes
3. para fixtures de FASE 3/4, valide se um `Synthesizer` seguindo os contratos:
   - gera os arquivos consolidados esperados
   - registra `gaps.md`
   - emite `remediation-requests.md` apenas quando cabível
4. para fixtures de FASE 5, valide se um `Validator`:
   - aprova itens presentes e rastreáveis
   - falha quando a cobertura ou reconciliação estiverem insuficientes
   - respeita `target_type` e contexto explícito do escopo
5. para fixtures de FASE 6, valide se um `SDD-Writer`:
   - lê apenas a base consolidada
   - respeita `validation-report.md` e `user-confirmation.md`
   - gera o pacote `sdd/` com `sdd-index.md`

Esses fixtures são intencionalmente pequenos. O objetivo é testar contrato e raciocínio, não volume.
