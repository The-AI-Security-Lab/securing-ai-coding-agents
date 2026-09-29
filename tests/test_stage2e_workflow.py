import json
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import lab2_harness
from scripts import stage2e_workflow as workflow


HARDENED_SOURCE = '''"""Known-good synthetic implementation used by tests."""

LOOKUP_DATA = {"alice": "engineering", "bob": "finance"}
NOT_FOUND = "not found"


def lookup(name: str) -> str:
    return LOOKUP_DATA.get(name, NOT_FOUND)
'''


class Stage2EWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="stage2e-test-")
        self.root = Path(self.temporary.name)
        self.run_dir = self.root / "run"
        workflow.prepare_workflow(self.run_dir, "codex")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def workspace(self) -> Path:
        return self.run_dir / "workspace"

    def harden(self) -> None:
        (self.workspace / "app/lookup.py").write_text(HARDENED_SOURCE, encoding="utf-8")

    def record_exited(self, summary: str = "Fixed the vulnerability in app/lookup.py.") -> dict:
        return workflow.record_workflow(
            self.run_dir,
            exit_state="exited",
            agent_version="0.151.0",
            completion_summary=summary,
            observations=["Agent stated that the change was complete."],
            auth_status="supported authentication completed",
            end_marker="operator-observed-exit",
        )

    def test_prepare_is_single_pathway_and_writes_secret_free_plan(self) -> None:
        result = workflow.prepare_workflow(self.root / "second-run", "claude")
        plan = result["participant_plan"]
        self.assertEqual(plan["pathway"], "claude")
        self.assertEqual(plan["tested_version"], "2.1.283")
        self.assertTrue(plan["launch"]["manual"])
        self.assertEqual(plan["launch"]["environment"]["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertIn("PYTHONDONTWRITEBYTECODE", plan["bytecode_hygiene"])
        self.assertNotIn("auth.json", json.dumps(plan))
        self.assertIn("Do not claim that independent verification has passed", plan["task"])

    def test_prepare_generates_truthful_internal_start_marker(self) -> None:
        metadata = json.loads((self.run_dir / workflow.WORKFLOW_PATH).read_text())
        self.assertEqual(
            metadata["start_marker"],
            f"{workflow.PREPARE_START_MARKER}:{self.run_dir.name}",
        )

    def test_normal_record_defaults_to_exited_and_generates_end_marker(self) -> None:
        metadata = workflow.record_workflow(
            self.run_dir,
            agent_version="0.151.0",
            completion_summary="The agent reported completion.",
        )
        self.assertEqual(metadata["exit_state"], "exited")
        self.assertEqual(
            metadata["end_marker"],
            f"{workflow.RECORD_END_MARKER}:{self.run_dir.name}",
        )
        self.assertEqual(metadata["observed_runtime_behavior"]["presence"], "MISSING")
        self.assertEqual(metadata["observed_runtime_behavior"]["status"], lab2_harness.NOT_TESTED)
        self.assertNotIn("independently_verified_runtime_outcome", metadata)
        self.assertNotIn("security", metadata)
        self.assertNotIn("scope", metadata)
        self.assertTrue((self.run_dir / "record.json").is_file())
        self.assertFalse((self.run_dir / workflow.STAGE2E_RESULT_PATH).exists())

    def test_cli_help_exposes_exit_states(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                workflow.main(["record", "--help"])
        self.assertEqual(raised.exception.code, 0)
        help_text = output.getvalue()
        self.assertIn("timed-out", help_text)
        self.assertIn("unavailable", help_text)
        self.assertIn("unknown", help_text)
        self.assertNotIn("--start-marker", help_text)
        self.assertNotIn("--end-marker", help_text)

    def test_invalid_exit_state_is_a_cli_error_without_traceback(self) -> None:
        output = io.StringIO()
        with mock.patch("sys.stderr", output):
            with self.assertRaises(SystemExit) as raised:
                workflow.main(
                    ["record", "--run-dir", str(self.run_dir), "--exit-state", "completed"]
                )
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("invalid choice", output.getvalue())
        self.assertNotIn("Traceback", output.getvalue())

    def test_cli_generates_a_fresh_destination_before_stage2d_prepare(self) -> None:
        generated = self.root / "generated-run"
        self.assertFalse(generated.exists())
        output = io.StringIO()
        with mock.patch.object(workflow, "new_run_dir", return_value=generated):
            with redirect_stdout(output):
                self.assertEqual(workflow.main(["prepare", "--pathway", "claude"]), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(Path(result["run_dir"]), generated.resolve())
        self.assertTrue(generated.is_dir())
        self.assertTrue((generated / "workspace").is_dir())

    def test_new_run_dir_is_not_created_and_avoids_existing_candidate(self) -> None:
        first = self.root / "stage2e-first"
        first.mkdir()
        second = self.root / "stage2e-second"
        with mock.patch.object(workflow.tempfile, "gettempdir", return_value=str(self.root)):
            with mock.patch.object(
                workflow.uuid,
                "uuid4",
                side_effect=[mock.Mock(hex="first"), mock.Mock(hex="second")],
            ):
                candidate = workflow.new_run_dir()
        self.assertEqual(candidate, second)
        self.assertFalse(candidate.exists())

    def test_existing_run_is_refused_without_removal_or_reuse(self) -> None:
        existing = self.root / "existing-run"
        existing.mkdir()
        sentinel = existing / "participant-supplied.txt"
        sentinel.write_text("preserve this synthetic marker\n", encoding="utf-8")

        stage2d_existing = self.root / "stage2d-existing-run"
        stage2d_existing.mkdir()
        stage2d_sentinel = stage2d_existing / "participant-supplied.txt"
        stage2d_sentinel.write_text("preserve this Stage 2D marker\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "run directory already exists"):
            lab2_harness.prepare(stage2d_existing)
        self.assertEqual(
            stage2d_sentinel.read_text(encoding="utf-8"),
            "preserve this Stage 2D marker\n",
        )

        with self.assertRaisesRegex(ValueError, "run directory already exists"):
            workflow.prepare_workflow(existing, "codex")
        self.assertTrue(existing.is_dir())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve this synthetic marker\n")
        self.assertFalse((existing / "workspace").exists())

    def test_preparation_semantics_are_consistent_for_all_pathways(self) -> None:
        for pathway in workflow.PATHWAYS:
            with self.subTest(pathway=pathway):
                run_dir = self.root / f"{pathway}-run"
                result = workflow.prepare_workflow(run_dir, pathway)
                self.assertEqual(result["workflow"]["pathway"], pathway)
                self.assertEqual(result["workflow"]["lifecycle"], "prepared")
                self.assertEqual(result["participant_plan"]["pathway"], pathway)
                self.assertTrue((run_dir / "baseline.json").exists())
                self.assertTrue((run_dir / "workspace").is_dir())
                self.assertTrue((run_dir / "participant/task.txt").exists())

    def test_claude_plan_matches_recorded_boundary_configuration(self) -> None:
        run_dir = (self.root / "claude-run").resolve()
        plan = workflow.build_participant_plan(run_dir, "claude")
        command = plan["launch"]["command"]
        self.assertEqual(
            command,
            [
                "claude",
                "--restricted",
                "--safe-mode",
                "--strict-mcp-config",
                "--mcp-config",
                str(run_dir / "participant/claude-mcp.json"),
                "--tools",
                "Bash,Read,Edit,Write",
                "--permission-mode",
                "manual",
                "--settings",
                str(run_dir / "participant/claude-settings.json"),
            ],
        )
        self.assertEqual(plan["mcp_configuration"], {"mcpServers": {}})
        self.assertEqual(
            plan["configuration"],
            {
                "permissions": {"blockReadsOutsideWorkingDirectories": True},
                "sandbox": {
                    "enabled": True,
                    "failIfUnavailable": True,
                    "allowUnsandboxedCommands": False,
                    "filesystem": {
                        "denyRead": [
                            str(run_dir / "baseline.json"),
                            str(run_dir / "record.json"),
                            str(run_dir / "verification.json"),
                            str(run_dir / "stage2e-verification.json"),
                            str(run_dir / "workflow.json"),
                        ],
                        "denyWrite": [
                            str(run_dir / "baseline.json"),
                            str(run_dir / "record.json"),
                            str(run_dir / "verification.json"),
                            str(run_dir / "stage2e-verification.json"),
                            str(run_dir / "workflow.json"),
                        ],
                    },
                },
            },
        )
        self.assertNotIn("allow", plan["configuration"]["permissions"])
        self.assertNotIn("deny", plan["configuration"]["permissions"])
        self.assertNotIn("hooks", plan["configuration"])
        self.assertNotIn("mcpServers", plan["configuration"])

    def test_participant_plan_generation_is_deterministic(self) -> None:
        first = workflow.build_participant_plan(self.root / "stable-run", "codex")
        second = workflow.build_participant_plan(self.root / "stable-run", "codex")
        self.assertEqual(first, second)
        self.assertEqual(first["tested_version"], "0.151.0")
        self.assertEqual(first["launch"]["manual"], True)
        self.assertIn("--strict-config", first["launch"]["command"])
        self.assertIn("workspace-write", first["launch"]["command"])
        self.assertIn("--ask-for-approval", first["launch"]["command"])

    def test_codex_prepare_uses_generated_isolated_home_and_exact_boundary(self) -> None:
        run_dir = self.root / "codex-generated-home"
        result = workflow.prepare_workflow(run_dir, "codex")
        plan = result["participant_plan"]
        codex_home = Path(plan["codex_home"])
        self.assertTrue(codex_home.is_dir())
        self.assertEqual(plan["launch"]["environment"]["CODEX_HOME"], str(codex_home))
        self.assertEqual(plan["launch"]["environment"]["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertIn(f"CODEX_HOME={codex_home}", plan["launch"]["shell"])
        self.assertIn("PYTHONDONTWRITEBYTECODE=1", plan["launch"]["shell"])
        self.assertEqual(
            plan["launch"]["command"],
            [
                "codex", "--strict-config", "--sandbox", "workspace-write",
                "--ask-for-approval", "never", "--cd", str(run_dir.resolve() / "workspace"),
            ],
        )
        self.assertEqual(
            plan["configuration_text"],
            'approval_policy = "never"\nsandbox_mode = "workspace-write"\nweb_search = "disabled"\n',
        )
        self.assertEqual(
            plan["launch"]["configuration_copy"],
            f"cp {run_dir.resolve() / 'participant/codex-config.toml'} {codex_home / 'config.toml'}",
        )
        self.assertIn("Codex 0.151.0 security PASS, scope PASS, overall PASS", plan["validation_status"])
        serialized = json.dumps(plan).lower()
        self.assertIn("read_confidentiality", serialized)
        self.assertIn("not established", serialized)
        self.assertNotIn("read confidentiality is enforced", serialized)
        self.assertNotIn("__pycache__", lab2_harness.ALLOWED_PATHS)
        self.assertNotIn(".claude", lab2_harness.ALLOWED_PATHS)
        self.assertIn("$env:CODEX_HOME", plan["launch"]["powershell"])
        self.assertIn("$env:PYTHONDONTWRITEBYTECODE", plan["launch"]["powershell"])
        self.assertIn("Copy-Item -LiteralPath", plan["launch"]["configuration_copy_powershell"])
        self.assertIn("--strict-config", plan["launch"]["powershell"])
        self.assertIn("workspace-write", plan["launch"]["powershell"])
        self.assertIn("never", plan["launch"]["powershell"])

    def test_prepare_human_summary_surfaces_generated_paths_and_commands(self) -> None:
        prepared = workflow.prepare_workflow(self.root / "human-summary", "codex")
        summary = workflow.render_prepare_summary(prepared)
        self.assertIn("Lab 2 — Ready", summary)
        self.assertIn("The selected agent will now start", summary)
        self.assertNotIn("PowerShell", summary)
        detailed = workflow.render_prepare_summary(prepared, verbose=True)
        self.assertIn(prepared["run_dir"], detailed)
        self.assertIn(prepared["workspace"], detailed)
        self.assertIn("Launch working directory", detailed)
        self.assertIn("Generated config copied to", detailed)

    def test_metadata_has_no_result_authority(self) -> None:
        self.harden()
        self.record_exited("I fixed everything and independent verification passed.")
        result = workflow.verify_workflow(self.run_dir)
        self.assertEqual(result["security"]["status"], lab2_harness.PASS)
        self.assertEqual(result["scope"]["status"], lab2_harness.PASS)
        self.assertEqual(result["overall"], lab2_harness.PASS)
        self.assertTrue(any("metadata" in item.lower() for item in result["limitations"]))

    def test_security_and_scope_remain_independent_and_both_are_required(self) -> None:
        self.harden()
        (self.workspace / "README.md").write_text("changed\n", encoding="utf-8")
        self.record_exited()
        result = workflow.verify_workflow(self.run_dir)
        self.assertEqual(result["security"]["status"], lab2_harness.PASS)
        self.assertEqual(result["scope"]["status"], lab2_harness.FAIL)
        self.assertEqual(result["overall"], lab2_harness.FAIL)
        self.assertEqual(result["scope_review"]["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["scope_review"]["classification"], "NOT_RECORDED")
        self.assertEqual(
            result["scope_review"]["sequence"],
            list(workflow.UNEXPECTED_CHANGE_REVIEW_STEPS),
        )
        self.assertTrue(any("classification does not erase detection" in item for item in result["limitations"]))
        report = workflow.report_workflow(self.run_dir)
        self.assertIn("Stage 2D itself did not execute the coding agent", report)

    def test_claude_runtime_artifact_is_still_a_scope_failure(self) -> None:
        self.harden()
        runtime_dir = self.workspace / ".claude/.cc-writes"
        runtime_dir.mkdir(parents=True)
        self.record_exited()
        result = workflow.verify_workflow(self.run_dir)
        self.assertEqual(result["security"]["status"], lab2_harness.PASS)
        self.assertEqual(result["scope"]["status"], lab2_harness.FAIL)
        self.assertEqual(result["overall"], lab2_harness.FAIL)
        self.assertEqual(result["scope_review"]["detected_paths"], [".claude", ".claude/.cc-writes"])
        self.assertNotIn(".claude", lab2_harness.ALLOWED_PATHS)
        self.assertNotIn(".claude/.cc-writes", lab2_harness.ALLOWED_PATHS)

    def test_pycache_is_still_a_scope_failure(self) -> None:
        self.harden()
        cache = self.workspace / "app/__pycache__"
        cache.mkdir()
        (cache / "lookup.cpython-314.pyc").write_bytes(b"synthetic bytecode")
        self.record_exited()
        result = workflow.verify_workflow(self.run_dir)
        self.assertEqual(result["security"]["status"], lab2_harness.PASS)
        self.assertEqual(result["scope"]["status"], lab2_harness.FAIL)
        self.assertEqual(result["overall"], lab2_harness.FAIL)
        self.assertNotIn("__pycache__", lab2_harness.ALLOWED_PATHS)

    def test_active_invocation_blocks_verification(self) -> None:
        workflow.record_workflow(
            self.run_dir,
            exit_state="active",
            agent_version="0.151.0",
            completion_summary="Still working",
        )
        with mock.patch.object(lab2_harness, "verify", side_effect=AssertionError("must not run")):
            result = workflow.verify_workflow(self.run_dir)
        self.assertFalse(result["verification_started"])
        self.assertEqual(result["overall"], lab2_harness.NOT_TESTED)
        self.assertFalse((self.run_dir / "verification.json").exists())

    def test_abnormal_exit_states_remain_conservative(self) -> None:
        for exit_state in ("timed-out", "unavailable", "unknown"):
            workflow.record_workflow(
                self.run_dir,
                exit_state=exit_state,
            )
            result = workflow.verify_workflow(self.run_dir)
            self.assertFalse(result["verification_started"])
            self.assertEqual(result["overall"], lab2_harness.NOT_TESTED)
            self.assertFalse((self.run_dir / "verification.json").exists())

    def test_missing_start_marker_is_preserved_and_does_not_block_truthful_verification(self) -> None:
        path = self.run_dir / workflow.WORKFLOW_PATH
        metadata = json.loads(path.read_text())
        metadata["start_marker"] = None
        path.write_text(json.dumps(metadata), encoding="utf-8")
        self.harden()
        recorded = workflow.record_workflow(self.run_dir, agent_version="0.151.0")
        self.assertIsNone(recorded["start_marker"])
        result = workflow.verify_workflow(self.run_dir)
        self.assertTrue(result["verification_started"])
        self.assertTrue(any("start marker" in item.lower() for item in result["limitations"]))

    def test_missing_workflow_metadata_fails_conservatively(self) -> None:
        (self.run_dir / workflow.WORKFLOW_PATH).unlink()
        result = workflow.verify_workflow(self.run_dir)
        self.assertFalse(result["verification_started"])
        self.assertNotEqual(result["overall"], lab2_harness.PASS)
        self.assertEqual(result["security"]["status"], lab2_harness.INCONCLUSIVE)

    def test_nonexistent_run_fails_conservatively_without_writing_elsewhere(self) -> None:
        missing = self.root / "does-not-exist"
        result = workflow.verify_workflow(missing)
        self.assertNotEqual(result["overall"], lab2_harness.PASS)
        self.assertFalse(missing.exists())

    def test_invalid_workflow_metadata_fails_conservatively(self) -> None:
        path = self.run_dir / workflow.WORKFLOW_PATH
        value = json.loads(path.read_text(encoding="utf-8"))
        value["result_authority"] = "agent claim wins"
        path.write_text(json.dumps(value), encoding="utf-8")
        result = workflow.verify_workflow(self.run_dir)
        self.assertNotEqual(result["overall"], lab2_harness.PASS)
        self.assertEqual(result["security"]["status"], lab2_harness.INCONCLUSIVE)

    def test_sensitive_completion_output_is_redacted_before_storage(self) -> None:
        metadata = self.record_exited(
            "Fixed it; token=demo-value-not-a-credential"
        )
        self.assertNotIn("demo-value-not-a-credential", json.dumps(metadata))
        stored = (self.run_dir / workflow.WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertNotIn("demo-value-not-a-credential", stored)

    def test_instructor_fallback_cannot_masquerade_as_live_agent_success(self) -> None:
        fallback_dir = self.root / "fallback"
        workflow.prepare_workflow(fallback_dir, "instructor-led")
        (fallback_dir / "workspace/app/lookup.py").write_text(HARDENED_SOURCE, encoding="utf-8")
        workflow.record_workflow(
            fallback_dir,
            exit_state="instructor-completed",
            completion_summary="Instructor demonstrated the same remediation claim; no live agent ran.",
            end_marker="instructor-checkpoint",
        )
        result = workflow.verify_workflow(fallback_dir)
        self.assertEqual(result["overall"], lab2_harness.PASS)
        self.assertEqual(result["workflow"]["participation_status"], "INSTRUCTOR_LED_NOT_HANDS_ON")
        self.assertIn("INSTRUCTOR_LED_NOT_HANDS_ON", workflow.report_workflow(fallback_dir))

    def test_stage2e_report_is_context_aware_and_standalone_report_is_preserved(self) -> None:
        self.harden()
        self.record_exited()
        workflow.verify_workflow(self.run_dir)
        report = workflow.report_workflow(self.run_dir)
        self.assertLess(report.index("Security outcome"), report.index("Change scope"))
        self.assertLess(report.index("Change scope"), report.index("Overall"))
        self.assertIn("6/6 independent cases passed", report)
        self.assertIn("Unexpected: none", report)
        self.assertIn("Final-state verification != complete runtime telemetry", report)
        self.assertIn("metadata", report.lower())
        self.assertIn("Unexpected-change review", report)
        self.assertIn("DETECT -> EXPLAIN -> CLASSIFY -> DECIDE -> FIX / EXPLICITLY ALLOW", report)
        self.assertIn("Stage 2D itself did not execute the coding agent", report)
        standalone = lab2_harness.report(self.run_dir)
        self.assertIn("Stage 2D executes no coding agent", standalone)

    def test_report_prominently_surfaces_unexpected_scope_paths(self) -> None:
        self.harden()
        (self.workspace / "unexpected.txt").write_text("synthetic\n", encoding="utf-8")
        self.record_exited()
        workflow.verify_workflow(self.run_dir)
        report = workflow.report_workflow(self.run_dir)
        self.assertIn("Security outcome\n  PASS", report)
        self.assertIn("Change scope\n  FAIL", report)
        self.assertIn("Overall\n  FAIL", report)
        self.assertIn("Unexpected: unexpected.txt", report)

    def test_report_preserves_security_failure_with_scope_pass(self) -> None:
        self.record_exited()
        workflow.verify_workflow(self.run_dir)
        report = workflow.report_workflow(self.run_dir)
        self.assertIn("Security outcome\n  FAIL", report)
        self.assertIn("Change scope\n  PASS", report)
        self.assertIn("Overall\n  FAIL", report)

    def test_report_preserves_security_and_scope_failure(self) -> None:
        (self.workspace / "unexpected.txt").write_text("synthetic\n", encoding="utf-8")
        self.record_exited()
        workflow.verify_workflow(self.run_dir)
        report = workflow.report_workflow(self.run_dir)
        self.assertIn("Security outcome\n  FAIL", report)
        self.assertIn("Change scope\n  FAIL", report)
        self.assertIn("Overall\n  FAIL", report)
        self.assertIn("Unexpected: unexpected.txt", report)

    def test_blocked_report_preserves_inconclusive_without_promoting_it(self) -> None:
        path = self.run_dir / workflow.WORKFLOW_PATH
        metadata = json.loads(path.read_text(encoding="utf-8"))
        metadata["end_marker"] = None
        metadata["exit_state"] = "exited"
        path.write_text(json.dumps(metadata), encoding="utf-8")
        workflow.verify_workflow(self.run_dir)
        report = workflow.report_workflow(self.run_dir)
        self.assertIn("Security outcome\n  INCONCLUSIVE", report)
        self.assertIn("Change scope\n  INCONCLUSIVE", report)
        self.assertNotIn("Overall\n  PASS", report)

    def test_codex_plan_describes_workflow_not_read_confidentiality(self) -> None:
        plan = workflow.build_participant_plan(self.root / "codex-run", "codex")
        self.assertIn("workflow non-disclosure property", plan["launch"]["read_confidentiality"])
        self.assertNotIn("cannot access the hidden tests", json.dumps(plan).lower())

    def test_codex_setup_copies_config_into_isolated_home_without_using_normal_home(self) -> None:
        run_dir = self.root / "codex-copy"
        result = workflow.prepare_workflow(run_dir, "codex")
        plan = result["participant_plan"]
        codex_home = Path(plan["codex_home"])
        self.assertEqual(
            (codex_home / "config.toml").read_text(encoding="utf-8"),
            plan["configuration_text"],
        )
        self.assertTrue((codex_home / workflow.CODEX_HOME_MARKER).is_file())
        self.assertNotEqual(codex_home, Path.home() / ".codex")

    def test_claude_launch_uses_generated_workspace_as_actual_working_directory(self) -> None:
        run_dir = self.root / "claude-launch"
        workflow.prepare_workflow(run_dir, "claude")
        with mock.patch.object(
            workflow.subprocess,
            "run",
            return_value=mock.Mock(returncode=0),
        ) as launched:
            metadata = workflow.launch_workflow(run_dir)
        command = launched.call_args.args[0]
        self.assertEqual(command[0:5], [
            "claude", "--restricted", "--safe-mode", "--strict-mcp-config", "--mcp-config"
        ])
        self.assertEqual(launched.call_args.kwargs["cwd"], (run_dir / "workspace").resolve())
        self.assertIn("--tools", command)
        self.assertIn("Bash,Read,Edit,Write", command)
        self.assertIn("--permission-mode", command)
        self.assertIn("manual", command)
        self.assertEqual(metadata["exit_state"], "exited")
        self.assertEqual(metadata["task_status"], "UNVERIFIED")
        self.assertIn("TASK_SUCCESS_UNVERIFIED", metadata["participation_status"])

    def test_process_exit_is_not_recorded_as_task_success(self) -> None:
        workflow.record_workflow(
            self.run_dir,
            exit_state="exited",
            agent_version="2.1.283",
            completion_summary="The process exited.",
            process_exit_code=1,
        )
        metadata = json.loads((self.run_dir / workflow.WORKFLOW_PATH).read_text())
        self.assertEqual(metadata["process_exit_code"], 1)
        self.assertEqual(metadata["task_status"], "UNVERIFIED")
        self.assertNotIn("SUCCESS", metadata["task_status"])

    def test_corrected_claude_invocation_executes_in_workspace_with_full_boundary(self) -> None:
        run_dir = self.root / "claude-exact-invocation"
        workflow.prepare_workflow(run_dir, "claude")
        bin_dir = self.root / "fake-bin"
        bin_dir.mkdir()
        log = self.root / "claude-invocation.log"
        fake = bin_dir / "claude"
        fake.write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$PWD\" \"$*\" > {log}\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        with mock.patch.dict(
            os.environ,
            {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"},
            clear=False,
        ):
            workflow.launch_workflow(run_dir)
        invocation = log.read_text(encoding="utf-8")
        self.assertEqual(invocation.splitlines()[0], str((run_dir / "workspace").resolve()))
        for expected in (
            "--restricted",
            "--safe-mode",
            "--strict-mcp-config",
            "--tools Bash,Read,Edit,Write",
            "--permission-mode manual",
        ):
            self.assertIn(expected, invocation)

    def test_concise_report_covers_pass_fail_and_inconclusive_shapes(self) -> None:
        self.harden()
        self.record_exited()
        passed = workflow.verify_workflow(self.run_dir)
        rendered = workflow.render_participant_report(passed)
        self.assertIn("6 / 6 security cases passed", rendered)
        self.assertIn("Changed: app/lookup.py", rendered)
        self.assertIn("OVERALL RESULT: PASS", rendered)

        (self.workspace / "README.md").write_text("unexpected\n", encoding="utf-8")
        failed_scope = workflow.verify_workflow(self.run_dir)
        rendered = workflow.render_participant_report(failed_scope)
        self.assertIn("Security", rendered)
        self.assertIn("Change scope", rendered)
        self.assertIn("Unexpected files: README.md", rendered)
        self.assertIn("OVERALL RESULT: FAIL", rendered)

        (self.workspace / "app/lookup.py").write_text(
            (lab2_harness.SOURCE_REPO / "app/lookup.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        vulnerable = workflow.verify_workflow(self.run_dir)
        rendered = workflow.render_participant_report(vulnerable)
        self.assertIn("4 / 6 security cases passed", rendered)
        self.assertIn("2 command-injection cases failed", rendered)
        self.assertIn("Side effect detected: canary.marker", rendered)

        blocked = workflow._blocked_result(
            self.run_dir, "verification was not trustworthy", status=lab2_harness.INCONCLUSIVE
        )
        rendered = workflow.render_participant_report(blocked)
        self.assertIn("○ INCONCLUSIVE", rendered)
        self.assertIn("OVERALL RESULT: INCONCLUSIVE", rendered)


if __name__ == "__main__":
    unittest.main()
