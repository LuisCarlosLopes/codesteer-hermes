import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const repoRoot = path.resolve(import.meta.dirname, "..");
const binPath = path.join(repoRoot, "bin", "codesteer-hermes.js");

function makeProject() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "codesteer-hermes-test-"));
  fs.writeFileSync(path.join(root, "package.json"), JSON.stringify({ name: "fixture", private: true }, null, 2));
  return root;
}

function runCli(projectDir, ...args) {
  const result = spawnSync(process.execPath, [binPath, ...args, "--cwd", projectDir, "--yes"], {
    cwd: repoRoot,
    encoding: "utf8",
  });
  assert.equal(result.status, 0, result.stderr || result.stdout);
  return result;
}

test("install creates bundle, manifest and selected IDE artifacts", () => {
  const projectDir = makeProject();

  runCli(projectDir, "install", "--ides", "codex,cursor");

  const manifest = JSON.parse(
    fs.readFileSync(path.join(projectDir, ".codesteer-hermes-install.json"), "utf8"),
  );
  assert.deepEqual(manifest.selected_ides, ["codex", "cursor"]);
  assert.equal(fs.existsSync(path.join(projectDir, "_codesteer-hermes")), true);
  assert.equal(fs.existsSync(path.join(projectDir, ".codex", "agents")), true);
  assert.equal(fs.existsSync(path.join(projectDir, ".cursor", "agents")), true);
  assert.equal(fs.existsSync(path.join(projectDir, "AGENTS.md")), false);
  assert.equal(fs.existsSync(path.join(projectDir, "_hermes", ".sessions-index.yaml")), true);
});

test("install preserves unmanaged AGENTS.md untouched", () => {
  const projectDir = makeProject();
  fs.writeFileSync(path.join(projectDir, "AGENTS.md"), "manual agents\n", "utf8");

  runCli(projectDir, "install", "--ides", "codex");

  const manifest = JSON.parse(
    fs.readFileSync(path.join(projectDir, ".codesteer-hermes-install.json"), "utf8"),
  );
  assert.equal(fs.readFileSync(path.join(projectDir, "AGENTS.md"), "utf8"), "manual agents\n");
  assert.equal(manifest.conflicts.some((item) => item.path === "AGENTS.md"), false);
});

test("update keeps selected IDEs in sync and removes deselected artifacts", () => {
  const projectDir = makeProject();

  runCli(projectDir, "install", "--ides", "codex,cursor");
  runCli(projectDir, "update", "--ides", "codex");

  const manifest = JSON.parse(
    fs.readFileSync(path.join(projectDir, ".codesteer-hermes-install.json"), "utf8"),
  );
  assert.deepEqual(manifest.selected_ides, ["codex"]);
  assert.equal(fs.existsSync(path.join(projectDir, ".codex")), true);
  assert.equal(fs.existsSync(path.join(projectDir, ".cursor", "agents", "hermes.mdc")), false);
});

test("remove deletes managed files and preserves _hermes", () => {
  const projectDir = makeProject();

  runCli(projectDir, "install", "--ides", "codex");
  fs.mkdirSync(path.join(projectDir, "_hermes", "session-1"), { recursive: true });
  fs.writeFileSync(path.join(projectDir, "_hermes", "session-1", "scope.md"), "# scope\n", "utf8");

  runCli(projectDir, "remove");

  assert.equal(fs.existsSync(path.join(projectDir, "_codesteer-hermes")), false);
  assert.equal(fs.existsSync(path.join(projectDir, ".codex", "agents", "hermes.md")), false);
  assert.equal(fs.existsSync(path.join(projectDir, ".codesteer-hermes-install.json")), false);
  assert.equal(fs.existsSync(path.join(projectDir, "_hermes", "session-1", "scope.md")), true);
});
