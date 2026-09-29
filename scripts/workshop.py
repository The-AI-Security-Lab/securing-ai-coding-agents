#!/usr/bin/env python3
"""Manage the workshop-owned Kaapi dependency and launch Lab 1 with it."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

try:
    from scripts import stage2e_workflow
except ModuleNotFoundError as exc:  # Support direct ``python3 scripts/workshop.py``.
    if exc.name != "scripts":
        raise
    import stage2e_workflow  # type: ignore[no-redef]


REPO_ROOT = Path(__file__).resolve().parents[1]
DEPENDENCY_ROOT = REPO_ROOT / ".workshop-deps"
KAAPI_SOURCE = "https://github.com/The-AI-Security-Lab/kaapi.git"
KAAPI_COMMIT = "9a0bc6ba34576782675aded9e16b718c24fea9bd"
KAAPI_VERSION = "1.1.0"
MIN_PYTHON = (3, 11)
WORKSHOP_STATE_ROOT = REPO_ROOT / ".workshop-state"
ACTIVE_LAB2_STATE = WORKSHOP_STATE_ROOT / "active-lab2.json"
WORKSHOP_STATE_SCHEMA_VERSION = 1


def _canonical_state_path() -> Path:
    repository = REPO_ROOT.absolute()
    home = Path.home().resolve(strict=False)
    filesystem_root = Path(repository.anchor)
    if repository in {filesystem_root, home} or not repository.is_dir() or repository.is_symlink():
        raise ValueError("repository root is not a safe workshop-state boundary")
    state_root = repository / ".workshop-state"
    state_path = state_root / "active-lab2.json"
    if state_root.is_symlink() or state_path.is_symlink():
        raise ValueError("canonical workshop state must not be symlinked")
    resolved_root = state_root.resolve(strict=False)
    if resolved_root != repository.resolve(strict=True) / ".workshop-state":
        raise ValueError("workshop state does not resolve to the canonical repository location")
    return state_path


@dataclass(frozen=True)
class KaapiStatus:
    state: str
    detail: str
    root: Path

    @property
    def ready(self) -> bool:
        return self.state == "READY"


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: float = 180,
) -> tuple[int, str]:
    try:
        result = subprocess.run(
            list(command),
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)
    output = result.stdout.strip() or result.stderr.strip()
    return result.returncode, " ".join(output.splitlines())[:500]


def _managed_python(root: Path) -> Path:
    if os.name == "nt":
        return root / ".venv" / "Scripts" / "python.exe"
    return root / ".venv" / "bin" / "python"


def _safe_managed_paths(dependency_root: Path) -> tuple[Path, Path]:
    root = dependency_root.expanduser().absolute()
    if root.is_symlink():
        raise ValueError(f"managed dependency root must not be a symlink: {root}")
    kaapi = root / "kaapi"
    if kaapi.is_symlink():
        raise ValueError(f"managed Kaapi path must not be a symlink: {kaapi}")
    return root, kaapi


def inspect_kaapi(
    dependency_root: Path = DEPENDENCY_ROOT,
    *,
    runner=_run,
) -> KaapiStatus:
    try:
        root, kaapi = _safe_managed_paths(dependency_root)
    except ValueError as exc:
        return KaapiStatus("UNVERIFIED", str(exc), Path(dependency_root))
    if not kaapi.is_dir():
        return KaapiStatus(
            "NOT_PREPARED",
            "run the workshop setup command to prepare pinned Kaapi",
            kaapi,
        )
    if not (kaapi / ".git").exists():
        return KaapiStatus("UNVERIFIED", "managed Kaapi is not a Git checkout", kaapi)

    code, head = runner(["git", "rev-parse", "HEAD"], cwd=kaapi)
    if code != 0 or head != KAAPI_COMMIT:
        return KaapiStatus(
            "UNVERIFIED",
            f"expected revision {KAAPI_COMMIT}; observed {head or 'unavailable'}",
            kaapi,
        )
    code, source = runner(["git", "remote", "get-url", "origin"], cwd=kaapi)
    if code != 0 or source.rstrip("/") != KAAPI_SOURCE.rstrip("/"):
        return KaapiStatus(
            "UNVERIFIED",
            f"expected canonical source {KAAPI_SOURCE}; observed {source or 'unavailable'}",
            kaapi,
        )
    python = _managed_python(kaapi)
    if not python.is_file():
        return KaapiStatus(
            "NOT_PREPARED",
            "managed Kaapi checkout exists but its locked environment is absent",
            kaapi,
        )
    probe = (
        "from kaapi import __version__, analyze_text; "
        f"assert __version__ == {KAAPI_VERSION!r}; "
        "assert callable(analyze_text); print(__version__)"
    )
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    code, output = runner([str(python), "-B", "-c", probe], cwd=kaapi, env=env)
    if code != 0 or output != KAAPI_VERSION:
        return KaapiStatus(
            "UNVERIFIED",
            f"expected Kaapi {KAAPI_VERSION} public API; probe returned {output or 'no result'}",
            kaapi,
        )
    return KaapiStatus(
        "READY",
        f"Kaapi {KAAPI_VERSION} at exact revision {KAAPI_COMMIT}",
        kaapi,
    )


def setup_kaapi(dependency_root: Path = DEPENDENCY_ROOT) -> KaapiStatus:
    if sys.version_info[:2] < MIN_PYTHON:
        return KaapiStatus(
            "FAILED",
            "Python 3.11 or newer is required before workshop setup can run",
            Path(dependency_root),
        )
    if shutil.which("git") is None:
        return KaapiStatus("FAILED", "Git is required to acquire public Kaapi source", Path(dependency_root))
    if shutil.which("uv") is None:
        return KaapiStatus(
            "FAILED",
            "uv is required but was not found on PATH; install uv through your approved software channel, then rerun setup",
            Path(dependency_root),
        )
    try:
        root, kaapi = _safe_managed_paths(dependency_root)
    except ValueError as exc:
        return KaapiStatus("FAILED", str(exc), Path(dependency_root))
    existing = inspect_kaapi(root)
    if existing.ready:
        return existing
    if kaapi.exists():
        return KaapiStatus(
            "FAILED",
            f"managed Kaapi path already exists but is not ready: {existing.detail}; preserve and inspect it before cleanup",
            kaapi,
        )

    root.mkdir(parents=True, exist_ok=True)
    staging = root / f".kaapi-setup-{uuid.uuid4().hex}"
    env = os.environ.copy()
    env.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ASKPASS": os.devnull,
            "SSH_ASKPASS": os.devnull,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    try:
        code, output = _run(
            ["git", "-c", "credential.helper=", "clone", "--no-checkout", KAAPI_SOURCE, str(staging)],
            cwd=root,
            env=env,
        )
        if code != 0:
            return KaapiStatus("FAILED", f"public Kaapi acquisition failed: {output}", kaapi)
        code, output = _run(["git", "checkout", "--detach", KAAPI_COMMIT], cwd=staging, env=env)
        if code != 0:
            return KaapiStatus("FAILED", f"pinned Kaapi checkout failed: {output}", kaapi)
        code, head = _run(["git", "rev-parse", "HEAD"], cwd=staging, env=env)
        if code != 0 or head != KAAPI_COMMIT:
            return KaapiStatus("FAILED", f"Kaapi revision verification failed: {head}", kaapi)
        code, output = _run(["uv", "sync", "--frozen", "--group", "dev"], cwd=staging, env=env)
        if code != 0:
            return KaapiStatus("FAILED", f"locked Kaapi environment preparation failed: {output}", kaapi)
        staging.rename(kaapi)
        status = inspect_kaapi(root)
        if not status.ready:
            return KaapiStatus("FAILED", f"prepared Kaapi did not pass validation: {status.detail}", kaapi)
        state_path = root / "kaapi-state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "source": KAAPI_SOURCE,
                    "revision": KAAPI_COMMIT,
                    "version": KAAPI_VERSION,
                    "status": "PUBLIC_AND_ACCESSIBLE",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return status
    finally:
        if staging.exists() and not staging.is_symlink():
            shutil.rmtree(staging)


def run_lab1(agent: str, dependency_root: Path = DEPENDENCY_ROOT) -> int:
    status = inspect_kaapi(dependency_root)
    if not status.ready:
        print(f"Workshop Kaapi is not ready: {status.detail}", file=sys.stderr)
        print("Run: python scripts/workshop.py setup", file=sys.stderr)
        return 2
    python = _managed_python(status.root)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(status.root)
    result = subprocess.run(
        [str(python), "-B", str(REPO_ROOT / "scripts" / "lab1.py"), "--agent", agent],
        cwd=REPO_ROOT,
        env=env,
        check=False,
    )
    return result.returncode


def _write_state(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_active_lab2_state() -> dict[str, object]:
    state_path = _canonical_state_path()
    if state_path.is_symlink() or not state_path.is_file():
        raise ValueError("no active Lab 2 run is recorded; run workshop.py lab2 --agent first")
    try:
        value = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"active Lab 2 state is unreadable: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != WORKSHOP_STATE_SCHEMA_VERSION:
        raise ValueError("active Lab 2 state is invalid; run cleanup and prepare a new Lab 2 run")
    if value.get("context") != "participant-self-service":
        raise ValueError("active Lab 2 state has an unexpected context")
    if value.get("repository") != str(REPO_ROOT.resolve()):
        raise ValueError("active Lab 2 state belongs to a different workshop checkout")
    return value


def _owned_directory(path: Path, *, label: str) -> Path:
    path = path.expanduser().absolute()
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"{label} is missing or symlinked: {path}")
    return path


def _validate_owned_lab2_state(state: dict[str, object]) -> tuple[Path, Path | None]:
    run_value = state.get("run_dir")
    if not isinstance(run_value, str):
        raise ValueError("active Lab 2 state has no run directory")
    run_dir = _owned_directory(Path(run_value), label="Lab 2 run directory")
    workflow = stage2e_workflow._load_workflow(run_dir)
    if workflow.get("context") != stage2e_workflow.WORKFLOW_CONTEXT:
        raise ValueError(f"Lab 2 run has unexpected workflow context: {run_dir}")
    if workflow.get("pathway") != state.get("pathway"):
        raise ValueError(f"Lab 2 run pathway does not match active state: {run_dir}")
    if workflow.get("workspace") != str(run_dir / "workspace"):
        raise ValueError(f"Lab 2 workspace identity is invalid: {run_dir}")
    _owned_directory(run_dir / "workspace", label="Lab 2 workspace")
    codex_value = state.get("codex_home")
    if codex_value is None:
        return run_dir, None
    if not isinstance(codex_value, str):
        raise ValueError("active Codex home path is invalid")
    codex_home = _owned_directory(Path(codex_value), label="isolated Codex home")
    marker = codex_home / stage2e_workflow.CODEX_HOME_MARKER
    if marker.is_symlink() or not marker.is_file():
        raise ValueError(f"isolated Codex home has no ownership marker: {codex_home}")
    try:
        marker_value = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"isolated Codex home marker is invalid: {exc}") from exc
    expected = {
        "schema_version": 1,
        "context": "participant-self-service",
        "repository": str(stage2e_workflow.ROOT.resolve()),
        "run_dir": str(run_dir.resolve()),
        "purpose": "isolated workshop Codex configuration",
    }
    if marker_value != expected:
        raise ValueError(f"isolated Codex home ownership could not be established: {codex_home}")
    return run_dir, codex_home


def prepare_lab2(agent: str, *, verbose: bool = False) -> dict[str, object]:
    """Prepare one owned Lab 2 run and remember it without exposing its ID."""

    state_path = _canonical_state_path()
    if state_path.exists() or state_path.is_symlink():
        try:
            _load_active_lab2_state()
        except ValueError as exc:
            raise ValueError(
                f"an active Lab 2 state is present but unsafe: {exc}; run cleanup --verbose to inspect it"
            ) from exc
        raise ValueError("a Lab 2 run is already active; exit it, verify it, or run cleanup")
    run_dir = stage2e_workflow.new_run_dir()
    prepared = stage2e_workflow.prepare_workflow(run_dir, agent)
    plan = prepared["participant_plan"]
    state = {
        "schema_version": WORKSHOP_STATE_SCHEMA_VERSION,
        "context": "participant-self-service",
        "repository": str(REPO_ROOT.resolve()),
        "run_dir": prepared["run_dir"],
        "workspace": prepared["workspace"],
        "pathway": agent,
        "codex_home": plan.get("codex_home"),
    }
    _write_state(state_path, state)
    return prepared


def start_lab2(agent: str, *, verbose: bool = False) -> int:
    prepared = prepare_lab2(agent, verbose=verbose)
    print(stage2e_workflow.render_prepare_summary(prepared, verbose=verbose))
    print("\nTask to give the selected agent:\n")
    print(prepared["participant_plan"]["task"])
    print("\nStarting the selected coding agent. Read the task, complete it, then exit the agent.")
    metadata = stage2e_workflow.launch_workflow(Path(prepared["run_dir"]))
    if metadata.get("exit_state") == "exited":
        print("\nThe agent process exited; task success is not established by exit alone.")
        print("Next action: run the independent verification command shown below.")
        print("  " + _participant_command("lab2 verify", verbose=verbose))
        return 0
    print(
        "\nThe selected agent could not complete a recorded lifecycle exit. "
        "Review the message, then use cleanup or retry after resolving it.",
        file=sys.stderr,
    )
    return 1


def verify_lab2(*, verbose: bool = False, evidence: bool = False) -> int:
    state = _load_active_lab2_state()
    run_dir, _ = _validate_owned_lab2_state(state)
    metadata = stage2e_workflow._load_workflow(run_dir)
    if metadata.get("exit_state") != "exited":
        raise ValueError(
            "Lab 2 verification is not available until the selected agent process has exited; "
            "if it is still running, exit it first"
        )
    result = stage2e_workflow.verify_workflow(run_dir)
    if evidence:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(stage2e_workflow.render_participant_report(result))
        if verbose:
            print(f"\nDetailed evidence: {run_dir / stage2e_workflow.STAGE2E_RESULT_PATH}")
    return 0 if result.get("overall") == stage2e_workflow.lab2_harness.PASS else 1


def _participant_command(value: str, *, verbose: bool = False) -> str:
    python = "python" if os.name == "nt" else "python3"
    return f"{python} scripts/workshop.py {value}"


def _canonical_cleanup_paths() -> tuple[Path, Path, Path]:
    """Return the one cleanup boundary authorized for this repository."""

    repository = REPO_ROOT.absolute()
    home = Path.home().resolve(strict=False)
    filesystem_root = Path(repository.anchor)
    if repository in {filesystem_root, home}:
        raise ValueError("repository root is not a safe cleanup boundary")
    if not repository.is_dir() or repository.is_symlink():
        raise ValueError("repository root is missing or redirected through a symlink")

    dependency_root = repository / ".workshop-deps"
    kaapi = dependency_root / "kaapi"
    if dependency_root.is_symlink():
        raise ValueError("canonical .workshop-deps must not be a symlink")
    if kaapi.is_symlink():
        raise ValueError("canonical managed Kaapi target must not be a symlink")

    resolved_repository = repository.resolve(strict=True)
    resolved_dependency_root = dependency_root.resolve(strict=False)
    resolved_kaapi = kaapi.resolve(strict=False)
    expected_dependency_root = resolved_repository / ".workshop-deps"
    expected_kaapi = expected_dependency_root / "kaapi"
    if resolved_dependency_root != expected_dependency_root or resolved_kaapi != expected_kaapi:
        raise ValueError("cleanup target does not resolve to canonical workshop-managed state")
    if resolved_kaapi in {filesystem_root, home, resolved_repository, expected_dependency_root}:
        raise ValueError("cleanup target resolves to a protected boundary")
    if resolved_repository not in resolved_kaapi.parents:
        raise ValueError("cleanup target resolves outside the workshop repository")
    return expected_dependency_root, expected_kaapi, expected_dependency_root / "kaapi-state.json"


def _validate_cleanup_marker(state: Path) -> None:
    if state.is_symlink() or not state.is_file():
        raise ValueError("workshop-managed Kaapi metadata is missing or redirected")
    try:
        value = json.loads(state.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"workshop-managed Kaapi metadata is invalid: {exc}") from exc
    expected = {
        "schema_version": 1,
        "source": KAAPI_SOURCE,
        "revision": KAAPI_COMMIT,
        "version": KAAPI_VERSION,
        "status": "PUBLIC_AND_ACCESSIBLE",
    }
    if value != expected:
        raise ValueError("workshop-managed Kaapi metadata does not match the accepted dependency")


def cleanup_kaapi(*, dry_run: bool = False) -> KaapiStatus:
    """Remove only this repository's verified workshop-managed Kaapi state."""

    try:
        dependency_root, kaapi, state = _canonical_cleanup_paths()
    except (OSError, ValueError) as exc:
        return KaapiStatus("FAILED", f"refusing cleanup: {exc}", REPO_ROOT)
    if not kaapi.exists() and not state.exists():
        return KaapiStatus("NOT_PREPARED", "workshop-managed Kaapi is already absent", kaapi)
    try:
        _validate_cleanup_marker(state)
    except ValueError as exc:
        return KaapiStatus("FAILED", f"refusing cleanup: {exc}", kaapi)
    status = inspect_kaapi(dependency_root)
    if status.state == "NOT_PREPARED" and not status.root.exists():
        return KaapiStatus("NOT_PREPARED", "workshop-managed Kaapi is already absent", status.root)
    if not status.ready:
        return KaapiStatus(
            "FAILED",
            f"refusing cleanup because managed Kaapi is not verified: {status.detail}",
            status.root,
        )
    if dry_run:
        return KaapiStatus("DRY_RUN", "would remove verified workshop-managed Kaapi state", kaapi)
    shutil.rmtree(kaapi)
    state.unlink()
    return KaapiStatus("REMOVED", "workshop-managed Kaapi state removed", kaapi)


