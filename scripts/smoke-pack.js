const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");

const root = path.resolve(__dirname, "..");
const npmCacheDir = fs.mkdtempSync(path.join(os.tmpdir(), "codesteer-hermes-npm-cache-"));
const npmEnv = { ...process.env, npm_config_cache: npmCacheDir };
const packJson = execFileSync("npm", ["pack", "--json"], {
  cwd: root,
  encoding: "utf8",
  env: npmEnv,
});
const packData = JSON.parse(packJson)[0];
const tarballPath = path.join(root, packData.filename);
const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), "codesteer-hermes-pack-"));
const projectDir = path.join(tmpRoot, "project");

fs.mkdirSync(projectDir);
fs.writeFileSync(path.join(projectDir, "package.json"), JSON.stringify({ name: "smoke-project", private: true }, null, 2));

function npmExec(commandArgs) {
  execFileSync(
    "npm",
    ["exec", "--yes", `--package=file:${tarballPath}`, "codesteer-hermes", "--", ...commandArgs],
    {
      cwd: root,
      stdio: "inherit",
      env: npmEnv,
    },
  );
}

npmExec(["install", "--cwd", projectDir, "--ides", "codex,cursor", "--yes"]);
npmExec(["update", "--cwd", projectDir, "--ides", "codex", "--yes"]);
npmExec(["remove", "--cwd", projectDir, "--yes"]);

fs.rmSync(tarballPath, { force: true });
fs.rmSync(tmpRoot, { recursive: true, force: true });
fs.rmSync(npmCacheDir, { recursive: true, force: true });
