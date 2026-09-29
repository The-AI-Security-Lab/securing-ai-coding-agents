#!/usr/bin/env python3
"""Manage the workshop-owned Kaapi dependency and launch Lab 1 with it."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEPENDENCY_ROOT = REPO_ROOT / ".workshop-deps"
KAAPI_SOURCE = "https://github.com/The-AI-Security-Lab/kaapi.git"
KAAPI_COMMIT = "9a0bc6ba34576782675aded9e16b718c24fea9bd"
KAAPI_VERSION = "1.1.0"
MIN_PYTHON = (3, 11)


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


def cleanup_kaapi() -> KaapiStatus:
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
    shutil.rmtree(kaapi)
    state.unlink()
    return KaapiStatus("REMOVED", "workshop-managed Kaapi state removed", kaapi)


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
    subparsers.add_parser("cleanup", help="remove only verified workshop-managed Kaapi state")
    lab1 = subparsers.add_parser("lab1", help="run Lab 1 with workshop-managed Kaapi")
    lab1.add_argument("--agent", choices=("claude", "codex"), required=True)
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
        status = cleanup_kaapi()
        print(f"Workshop Kaapi: {status.state}")
        print(status.detail)
        return 0 if status.state in {"REMOVED", "NOT_PREPARED"} else 1
    return run_lab1(args.agent, dependency_root)


if __name__ == "__main__":
    raise SystemExit(main())
