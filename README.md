# HERMES — Hierarchical Engineering Reverse-Map & Extraction Squad

HERMES é uma squad agentic do Code Steer para engenharia reversa de artefatos de software e geração de SDDs rastreáveis.

- Site do Code Steer: [codesteer.vercel.app](https://codesteer.vercel.app)


## Visão geral

A HERMES não é um produto separado do ecossistema. Ela é uma squad do Code Steer especializada em engenharia reversa e documentação técnica rastreável.

O projeto segue quatro invariantes centrais:

- Zero inferência: quando falta evidência, a saída correta é pergunta estruturada ou pendência explícita.
- Não modifica o artefato analisado: toda saída vai para `_hermes/{scope-slug}/`.
- Fonte canônica única: agentes, skills, contratos e templates vivem em `_codesteer-hermes/`.
- Sessões isoladas: cada análise mantém seus próprios artefatos e memória auditável.


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

no chat digite e inicie o fluxo:

```
@hermes
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
- `agent_prefix` e `agent_suffix`: naming dos agentes gerados
- `skill_prefix` e `skill_suffix`: naming das skills geradas

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

## Licença

O repositório já contém [LICENSE](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/LICENSE:1).
