import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ParticipantDocumentationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.guide = (ROOT / "docs/participant-guide.md").read_text(encoding="utf-8")

    def test_readme_is_a_participant_front_door(self) -> None:
        for expected in (
            "## Start here",
            "docs/participant-guide.md",
            "--agent claude",
            "--agent codex",
            "--agent none",
            "Lab 1",
            "Lab 2",
            "Cleanup",
            "Troubleshooting",
        ):
            self.assertIn(expected, self.readme)
        self.assertNotIn("materials will be published", self.readme.lower())
        self.assertIn("participant-guide.md#7-troubleshooting-and-recovery", self.readme)

    def test_guide_preserves_required_evidence_and_scope_semantics(self) -> None:
        for expected in (
            "configured authority",
            "resolved permitted capabilities",
            "configured authority",
            "resolved permitted capabilities",
            "observed runtime behavior",
            "independently verified",
            "Only `app/lookup.py` may change",
            "Detect → Explain → Classify → Decide → Fix / Explicitly Allow",
            "Do not whitelist what you have not explained",
            "Bytecode hygiene is not security isolation",
            "not proof of server-side token/session revocation",
        ):
            self.assertIn(expected, self.guide)

    def test_guide_has_platform_and_validation_boundaries(self) -> None:
        self.assertIn("Windows/PowerShell", self.guide)
        self.assertIn("Primary end-to-end", self.guide)
        self.assertIn("performed on macOS", self.guide)
        self.assertIn("not been independently validated", self.guide)
        self.assertNotIn("/private/var/folders/", self.guide)

    def test_guide_references_real_commands_and_no_runtime_allowlist(self) -> None:
        for expected in (
            "scripts/preflight.py",
            "scripts/workshop.py setup",
            "scripts/workshop.py lab1",
            "scripts/workshop.py lab2 --agent codex",
            "scripts/workshop.py lab2 verify",
            "scripts/workshop.py cleanup",
            "--dry-run --verbose",
        ):
            self.assertIn(expected, self.guide)
        self.assertNotIn("whitelist `.claude`", self.guide)
        self.assertNotIn("whitelist `__pycache__`", self.guide)

    def test_managed_kaapi_path_is_pinned_and_not_manual(self) -> None:
        combined = self.readme + self.guide
        self.assertIn("9a0bc6ba34576782675aded9e16b718c24fea9bd", combined)
        self.assertIn("Kaapi `1.1.0`", combined)
        self.assertIn(".workshop-deps/", combined)
        self.assertNotIn("/Users/ashish/Documents/Codex-Projects/kaapi", combined)


if __name__ == "__main__":
    unittest.main()
