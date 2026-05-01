const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const {
  BUNDLE_DIRNAME,
  BUNDLE_SOURCE_DIR,
  MANIFEST_FILENAME,
  PACKAGE_JSON_PATH,
  SUPPORTED_IDES,
} = require("./constants");
const {
  computeManagedSignature,
  copyDirectory,
  ensureDir,
  fromRelative,
  pathExists,
  readJson,
  removeEmptyDirectories,
  removePath,
  toPosixRelative,
  writeJson,
} = require("./fs-utils");
const { promptMultiSelect } = require("./prompt");

const INSTALL_SCHEMA_VERSION = 1;

function nowIso() {
  return new Date().toISOString();
}

function loadPackageMetadata() {
  return readJson(PACKAGE_JSON_PATH);
}

function parseArgs(argv) {
  const options = {
    dryRun: false,
    force: false,
    yes: false,
    cwd: process.cwd(),
    ides: null,
  };
  const positional = [];

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--dry-run") {
      options.dryRun = true;
      continue;
    }
    if (token === "--force") {
      options.force = true;
      continue;
    }
    if (token === "--yes") {
      options.yes = true;
      continue;
    }
    if (token === "--cwd") {
      index += 1;
      options.cwd = argv[index];
      continue;
    }
    if (token === "--ides") {
      index += 1;
      options.ides = parseIdeList(argv[index]);
      continue;
    }
    if (token === "--help" || token === "-h") {
      options.help = true;
      continue;
    }
    positional.push(token);
  }

  return {
    command: positional[0],
    options,
  };
}

function parseIdeList(rawValue) {
  if (!rawValue) {
    return [];
  }
  return rawValue
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function printHelp() {
  console.log(
    [
      "Uso: codesteer-hermes <install|update|remove|validate> [opções]",
      "",
      "Opções:",
      "  --ides codex,cursor     Seleção explícita de IDEs",
      "  --cwd <path>            Diretório alvo",
      "  --dry-run               Simula sem escrever",
      "  --force                 Sobrescreve drift/conflitos quando suportado",
      "  --yes                   Aceita defaults e evita prompt",
    ].join("\n"),
  );
}

function ensureSupportedIdes(ides) {
  const invalid = ides.filter((ide) => !SUPPORTED_IDES.includes(ide));
  if (invalid.length > 0) {
    throw new Error(`IDE(s) não suportadas: ${invalid.join(", ")}`);
  }
}

function manifestPathFor(rootDir) {
  return path.join(rootDir, MANIFEST_FILENAME);
}

function bundleRootFor(rootDir) {
  return path.join(rootDir, BUNDLE_DIRNAME);
}

function loadManifest(rootDir, required = false) {
  const manifestPath = manifestPathFor(rootDir);
  if (!pathExists(manifestPath)) {
    if (required) {
      throw new Error(`Manifesto de instalação não encontrado em ${manifestPath}.`);
    }
    return null;
  }
  return readJson(manifestPath);
}

function ensureProjectRoot(rootDir) {
  const markers = [
    ".git",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "README.md",
  ];
  if (!fs.existsSync(rootDir) || !fs.lstatSync(rootDir).isDirectory()) {
    throw new Error(`Diretório alvo inválido: ${rootDir}`);
  }
  if (!markers.some((marker) => pathExists(path.join(rootDir, marker)))) {
    throw new Error("O diretório alvo não parece ser a raiz de um projeto.");
  }
}

async function resolveSelectedIdes(command, options, manifest) {
  if (options.ides && options.ides.length > 0) {
    ensureSupportedIdes(options.ides);
    return options.ides;
  }

  if (command === "update" || command === "validate") {
    if (manifest && Array.isArray(manifest.selected_ides) && manifest.selected_ides.length > 0) {
      return manifest.selected_ides;
    }
    return [...SUPPORTED_IDES];
  }

  if (command === "install") {
    if (options.yes) {
      return [...SUPPORTED_IDES];
    }
    return promptMultiSelect(SUPPORTED_IDES);
  }

  return manifest && Array.isArray(manifest.selected_ides) ? manifest.selected_ides : [...SUPPORTED_IDES];
}

function runCommand(command, args, options = {}) {
  const result = spawnSync(command, args, {
    stdio: options.captureOutput ? "pipe" : "inherit",
    cwd: options.cwd,
    encoding: "utf8",
  });

  if (result.error) {
    throw result.error;
  }

  if (result.status !== 0) {
    const stderr = options.captureOutput ? result.stderr : "";
    throw new Error(`Comando falhou: ${command} ${args.join(" ")}${stderr ? `\n${stderr}` : ""}`);
  }

  return result;
}

function detectPython3() {
  const result = spawnSync("python3", ["--version"], { encoding: "utf8" });
  if (result.error || result.status !== 0) {
    throw new Error("python3 não encontrado. Instale Python 3 para usar o pacote.");
  }
  return "python3";
}

function ensurePythonRuntime(rootDir, dryRun) {
  const bundleRoot = bundleRootFor(rootDir);
  const runtimeRoot = path.join(bundleRoot, ".runtime");
  const venvDir = path.join(runtimeRoot, "venv");
  const pythonCommand = detectPython3();
  const venvPython = path.join(venvDir, "bin", "python");

  if (dryRun) {
    return {
      systemPython: pythonCommand,
      venvPython,
      runtimeRoot,
      venvDir,
    };
  }

  ensureDir(runtimeRoot);
  if (!pathExists(venvPython)) {
    runCommand(pythonCommand, ["-m", "venv", "--system-site-packages", venvDir], { cwd: rootDir });
  }

  const yamlCheck = spawnSync(venvPython, ["-c", "import yaml"], { encoding: "utf8" });
  if (yamlCheck.status !== 0) {
    runCommand(venvPython, ["-m", "pip", "install", "PyYAML"], { cwd: rootDir });
  }

  return {
    systemPython: pythonCommand,
    venvPython,
    runtimeRoot,
    venvDir,
  };
}

function createTemporarySummaryPath(prefix) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "codesteer-hermes-"));
  return path.join(directory, `${prefix}.json`);
}

