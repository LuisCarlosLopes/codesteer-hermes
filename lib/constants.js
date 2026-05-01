const path = require("path");

const PACKAGE_ROOT = path.resolve(__dirname, "..");
const PACKAGE_JSON_PATH = path.join(PACKAGE_ROOT, "package.json");
const BUNDLE_DIRNAME = "_codesteer-hermes";
const BUNDLE_SOURCE_DIR = path.join(PACKAGE_ROOT, BUNDLE_DIRNAME);
const MANIFEST_FILENAME = ".codesteer-hermes-install.json";
const SUPPORTED_IDES = ["claude-code", "kiro", "cursor", "copilot", "agent", "codex"];

module.exports = {
  BUNDLE_DIRNAME,
  BUNDLE_SOURCE_DIR,
  MANIFEST_FILENAME,
  PACKAGE_JSON_PATH,
  PACKAGE_ROOT,
  SUPPORTED_IDES,
};
