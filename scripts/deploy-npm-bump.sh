#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f package.json ]]; then
  echo "package.json não encontrado em $REPO_ROOT" >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git não encontrado no PATH" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
  echo "Working tree não está limpa. Faça commit ou stash antes do bump." >&2
  exit 1
fi

REMOTE="${REMOTE:-origin}"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"

echo "Repositório: $REPO_ROOT"
echo "Branch atual: $BRANCH"
echo "Remoto: $REMOTE"
echo ""
CURRENT="$(node -p "require('./package.json').version")"
echo "Versão atual: $CURRENT"
echo ""
echo "Tipo de incremento semver:"
echo "  1) patch — correções (x.y.Z+1)"
echo "  2) minor — compatível (x.Y+1.0)"
echo "  3) major — breaking (X+1.0.0)"
echo ""

VERSION_KIND=""
while [[ -z "$VERSION_KIND" ]]; do
  read -r -p "Escolha [1-3]: " choice || exit 1
  case "$choice" in
    1) VERSION_KIND=patch ;;
    2) VERSION_KIND=minor ;;
    3) VERSION_KIND=major ;;
    *)
      echo "Opção inválida: escolha 1, 2 ou 3." >&2
      ;;
  esac
done

npm version "$VERSION_KIND" -m "version bump %s"

git push "$REMOTE" "$BRANCH" --follow-tags

echo "Push enviado para $REMOTE $BRANCH (com tags)."