function buildDeployArgs(ides, options, summaryPath, planOnly) {
  const args = [path.join(BUNDLE_DIRNAME, "deploy", "deploy.py")];
  for (const ide of ides) {
    args.push("--ide", ide);
  }
  if (options.dryRun) {
    args.push("--dry-run");
  }
  if (options.force) {
    args.push("--force");
  }
  if (planOnly) {
    args.push("--plan-only");
  }
  if (summaryPath) {
    args.push("--summary-json", summaryPath);
  }
  return args;
}

function runDeploy(rootDir, runtime, ides, options, planOnly = false) {
  const summaryPath = createTemporarySummaryPath(planOnly ? "deploy-plan" : "deploy-summary");
  const args = buildDeployArgs(ides, options, summaryPath, planOnly);
  runCommand(runtime.venvPython, args, { cwd: rootDir });
  const summary = readJson(summaryPath);
  fs.rmSync(path.dirname(summaryPath), { recursive: true, force: true });
  return summary;
}

function collectManagedFilesFromSummary(rootDir, summary, selectedIdes) {
  const managedFiles = [];
  for (const target of summary.targets) {
    if (!selectedIdes.includes(target.ide)) {
      continue;
    }
    for (const operation of target.operations) {
      if (!["create", "update", "unchanged", "force"].includes(operation.status)) {
        continue;
      }
      managedFiles.push({
        ide: target.ide,
        kind: operation.kind,
        path: toPosixRelative(rootDir, operation.path),
        source: operation.source,
        signature: operation.signature,
      });
    }
  }
  return managedFiles;
}

function collectConflictsFromSummary(rootDir, summary) {
  const conflicts = [];
  for (const target of summary.targets) {
    for (const operation of target.operations) {
      if (operation.status !== "conflict") {
        continue;
      }
      conflicts.push({
        ide: target.ide,
        kind: operation.kind,
        path: toPosixRelative(rootDir, operation.path),
        reason: operation.message,
      });
    }
  }
  return conflicts;
}

function collectCandidateDirectories(rootDir, planSummary) {
  const candidates = new Set();
  for (const target of planSummary.targets) {
    for (const operation of target.operations) {
      const absolutePath = operation.path;
      let current = path.dirname(absolutePath);
      while (current.startsWith(rootDir) && current !== rootDir) {
        candidates.add(toPosixRelative(rootDir, current));
        current = path.dirname(current);
      }
    }
  }
  return [...candidates].sort();
}

function identifyMissingDirectories(rootDir, candidateDirectories, bundleCopiedNow) {
  const created = new Set();
  for (const directory of candidateDirectories) {
    if (!pathExists(fromRelative(rootDir, directory))) {
      created.add(directory);
    }
  }
  if (bundleCopiedNow) {
    created.add(BUNDLE_DIRNAME);
  }
  return [...created].sort();
}

function copyBundle(rootDir, dryRun) {
  const destination = bundleRootFor(rootDir);
  const existedBefore = pathExists(destination);
  if (dryRun) {
    return { existedBefore, destination };
  }

  removePath(destination);
  copyDirectory(BUNDLE_SOURCE_DIR, destination);
  return { existedBefore, destination };
}

