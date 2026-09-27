---
type: overview
status: provisional
updated: 2026-09-27
sources:
  - ../../docs/stage-2e-live-agent-workflow-design.md
  - ../sources/stage-2e-live-agent-experiments.md
  - ../../docs/stage-2d-lab2-verification-harness.md
tags: [workshop, stage-2e, live-agent, verification, provenance]
---

# Stage 2E live coding-agent workflow

Stage 2E is a design-only extension around the accepted Stage 2D Lab 2
verifier. It adds the live sequence—prepare, launch one selected coding agent,
finish/exit, record metadata, independently verify, report, and decide—without
changing the Stage 2D security contract, scope allowlist, or status semantics.

Participants choose Claude Code, Codex, or an instructor-led fallback; both
agents are not required. The agent's task, reasoning, local checks, and
completion claim remain agent-controlled or agent-accessible evidence. The
trusted baseline, verifier-owned cases, evaluator, and final requirement result
remain verifier-controlled. Execution metadata records workflow context but
does not establish observed runtime behavior or a security outcome.

Stage 2E owns validated manual participant launch/configuration procedures for
both Claude Code and Codex. Participants manually launch and use only their
selected agent. Automated or programmatic launch adapters that hide this
interaction remain deferred.

The provisional live observations are version/profile scoped. Claude Code
`2.1.282` exercised the tested filesystem boundary under the recorded
configuration. Codex `0.151.0` showed that approval is not necessarily a hard
verifier boundary and that the tested “never” profile blocked exercised outside
writes but allowed an outside read. A real Codex remediation run passed the
bounded security cases but failed final-state scope because Python created
`app/__pycache__/lookup.cpython-314.pyc`; the artifact must remain a scope
failure, not become an allowlist exception.

The normal path should set bytecode-safe conditions for participant-run Python
checks or avoid agent-run imports, while preserving strict final-state scope
verification. Stronger hidden-test confidentiality, richer independent evidence
sufficient to establish `observed_runtime_behavior` beyond bounded manual
observations, complete runtime telemetry, real AppSec integration, and
production security claims remain unresolved or deferred. For the tested Codex
workflow,
non-disclosure of verifier material is a workshop workflow property, not an
enforced read-confidentiality boundary: the tested `workspace-write + never`
profile blocked exercised outside writes but allowed an outside read. AppSec
evidence may be retained independently with provenance; disagreement
arbitration is future policy, not a Stage 2E capability.

This page is a provisional synthesis, not independent security evidence. The
canonical design and experiment provenance note carry the detailed scope and
limitations.

## Sources and related pages

- [Stage 2E live-agent workflow design](../../docs/stage-2e-live-agent-workflow-design.md)
- [Stage 2E live-agent experiment record](../sources/stage-2e-live-agent-experiments.md)
- [Stage 2D Lab 2 verification harness](stage-2d-lab2-verification-harness.md)
- [Evidence and provenance](evidence-and-provenance.md)
- [Participant pathways](participant-pathways.md)
