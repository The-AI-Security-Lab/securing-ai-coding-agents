---
type: concept
status: current
updated: 2026-09-26
sources:
  - ../sources/repository-source-map.md
  - ../../docs/know-before-you-go.md
  - ../../docs/hands-on-setup.md
  - ../../docs/stage-2a-validation-report.md
  - ../../docs/stage-2a.1-kaapi-consumer-validation.md
  - ../../scripts/kaapi_consumer.py
  - ../../tests/test_kaapi_consumer.py
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

## Kaapi's role in the workshop

Stage 2A.1 consumer-tested Kaapi P2.1 at commit
`9a0bc6ba34576782675aded9e16b718c24fea9bd` through the public
`kaapi.analyze_text(...)` API. Kaapi handles configuration and policy analysis.
It can provide evidence about configured authority and resolved permitted
capabilities.

A Kaapi `PASS` does not show that a live coding agent followed or enforced the
configuration. Observed runtime behavior and independently verified runtime
outcomes are separate evidence categories that the workshop must collect and
evaluate. The workshop-side consumer must keep those categories separate and
must not turn configuration evidence into proof of runtime security.

The validation found no blocking Kaapi defect. It did identify one non-blocking
API limitation: malformed input raises an internal exception type rather than
a stable, documented public exception contract. The Stage 2A.1 adapter handles
that case conservatively as `NOT_TESTED` without importing Kaapi internals.

The adapter and contract tests are candidate workshop infrastructure. Stage 2D
now adds a separate standard-library-only Lab 2 verifier: it checks final-state
scope and a defined local golden security contract without executing an agent.
It does not replace Kaapi configuration evidence or establish agent runtime
behavior. Stage 2E remains the deferred agent-execution boundary.

## Sources and related pages

- [Evidence and provenance](evidence-and-provenance.md)
- [Readiness and status semantics](readiness-and-status-semantics.md)
- [Hands-on setup and preflight](../../docs/hands-on-setup.md)
- [Stage 2A validation report](../../docs/stage-2a-validation-report.md)
- [Stage 2A.1 Kaapi consumer validation](../../docs/stage-2a.1-kaapi-consumer-validation.md)
- [Stage 2D Lab 2 verification harness](../../docs/stage-2d-lab2-verification-harness.md)
