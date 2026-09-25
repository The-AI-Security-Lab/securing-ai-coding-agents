---
type: overview
status: current
updated: 2026-09-25
sources:
  - ../sources/repository-source-map.md
  - ../../README.md
  - ../../docs/know-before-you-go.md
  - ../../docs/stage-2a.1-kaapi-consumer-validation.md
tags: [workshop, scope, orientation]
---

# Project overview

This repository supports a 90-minute AI Security Lab workshop on governing AI
coding agents and verifying whether security controls work as intended. It
covers Claude Code and Codex without treating them as interchangeable.

The project has two connected labs:

1. **Govern and harden** — identify agent capabilities, permissions, tools,
   execution boundaries, and practical controls.
2. **Verify security controls** — define small security evals, exercise a
   golden dataset, run deterministic checks, and preserve inspectable evidence.

The current repository establishes the Stage 2A technical baseline, the
Stage 2A.1 Kaapi consumer validation, and the accepted Stage 2B lab design.
It does not publish the complete Lab 1 or Lab 2 fixtures, and it does not claim
a production security guarantee.

Stage 2A.1 confirmed that the workshop can consume Kaapi P2.1 configuration
and policy analysis through its public API. It did not establish live agent
enforcement: runtime behavior and independently verified outcomes remain
separate workshop evidence. Stage 2B defines the next lab architecture but does
not implement it.

Participants may choose hands-on Claude Code, hands-on Codex, or an
instructor-led path. Only one agent is required for hands-on participation.

## Sources and related pages

- [Hands-on setup and preflight](../../docs/hands-on-setup.md)
- [Know Before You Go](../../docs/know-before-you-go.md)
- [Participant pathways](participant-pathways.md)
- [Security verification model](security-verification-model.md)
- [Accepted Stage 2B lab design](stage-2b-lab-design.md)
- [Stage 2A.1 Kaapi consumer validation](../../docs/stage-2a.1-kaapi-consumer-validation.md)
