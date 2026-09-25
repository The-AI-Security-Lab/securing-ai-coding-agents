---
type: source-manifest
status: current
updated: 2026-09-25
sources:
  - ../../README.md
  - ../../CONTRIBUTING.md
  - ../../docs/know-before-you-go.md
  - ../../docs/hands-on-setup.md
  - ../../docs/stage-2a-validation-report.md
tags: [provenance, repository]
---

# Repository source map

This manifest identifies the local documents used to compile the initial wiki.
The files listed here remain the source of truth for their respective claims;
wiki pages should link to them and should not silently diverge from them.

| Source | Role in the knowledge base |
| --- | --- |
| [`README.md`](../../README.md) | Public project purpose, workshop structure, and scope. |
| [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | Contribution, safety, provenance, and review expectations. |
| [`docs/know-before-you-go.md`](../../docs/know-before-you-go.md) | Participant learning goals and participation choices. |
| [`docs/hands-on-setup.md`](../../docs/hands-on-setup.md) | Participant setup, safety boundary, preflight, and synthetic workflow. |
| [`docs/stage-2a-validation-report.md`](../../docs/stage-2a-validation-report.md) | Engineering evidence, limitations, status vocabulary, and validation scope. |
| [`scripts/preflight.py`](../../scripts/preflight.py) | Executable behavior for deterministic checks and synthetic artifact verification. |
| [`tests/test_preflight.py`](../../tests/test_preflight.py) | Mocked regression coverage for the preflight contract. |

## Provenance rule

Local documentation can establish what this repository intends or what its
tests observed. It does not automatically establish current vendor behavior or
security of a production deployment.
