#!/usr/bin/env python3
"""Run the deterministic Stage 2A workshop preflight.

The preflight checks local prerequisites and can prepare or independently
verify a bounded synthetic workspace. It intentionally does not start Claude
Code or Codex, inspect credentials, or grant permissions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence


PASS = "PASS"
FAIL = "FAIL"
INCONCLUSIVE = "INCONCLUSIVE"
NOT_TESTED = "NOT TESTED"
NOT_APPLICABLE = "NOT APPLICABLE"
STATUSES = {PASS, FAIL, INCONCLUSIVE, NOT_TESTED, NOT_APPLICABLE}

REPO_ROOT = Path(__file__).resolve().parents[1]
MIN_PYTHON = (3, 11)
SYNTHETIC_INPUT = "stage2a-input.txt"
SYNTHETIC_OUTPUT = "stage2a-output.sha256"
SYNTHETIC_CONTENT = "Stage 2A synthetic input. No real credentials or source code.\n"

CommandRunner = Callable[[Sequence[str], Path], tuple[int, str]]
CommandLocator = Callable[[str], str | None]


@dataclass(frozen=True)
class Check:
    name: str
    category: str
    status: str
    command_or_action: str
    observed: str
    limitations: str

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"Unknown preflight status: {self.status}")


@dataclass(frozen=True)
class PreflightResult:
    checks: list[Check]
    selected_agent: str
    acquisition: str
    kaapi_probe: str
    synthetic_action: str

    @property
    def required_failures(self) -> list[Check]:
        return [check for check in self.checks if check.status == FAIL]

    @property
    def unresolved_checks(self) -> list[Check]:
        return [
            check
            for check in self.checks
            if check.status in {NOT_TESTED, INCONCLUSIVE}
        ]

    @property
    def exit_code(self) -> int:
        """The process gate is deliberately narrower than readiness."""

        return 1 if self.required_failures else 0

    @property
    def automated_gate(self) -> str:
        return "BLOCKED" if self.required_failures else "CLEAR"

    @property
    def readiness_state(self) -> str:
        if self.selected_agent == "none":
            return "INSTRUCTOR_LED_NOT_HANDS_ON"
        if self.required_failures:
            return "BLOCKED_BY_AUTOMATED_FAILURE"
        if self.unresolved_checks:
            return "UNRESOLVED_MANUAL_EVIDENCE"
        return "MANUAL_EVIDENCE_REVIEW_REQUIRED"

    @property
    def hands_on_ready(self) -> bool:
        """Never infer readiness from automated checks alone.

        Manual authentication, agent provenance, and approval evidence must be
        reviewed outside this process. There is deliberately no CLI flag or
        self-attestation path that can turn this value into ``True``.
        """

        return False


def _one_line(value: str) -> str:
    """Keep command output useful without echoing arbitrary multiline data."""

    return " ".join(value.strip().splitlines())[:240]


def _run(
    command: Sequence[str],
    cwd: Path = REPO_ROOT,
    timeout_seconds: float = 10,
) -> tuple[int, str]:
    """Run a bounded command without a shell or environment dump."""

    try:
        result = subprocess.run(
            list(command),
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return 124, f"timed out after {timeout_seconds:g}s: {exc}"
    except OSError as exc:
        return 127, str(exc)
    output = result.stdout.strip() or result.stderr.strip()
    return result.returncode, _one_line(output)


def _command_text(command: Sequence[str]) -> str:
    return " ".join(command)


def _version_check(
    name: str,
    command_name: str,
    category: str,
    *,
    cwd: Path,
    runner: CommandRunner,
    locator: CommandLocator,
    version_args: Sequence[str] = ("--version",),
    missing_status: str = FAIL,
    missing_limitation: str | None = None,
) -> Check:
    command = [command_name, *version_args]
    command_path = locator(command_name)
    if command_path is None:
        return Check(
            name=name,
            category=category,
            status=missing_status,
            command_or_action=_command_text(command),
            observed=f"{command_name!r} was not found on PATH",
            limitations=missing_limitation
            or "The selected command is required for this pathway; install it through an approved channel and rerun the preflight.",
        )

    returncode, output = runner(command, cwd)
    if returncode != 0:
        return Check(
            name=name,
            category=category,
            status=FAIL,
            command_or_action=_command_text(command),
            observed=f"exit {returncode}: {output or 'no version output'}",
            limitations="The executable was found but did not provide a usable version result.",
        )
    return Check(
        name=name,
        category=category,
        status=PASS,
        command_or_action=_command_text(command),
        observed=f"{output} ({command_path})",
        limitations="This verifies executable discovery and version reporting only; it does not verify authentication, permissions, provider access, or agent behavior.",
    )


def _participant_file_check(repo_root: Path) -> Check:
    required_files = ("scripts/preflight.py", "docs/hands-on-setup.md")
    missing = [path for path in required_files if not (repo_root / path).is_file()]
    return Check(
        name="Participant files",
        category="common",
        status=PASS if not missing else FAIL,
        command_or_action="read participant preflight and setup-guide paths",
        observed="all required participant paths are present"
        if not missing
        else f"missing: {', '.join(missing)}",
        limitations="The validation report, README, and GitHub credentials are maintainer/orientation concerns and are not required by this participant check. Event lab files are not checked in Stage 2A.",
    )


def _acquisition_checks(
    repo_root: Path,
    acquisition: str,
    *,
    runner: CommandRunner,
    locator: CommandLocator,
) -> tuple[str, list[Check]]:
    git_root_code, git_root_output = runner(
        ["git", "rev-parse", "--show-toplevel"], repo_root
    )
    is_git_checkout = (
        git_root_code == 0
        and bool(git_root_output)
        and Path(git_root_output).resolve() == repo_root.resolve()
    )
    effective = "git" if acquisition == "auto" and is_git_checkout else acquisition
    if acquisition == "auto" and not is_git_checkout:
        effective = "zip"

    if effective == "zip":
        return effective, [
            Check(
                name="Workshop acquisition",
                category="common",
                status=PASS,
                command_or_action="use the extracted workshop directory; Git metadata is optional",
                observed="ZIP/extracted-directory acquisition supported",
                limitations="The archive must contain the participant files. Git clone history, remotes, and GitHub write access are not checked or required.",
            ),
            Check(
                name="Git executable",
                category="common",
                status=NOT_APPLICABLE,
                command_or_action="git --version",
                observed="not required for ZIP/extracted-directory acquisition",
                limitations="Git may be useful for later lab workflows, but it is not a Stage 2A participant prerequisite on this pathway.",
            ),
        ]

    git_check = _version_check(
        "Git executable",
        "git",
        "common",
        cwd=repo_root,
        runner=runner,
        locator=locator,
    )
    checkout_status = PASS if is_git_checkout else FAIL
    checkout_observed = git_root_output or f"exit {git_root_code}: no repository root returned"
    if acquisition == "git" and git_check.status == FAIL:
        checkout_status = FAIL
    return effective, [
        Check(
            name="Workshop acquisition",
            category="common",
            status=checkout_status,
            command_or_action="git rev-parse --show-toplevel",
            observed=checkout_observed,
            limitations="Git clone acquisition requires a local checkout. This does not validate remote access, GitHub authentication, or push permission.",
        ),
        git_check,
    ]


def common_checks(
    repo_root: Path,
    acquisition: str,
    *,
    python_version: tuple[int, int, int] | None = None,
    runner: CommandRunner = _run,
    locator: CommandLocator = shutil.which,
) -> tuple[str, list[Check]]:
    checks: list[Check] = []
    active_python = python_version or sys.version_info[:3]
    python_text = ".".join(str(part) for part in active_python)
    python_status = PASS if active_python >= MIN_PYTHON else FAIL
    checks.append(
        Check(
            name="Python runtime",
            category="common",
            status=python_status,
            command_or_action="python3 --version",
            observed=f"Python {python_text}; required baseline is >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]}",
            limitations="The preflight uses only the Python standard library. Python 3.11 is the minimum shared baseline for this harness and the inspected Kaapi source; the eventual labs may add dependencies that are not present yet.",
        )
    )
    effective_acquisition, acquisition_checks = _acquisition_checks(
        repo_root, acquisition, runner=runner, locator=locator
    )
    checks.extend(acquisition_checks)
    checks.append(_participant_file_check(repo_root))
    return effective_acquisition, checks


def _safe_synthetic_dir(repo_root: Path, synthetic_dir: Path) -> Path:
    resolved = synthetic_dir.expanduser().resolve()
    root = repo_root.resolve()
    if resolved == root or root in resolved.parents:
        raise ValueError("synthetic directory must not be the workshop checkout or one of its children")
    return resolved


def prepare_synthetic_workspace(repo_root: Path, synthetic_dir: Path) -> Check:
    try:
        target = _safe_synthetic_dir(repo_root, synthetic_dir)
        if target.exists() and not target.is_dir():
            raise ValueError("synthetic path exists and is not a directory")
        if target.exists() and any(target.iterdir()):
            raise ValueError("synthetic directory exists and is not empty")
        target.mkdir(parents=True, exist_ok=True)
        (target / SYNTHETIC_INPUT).write_text(SYNTHETIC_CONTENT, encoding="utf-8")
    except (OSError, ValueError) as exc:
        return Check(
            name="Synthetic workspace preparation",
            category="synthetic",
            status=FAIL,
            command_or_action=f"create disposable directory and write {SYNTHETIC_INPUT}",
            observed=str(exc),
            limitations="No existing non-empty directory is modified. Choose a new empty path outside the workshop checkout and retry.",
        )
    return Check(
        name="Synthetic workspace preparation",
        category="synthetic",
        status=PASS,
        command_or_action=f"create disposable directory and write {SYNTHETIC_INPUT}",
        observed=f"created {target} with one known synthetic input file",
        limitations="Preparation proves only that the local fixture can be created; it does not prove agent authentication or execution.",
    )


def verify_synthetic_workspace(repo_root: Path, synthetic_dir: Path) -> Check:
    try:
        target = _safe_synthetic_dir(repo_root, synthetic_dir)
        if not target.is_dir():
            raise ValueError("synthetic directory does not exist")
        entries = sorted(target.iterdir(), key=lambda entry: entry.name)
        expected_names = sorted((SYNTHETIC_INPUT, SYNTHETIC_OUTPUT))
        if [entry.name for entry in entries] != expected_names:
            raise ValueError(
                f"expected only {expected_names}, found {[entry.name for entry in entries]}"
            )
        if any(entry.is_symlink() or not entry.is_file() for entry in entries):
            raise ValueError("synthetic workspace contains a non-regular or symlink entry")
        input_bytes = (target / SYNTHETIC_INPUT).read_bytes()
        actual = (target / SYNTHETIC_OUTPUT).read_text(encoding="utf-8").strip()
        original_input = SYNTHETIC_CONTENT.encode("utf-8")
        expected = hashlib.sha256(original_input).hexdigest()
        if input_bytes != original_input:
            raise ValueError("input does not match the original known synthetic fixture")
        if actual != expected:
            raise ValueError("output digest does not match the independently computed input digest")
    except (OSError, UnicodeError, ValueError) as exc:
        return Check(
            name="Independent synthetic artifact verification",
            category="synthetic",
            status=FAIL,
            command_or_action=f"hash {SYNTHETIC_INPUT} and compare {SYNTHETIC_OUTPUT}; reject extra files",
            observed=str(exc),
            limitations="This check verifies the artifact and file scope only. It cannot prove which process created the output or that an approval prompt was handled correctly.",
        )
    return Check(
        name="Independent synthetic artifact verification",
        category="synthetic",
        status=PASS,
        command_or_action=f"hash {SYNTHETIC_INPUT} and compare {SYNTHETIC_OUTPUT}; reject extra files",
        observed="output digest matches and workspace contains only the two expected regular files",
        limitations="Artifact success is not proof of authentication, agent provenance, or approval behavior; retain the participant's manual evidence separately.",
    )


def synthetic_checks(
    repo_root: Path,
    agent: str,
    action: str,
    synthetic_dir: Path | None,
) -> list[Check]:
    if agent == "none":
        return [
            Check(
                name="Synthetic agent action",
                category="synthetic",
                status=NOT_APPLICABLE,
                command_or_action="select Claude Code or Codex for a hands-on synthetic action",
                observed="no coding agent selected",
                limitations="Instructor-led participation is not hands-on readiness.",
            )
        ]
    if action == "none":
        return [
            Check(
                name="Synthetic agent action",
                category="synthetic",
                status=NOT_TESTED,
                command_or_action="prepare a disposable fixture, perform the bounded manual action, then rerun with --synthetic verify",
                observed="not attempted by the automated preflight",
                limitations="The preflight never starts an agent, sends a prompt, or changes agent permissions.",
            ),
            Check(
                name="Manual approval review",
                category="synthetic",
                status=NOT_TESTED,
                command_or_action="manual: keep approval prompts enabled and record whether the proposed action was reviewed and approved",
                observed="not attempted by the automated preflight",
                limitations="Approval behavior is interactive and agent-specific; no natural-language response is accepted as proof.",
            ),
        ]
    if synthetic_dir is None:
        raise ValueError("--synthetic-dir is required with --synthetic prepare or verify")

    checks: list[Check] = []
    if action == "prepare":
        checks.append(prepare_synthetic_workspace(repo_root, synthetic_dir))
        checks.append(
            Check(
                name="Synthetic agent action",
                category="synthetic",
                status=NOT_TESTED,
                command_or_action=f"manual: in the fixture, write {SYNTHETIC_OUTPUT} with the SHA-256 digest of {SYNTHETIC_INPUT}",
                observed="fixture prepared; agent action not attempted by the automated preflight",
                limitations="Do not run the agent against the workshop checkout. Keep approval prompts enabled and record the observed tool action separately.",
            )
        )
    else:
        checks.append(
            Check(
                name="Synthetic agent action provenance",
                category="synthetic",
                status=NOT_TESTED,
                command_or_action=f"manual: record selected agent, version, session time, and approved action for {synthetic_dir}",
                observed="not independently attributable from filesystem contents",
                limitations="A matching output file does not prove which process created it or that authentication succeeded.",
            )
        )
        checks.append(verify_synthetic_workspace(repo_root, synthetic_dir))
    checks.append(
        Check(
            name="Manual approval review",
            category="synthetic",
            status=NOT_TESTED,
            command_or_action="manual: record whether the agent proposed the bounded action and whether approval was requested before execution",
            observed="not attempted by the automated preflight",
            limitations="The verifier checks file content and scope only; it does not observe the agent UI or approval event.",
        )
    )
    return checks


def agent_checks(
    agent: str,
    *,
    repo_root: Path,
    runner: CommandRunner,
    locator: CommandLocator,
) -> list[Check]:
    if agent == "none":
        return [
            Check(
                name="Claude Code pathway",
                category="agent-specific",
                status=NOT_APPLICABLE,
                command_or_action="select --agent claude to test this pathway",
                observed="Claude Code was not selected",
                limitations="An unselected agent does not affect the preflight result.",
            ),
            Check(
                name="Codex pathway",
                category="agent-specific",
                status=NOT_APPLICABLE,
                command_or_action="select --agent codex to test this pathway",
                observed="Codex was not selected",
                limitations="An unselected agent does not affect the preflight result.",
            ),
        ]

    selected_name = "Claude Code" if agent == "claude" else "Codex"
    return [
        _version_check(
            f"Selected agent executable ({selected_name})",
            agent,
            "agent-specific",
            cwd=repo_root,
            runner=runner,
            locator=locator,
        ),
        Check(
            name=f"{selected_name} authentication/provider access",
            category="agent-specific",
            status=NOT_TESTED,
            command_or_action=f"manual: authenticate through the approved {selected_name} flow",
            observed="not attempted by the automated preflight",
            limitations="Authentication state may contain sensitive information and provider access varies by account, workspace, and region. Do not paste credentials or tokens into evidence.",
        ),
    ]


def kaapi_check(
    mode: str,
    project: Path | None,
    *,
    cwd: Path,
    runner: CommandRunner,
    locator: CommandLocator,
) -> Check:
    if mode == "skip":
        return Check(
            name="Kaapi CLI availability",
            category="optional",
            status=NOT_APPLICABLE,
            command_or_action="use --kaapi check only for an explicit, approved Kaapi CLI availability probe",
            observed="Kaapi is not a Stage 2A participant prerequisite",
            limitations="Kaapi installation and participant execution requirements are not a validated workshop dependency. This check is non-gating.",
        )

    command: list[str]
    command_path: str | None
    working_directory = cwd
    if project is not None:
        project = project.expanduser().resolve()
        if not project.is_dir() or not (project / "pyproject.toml").is_file():
            return Check(
                name="Kaapi CLI availability",
                category="optional",
                status=INCONCLUSIVE,
                command_or_action=f"uv run --project {project} kaapi version",
                observed="explicit Kaapi project is missing or does not contain pyproject.toml",
                limitations="The optional probe does not install dependencies or modify the Kaapi repository. Use the canonical source and a prepared environment.",
            )
        venv_command = project / ".venv" / "bin" / "kaapi"
        if venv_command.is_file() and venv_command.stat().st_mode & 0o111:
            command = [str(venv_command), "version"]
            command_path = str(venv_command)
        elif locator("uv") is not None:
            command = ["uv", "run", "--project", str(project), "kaapi", "version"]
            command_path = locator("uv")
        else:
            return Check(
                name="Kaapi CLI availability",
                category="optional",
                status=INCONCLUSIVE,
                command_or_action=f"uv run --project {project} kaapi version",
                observed="Kaapi source was found, but neither its prepared .venv nor uv was available",
                limitations="The optional probe does not install dependencies or modify the Kaapi repository; this is not a participant failure.",
            )
        working_directory = project
    else:
        command_path = locator("kaapi")
        command = ["kaapi", "version"]
        if command_path is None:
            return Check(
                name="Kaapi CLI availability",
                category="optional",
                status=INCONCLUSIVE,
                command_or_action="kaapi version",
                observed="Kaapi was not found on PATH",
                limitations="This optional probe cannot establish compatibility without Kaapi installed. The result never causes the preflight to fail.",
            )

    returncode, output = runner(command, working_directory)
    return Check(
        name="Kaapi CLI availability",
        category="optional",
        status=PASS if returncode == 0 else INCONCLUSIVE,
        command_or_action=_command_text(command),
        observed=f"{output or f'exit {returncode}: no version output'} ({command_path})",
        limitations="A version result is not evidence of workshop-lab integration, participant execution requirements, or runtime security outcomes. This check is informational and non-gating.",
    )


def build_result(
    *,
    agent: str,
    acquisition: str,
    kaapi_mode: str,
    kaapi_project: Path | None,
    synthetic_action: str,
    synthetic_dir: Path | None,
    repo_root: Path = REPO_ROOT,
    python_version: tuple[int, int, int] | None = None,
    runner: CommandRunner = _run,
    locator: CommandLocator = shutil.which,
) -> PreflightResult:
    effective_acquisition, checks = common_checks(
        repo_root,
        acquisition,
        python_version=python_version,
        runner=runner,
        locator=locator,
    )
    checks.extend(
        agent_checks(
            agent,
            repo_root=repo_root,
            runner=runner,
            locator=locator,
        )
    )
    checks.extend(synthetic_checks(repo_root, agent, synthetic_action, synthetic_dir))
    checks.append(
        kaapi_check(
            kaapi_mode,
            kaapi_project,
            cwd=repo_root,
            runner=runner,
            locator=locator,
        )
    )
    return PreflightResult(
        checks=checks,
        selected_agent=agent,
        acquisition=effective_acquisition,
        kaapi_probe=kaapi_mode,
        synthetic_action=synthetic_action,
    )


def result_as_dict(result: PreflightResult) -> dict[str, object]:
    return {
        "stage": "2A",
        "selected_agent": result.selected_agent,
        "acquisition": result.acquisition,
        "kaapi_probe": result.kaapi_probe,
        "synthetic_action": result.synthetic_action,
        "environment": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": ".".join(str(part) for part in sys.version_info[:3]),
        },
        "automated_gate": result.automated_gate,
        "exit_code": result.exit_code,
        "readiness": {
            "state": result.readiness_state,
            "hands_on_ready": result.hands_on_ready,
            "explanation": "Exit code 0 means only that no required automated check failed; it is not proof of full workshop readiness. This preflight never marks hands-on readiness true because manual evidence must be reviewed separately.",
        },
        "checks": [asdict(check) for check in result.checks],
    }


def render_text(result: PreflightResult) -> str:
    lines = [
        "Stage 2A local preflight",
        f"Selected agent: {result.selected_agent}",
        f"Acquisition: {result.acquisition}",
        f"Kaapi probe: {result.kaapi_probe}",
        f"Synthetic action: {result.synthetic_action}",
        f"Environment: {platform.system()} {platform.release()} {platform.machine()}",
        "",
    ]
    for check in result.checks:
        lines.extend(
            [
                f"[{check.status}] {check.name} ({check.category})",
                f"  command/action: {check.command_or_action}",
                f"  observed: {check.observed}",
                f"  limitations: {check.limitations}",
            ]
        )
    lines.extend(
        [
            "",
            f"Automated gate: {result.automated_gate}",
            "Readiness: " + result.readiness_state,
            "Hands-on readiness established: " + ("YES" if result.hands_on_ready else "NO"),
            f"Exit code: {result.exit_code} (0 means only that no required automated check failed)",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent",
        choices=("claude", "codex", "none"),
        required=True,
        help="selected participant pathway; use none for instructor-led participation",
    )
    parser.add_argument(
        "--acquisition",
        choices=("auto", "git", "zip"),
        default="auto",
        help="workshop acquisition method; auto supports Git checkouts and extracted ZIPs",
    )
    parser.add_argument(
        "--kaapi",
        choices=("skip", "check"),
        default="skip",
        help="optional informational Kaapi CLI availability probe; it never gates the result",
    )
    parser.add_argument(
        "--kaapi-project",
        type=Path,
        help="explicit local Kaapi source checkout for the optional CLI availability probe",
    )
    parser.add_argument(
        "--synthetic",
        choices=("none", "prepare", "verify"),
        default="none",
        help="prepare or independently verify a bounded disposable synthetic workspace",
    )
    parser.add_argument(
        "--synthetic-dir",
        type=Path,
        help="path outside the workshop checkout for --synthetic prepare/verify",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.kaapi_project is not None and args.kaapi != "check":
        raise SystemExit("--kaapi-project requires --kaapi check")
    if args.synthetic in {"prepare", "verify"} and args.synthetic_dir is None:
        raise SystemExit("--synthetic-dir is required with --synthetic prepare or verify")
    result = build_result(
        agent=args.agent,
        acquisition=args.acquisition,
        kaapi_mode=args.kaapi,
        kaapi_project=args.kaapi_project,
        synthetic_action=args.synthetic,
        synthetic_dir=args.synthetic_dir,
    )
    if args.format == "json":
        print(json.dumps(result_as_dict(result), indent=2, sort_keys=True))
    else:
        print(render_text(result))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