function validateManifestFile(rootDir) {
  const manifest = loadManifest(rootDir, true);
  if (manifest.schema_version !== INSTALL_SCHEMA_VERSION) {
    throw new Error(`Versão de manifesto não suportada: ${manifest.schema_version}`);
  }
  return manifest;
}

function buildManifest(rootDir, packageMetadata, selectedIdes, runtime, summary, previousManifest, createdDirectories) {
  const previousCreated = new Set(previousManifest ? previousManifest.created_directories || [] : []);
  for (const directory of createdDirectories) {
    previousCreated.add(directory);
  }

  return {
    schema_version: INSTALL_SCHEMA_VERSION,
    package_name: packageMetadata.name,
    package_version: packageMetadata.version,
    bundle_root: BUNDLE_DIRNAME,
    selected_ides: [...selectedIdes],
    installed_at: previousManifest ? previousManifest.installed_at : nowIso(),
    updated_at: nowIso(),
    runtime: {
      system_python: runtime.systemPython,
      venv_python: toPosixRelative(rootDir, runtime.venvPython),
      venv_dir: toPosixRelative(rootDir, runtime.venvDir),
    },
    managed_files: collectManagedFilesFromSummary(rootDir, summary, selectedIdes),
    created_directories: [...previousCreated].sort(),
    conflicts: collectConflictsFromSummary(rootDir, summary),
  };
}

function writeManifest(rootDir, manifest, dryRun) {
  const manifestPath = manifestPathFor(rootDir);
  if (dryRun) {
    console.log(`[DRY-RUN] Manifesto seria gravado em ${manifestPath}`);
    return;
  }
  writeJson(manifestPath, manifest);
}

function summarizeConflicts(manifest) {
  if (!manifest.conflicts || manifest.conflicts.length === 0) {
    return;
  }
  console.warn("[codesteer-hermes] Conflitos detectados e preservados:");
  for (const conflict of manifest.conflicts) {
    console.warn(`- ${conflict.path}: ${conflict.reason}`);
  }
}

function filterManifestForIdes(manifest, ides) {
  return {
    ...manifest,
    selected_ides: manifest.selected_ides.filter((ide) => ides.includes(ide)),
    managed_files: manifest.managed_files.filter((item) => ides.includes(item.ide)),
    conflicts: (manifest.conflicts || []).filter((item) => ides.includes(item.ide)),
  };
}

function removeManagedFiles(rootDir, manifest, options, preserveBundle) {
  const drifted = [];

  for (const item of manifest.managed_files) {
    const absolutePath = fromRelative(rootDir, item.path);
    if (!pathExists(absolutePath)) {
      continue;
    }
    const actualSignature = computeManagedSignature(absolutePath, item.kind);
    if (!options.force && actualSignature !== item.signature) {
      drifted.push(item.path);
      continue;
    }
    if (!options.dryRun) {
      fs.rmSync(absolutePath, { recursive: false, force: true });
    }
  }

  if (!preserveBundle) {
    const bundleRoot = bundleRootFor(rootDir);
    if (pathExists(bundleRoot) && !options.dryRun) {
      removePath(bundleRoot);
    }
  }

  if (!options.dryRun) {
    removeEmptyDirectories(
      rootDir,
      manifest.created_directories.filter((directory) => preserveBundle || directory !== BUNDLE_DIRNAME),
    );
  }

  return drifted;
}

function printRemovalSummary(drifted) {
  if (drifted.length === 0) {
    return;
  }
  console.warn("[codesteer-hermes] Arquivos preservados por drift:");
  for (const filePath of drifted) {
    console.warn(`- ${filePath}`);
  }
}

function printDryRunSummary(command, rootDir, selectedIdes, extraLines = []) {
  console.log(`[DRY-RUN] ${command} seria executado em ${rootDir}`);
  console.log(`[DRY-RUN] IDEs: ${selectedIdes.join(", ")}`);
  for (const line of extraLines) {
    console.log(`[DRY-RUN] ${line}`);
  }
}

