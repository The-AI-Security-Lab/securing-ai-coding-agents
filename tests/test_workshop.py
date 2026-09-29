import contextlib
import io
import json
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


if __name__ == "__main__":
    unittest.main()
