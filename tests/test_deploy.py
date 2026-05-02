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

from adapters.base import BaseAdapter  # noqa: E402


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

    def test_process_target_marks_unmanaged_file_as_conflict(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target_file = root / "AGENTS.md"
            target_file.write_text("manual file", encoding="utf-8")

            adapter = FakeAdapter(
                "codex",
                {
                    "kind": "bootstrap",
                    "path": str(target_file),
                    "source": "_codesteer-hermes/deploy/config.yaml",
                    "signature": deploy.sha256_text("../_codesteer-hermes/deploy/config.yaml"),
                    "link_target": "../_codesteer-hermes/deploy/config.yaml",
                },
            )
            args = SimpleNamespace(force=False, validate=False, dry_run=False, plan_only=False)
            log_payload = {"targets": {}, "runs": []}

            with mock.patch.object(deploy, "ROOT_DIR", root):
                result = deploy.process_target(adapter, [], [], args, log_payload)

            self.assertEqual(result["errors"], [])
            self.assertEqual(len(result["warnings"]), 1)
            self.assertEqual(result["operations"][0]["status"], "conflict")

    def test_process_target_can_emit_plan_without_writing(self):
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
            args = SimpleNamespace(force=False, validate=False, dry_run=False, plan_only=True)
            log_payload = {"targets": {}, "runs": []}

            with mock.patch.object(deploy, "ROOT_DIR", root):
                result = deploy.process_target(adapter, [], [], args, log_payload)

            self.assertEqual(result["errors"], [])
            self.assertFalse(target_file.exists())
            self.assertEqual(result["operations"][0]["status"], "create")

    def test_default_agent_filename_primary_hermes_avoids_double_prefix(self):
        base = REPO_ROOT / "_codesteer-hermes"
        adapter = BaseAdapter(
            "cursor",
            {
                "agent_prefix": "hermes-",
                "agent_suffix": ".mdc",
                "skill_prefix": "hermes-",
                "skill_suffix": ".mdc",
                "agents_dir": ".cursor/agents",
                "skills_dir": ".cursor/skills",
            },
            base,
            REPO_ROOT,
        )
        self.assertEqual(adapter.default_agent_filename("hermes"), "hermes.mdc")
        self.assertEqual(adapter.default_agent_filename("clarifier"), "hermes-clarifier.mdc")

    def test_default_agent_filename_can_diverge_from_skill_suffix_for_copilot(self):
        base = REPO_ROOT / "_codesteer-hermes"
        adapter = BaseAdapter(
            "copilot",
            {
                "agent_prefix": "hermes-",
                "agent_suffix": ".agent.md",
                "skill_prefix": "hermes-",
                "skill_suffix": ".instructions.md",
                "agents_dir": ".github/agents",
                "skills_dir": ".github/skills",
            },
            base,
            REPO_ROOT,
        )
        self.assertEqual(adapter.default_agent_filename("hermes"), "hermes.agent.md")
        self.assertEqual(adapter.default_agent_filename("clarifier"), "hermes-clarifier.agent.md")

    def test_skill_link_name_avoids_double_hermes_prefix(self):
        base = REPO_ROOT / "_codesteer-hermes"
        adapter = BaseAdapter(
            "cursor",
            {
                "skill_prefix": "hermes-",
                "skill_suffix": ".mdc",
                "agents_dir": ".cursor/agents",
                "skills_dir": ".cursor/skills",
            },
            base,
            REPO_ROOT,
        )
        self.assertEqual(adapter.skill_link_name("hermes-help"), "hermes-help")
        self.assertEqual(adapter.skill_link_name("hermes-api-reverse"), "hermes-api-reverse")

    def test_skill_link_name_skills_without_prefix(self):
        base = REPO_ROOT / "_codesteer-hermes"
        adapter = BaseAdapter(
            "cursor",
            {
                "skill_prefix": "hermes-",
                "skills_without_prefix": ["playwright-cli"],
                "agents_dir": ".cursor/agents",
                "skills_dir": ".cursor/skills",
            },
            base,
            REPO_ROOT,
        )
        self.assertEqual(adapter.skill_link_name("playwright-cli"), "playwright-cli")
        self.assertEqual(adapter.skill_link_name("api-reverse"), "hermes-api-reverse")

    def test_canonical_skills_list_includes_ensure_skills(self):
        skills = deploy.canonical_skills_list(REPO_ROOT / "_codesteer-hermes", ["playwright-cli"])
        self.assertIn("playwright-cli", skills)
        self.assertIn("hermes-help", skills)


if __name__ == "__main__":
    unittest.main()
