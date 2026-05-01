import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = REPO_ROOT / "_codesteer-hermes" / "validation"
sys.path.insert(0, str(VALIDATION_DIR))

import artifact_validator  # noqa: E402


class ArtifactValidatorTests(unittest.TestCase):
    def test_l1_fixture_is_valid(self):
        fixture = REPO_ROOT / "_hermes" / "fixtures" / "phase56-l1-happy-path"
        errors = artifact_validator.validate_session_directory(fixture)
        self.assertEqual(errors, [])

    def test_l3_fixture_requires_rebuild_readiness_and_passes(self):
        fixture = REPO_ROOT / "_hermes" / "fixtures" / "phase56-l3-security-and-pii"
        errors = artifact_validator.validate_session_directory(fixture)
        self.assertEqual(errors, [])

    def test_missing_required_artifact_fixture_fails(self):
        fixture = REPO_ROOT / "_hermes" / "fixtures" / "phase56-missing-required-artifact"
        errors = artifact_validator.validate_session_directory(fixture)
        self.assertTrue(any("db-schema.md" in error for error in errors))

    def test_generic_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact = Path(tmp_dir) / "screen-inventory.md"
            artifact.write_text(
                "\n".join(
                    [
                        "# Screen Inventory",
                        "## Escopo consolidado",
                        "## Evidências consolidadas",
                        "- Evidência: na UI",
                        "## Conteúdo reconciliado",
                        "## Itens pendentes de validação",
                        "## Conflitos e gaps relacionados",
                    ]
                ),
                encoding="utf-8",
            )

            errors = artifact_validator.validate_markdown(artifact)
            self.assertTrue(any("evidência genérica" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
