---
type: overview
status: current
updated: 2026-09-25
sources:
  - ../../docs/stage-2b-lab-technical-design.md
  - ../../docs/stage-2a.1-kaapi-consumer-validation.md
  - ../../docs/stage-2a-validation-report.md
  - ../sources/repository-source-map.md
tags: [workshop, stage-2b, labs, evidence]
---

# Accepted Stage 2B lab design

The Stage 2B Lab Technical Design is accepted. It remains a design artifact;
Lab 1 and Lab 2 implementation has not started.

The workshop keeps one visible workflow:

`Inspect → Constrain → Run → Observe → Verify → Decide`

## Lab 1

Lab 1 uses **Demonstrate → Choose → Practice**. The design contains six
configuration fixtures: risky, hardened, and malformed for both Claude Code and
Codex. Each participant runs only the three fixtures for their selected agent.
Running all six is optional for participants who have both agents or enough
time. The instructor demonstrates the other vendor where practical, without
requiring participants to install or switch agents. Participants stay on their
selected agent for Lab 2.

The three cases ask different questions:

- risky: can the concerning authority or capability be identified first?
- hardened: does the candidate meet the declared configuration baseline?
- malformed: what can be concluded when evidence cannot be safely assessed?

Kaapi supplies configuration and policy evidence only. A configuration
`PASS` does not establish runtime enforcement or a security outcome. The same
organisational requirement may map differently to Claude Code and Codex.

## Lab 2

Lab 2 remains a bounded write-scope task with a small synthetic
command-injection-style security fix and independent verification. The harness
independently checks both task/write scope and the security outcome.

The four evidence categories remain separate:

1. configured authority;
2. resolved permitted capabilities;
3. observed runtime behaviour; and
4. independently verified runtime outcome.

Participant-facing language is simplified into baseline, task-scope, verified
outcome, evidence present/missing, and a plain-English conclusion. This display
does not collapse the formal evidence categories used by the report and
harness.

The existing statuses remain `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT TESTED`, and
`NOT APPLICABLE`. No additional `ACCEPT`/`REJECT`/`INVESTIGATE` status layer was
adopted.

MCP and GitHub Actions remain instructor-demo or future/advanced candidates,
not part of the main hands-on path. Hard-coded secret exposure and a simple
security-setting fix remain parked scenarios.

## Evidence boundary

This page is a maintained synthesis, not independent security evidence. The
[Stage 2B Lab Technical Design](../../docs/stage-2b-lab-technical-design.md)
is the accepted design source. Stage 2B does not establish a production
security guarantee and does not modify Kaapi.

## Sources and related pages

- [Stage 2B Lab Technical Design](../../docs/stage-2b-lab-technical-design.md)
- [Project overview](project-overview.md)
- [Security verification model](security-verification-model.md)
- [Evidence and provenance](evidence-and-provenance.md)
