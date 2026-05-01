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
const entries = execFileSync("tar", ["-tf", tarballPath], {
  cwd: root,
  encoding: "utf8",
})
  .trim()
  .split("\n")
  .filter(Boolean);

const allowedPrefixes = [
  "package/package.json",
  "package/README.md",
  "package/LICENSE",
  "package/bin/",
  "package/lib/",
  "package/_codesteer-hermes/",
];

const disallowed = entries.filter((entry) => !allowedPrefixes.some((prefix) => entry === prefix || entry.startsWith(prefix)));

fs.rmSync(tarballPath, { force: true });
fs.rmSync(npmCacheDir, { recursive: true, force: true });

if (disallowed.length > 0) {
  console.error("Arquivos fora da allowlist encontrados no pacote:");
  for (const entry of disallowed) {
    console.error(`- ${entry}`);
  }
  process.exit(1);
}

console.log(`Packlist validada com ${entries.length} entrada(s).`);
