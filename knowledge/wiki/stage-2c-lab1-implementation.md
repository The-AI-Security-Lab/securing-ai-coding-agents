---
type: evidence
status: current
updated: 2026-09-25
sources:
  - ../../docs/lab-1-configuration-assessment.md
  - ../../docs/stage-2a.1-kaapi-consumer-validation.md
  - ../../scripts/kaapi_consumer.py
  - ../../scripts/lab1.py
  - ../../tests/test_kaapi_consumer.py
  - ../../tests/test_lab1.py
  - ../sources/repository-source-map.md
tags: [workshop, stage-2c, lab-1, evidence]
---

# Stage 2C Lab 1 implementation

The Stage 2C Lab 1 implementation is present. It provides six synthetic
configuration fixtures—risky, hardened, and malformed for both Claude Code
and Codex—and the Demonstrate → Choose → Practice workflow. Participants use
the three fixtures for their selected agent; comparison with the other vendor
remains optional.

The implementation was exercised through the accepted Stage 2A.1 consumer
boundary and the public Kaapi API at exact P2.1 commit
`9a0bc6ba34576782675aded9e16b718c24fea9bd`. The real results were `FAIL` for
both risky fixtures, `PASS` for both hardened fixtures, and `NOT TESTED` for
both malformed fixtures.

Lab 1 establishes configuration and policy evidence only. It does not
establish runtime enforcement, observed runtime behavior, or an independently
verified security outcome. Lab 2 remains unimplemented.

This page is a maintained provenance summary, not canonical implementation or
independent security evidence.

## Sources and related pages

- [Lab 1 configuration assessment](../../docs/lab-1-configuration-assessment.md)
- [Stage 2A.1 Kaapi consumer validation](../../docs/stage-2a.1-kaapi-consumer-validation.md)
- [Accepted Stage 2B lab design](stage-2b-lab-design.md)
- [Evidence and provenance](evidence-and-provenance.md)
