---
type: concept
status: current
updated: 2026-09-25
sources:
  - ../sources/repository-source-map.md
  - ../../docs/know-before-you-go.md
  - ../../docs/hands-on-setup.md
  - ../../docs/stage-2a-validation-report.md
tags: [security, verification, evals]
---

# Security verification model

The project connects governance with verification. A configuration or policy
is a stated control; a repeatable test and independently checked outcome are
evidence about whether a particular property held in a particular environment.

The working model is:

`control statement → security eval → bounded action → independent check → scoped evidence`

The Stage 2A synthetic check uses a known input and expects exactly one output:
the input's SHA-256 digest. The verifier anchors the input to the original
fixture, checks the digest independently, rejects extra files and symlinks,
and reports manual agent provenance or approval observations separately.

This separation matters because an agent's natural-language report is not an
independent security result. Likewise, a passing deterministic preflight says
that required automated checks did not fail; it does not prove authentication,
provider access, approval enforcement, or production safety.

## Sources and related pages

- [Evidence and provenance](evidence-and-provenance.md)
- [Readiness and status semantics](readiness-and-status-semantics.md)
- [Hands-on setup and preflight](../../docs/hands-on-setup.md)
- [Stage 2A validation report](../../docs/stage-2a-validation-report.md)
