---
type: source-summary
status: provisional
updated: 2026-09-28
sources:
  - ../../README.md
  - ../../docs/participant-guide.md
  - ../../scripts/stage2e_workflow.py
  - ../../tests/test_participant_docs.py
  - ../../tests/test_stage2e_workflow.py
tags: [provenance, participant-ux, rehearsal, stage-2e, Codex]
---

# Participant self-service deterministic rehearsal

This sanitized record summarizes the Participant Self-Service rehearsal. The
raw disposable run and empty generated agent home are preserved outside the
repository for implementation review. Their developer-specific temporary
paths, raw transcript, and any authentication material are intentionally not
recorded here.

## Rehearsed journey

The rehearsal followed the README and Participant Lab Guide through:

```text
preflight → choose Codex → Lab 1 dependency check → Lab 2 prepare
→ deterministic allowed remediation → record → verify → human report
```

No live coding agent was launched and no authentication was performed. The
allowed `app/lookup.py` remediation was applied deterministically so the
participant preparation, lifecycle, independent verification, and reporting
surfaces could be exercised without a provider session.

The generated human preparation summary exposed the disposable run,
workspace, task, isolated Codex home, config-copy commands, and macOS and
PowerShell launch commands. The participant-readable verification report was
then exercised.

## Result and evidence boundary

The preserved machine-readable result reported:

```text
Security: PASS (6/6 independent cases)
Scope:    PASS
Overall:  PASS
Changed:  app/lookup.py only
```

No paths were created or unauthorized. Observed runtime behavior remained
`MISSING` / `NOT TESTED`, as required because no live agent ran. Workflow
metadata and the deterministic edit are not represented as live runtime
telemetry or agent evidence.

Preflight found the selected Codex executable and produced a clear automated
gate while retaining unresolved manual authentication evidence. The local
environment did not provide Kaapi's accepted P2.1 public API at that rehearsal
checkpoint, so Lab 1 truthfully returned `NOT TESTED`. Later public acquisition
validation established the workshop-managed setup route recorded separately.

## Cleanup and limitations

Cleanup was intentionally deferred for review. The generated Codex home was
empty and contained no filename-level authentication/session indicator at the
inspection checkpoint. This does not generalize to an authenticated run.

This rehearsal validates deterministic participant workflow and output, not
live Codex behavior, authentication, Windows end-to-end execution, complete
runtime telemetry, or server-side session cleanup. Primary live-agent
acceptance remains the separate version-scoped Stage 2E evidence.

## Sources and related pages

- [Participant Lab Guide](../../docs/participant-guide.md)
- [Stage 2E workflow implementation](../../scripts/stage2e_workflow.py)
- [Participant documentation tests](../../tests/test_participant_docs.py)
- [Stage 2E workflow tests](../../tests/test_stage2e_workflow.py)
- [Codex 0.151.0 live acceptance](stage-2e-codex-0.151.0-acceptance.md)
- [Kaapi public acquisition validation](kaapi-public-acquisition-validation.md)
