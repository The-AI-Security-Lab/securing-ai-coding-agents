---
type: concept
status: current
updated: 2026-09-25
sources:
  - ../sources/repository-source-map.md
  - ../../docs/hands-on-setup.md
  - ../../docs/stage-2a-validation-report.md
tags: [readiness, preflight, evidence]
---

# Readiness and status semantics

The preflight intentionally separates three outcomes:

| Field | Meaning |
| --- | --- |
| `automated_gate` | Whether a required deterministic check failed (`CLEAR` or `BLOCKED`). |
| `exit_code` | `0` only when no required automated check failed. |
| `readiness.state` and `readiness.hands_on_ready` | Whether the broader hands-on claim has been resolved by reviewed evidence. |

The status vocabulary is equally explicit:

- `PASS` — the stated deterministic check succeeded in the recorded
  environment;
- `FAIL` — a required deterministic check did not succeed;
- `INCONCLUSIVE` — a probe cannot establish the stated property;
- `NOT TESTED` — participant or live behavior remains outstanding; and
- `NOT APPLICABLE` — the check is outside the selected path or optional.

Therefore, exit code `0` is not an overall workshop pass. Without reviewed
manual evidence, the preflight keeps hands-on readiness unresolved. The
instructor-led path is supported participation but is explicitly not
hands-on readiness.

## Sources and related pages

- [Preflight implementation](../../scripts/preflight.py)
- [Stage 2A validation report](../../docs/stage-2a-validation-report.md)
- [Evidence and provenance](evidence-and-provenance.md)
