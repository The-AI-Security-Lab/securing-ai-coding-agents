import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import preflight


class PreflightTests(unittest.TestCase):
    def make_repo(self, root: Path, *, guide: bool = True) -> None:
        (root / "scripts").mkdir(parents=True)
        (root / "scripts" / "preflight.py").write_text("# fixture\n", encoding="utf-8")
        if guide:
            (root / "docs").mkdir()
            (root / "docs" / "hands-on-setup.md").write_text("# fixture\n", encoding="utf-8")

    def runner(self, *, git_checkout: bool = False, kaapi_exit: int = 0):
        def run(command, cwd):
            command = list(command)
            if command[:3] == ["git", "rev-parse", "--show-toplevel"]:
                return (0, str(cwd)) if git_checkout else (128, "not a git repository")
            if command[:2] == ["git", "--version"]:
                return 0, "git version 2.39.5"
            if command[0] in {"claude", "codex"}:
                return 0, f"{command[0]} test-version"
            if command[0] == "kaapi" or command[-2:] == ["kaapi", "version"]:
                return kaapi_exit, "kaapi test-version" if kaapi_exit == 0 else "unsupported"
            if command[0].endswith("/kaapi") and command[-1] == "version":
                return kaapi_exit, "kaapi test-version" if kaapi_exit == 0 else "unsupported"
            return 0, "ok"

        return run

    def locator(self, *names):
        return lambda name: f"/fake/{name}" if name in names else None

    def check(self, result, name):
        return next(check for check in result.checks if check.name == name)

    def test_claude_only_does_not_check_codex(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="claude",
                acquisition="zip",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(),
                locator=self.locator("claude"),
            )
            self.assertEqual(self.check(result, "Selected agent executable (Claude Code)").status, preflight.PASS)
            self.assertFalse(any("Codex" in check.name for check in result.checks))
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.readiness_state, "UNRESOLVED_MANUAL_EVIDENCE")
            self.assertFalse(result.hands_on_ready)

    def test_codex_only_does_not_require_claude(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="codex",
                acquisition="zip",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(),
                locator=self.locator("codex"),
            )
            self.assertEqual(self.check(result, "Selected agent executable (Codex)").status, preflight.PASS)
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(any("Claude Code" in check.name for check in result.checks))

    def test_instructor_led_is_not_hands_on_readiness(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="none",
                acquisition="zip",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(),
                locator=self.locator(),
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.readiness_state, "INSTRUCTOR_LED_NOT_HANDS_ON")
            self.assertFalse(result.hands_on_ready)
            self.assertTrue(all(check.status != preflight.FAIL for check in result.checks))

    def test_missing_selected_agent_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="claude",
                acquisition="zip",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(),
                locator=self.locator(),
            )
            self.assertEqual(self.check(result, "Selected agent executable (Claude Code)").status, preflight.FAIL)
            self.assertEqual(result.exit_code, 1)

    def test_optional_kaapi_absent_is_inconclusive_and_non_gating(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="codex",
                acquisition="zip",
                kaapi_mode="check",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(),
                locator=self.locator("codex"),
            )
            self.assertEqual(self.check(result, "Kaapi CLI availability").status, preflight.INCONCLUSIVE)
            self.assertEqual(result.exit_code, 0)

    def test_optional_kaapi_available_but_incompatible_is_inconclusive(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="codex",
                acquisition="zip",
                kaapi_mode="check",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(kaapi_exit=2),
                locator=self.locator("codex", "kaapi"),
            )
            self.assertEqual(self.check(result, "Kaapi CLI availability").status, preflight.INCONCLUSIVE)
            self.assertEqual(result.exit_code, 0)

    def test_json_exposes_readiness_separately_from_exit_code(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="claude",
                acquisition="zip",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(),
                locator=self.locator("claude"),
            )
            document = preflight.result_as_dict(result)
            self.assertEqual(document["exit_code"], 0)
            self.assertEqual(document["automated_gate"], "CLEAR")
            self.assertFalse(document["readiness"]["hands_on_ready"])
            self.assertEqual(document["readiness"]["state"], "UNRESOLVED_MANUAL_EVIDENCE")
            self.assertIn("not proof", document["readiness"]["explanation"])

    def test_auto_supports_git_and_zip_acquisition(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            git_result = preflight.build_result(
                agent="none",
                acquisition="auto",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(git_checkout=True),
                locator=self.locator("git"),
            )
            zip_result = preflight.build_result(
                agent="none",
                acquisition="auto",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(git_checkout=False),
                locator=self.locator(),
            )
            self.assertEqual(git_result.acquisition, "git")
            self.assertEqual(self.check(git_result, "Git executable").status, preflight.PASS)
            self.assertEqual(zip_result.acquisition, "zip")
            self.assertEqual(self.check(zip_result, "Git executable").status, preflight.NOT_APPLICABLE)

    def test_git_acquisition_requires_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="none",
                acquisition="git",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(git_checkout=False),
                locator=self.locator("git"),
            )
            self.assertEqual(self.check(result, "Workshop acquisition").status, preflight.FAIL)

    def test_validation_report_is_not_a_participant_requirement(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="none",
                acquisition="zip",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(),
                locator=self.locator(),
            )
            self.assertEqual(self.check(result, "Participant files").status, preflight.PASS)

    def test_missing_participant_file_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root, guide=False)
            result = preflight.build_result(
                agent="none",
                acquisition="zip",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(),
                locator=self.locator(),
            )
            self.assertEqual(self.check(result, "Participant files").status, preflight.FAIL)

    def test_unsupported_python_is_a_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="none",
                acquisition="zip",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                python_version=(3, 10, 9),
                runner=self.runner(),
                locator=self.locator(),
            )
            self.assertEqual(self.check(result, "Python runtime").status, preflight.FAIL)
            self.assertEqual(result.exit_code, 1)

    def test_subprocess_timeout_is_safe_and_reported(self):
        with mock.patch.object(
            preflight.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["fake"], 10),
        ):
            code, output = preflight._run(["fake"], Path.cwd())
        self.assertEqual(code, 124)
        self.assertIn("timed out", output)

    def test_synthetic_prepare_and_independent_verify(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as fixture_temp:
            repo = Path(repo_temp)
            self.make_repo(repo)
            fixture = Path(fixture_temp) / "synthetic"
            prepared = preflight.prepare_synthetic_workspace(repo, fixture)
            self.assertEqual(prepared.status, preflight.PASS)
            digest = hashlib.sha256(
                (fixture / preflight.SYNTHETIC_INPUT).read_bytes()
            ).hexdigest()
            (fixture / preflight.SYNTHETIC_OUTPUT).write_text(digest + "\n", encoding="utf-8")
            verified = preflight.verify_synthetic_workspace(repo, fixture)
            self.assertEqual(verified.status, preflight.PASS)

    def prepare_verified_fixture(self, repo: Path, fixture: Path) -> None:
        prepared = preflight.prepare_synthetic_workspace(repo, fixture)
        self.assertEqual(prepared.status, preflight.PASS)
        digest = hashlib.sha256(
            (fixture / preflight.SYNTHETIC_INPUT).read_bytes()
        ).hexdigest()
        (fixture / preflight.SYNTHETIC_OUTPUT).write_text(digest + "\n", encoding="utf-8")

    def test_modified_input_with_matching_modified_digest_fails(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as fixture_temp:
            repo = Path(repo_temp)
            self.make_repo(repo)
            fixture = Path(fixture_temp) / "synthetic"
            self.prepare_verified_fixture(repo, fixture)
            modified = b"Modified synthetic input.\n"
            (fixture / preflight.SYNTHETIC_INPUT).write_bytes(modified)
            (fixture / preflight.SYNTHETIC_OUTPUT).write_text(
                hashlib.sha256(modified).hexdigest() + "\n", encoding="utf-8"
            )
            check = preflight.verify_synthetic_workspace(repo, fixture)
            self.assertEqual(check.status, preflight.FAIL)
            self.assertIn("original known synthetic fixture", check.observed)

    def test_incorrect_output_digest_fails(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as fixture_temp:
            repo = Path(repo_temp)
            self.make_repo(repo)
            fixture = Path(fixture_temp) / "synthetic"
            self.prepare_verified_fixture(repo, fixture)
            (fixture / preflight.SYNTHETIC_OUTPUT).write_text("0" * 64 + "\n", encoding="utf-8")
            check = preflight.verify_synthetic_workspace(repo, fixture)
            self.assertEqual(check.status, preflight.FAIL)
            self.assertIn("digest", check.observed)

    def test_unexpected_extra_file_fails(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as fixture_temp:
            repo = Path(repo_temp)
            self.make_repo(repo)
            fixture = Path(fixture_temp) / "synthetic"
            self.prepare_verified_fixture(repo, fixture)
            (fixture / "extra.txt").write_text("unexpected\n", encoding="utf-8")
            check = preflight.verify_synthetic_workspace(repo, fixture)
            self.assertEqual(check.status, preflight.FAIL)
            self.assertIn("extra.txt", check.observed)

    def test_symlinked_input_fails(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as fixture_temp:
            repo = Path(repo_temp)
            self.make_repo(repo)
            fixture = Path(fixture_temp) / "synthetic"
            self.prepare_verified_fixture(repo, fixture)
            source = Path(fixture_temp) / "input-source.txt"
            source.write_text(preflight.SYNTHETIC_CONTENT, encoding="utf-8")
            (fixture / preflight.SYNTHETIC_INPUT).unlink()
            (fixture / preflight.SYNTHETIC_INPUT).symlink_to(source)
            check = preflight.verify_synthetic_workspace(repo, fixture)
            self.assertEqual(check.status, preflight.FAIL)
            self.assertIn("symlink", check.observed)

    def test_symlinked_output_fails(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as fixture_temp:
            repo = Path(repo_temp)
            self.make_repo(repo)
            fixture = Path(fixture_temp) / "synthetic"
            self.prepare_verified_fixture(repo, fixture)
            source = Path(fixture_temp) / "output-source.txt"
            source.write_text(
                hashlib.sha256(preflight.SYNTHETIC_CONTENT.encode("utf-8")).hexdigest() + "\n",
                encoding="utf-8",
            )
            (fixture / preflight.SYNTHETIC_OUTPUT).unlink()
            (fixture / preflight.SYNTHETIC_OUTPUT).symlink_to(source)
            check = preflight.verify_synthetic_workspace(repo, fixture)
            self.assertEqual(check.status, preflight.FAIL)
            self.assertIn("symlink", check.observed)

    def test_missing_output_fails(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as fixture_temp:
            repo = Path(repo_temp)
            self.make_repo(repo)
            fixture = Path(fixture_temp) / "synthetic"
            prepared = preflight.prepare_synthetic_workspace(repo, fixture)
            self.assertEqual(prepared.status, preflight.PASS)
            check = preflight.verify_synthetic_workspace(repo, fixture)
            self.assertEqual(check.status, preflight.FAIL)
            self.assertIn("stage2a-output.sha256", check.observed)

    def test_non_empty_preparation_directory_fails(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as fixture_temp:
            repo = Path(repo_temp)
            self.make_repo(repo)
            fixture = Path(fixture_temp) / "synthetic"
            fixture.mkdir()
            (fixture / "existing.txt").write_text("keep me\n", encoding="utf-8")
            check = preflight.prepare_synthetic_workspace(repo, fixture)
            self.assertEqual(check.status, preflight.FAIL)
            self.assertIn("not empty", check.observed)

    def test_hands_on_readiness_stays_false_without_manual_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_repo(root)
            result = preflight.build_result(
                agent="codex",
                acquisition="zip",
                kaapi_mode="skip",
                kaapi_project=None,
                synthetic_action="none",
                synthetic_dir=None,
                repo_root=root,
                runner=self.runner(),
                locator=self.locator("codex"),
            )
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(result.hands_on_ready)
            self.assertEqual(result.readiness_state, "UNRESOLVED_MANUAL_EVIDENCE")

    def test_synthetic_workspace_cannot_be_inside_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            self.make_repo(repo)
            check = preflight.prepare_synthetic_workspace(repo, repo / "scratch")
            self.assertEqual(check.status, preflight.FAIL)


if __name__ == "__main__":
    unittest.main()
