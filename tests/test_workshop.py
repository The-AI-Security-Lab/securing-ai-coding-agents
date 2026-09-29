import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import workshop


class WorkshopDependencyTests(unittest.TestCase):
    def write_managed_marker(self, root: Path) -> Path:
        state = root / ".workshop-deps" / "kaapi-state.json"
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "source": workshop.KAAPI_SOURCE,
                    "revision": workshop.KAAPI_COMMIT,
                    "version": workshop.KAAPI_VERSION,
                    "status": "PUBLIC_AND_ACCESSIBLE",
                }
            ),
            encoding="utf-8",
        )
        return state

    def test_constants_pin_the_accepted_public_revision(self):
        self.assertEqual(
            workshop.KAAPI_SOURCE,
            "https://github.com/The-AI-Security-Lab/kaapi.git",
        )
        self.assertEqual(
            workshop.KAAPI_COMMIT,
            "9a0bc6ba34576782675aded9e16b718c24fea9bd",
        )
        self.assertEqual(workshop.KAAPI_VERSION, "1.1.0")

    def test_missing_managed_dependency_does_not_use_global_kaapi(self):
        with tempfile.TemporaryDirectory() as temporary:
            status = workshop.inspect_kaapi(Path(temporary) / ".workshop-deps")
        self.assertEqual(status.state, "NOT_PREPARED")
        self.assertFalse(status.ready)

    def test_symlinked_dependency_root_is_unverified(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            target = base / "target"
            target.mkdir()
            link = base / "deps"
            link.symlink_to(target, target_is_directory=True)
            status = workshop.inspect_kaapi(link)
        self.assertEqual(status.state, "UNVERIFIED")
        self.assertIn("symlink", status.detail)

    def test_exact_revision_version_and_api_are_required(self):
        with tempfile.TemporaryDirectory() as temporary:
            dependency_root = Path(temporary) / ".workshop-deps"
            kaapi = dependency_root / "kaapi"
            (kaapi / ".git").mkdir(parents=True)
            python = workshop._managed_python(kaapi)
            python.parent.mkdir(parents=True)
            python.write_text("fixture", encoding="utf-8")

            def runner(command, *, cwd, env=None, timeout=180):
                if command[-2:] == ["rev-parse", "HEAD"]:
                    return 0, workshop.KAAPI_COMMIT
                if command[-3:] == ["remote", "get-url", "origin"]:
                    return 0, workshop.KAAPI_SOURCE
                return 0, workshop.KAAPI_VERSION

            status = workshop.inspect_kaapi(dependency_root, runner=runner)
        self.assertTrue(status.ready)

    def test_wrong_revision_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            dependency_root = Path(temporary) / ".workshop-deps"
            kaapi = dependency_root / "kaapi"
            (kaapi / ".git").mkdir(parents=True)

            def runner(command, *, cwd, env=None, timeout=180):
                return 0, "0" * 40

            status = workshop.inspect_kaapi(dependency_root, runner=runner)
        self.assertEqual(status.state, "UNVERIFIED")
        self.assertIn("expected revision", status.detail)

    def test_missing_uv_is_actionable_and_does_not_create_state(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            workshop.shutil, "which", side_effect=lambda name: "/git" if name == "git" else None
        ):
            root = Path(temporary) / ".workshop-deps"
            status = workshop.setup_kaapi(root)
            self.assertFalse(root.exists())
        self.assertEqual(status.state, "FAILED")
        self.assertIn("uv is required", status.detail)

    def test_platform_specific_managed_interpreter_paths(self):
        root = Path("managed")
        with mock.patch.object(workshop.os, "name", "posix"):
            self.assertEqual(workshop._managed_python(root), root / ".venv/bin/python")
        with mock.patch.object(workshop.os, "name", "nt"):
            self.assertEqual(
                workshop._managed_python(root), root / ".venv/Scripts/python.exe"
            )

    def test_cleanup_rejects_filesystem_root(self):
        with mock.patch.object(workshop, "REPO_ROOT", Path("/")):
            status = workshop.cleanup_kaapi()
        self.assertEqual(status.state, "FAILED")
        self.assertIn("safe cleanup boundary", status.detail)

    def test_cleanup_rejects_user_home(self):
        with mock.patch.object(workshop, "REPO_ROOT", Path.home()):
            status = workshop.cleanup_kaapi()
        self.assertEqual(status.state, "FAILED")
        self.assertIn("safe cleanup boundary", status.detail)

    def assert_cleanup_override_rejected(self, value: Path) -> None:
        argv = ["workshop.py", "--dependency-root", str(value), "cleanup"]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
            workshop, "cleanup_kaapi"
        ) as cleanup, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(
            SystemExit
        ) as raised:
            workshop.main()
        self.assertEqual(raised.exception.code, 2)
        cleanup.assert_not_called()

    def test_cleanup_rejects_repository_root_override(self):
        self.assert_cleanup_override_rejected(workshop.REPO_ROOT)

    def test_cleanup_rejects_arbitrary_outside_absolute_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary) / "outside"
            outside.mkdir()
            marker = outside / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            self.assert_cleanup_override_rejected(outside)
            self.assertTrue(marker.exists())

    def test_cleanup_rejects_noncanonical_dependency_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assert_cleanup_override_rejected(Path(temporary) / "deps")

    def test_cleanup_rejects_traversal_override(self):
        self.assert_cleanup_override_rejected(
            workshop.DEPENDENCY_ROOT / ".." / ".." / "outside"
        )

    def test_cleanup_rejects_symlinked_kaapi_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository = base / "repository"
            dependency_root = repository / ".workshop-deps"
            outside = base / "outside-kaapi"
            dependency_root.mkdir(parents=True)
            outside.mkdir()
            marker = outside / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            (dependency_root / "kaapi").symlink_to(outside, target_is_directory=True)
            with mock.patch.object(workshop, "REPO_ROOT", repository):
                status = workshop.cleanup_kaapi()
            self.assertTrue(marker.exists())
        self.assertEqual(status.state, "FAILED")
        self.assertIn("must not be a symlink", status.detail)

    def test_cleanup_rejects_symlinked_dependency_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository = base / "repository"
            repository.mkdir()
            outside = base / "outside-deps"
            (outside / "kaapi").mkdir(parents=True)
            marker = outside / "kaapi" / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            (repository / ".workshop-deps").symlink_to(outside, target_is_directory=True)
            with mock.patch.object(workshop, "REPO_ROOT", repository):
                status = workshop.cleanup_kaapi()
            self.assertTrue(marker.exists())
        self.assertEqual(status.state, "FAILED")
        self.assertIn("must not be a symlink", status.detail)

    def test_cleanup_refuses_unverified_managed_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            root = repository / ".workshop-deps"
            kaapi = root / "kaapi"
            kaapi.mkdir(parents=True)
            self.write_managed_marker(repository)
            marker = kaapi / "preserve.txt"
            marker.write_text("unexpected", encoding="utf-8")
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop,
                "inspect_kaapi",
                return_value=workshop.KaapiStatus("UNVERIFIED", "wrong revision", kaapi),
            ):
                status = workshop.cleanup_kaapi()
            self.assertTrue(marker.exists())
        self.assertEqual(status.state, "FAILED")

    def test_cleanup_reports_absent_without_broadening_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            repository.mkdir()
            with mock.patch.object(workshop, "REPO_ROOT", repository):
                status = workshop.cleanup_kaapi()
            self.assertFalse((repository / ".workshop-deps").exists())
        self.assertEqual(status.state, "NOT_PREPARED")

    def test_cleanup_removes_only_verified_canonical_managed_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository = base / "repository"
            kaapi = repository / ".workshop-deps" / "kaapi"
            kaapi.mkdir(parents=True)
            (kaapi / "managed.txt").write_text("managed", encoding="utf-8")
            state = self.write_managed_marker(repository)
            repository_file = repository / "README.md"
            repository_file.write_text("keep", encoding="utf-8")
            sibling = repository / ".workshop-deps" / "sibling"
            sibling.mkdir()
            (sibling / "keep.txt").write_text("keep", encoding="utf-8")
            external = base / "kaapi"
            external.mkdir()
            (external / "keep.txt").write_text("keep", encoding="utf-8")
            ready = workshop.KaapiStatus("READY", "verified", kaapi)
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop, "inspect_kaapi", return_value=ready
            ):
                status = workshop.cleanup_kaapi()
            self.assertFalse(kaapi.exists())
            self.assertFalse(state.exists())
            self.assertTrue((repository / ".workshop-deps").is_dir())
            self.assertTrue(repository_file.is_file())
            self.assertTrue((sibling / "keep.txt").is_file())
            self.assertTrue((external / "keep.txt").is_file())
        self.assertEqual(status.state, "REMOVED")

    def test_lab2_wrapper_remembers_active_run_and_automatic_codex_setup(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as run_temp:
            repository = Path(repo_temp)
            run_path = Path(run_temp) / "stage2e-wrapper-run"
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop.stage2e_workflow, "new_run_dir", return_value=run_path
            ), mock.patch.object(workshop.tempfile, "gettempdir", return_value=run_temp):
                prepared = workshop.prepare_lab2("codex")
                state = json.loads(
                    (repository / ".workshop-state" / "active-lab2.json").read_text()
                )
            codex_home = Path(prepared["participant_plan"]["codex_home"])
            self.assertEqual(Path(state["run_dir"]), run_path.resolve())
            self.assertEqual(
                (codex_home / "config.toml").read_text(),
                prepared["participant_plan"]["configuration_text"],
            )
            self.assertTrue(codex_home.is_dir())
            shutil.rmtree(run_path)
            shutil.rmtree(codex_home)

    def test_lab1_participant_flags_forward_through_workshop_interface(self):
        ready = workshop.KaapiStatus("READY", "verified", Path("managed-kaapi"))
        with mock.patch.object(workshop, "inspect_kaapi", return_value=ready), mock.patch.object(
            workshop.subprocess, "run", return_value=mock.Mock(returncode=0)
        ) as run:
            for agent in ("claude", "codex"):
                self.assertEqual(workshop.run_lab1(agent, verbose=True), 0)
                command = run.call_args.args[0]
                self.assertEqual(command[-1], "--verbose")
                self.assertNotIn("--format", command)

                self.assertEqual(workshop.run_lab1(agent, evidence=True), 0)
                command = run.call_args.args[0]
                self.assertEqual(command[-2:], ["--format", "evidence"])

    def test_lab1_participant_flags_are_accepted_by_workshop_cli(self):
        with mock.patch.object(workshop, "run_lab1", return_value=0) as run:
            for agent in ("claude", "codex"):
                self.assertEqual(workshop.main(["lab1", "--agent", agent, "--verbose"]), 0)
                run.assert_called_with(
                    agent,
                    workshop.DEPENDENCY_ROOT,
                    verbose=True,
                    evidence=False,
                )
                self.assertEqual(workshop.main(["lab1", "--agent", agent, "--evidence"]), 0)
                run.assert_called_with(
                    agent,
                    workshop.DEPENDENCY_ROOT,
                    verbose=False,
                    evidence=True,
                )

    def test_completed_verified_run_is_retained_and_second_start_is_cleanly_refused(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as run_temp:
            repository = Path(repo_temp)
            run_path = Path(run_temp) / "stage2e-completed-run"
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop.stage2e_workflow, "new_run_dir", return_value=run_path
            ), mock.patch.object(workshop.tempfile, "gettempdir", return_value=run_temp):
                workshop.prepare_lab2("codex")
                (run_path / workshop.stage2e_workflow.STAGE2E_RESULT_PATH).write_text(
                    json.dumps({"context": workshop.stage2e_workflow.WORKFLOW_CONTEXT}),
                    encoding="utf-8",
                )
                error = io.StringIO()
                with mock.patch("sys.stderr", error):
                    code = workshop.main(["lab2", "--agent", "claude"])
            self.assertEqual(code, 2)
            message = error.getvalue()
            self.assertIn("completed Codex run", message)
            self.assertIn("verification evidence is being retained", message)
            self.assertIn("python3 scripts/workshop.py lab2 cleanup", message)
            self.assertIn("python3 scripts/workshop.py lab2 --agent claude", message)
            self.assertNotIn("Traceback", message)
            self.assertTrue(run_path.is_dir())
            shutil.rmtree(run_path)
            shutil.rmtree(run_path.with_name(f".{run_path.name}-codex-home"))

    def test_active_or_incomplete_run_is_cleanly_refused_without_traceback(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as run_temp:
            repository = Path(repo_temp)
            run_path = Path(run_temp) / "stage2e-active-run"
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop.stage2e_workflow, "new_run_dir", return_value=run_path
            ), mock.patch.object(workshop.tempfile, "gettempdir", return_value=run_temp):
                workshop.prepare_lab2("claude")
                error = io.StringIO()
                with mock.patch("sys.stderr", error):
                    code = workshop.main(["lab2", "--agent", "codex"])
            self.assertEqual(code, 2)
            self.assertIn("active or incomplete Claude run", error.getvalue())
            self.assertIn("lab2 cleanup", error.getvalue())
            self.assertNotIn("Traceback", error.getvalue())
            shutil.rmtree(run_path)

    def test_lab2_verify_and_cleanup_no_run_are_human_readable(self):
        with tempfile.TemporaryDirectory() as repository_temp:
            repository = Path(repository_temp)
            error = io.StringIO()
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch(
                "sys.stderr", error
            ):
                verify_code = workshop.main(["lab2", "verify"])
            self.assertEqual(verify_code, 2)
            self.assertIn("no retained Lab 2 run", error.getvalue())
            self.assertNotIn("Traceback", error.getvalue())

            output = io.StringIO()
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch(
                "sys.stdout", output
            ):
                cleanup_code = workshop.main(["lab2", "cleanup"])
            self.assertEqual(cleanup_code, 0)
            self.assertIn("No retained Lab 2 run found", output.getvalue())
            self.assertIn("Nothing was removed", output.getvalue())

    def test_lab2_cleanup_removes_only_verified_lab2_state_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as run_temp:
            repository = Path(repo_temp)
            run_path = Path(run_temp) / "stage2e-cleanup-only-run"
            normal_codex = Path(run_temp) / "normal-codex"
            normal_claude = Path(run_temp) / "normal-claude"
            normal_codex.mkdir()
            normal_claude.mkdir()
            (normal_codex / "auth.json").write_text("preserve", encoding="utf-8")
            (normal_claude / "session.json").write_text("preserve", encoding="utf-8")
            kaapi = repository / ".workshop-deps" / "kaapi"
            kaapi.mkdir(parents=True)
            (kaapi / "keep.txt").write_text("preserve", encoding="utf-8")
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop.stage2e_workflow, "new_run_dir", return_value=run_path
            ), mock.patch.object(workshop.tempfile, "gettempdir", return_value=run_temp):
                prepared = workshop.prepare_lab2("codex")
                codex_home = Path(prepared["participant_plan"]["codex_home"])
                code, output = workshop.cleanup_lab2(verbose=True)
                self.assertEqual(code, 0)
                self.assertIn("Retained Lab 2 run, workspace, and evidence removed", output)
                self.assertIn("Temporary Codex workshop configuration removed", output)
                self.assertFalse(run_path.exists())
                self.assertFalse(codex_home.exists())
                self.assertFalse((repository / ".workshop-state" / "active-lab2.json").exists())
                self.assertTrue((kaapi / "keep.txt").exists())
                self.assertTrue((normal_codex / "auth.json").exists())
                self.assertTrue((normal_claude / "session.json").exists())

                code, repeated = workshop.cleanup_lab2()
                self.assertEqual(code, 0)
                self.assertIn("No retained Lab 2 run found", repeated)

    def test_lab2_cleanup_rejects_symlinked_run_without_touching_target(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as run_temp:
            repository = Path(repo_temp)
            run_path = Path(run_temp) / "stage2e-symlink-cleanup-run"
            outside = Path(run_temp) / "outside"
            outside.mkdir()
            (outside / "keep.txt").write_text("keep", encoding="utf-8")
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop.stage2e_workflow, "new_run_dir", return_value=run_path
            ), mock.patch.object(workshop.tempfile, "gettempdir", return_value=run_temp):
                workshop.prepare_lab2("claude")
                real_run = run_path.with_name("real-run")
                run_path.rename(real_run)
                run_path.symlink_to(real_run, target_is_directory=True)
                code, output = workshop.cleanup_lab2()
            self.assertEqual(code, 1)
            self.assertIn("symlinked", output)
            self.assertTrue((outside / "keep.txt").exists())
            self.assertTrue(real_run.is_dir())
            self.assertTrue((repository / ".workshop-state" / "active-lab2.json").exists())
            shutil.rmtree(real_run)

    def test_lab2_cleanup_rejects_outside_run_and_symlinked_codex_home(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as run_temp:
            repository = Path(repo_temp)
            run_path = Path(run_temp) / "stage2e-unsafe-run"
            outside_run = Path(repo_temp) / "outside-run"
            outside_run.mkdir()
            outside_keep = outside_run / "keep.txt"
            outside_keep.write_text("keep", encoding="utf-8")
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop.stage2e_workflow, "new_run_dir", return_value=run_path
            ), mock.patch.object(workshop.tempfile, "gettempdir", return_value=run_temp):
                workshop.prepare_lab2("codex")
                state_path = repository / ".workshop-state" / "active-lab2.json"
                state = json.loads(state_path.read_text(encoding="utf-8"))
                canonical_run = state["run_dir"]
                state["run_dir"] = str(outside_run)
                workshop._write_state(state_path, state)
                code, output = workshop.cleanup_lab2()
                self.assertEqual(code, 1)
                self.assertIn("canonical directory", output)
                self.assertTrue(outside_keep.exists())
                self.assertTrue(state_path.exists())

                state["run_dir"] = canonical_run
                workshop._write_state(state_path, state)
                codex_home = Path(state["codex_home"])
                real_home = codex_home.with_name("real-codex-home")
                codex_home.rename(real_home)
                codex_home.symlink_to(real_home, target_is_directory=True)
                code, output = workshop.cleanup_lab2()
            self.assertEqual(code, 1)
            self.assertIn("symlinked", output)
            self.assertTrue(outside_keep.exists())
            self.assertTrue(real_home.is_dir())
            self.assertTrue((repository / ".workshop-state" / "active-lab2.json").exists())
            shutil.rmtree(run_path)
            shutil.rmtree(real_home)

    def test_lab2_cleanup_allows_a_new_run_after_reset(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as run_temp:
            repository = Path(repo_temp)
            first = Path(run_temp) / "stage2e-first-reset-run"
            second = Path(run_temp) / "stage2e-second-reset-run"
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop.stage2e_workflow, "new_run_dir", side_effect=[first, second]
            ), mock.patch.object(workshop.tempfile, "gettempdir", return_value=run_temp):
                workshop.prepare_lab2("codex")
                code, _ = workshop.cleanup_lab2()
                self.assertEqual(code, 0)
                prepared = workshop.prepare_lab2("claude")
                self.assertEqual(Path(prepared["run_dir"]), second.resolve())
                code, _ = workshop.cleanup_lab2()
                self.assertEqual(code, 0)

    def test_cleanup_dry_run_and_verbose_are_non_destructive_then_cleanup_is_idempotent(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as run_temp:
            repository = Path(repo_temp)
            run_path = Path(run_temp) / "stage2e-cleanup-run"
            normal_codex = Path(run_temp) / "normal-codex"
            normal_claude = Path(run_temp) / "normal-claude"
            normal_codex.mkdir()
            normal_claude.mkdir()
            (normal_codex / "auth.json").write_text("preserve", encoding="utf-8")
            (normal_claude / "session.json").write_text("preserve", encoding="utf-8")
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop.stage2e_workflow, "new_run_dir", return_value=run_path
            ), mock.patch.object(workshop.tempfile, "gettempdir", return_value=run_temp):
                prepared = workshop.prepare_lab2("codex")
                codex_home = Path(prepared["participant_plan"]["codex_home"])
                code, dry_run = workshop.cleanup_workshop(dry_run=True, verbose=True)
                self.assertEqual(code, 0)
                self.assertIn("would be removed", dry_run)
                self.assertTrue(run_path.is_dir())
                self.assertTrue(codex_home.is_dir())
                code, output = workshop.cleanup_workshop(verbose=True)
                self.assertEqual(code, 0)
                self.assertIn("WORKSHOP CLEANUP: COMPLETE", output)
                self.assertFalse(run_path.exists())
                self.assertFalse(codex_home.exists())
                self.assertTrue((normal_codex / "auth.json").exists())
                self.assertTrue((normal_claude / "session.json").exists())
                code, repeated = workshop.cleanup_workshop()
                self.assertEqual(code, 0)
                self.assertIn("already absent", repeated)

    def test_cleanup_refuses_symlinked_known_lab2_run_without_touching_target(self):
        with tempfile.TemporaryDirectory() as repo_temp, tempfile.TemporaryDirectory() as run_temp:
            repository = Path(repo_temp)
            run_path = Path(run_temp) / "stage2e-symlink-run"
            outside = Path(run_temp) / "outside"
            outside.mkdir()
            keep = outside / "keep.txt"
            keep.write_text("keep", encoding="utf-8")
            with mock.patch.object(workshop, "REPO_ROOT", repository), mock.patch.object(
                workshop.stage2e_workflow, "new_run_dir", return_value=run_path
            ):
                prepared = workshop.prepare_lab2("claude")
                state_path = repository / ".workshop-state" / "active-lab2.json"
                run_path.rename(run_path.with_name("real-run"))
                run_path.symlink_to(run_path.with_name("real-run"), target_is_directory=True)
                code, output = workshop.cleanup_workshop(verbose=True)
            self.assertEqual(code, 1)
            self.assertIn("not removed", output)
            self.assertTrue(keep.exists())
            self.assertTrue(state_path.exists())
            shutil.rmtree(run_path.with_name("real-run"))


if __name__ == "__main__":
    unittest.main()
