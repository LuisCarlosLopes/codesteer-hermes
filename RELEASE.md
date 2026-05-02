# Tutorial — Criar Nova Versão do `codesteer-hermes`

Este guia descreve o fluxo recomendado para gerar uma nova versão do pacote `codesteer-hermes`, validar o pacote localmente e publicar no `npm` via GitHub Actions.

## Pré-requisitos

- acesso de escrita ao repositório GitHub
- conta no `npm`
- secret `NPM_TOKEN` configurado no GitHub Actions
- `Node.js 18+`
- `Python 3`

## 1. Validar o estado do repositório

Antes de criar uma versão:

```bash
git status
```

O ideal é seguir com o working tree limpo ou entender exatamente quais mudanças entrarão na release.

## 2. Rodar as validações locais

Execute a suíte completa:

```bash
python3 -m pip install -r requirements-dev.txt
npm test
```

Valide a allowlist do pacote:

```bash
npm run pack:check
```

Rode o smoke test do tarball local:

```bash
npm run smoke:pack
```

Se algum desses passos falhar, não avance para a release.

## 3. Atualizar a versão no `package.json`

Escolha o tipo de incremento:

- `patch`: correções sem mudança de interface
- `minor`: nova funcionalidade compatível
- `major`: mudança incompatível

Comando:

```bash
npm version patch
```

Exemplos equivalentes:

```bash
npm version minor
npm version major
```

Esse comando atualiza o `package.json`, cria um commit e gera uma tag Git no formato `vX.Y.Z`.

Se preferir controlar manualmente a mensagem do commit:

```bash
npm version patch --no-git-tag-version
git add package.json
git commit -m "chore(release): v0.1.1"
git tag v0.1.1
```

## 4. Revisar a versão gerada

Confirme a versão atual:

```bash
node -p "require('./package.json').version"
```

Confirme a tag:

```bash
git tag --list | tail
```

## 5. Enviar commit e tag

Fluxo padrão:

```bash
git push origin main --follow-tags
```

Se a branch da release não for `main`, envie a branch primeiro e depois a tag:

```bash
git push origin <sua-branch>
git push origin v0.1.1
```

## 6. Publicação automática no GitHub Actions

O workflow de release está em:

- [.github/workflows/release.yml](/Users/luiscarloslopesjr/GitHub/codesteer-hermes/.github/workflows/release.yml)

Comportamento esperado:

- em `pull_request` e `push`, roda validações
- em tag `v*.*.*`, roda validações e publica no `npm`

Após enviar a tag:

1. abra a aba `Actions` no GitHub
2. encontre o workflow `Release`
3. confirme que os jobs `verify` e `publish` passaram

## 7. Validar a publicação no npm

Depois da pipeline terminar:

```bash
npm view codesteer-hermes version
```

Teste a instalação da versão publicada:

```bash
npx codesteer-hermes@latest --help
```

Ou teste um fluxo real:

```bash
mkdir /tmp/hermes-smoke
cd /tmp/hermes-smoke
printf '{"name":"hermes-smoke","private":true}\n' > package.json
npx codesteer-hermes@latest install --ides codex --yes
```

## 8. Primeira publicação manual

Se ainda não existir nenhuma versão publicada, faça uma publicação manual inicial:

```bash
npm publish --access public
```

Depois disso, use preferencialmente o fluxo por tag no GitHub Actions.

## Problemas comuns

### `NPM_TOKEN` ausente

Erro típico: falha no job `publish`.

Correção:

1. GitHub > `Settings`
2. `Secrets and variables` > `Actions`
3. criar ou atualizar o secret `NPM_TOKEN`

### Nome do pacote indisponível

Valide antes:

```bash
npm view codesteer-hermes
```

Se já existir outro pacote com esse nome, será necessário renomear o campo `name` no `package.json`.

### Falha no `npm run pack:check`

Isso indica que o tarball contém arquivos fora da allowlist definida para publicação. Corrija `files` no `package.json` e/ou `.npmignore`.

### Falha no `npm run smoke:pack`

Isso indica que o pacote empacotado não está conseguindo executar o ciclo real de `install/update/remove`. Corrija antes da release.

# Release
```
git fetch origin --tags --force
npm version 0.1.4
git push origin main --follow-tags
```