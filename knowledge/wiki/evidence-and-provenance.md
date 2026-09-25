---
type: evidence
status: current
updated: 2026-09-25
sources:
  - ../sources/repository-source-map.md
  - ../sources/external-source-map.md
  - ../../docs/stage-2a-validation-report.md
  - ../../docs/stage-2a.1-kaapi-consumer-validation.md
  - ../../scripts/kaapi_consumer.py
  - ../../tests/test_kaapi_consumer.py
  - ../../CONTRIBUTING.md
tags: [evidence, provenance, limitations]
---

# Evidence and provenance

The project uses evidence classes with different scopes. Keeping them
separate prevents a local demonstration from being inflated into a general
security claim.

| Evidence class | Can support | Cannot support by itself |
| --- | --- | --- |
| Vendor documentation | What a vendor documents as supported or configurable. | That the behavior occurred locally or is secure in production. |
| Repository documentation | Project intent, participant instructions, and stated boundaries. | That the instructions were followed or that a control was enforced. |
| Deterministic local tests | Reproducible behavior of the checked code and fixture in the recorded environment. | Provider behavior, agent provenance, or broad deployment security. |
| Manual live observation | What was observed in one bounded session, including approval prompts. | A guarantee that the agent's built-in control would enforce the same result in every context. |
| Independent artifact verification | Whether the expected filesystem result matches the known fixture and constraints. | Who created the artifact or why the action was allowed. |
| Kaapi configuration analysis | Configured authority and resolved permitted capabilities for the tested configuration. | That a live agent followed or enforced the configuration, or that a runtime outcome occurred. |

Every new wiki claim should identify its evidence class and preserve relevant
limitations. Synthetic data is mandatory for examples and fixtures; secrets,
personal data, production code, and third-party exploit instructions do not
belong in this repository.

Stage 2A.1 consumer-tested Kaapi P2.1 at commit
`9a0bc6ba34576782675aded9e16b718c24fea9bd` through the public
`kaapi.analyze_text(...)` API. The consumer validation found no blocking Kaapi
defect. A configuration `PASS` remains configuration evidence only; observed
runtime behavior and independently verified runtime outcomes must be collected
separately by the workshop.

## Sources and related pages

- [Security verification model](security-verification-model.md)
- [Readiness and status semantics](readiness-and-status-semantics.md)
- [Contributing safety and provenance](../../CONTRIBUTING.md)
- [Stage 2A validation report](../../docs/stage-2a-validation-report.md)
- [Stage 2A.1 Kaapi consumer validation](../../docs/stage-2a.1-kaapi-consumer-validation.md)
