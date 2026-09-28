---
type: overview
status: provisional
updated: 2026-09-28
sources:
  - ../../docs/stage-2e-live-agent-workflow-design.md
  - ../sources/stage-2e-live-agent-experiments.md
  - ../sources/stage-2e-claude-2.1.283-acceptance.md
  - ../sources/stage-2e-codex-0.151.0-acceptance.md
  - ../../docs/stage-2d-lab2-verification-harness.md
tags: [workshop, stage-2e, live-agent, verification, provenance]
---

# Stage 2E live coding-agent workflow

Stage 2E is an implementation wrapper around the accepted Stage 2D Lab 2
verifier. It adds the live sequence—prepare, manually launch one selected
coding agent, finish/exit, record metadata, independently verify, report, and
decide—without changing the Stage 2D security contract, scope allowlist, or
status semantics. The repository does not launch either agent.

Participants choose Claude Code, Codex, or an instructor-led fallback; both
agents are not required. The agent's task, reasoning, local checks, and
completion claim remain agent-controlled or agent-accessible evidence. The
trusted baseline, verifier-owned cases, evaluator, and final requirement result
remain verifier-controlled. Execution metadata records workflow context but
does not establish observed runtime behavior or a security outcome.

Stage 2E publishes manual participant launch/configuration procedures for both
Claude Code and Codex. Version-specific live acceptance for Claude Code
`2.1.283` and Codex `0.151.0` is recorded below. Participants
manually launch and use only their selected agent. Automated or programmatic
launch adapters that hide this interaction remain deferred.

The implementation writes a deterministic participant plan and secret-free
configuration for the selected pathway. Its lifecycle gate refuses
to start independent verification while a live invocation is recorded as
active, and its Stage 2E report keeps workflow metadata separate from the
Stage 2D result. An instructor-led fallback is explicitly marked
`INSTRUCTOR_LED_NOT_HANDS_ON`.

The provisional live observations are version/profile scoped. Claude Code
`2.1.282` exercised the tested filesystem boundary under the recorded
configuration. Codex `0.151.0` showed that approval is not necessarily a hard
verifier boundary and that the tested “never” profile blocked exercised outside
writes but allowed an outside read. A real Codex remediation run passed the
bounded security cases but failed final-state scope because Python created
`app/__pycache__/lookup.cpython-314.pyc`; the artifact must remain a scope
failure, not become an allowlist exception.

The accepted Claude Code `2.1.283` remediation run likewise passed the
bounded security cases but failed final-state scope because Claude created
`.claude/` and empty `.claude/.cc-writes/` runtime bookkeeping. Read-only
inspection of the installed runtime provides strong local evidence for that
classification, but classification does not erase detection or change the
strict Stage 2D result. The live evidence therefore teaches the bounded
review sequence **Detect → Explain → Classify → Decide → Fix / Explicitly
Allow**, without implementing a generic classifier or allowlist.

Security and scope are independent outcomes. A scope failure is evidence that
the declared change boundary was not met; it is not by itself evidence that the
security remediation failed. A one-time approval for an application edit is a
decision boundary, not proof that no other filesystem effect occurred.

The accepted Codex `0.151.0` run used the generated isolated `CODEX_HOME`,
strict configuration, `workspace-write`, approval policy `never`, disabled web
search, and `PYTHONDONTWRITEBYTECODE=1`. Codex used `python3 -B` after finding
no `python` executable. Independent verification found all six security cases
`PASS`, scope `PASS`, overall `PASS`, and only `app/lookup.py` changed. This is
specific to the tested version and boundary; it establishes exercised write
integrity, not read confidentiality outside the workspace.

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

Versioned revalidation, lifecycle signals, temporary credential cleanup, and
stronger runtime telemetry remain open concerns. This page is a provisional
synthesis, not independent security evidence. The canonical design, participant guide,
implementation tests, and experiment provenance note carry the detailed scope
and limitations.

## Sources and related pages

- [Stage 2E live-agent workflow design](../../docs/stage-2e-live-agent-workflow-design.md)
- [Stage 2E participant guide](../../docs/lab-2-live-agent-workflow.md)
- [Stage 2E workflow implementation](../../scripts/stage2e_workflow.py)
- [Stage 2E workflow tests](../../tests/test_stage2e_workflow.py)
- [Stage 2E live-agent experiment record](../sources/stage-2e-live-agent-experiments.md)
- [Claude Code 2.1.283 acceptance evidence](../sources/stage-2e-claude-2.1.283-acceptance.md)
- [Codex 0.151.0 acceptance evidence](../sources/stage-2e-codex-0.151.0-acceptance.md)
- [Stage 2D Lab 2 verification harness](stage-2d-lab2-verification-harness.md)
- [Evidence and provenance](evidence-and-provenance.md)
- [Participant pathways](participant-pathways.md)
