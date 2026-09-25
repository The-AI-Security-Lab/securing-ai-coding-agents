"""Deterministic structural health check for the project knowledge base."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"
INDEX = KNOWLEDGE / "index.md"
LOG = KNOWLEDGE / "log.md"
WIKI = KNOWLEDGE / "wiki"
SOURCES = KNOWLEDGE / "sources"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]*)?\)")
SUPPORTED_TYPES = frozenset(
    {"concept", "overview", "evidence", "pathway", "source-summary", "source-manifest"}
)
SUPPORTED_STATUSES = frozenset({"current", "provisional", "needs-review"})


def markdown_files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.rglob("*.md") if path.is_file())


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.relative_to(ROOT)} is missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path.relative_to(ROOT)} has unterminated frontmatter")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if line.startswith(("type:", "status:", "updated:", "sources:")):
            key, value = line.split(":", 1)
            values[key] = value.strip().strip("'\"")
    return values


def check_links(path: Path) -> list[str]:
    failures: list[str] = []
    for target in LINK_RE.findall(path.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.is_file():
            failures.append(
                f"{path.relative_to(ROOT)} links to missing file {target}"
            )
    return failures


def run() -> int:
    failures: list[str] = []
    required = [INDEX, LOG, WIKI, SOURCES]
    failures.extend(
        f"missing required knowledge path: {path.relative_to(ROOT)}"
        for path in required
        if not path.exists()
    )
    if failures:
        print("WIKI CHECK: FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1

    pages = markdown_files(WIKI) + markdown_files(SOURCES)
    for page in pages:
        try:
            metadata = frontmatter(page)
        except (OSError, ValueError) as exc:
            failures.append(str(exc))
            continue
        for key in ("type", "status", "updated", "sources"):
            if key not in metadata:
                failures.append(f"{page.relative_to(ROOT)} is missing frontmatter key {key}:")
        if "type" in metadata and metadata["type"] not in SUPPORTED_TYPES:
            failures.append(
                f"{page.relative_to(ROOT)} has unsupported type {metadata['type']!r}"
            )
        if "status" in metadata and metadata["status"] not in SUPPORTED_STATUSES:
            failures.append(
                f"{page.relative_to(ROOT)} has unsupported status {metadata['status']!r}"
            )
        failures.extend(check_links(page))

    failures.extend(check_links(INDEX))
    failures.extend(check_links(KNOWLEDGE / "README.md"))
    log_lines = LOG.read_text(encoding="utf-8").splitlines()
    entries = [line for line in log_lines if line.startswith("## [")]
    if not entries:
        failures.append("knowledge/log.md has no dated entries")
    elif any(not re.match(r"^## \[\d{4}-\d{2}-\d{2}\] \S+ \| .+", line) for line in entries):
        failures.append("knowledge/log.md contains a malformed dated entry")

    if failures:
        print("WIKI CHECK: FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"WIKI CHECK: PASS ({len(pages)} source/wiki pages, {len(entries)} log entries)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
