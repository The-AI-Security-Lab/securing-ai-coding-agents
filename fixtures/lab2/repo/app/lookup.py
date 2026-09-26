"""Synthetic lookup fixture for the Stage 2D verifier.

This initial version intentionally interpolates the lookup value into a local
shell command.  The verifier supplies only synthetic inputs and a disposable
canary directory; it does not require participants to learn an exploit.
"""

from __future__ import annotations

import subprocess


LOOKUP_DATA = {
    "alice": "engineering",
    "bob": "finance",
}
NOT_FOUND = "not found"


def lookup(name: str) -> str:
    """Return the department for a name, or the deterministic not-found value."""

    command = f"printf '%s' '{name}'"
    completed = subprocess.run(
        command,
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )
    return LOOKUP_DATA.get(completed.stdout, NOT_FOUND)