async function installCommand(rootDir, options) {
  ensureProjectRoot(rootDir);
  const packageMetadata = loadPackageMetadata();
  const selectedIdes = await resolveSelectedIdes("install", options, null);
  if (options.dryRun) {
    printDryRunSummary("install", rootDir, selectedIdes, [
      `bundle ${BUNDLE_DIRNAME}/ seria copiado`,
      "runtime Python local seria bootstrapado",
      `manifesto ${MANIFEST_FILENAME} seria criado`,
    ]);
    return;
  }
  const bundleCopy = copyBundle(rootDir, options.dryRun);
  const runtime = ensurePythonRuntime(rootDir, options.dryRun);
  const planSummary = runDeploy(rootDir, runtime, selectedIdes, options, true);
  const candidateDirectories = collectCandidateDirectories(rootDir, planSummary);
  const createdDirectories = identifyMissingDirectories(rootDir, candidateDirectories, !bundleCopy.existedBefore);
  const summary = runDeploy(rootDir, runtime, selectedIdes, options, false);
  const manifest = buildManifest(rootDir, packageMetadata, selectedIdes, runtime, summary, null, createdDirectories);
  writeManifest(rootDir, manifest, options.dryRun);
  summarizeConflicts(manifest);
}

async function updateCommand(rootDir, options) {
  ensureProjectRoot(rootDir);
  const previousManifest = validateManifestFile(rootDir);
  const packageMetadata = loadPackageMetadata();
  const selectedIdes = await resolveSelectedIdes("update", options, previousManifest);
  const deselectedIdes = previousManifest.selected_ides.filter((ide) => !selectedIdes.includes(ide));
  if (options.dryRun) {
    printDryRunSummary("update", rootDir, selectedIdes, [
      `bundle ${BUNDLE_DIRNAME}/ seria atualizado para ${packageMetadata.version}`,
      deselectedIdes.length > 0
        ? `arquivos das IDEs removidas seriam limpos: ${deselectedIdes.join(", ")}`
        : "nenhuma IDE seria removida",
    ]);
    return;
  }

  copyBundle(rootDir, options.dryRun);
  const runtime = ensurePythonRuntime(rootDir, options.dryRun);
  const planSummary = runDeploy(rootDir, runtime, selectedIdes, options, true);
  const candidateDirectories = collectCandidateDirectories(rootDir, planSummary);
  const createdDirectories = identifyMissingDirectories(rootDir, candidateDirectories, false);
  const summary = runDeploy(rootDir, runtime, selectedIdes, options, false);
  const nextManifest = buildManifest(
    rootDir,
    packageMetadata,
    selectedIdes,
    runtime,
    summary,
    previousManifest,
    createdDirectories,
  );

  if (deselectedIdes.length > 0) {
    const deselectedManifest = filterManifestForIdes(previousManifest, deselectedIdes);
    const drifted = removeManagedFiles(rootDir, deselectedManifest, options, true);
    printRemovalSummary(drifted);
    nextManifest.created_directories = nextManifest.created_directories.filter(
      (directory) => !deselectedManifest.created_directories.includes(directory),
    );
  }

  writeManifest(rootDir, nextManifest, options.dryRun);
  summarizeConflicts(nextManifest);
}

async function removeCommand(rootDir, options) {
  const manifest = validateManifestFile(rootDir);
  const drifted = removeManagedFiles(rootDir, manifest, options, false);
  printRemovalSummary(drifted);
  if (!options.dryRun) {
    fs.rmSync(manifestPathFor(rootDir), { force: true });
  }
}

async function validateCommand(rootDir, options) {
  const manifest = loadManifest(rootDir, false);
  const selectedIdes = await resolveSelectedIdes("validate", options, manifest);
  const runtime = ensurePythonRuntime(rootDir, options.dryRun);
  const args = buildDeployArgs(selectedIdes, options, null, false);
  args.push("--validate");
  runCommand(runtime.venvPython, args, { cwd: rootDir });

  if (!manifest) {
    return;
  }

  const drifted = [];
  for (const item of manifest.managed_files) {
    const absolutePath = fromRelative(rootDir, item.path);
    const actualSignature = computeManagedSignature(absolutePath, item.kind);
    if (actualSignature !== item.signature) {
      drifted.push(item.path);
    }
  }
  if (drifted.length > 0) {
    throw new Error(`Validação local encontrou drift em ${drifted.length} arquivo(s): ${drifted.join(", ")}`);
  }
}

async function runCli(argv) {
  const { command, options } = parseArgs(argv);
  if (options.help || !command) {
    printHelp();
    return;
  }

  const rootDir = fs.realpathSync(path.resolve(options.cwd));

  if (command === "install") {
    await installCommand(rootDir, options);
    return;
  }
  if (command === "update") {
    await updateCommand(rootDir, options);
    return;
  }
  if (command === "remove") {
    await removeCommand(rootDir, options);
    return;
  }
  if (command === "validate") {
    await validateCommand(rootDir, options);
    return;
  }

  throw new Error(`Comando desconhecido: ${command}`);
}

module.exports = {
  runCli,
};
