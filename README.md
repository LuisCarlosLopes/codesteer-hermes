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
- validação executável dos contratos com fixtures
- camada `L3` expandida para replatforming e `rebuild readiness`

## Limites atuais

Nem tudo descrito em `HERMES.md` está automatizado no deploy ainda.

Está implementado hoje no deploy:

- geração dos arquivos de agentes por IDE com frontmatter + corpo canônico
- symlink de skills para os destinos configurados
- criação de `_hermes/` e `_hermes/.sessions-index.yaml`
- `.deploy-log.yaml` com manifesto por IDE
- detecção de drift por assinatura dos artefatos gerados
- `--validate` para auditoria e `--force` para sobrescrita consciente
- symlinks principais por IDE, incluindo `CLAUDE.md`
- adapters com comportamento explícito por IDE

Ainda não está implementado de ponta a ponta:

- atualização automática de `.claude/settings.json`
- pilotos reais automatizados de ponta a ponta
- geração automática do pacote final `sdd/` a partir das fixtures

Em outras palavras: a camada documental e contratual da squad continua forte e a base operacional do deploy já saiu do estado parcial, mas ainda faltam validação em campo e automação completa da esteira.

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

### Instalação via `npx`

Pré-requisitos:

- Node.js 18+
- Python 3

Instalação interativa com multi-seleção de IDEs:

```bash
npx codesteer-hermes install
```

Instalação não interativa:

```bash
npx codesteer-hermes install --ides codex,cursor --yes
```

Atualização da instalação existente:

```bash
npx codesteer-hermes@latest update
```

Remoção apenas dos arquivos gerenciados pelo pacote:

```bash
npx codesteer-hermes remove --yes
```

Validação da instalação:

```bash
npx codesteer-hermes validate
```

O CLI:

- instala `_codesteer-hermes/` na raiz do projeto
- faz bootstrap de um runtime local Python em `_codesteer-hermes/.runtime/venv`
- preserva `_hermes/` na remoção
- não cria `AGENTS.md` na raiz do projeto durante o install
- não sobrescreve `CLAUDE.md` preexistente não gerenciado; registra conflito e segue

### Desenvolvimento local do pacote

Guia de versionamento e release:

- [RELEASE.md](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/RELEASE.md)

Executar a suíte local:

```bash
python3 -m pip install -r requirements-dev.txt
npm test
```

Validar allowlist do pacote:

```bash
npm run pack:check
```

Smoke test do tarball local:

```bash
npm run smoke:pack
```

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
