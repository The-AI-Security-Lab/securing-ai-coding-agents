---
type: evidence
status: current
updated: 2026-09-26
sources:
  - ../../docs/stage-2d-lab2-verification-harness.md
  - ../../fixtures/lab2/security-contract.json
  - ../../fixtures/lab2/golden-cases.json
  - ../../fixtures/lab2/additional-cases.json
  - ../../scripts/lab2_harness.py
  - ../../tests/test_lab2_harness.py
  - ../sources/repository-source-map.md
tags: [workshop, stage-2d, lab-2, verification]
---

# Stage 2D Lab 2 verification harness

Stage 2D implements the independent verifier for the accepted Lab 2 design.
It uses a small synthetic lookup application and does not execute Claude Code,
Codex, Kaapi, network services, containers, or third-party dependencies.

The verifier prepares a disposable workspace, records a trusted baseline,
stores bounded metadata, checks final-state file scope, and independently runs
the participant-visible and verifier-owned golden cases. Only `app/lookup.py`
may differ. The visible cases cover the two normal lookups, a synthetic
shell-looking value, empty input, and unknown Unicode input. Additional
deterministic cases remain verifier-owned and outside the participant workspace.

The verifier materializes the canary path into each test input itself; it does
not give the candidate a canary-path environment variable that can select the
observation target. The bounded result concerns expected output and residual
files in the verifier-owned evaluator directory.

The report preserves the four formal evidence categories and the existing
`PASS`, `FAIL`, `INCONCLUSIVE`, `NOT TESTED`, and `NOT APPLICABLE` semantics.
Stage 2D establishes only the defined bounded local security outcome and
final-state filesystem evidence. Missing or corrupt scope baseline evidence
does not erase an independently trustworthy security `PASS` or `FAIL`, but the
overall result remains conservative. It does not establish agent behavior,
complete runtime write-scope enforcement, or complete process, network,
syscall, or kernel telemetry. Stage 2E must protect the verifier checkout,
trusted manifests, baseline, evaluator, and report path from the coding agent.
Stage 2E remains responsible for agent execution and live observation.

This page is a maintained provenance summary, not canonical implementation or
independent security evidence.

## Sources and related pages

- [Stage 2D Lab 2 verification harness](../../docs/stage-2d-lab2-verification-harness.md)
- [Stage 2B lab design](stage-2b-lab-design.md)
- [Evidence and provenance](evidence-and-provenance.md)
- [Readiness and status semantics](readiness-and-status-semantics.md)
