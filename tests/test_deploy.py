import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_DIR = REPO_ROOT / "_codesteer-hermes" / "deploy"
sys.path.insert(0, str(DEPLOY_DIR))

import deploy  # noqa: E402


class FakeAdapter:
    def __init__(self, ide_name, operation):
        self.ide_name = ide_name
        self.operation = operation

    def plan_operations(self, agents, skills):
        return [self.operation]

    def validate(self):
        return []


class DeployTests(unittest.TestCase):
    def test_deploy_target_creates_file_and_updates_state(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target_file = root / ".codex" / "agents" / "hermes-test.md"
            content = "hello hermes"
            adapter = FakeAdapter(
                "codex",
                {
                    "kind": "agent",
                    "path": str(target_file),
                    "source": "_codesteer-hermes/agents/test.md",
                    "signature": deploy.sha256_text(content),
                    "content": content,
                },
            )
            args = SimpleNamespace(force=False, validate=False, dry_run=False)
            log_payload = {"targets": {}, "runs": []}

            with mock.patch.object(deploy, "ROOT_DIR", root):
                issues = deploy.deploy_target(adapter, [], [], args, log_payload)

            self.assertEqual(issues, [])
            self.assertTrue(target_file.exists())
            self.assertEqual(target_file.read_text(encoding="utf-8"), content)
            self.assertIn(str(target_file), log_payload["targets"]["codex"]["files"])

    def test_deploy_target_detects_drift_without_force(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target_file = root / ".codex" / "agents" / "hermes-test.md"
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text("manual change", encoding="utf-8")

            adapter = FakeAdapter(
                "codex",
                {
                    "kind": "agent",
                    "path": str(target_file),
                    "source": "_codesteer-hermes/agents/test.md",
                    "signature": deploy.sha256_text("generated"),
                    "content": "generated",
                },
            )
            args = SimpleNamespace(force=False, validate=False, dry_run=False)
            log_payload = {
                "targets": {
                    "codex": {
                        "files": {
                            str(target_file): {
                                "kind": "agent",
                                "source": "_codesteer-hermes/agents/test.md",
                                "signature": deploy.sha256_text("previous generated"),
                            }
                        }
                    }
                },
                "runs": [],
            }

            with mock.patch.object(deploy, "ROOT_DIR", root):
                issues = deploy.deploy_target(adapter, [], [], args, log_payload)

            self.assertEqual(target_file.read_text(encoding="utf-8"), "manual change")
            self.assertTrue(any("diverge do último deploy conhecido" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
