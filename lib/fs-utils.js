const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function writeJson(filePath, payload) {
  fs.writeFileSync(filePath, JSON.stringify(payload, null, 2) + "\n", "utf8");
}

function sha256Text(content) {
  return crypto.createHash("sha256").update(content, "utf8").digest("hex");
}

function pathExists(targetPath) {
  try {
    fs.lstatSync(targetPath);
    return true;
  } catch (error) {
    if (error && error.code === "ENOENT") {
      return false;
    }
    throw error;
  }
}

function ensureDir(targetPath) {
  fs.mkdirSync(targetPath, { recursive: true });
}

function copyDirectory(source, target) {
  fs.cpSync(source, target, {
    recursive: true,
    preserveTimestamps: true,
  });
}

function removePath(targetPath) {
  fs.rmSync(targetPath, { recursive: true, force: true });
}

function toPosixRelative(rootDir, targetPath) {
  return path.relative(rootDir, targetPath).split(path.sep).join("/");
}

function fromRelative(rootDir, relativePath) {
  return path.resolve(rootDir, relativePath);
}

function computeManagedSignature(targetPath, kind) {
  if (!pathExists(targetPath)) {
    return null;
  }

  const stats = fs.lstatSync(targetPath);
  if (kind === "skill" || kind === "bootstrap") {
    if (!stats.isSymbolicLink()) {
      return null;
    }
    return sha256Text(fs.readlinkSync(targetPath));
  }

  if (stats.isSymbolicLink()) {
    return null;
  }

  return sha256Text(fs.readFileSync(targetPath, "utf8"));
}

function removeEmptyDirectories(rootDir, directories) {
  const sorted = [...directories].sort((left, right) => right.length - left.length);
  for (const relativeDir of sorted) {
    const absoluteDir = fromRelative(rootDir, relativeDir);
    if (!pathExists(absoluteDir)) {
      continue;
    }
    const stats = fs.lstatSync(absoluteDir);
    if (!stats.isDirectory() || stats.isSymbolicLink()) {
      continue;
    }
    if (fs.readdirSync(absoluteDir).length === 0) {
      fs.rmdirSync(absoluteDir);
    }
  }
}

module.exports = {
  computeManagedSignature,
  copyDirectory,
  ensureDir,
  fromRelative,
  pathExists,
  readJson,
  removeEmptyDirectories,
  removePath,
  sha256Text,
  toPosixRelative,
  writeJson,
};