def cleanup_workshop(*, dry_run: bool = False, verbose: bool = False) -> tuple[int, str]:
    """Safely clean exact, provenance-verified state created by the wrapper."""

    lines = ["Workshop Cleanup", ""]
    kaapi = cleanup_kaapi(dry_run=dry_run)
    if kaapi.state == "REMOVED":
        lines.append("✓ Kaapi workshop dependency removed")
    elif kaapi.state == "DRY_RUN":
        lines.append("○ Kaapi workshop dependency would be removed")
    elif kaapi.state == "NOT_PREPARED":
        lines.append("○ Kaapi workshop dependency already absent")
    else:
        lines.append(f"✗ Kaapi workshop dependency not removed: {kaapi.detail}")

    try:
        state_path = _canonical_state_path()
    except ValueError as exc:
        return 1, f"Workshop Cleanup\n\n✗ Cleanup refused: {exc}"
    run_removed = False
    codex_removed = False
    preserved: list[str] = []
    discovered: list[str] = []
    removed: list[str] = []
    not_removed: list[str] = []
    if state_path.exists() or state_path.is_symlink():
        discovered.append(str(state_path))
        try:
            state = _load_active_lab2_state()
            run_dir, codex_home = _validate_owned_lab2_state(state)
            temp_root = Path(tempfile.gettempdir()).resolve()
            if run_dir.parent.resolve() != temp_root or not run_dir.name.startswith("stage2e-"):
                raise ValueError(f"run directory is not the canonical workshop temp location: {run_dir}")
            if codex_home is not None:
                expected_home = run_dir.parent / f".{run_dir.name}-codex-home"
                if codex_home != expected_home:
                    raise ValueError(f"isolated Codex home is not the canonical sibling: {codex_home}")
            targets = [run_dir] + ([codex_home] if codex_home is not None else [])
            discovered.extend(str(path) for path in targets)
            if dry_run:
                run_removed = True
                codex_removed = codex_home is not None
            else:
                for path in targets:
                    shutil.rmtree(path)
                    removed.append(str(path))
                state_path.unlink()
                removed.append(str(state_path))
                run_removed = True
                codex_removed = codex_home is not None
        except (OSError, ValueError) as exc:
            not_removed.extend(discovered)
            lines.append(f"✗ Lab 2 state not removed: {exc}")
            lines.append("  Inspect the exact path manually; no unsafe path was deleted.")
    else:
        lines.append("○ Lab 2 workspace and evidence already absent")

    if run_removed:
        lines.append(
            "✓ Lab 2 workspace and evidence removed"
            if not dry_run
            else "○ Lab 2 workspace and evidence would be removed"
        )
    if codex_removed:
        lines.append(
            "✓ Temporary Codex workshop configuration removed"
            if not dry_run
            else "○ Temporary Codex workshop configuration would be removed"
        )
    lines.extend(
        [
            "",
            "Not touched:",
            "  Your normal Codex configuration",
            "  Your normal Claude configuration",
            "  Authentication/session data",
        ]
    )
    if verbose:
        lines.extend(["", "Cleanup details"])
        lines.append("Discovered paths:")
        lines.extend(f"  {path}" for path in discovered) if discovered else lines.append("  <none>")
        lines.append("Removed paths:")
        lines.extend(f"  {path}" for path in removed) if removed else lines.append("  <none>")
        lines.append("Intentionally preserved paths:")
        lines.extend(f"  {path}" for path in preserved) if preserved else lines.append("  normal agent configuration and authentication state")
        lines.append("Not removed because ownership/safety could not be established:")
        lines.extend(f"  {path}" for path in not_removed) if not_removed else lines.append("  <none>")
    failure = kaapi.state == "FAILED" or bool(not_removed)
    lines.extend(["", f"WORKSHOP CLEANUP: {'INCOMPLETE' if failure else 'DRY RUN' if dry_run else 'COMPLETE'}"])
    return (1 if failure else 0), "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dependency-root",
        type=Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("setup", help="prepare the pinned workshop Kaapi dependency")
    cleanup = subparsers.add_parser(
        "cleanup", help="remove verified workshop-created workshop state"
    )
    cleanup.add_argument("--dry-run", action="store_true", help="show owned paths without removing them")
    cleanup.add_argument("--verbose", action="store_true", help="show exact discovered and preserved paths")
    lab1 = subparsers.add_parser("lab1", help="run Lab 1 with workshop-managed Kaapi")
    lab1.add_argument("--agent", choices=("claude", "codex"), required=True)
    lab2 = subparsers.add_parser("lab2", help="run the participant-facing Lab 2 workflow")
    lab2.add_argument("--agent", choices=("claude", "codex"))
    lab2.add_argument("--verbose", action="store_true", help="show exact generated paths and launch details")
    lab2_subparsers = lab2.add_subparsers(dest="lab2_command")
    lab2_verify = lab2_subparsers.add_parser("verify", help="independently verify the active Lab 2 run")
    lab2_verify.add_argument("--verbose", action="store_true", help="show the exact evidence path")
    lab2_verify.add_argument("--evidence", action="store_true", help="print machine-readable evidence JSON")
    args = parser.parse_args()
    dependency_root = args.dependency_root or DEPENDENCY_ROOT
    if args.command == "setup":
        status = setup_kaapi(dependency_root)
        print(f"Workshop Kaapi: {status.state}")
        print(status.detail)
        return 0 if status.ready else 1
    if args.command == "cleanup":
        if args.dependency_root is not None:
            parser.error("--dependency-root is not permitted with cleanup")
        code, output = cleanup_workshop(dry_run=args.dry_run, verbose=args.verbose)
        print(output)
        return code
    if args.command == "lab2":
        if args.lab2_command == "verify":
            try:
                return verify_lab2(verbose=args.verbose, evidence=args.evidence)
            except (OSError, ValueError) as exc:
                parser.error(str(exc))
        if args.agent is None:
            parser.error("lab2 requires --agent claude or --agent codex")
        return start_lab2(args.agent, verbose=args.verbose)
    return run_lab1(args.agent, dependency_root)


if __name__ == "__main__":
    raise SystemExit(main())
