# HERMES — Hierarchical Engineering Reverse-Map & Extraction Squad

HERMES é uma squad agentic do Code Steer para engenharia reversa de artefatos de software e geração de SDDs rastreáveis.

- Site do Code Steer: [codesteer.vercel.app](https://codesteer.vercel.app)
- Especificação canônica da squad: [HERMES.md](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/HERMES.md:1)

## Visão geral

A HERMES não é um produto separado do ecossistema. Ela é uma squad do Code Steer especializada em engenharia reversa e documentação técnica rastreável.

O projeto segue quatro invariantes centrais:

- Zero inferência: quando falta evidência, a saída correta é pergunta estruturada ou pendência explícita.
- Não modifica o artefato analisado: toda saída vai para `_hermes/{scope-slug}/`.
- Fonte canônica única: agentes, skills, contratos e templates vivem em `_codesteer-hermes/`.
- Sessões isoladas: cada análise mantém seus próprios artefatos e memória auditável.

## Estado atual

Hoje o repositório já contém a camada canônica principal da HERMES:

- agentes de FASE 1 a 6 em `_codesteer-hermes/agents/`
- skills canônicas em `_codesteer-hermes/skills/`
- contratos de artefato em `_codesteer-hermes/contracts/artifact-contracts.md`
- templates SDD por nível em `_codesteer-hermes/templates/l1`, `l2` e `l3`
- fixtures sintéticas em `_hermes/fixtures/` para validar FASES 3 a 6

Também já estão especificados e alinhados:

- `Synthesizer`
- `Validator`
- `SDD-Writer`
- separação entre base consolidada e pacote final `sdd/`

## Limites atuais

Nem tudo descrito em `HERMES.md` está automatizado no deploy ainda.

Está implementado hoje no deploy:

- geração dos arquivos de agentes por IDE com frontmatter + corpo canônico
- symlink de skills para os destinos configurados
- criação de `_hermes/` e `_hermes/.sessions-index.yaml`

Ainda não está implementado de ponta a ponta:

- detecção de drift por hash nos artefatos gerados
- `.deploy-log.yaml`
- criação dos symlinks principais `AGENTS.md` / `CLAUDE.md`
- atualização automática de `.claude/settings.json`
- adapters específicos por IDE com comportamento além do `BaseAdapter`

Em outras palavras: a camada documental e contratual da squad está forte; a camada operacional de deploy ainda está parcial.

## Estrutura do repositório

- [`_codesteer-hermes/`](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/_codesteer-hermes): fonte canônica da squad
  - `agents/`: corpos canônicos dos agentes
  - `skills/`: skills canônicas
  - `contracts/`: contratos de artefatos
  - `templates/`: templates finais de SDD
  - `ide-configs/`: frontmatter por IDE
  - `deploy/`: script e adapters de deploy
- [`_hermes/`](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/_hermes): memória de sessões, fixtures e planos de implementação
- [`HERMES.md`](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/HERMES.md:1): documento mestre da arquitetura e operação
- [`AGENTS.md`](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/AGENTS.md:1): contexto carregado nesta instância do projeto

## Fases da squad

Resumo do pipeline descrito em `HERMES.md`:

1. Intake e scoping
2. Exploração read-only
3. Análise read-only sobre `raw/`
4. Síntese e reconciliação
5. Validação e checkpoint HITL
6. Geração do pacote final `sdd/`

As FASES 5 e 6 já têm contrato canônico, agente e templates editoriais. As FASES 3 e 4 também já têm agentes e fixtures de apoio.

## Como usar hoje

### Pré-requisitos

- Python 3

### Deploy básico

Rodar para todas as IDEs habilitadas em [_codesteer-hermes/deploy/config.yaml](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/_codesteer-hermes/deploy/config.yaml:1):

```bash
python _codesteer-hermes/deploy/deploy.py
```

Simular sem escrita:

```bash
python _codesteer-hermes/deploy/deploy.py --dry-run
```

Rodar para uma IDE específica:

```bash
python _codesteer-hermes/deploy/deploy.py --ide cursor
```

Observação importante:

- `--validate` e `--force` existem na CLI, mas ainda não têm comportamento completo implementado

### Configuração dos targets

Edite [_codesteer-hermes/deploy/config.yaml](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/_codesteer-hermes/deploy/config.yaml:1).

Campos principais por target:

- `enabled`: ativa ou desativa a IDE
- `agents_dir`: destino dos agentes gerados
- `skills_dir`: destino das skills
- `skill_prefix` e `skill_suffix`: naming dos artefatos gerados

## Como utilizar

Uso recomendado da HERMES como squad do Code Steer:

1. Defina o alvo da análise.
   Pode ser `app`, `module`, `screen`, `api` ou `flow`.

2. Defina o nível de detalhe.
   Use `L1` para visão macro, `L2` para visão funcional e `L3` para documentação completa.

3. Garanta o acesso ao artefato.
   O fluxo pode partir de código-fonte, URL, APK/IPA ou combinação, conforme o escopo.

4. Rode a sessão pela IDE com os agentes HERMES disponíveis.
   O `Conductor` conduz intake, exploração, análise, síntese, validação e geração do pacote final.

5. Revise os checkpoints HITL ao fim de cada fase.
   A progressão correta da squad depende de aprovação explícita do usuário.

6. Consulte os artefatos gerados em `_hermes/{scope-slug}/`.
   Ali ficam `scope.md`, `session.yaml`, `raw/`, artefatos consolidados, `validation-report.md` e o pacote final `sdd/`.

Exemplo de uso esperado:

- alvo: `módulo de autenticação`
- nível: `L2`
- fonte: `código-fonte no repositório`
- saída: `_hermes/module-user-auth-YYYYMMDD/`

## Artefatos por sessão

Cada sessão deve gravar apenas em `_hermes/{scope-slug}/`.

Estrutura esperada em alto nível:

- `scope.md`
- `glossary.md`
- `session.yaml`
- `raw/`
- artefatos consolidados na raiz
- `validation-report.md`
- `user-confirmation.md`
- `sdd/`

## Fixtures

As fixtures em [_hermes/fixtures/](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/_hermes/fixtures/README.md:1) existem para validar contrato e raciocínio sem depender de um sistema real grande.

Hoje há cenários para:

- FASE 3 e 4
- FASE 5 com casos felizes e negativos
- FASE 6 com entrada pós-validação para `SDD-Writer`

## Convenções importantes

- Nunca escrever no código original do usuário.
- Nunca produzir saída fora de `_hermes/{scope-slug}/`.
- Toda afirmação relevante deve ser rastreável a evidência.
- Novas skills devem seguir a regra do projeto: usar `skill-creator`.

## Próximos passos recomendados

Se o objetivo for aderência completa ao `HERMES.md`, o próximo bloco de trabalho deve atacar o deploy operacional:

- implementar drift check e `.deploy-log.yaml`
- implementar `create_main_symlinks()`
- implementar atualização de settings para Claude
- alinhar paths e formatos gerados por IDE ao que o documento promete
- transformar os adapters específicos em adapters reais, não apenas subclasses vazias

## Licença

O repositório já contém [LICENSE](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/LICENSE:1).
