#!/usr/bin/env node
/**
 * Cross-platform runner for Python unit tests.
 * Tries "python3" first (Unix/macOS), then "python" and "py" (Windows).
 */

const { spawnSync } = require("child_process");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");

function findPython3() {
  const candidates = process.platform === "win32" ? ["python", "py"] : ["python3", "python"];
  for (const candidate of candidates) {
    const result = spawnSync(candidate, ["--version"], { encoding: "utf8" });
    if (!result.error && result.status === 0) {
      const output = (result.stdout || result.stderr || "").trim();
      if (/^Python 3\./.test(output)) {
        return candidate;
      }
    }
  }
  return null;
}

const python = findPython3();
if (!python) {
  console.error("[run-python-tests] Python 3 não encontrado no PATH. Instale Python 3 para rodar os testes Python.");
  process.exit(1);
}

const result = spawnSync(
  python,
  ["-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
  {
    cwd: repoRoot,
    stdio: "inherit",
    encoding: "utf8",
  },
);

if (result.error) {
  console.error(`[run-python-tests] Erro ao executar testes: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
