---
type: source-manifest
status: current
updated: 2026-09-29
sources:
  - ../../README.md
  - ../../CONTRIBUTING.md
  - ../../docs/know-before-you-go.md
  - ../../docs/hands-on-setup.md
  - ../../docs/participant-guide.md
  - ../../docs/stage-2a-validation-report.md
  - ../../docs/stage-2a.1-kaapi-consumer-validation.md
  - ../../scripts/kaapi_consumer.py
  - ../../tests/test_kaapi_consumer.py
  - ../../docs/stage-2b-lab-technical-design.md
  - ../../docs/lab-1-configuration-assessment.md
  - ../../scripts/lab1.py
  - ../../tests/test_lab1.py
  - ../../docs/stage-2d-lab2-verification-harness.md
  - ../../fixtures/lab2/security-contract.json
  - ../../fixtures/lab2/golden-cases.json
  - ../../fixtures/lab2/additional-cases.json
  - ../../fixtures/lab2/repo/app/lookup.py
  - ../../fixtures/lab2/repo/README.md
  - ../../fixtures/lab2/repo/tests/README.md
  - ../../fixtures/lab2/repo/.workshop/protected-sentinel.txt
  - ../../scripts/lab2_harness.py
  - ../../tests/test_lab2_harness.py
  - ../../docs/stage-2e-live-agent-workflow-design.md
  - ../../docs/lab-2-live-agent-workflow.md
  - ../../scripts/stage2e_workflow.py
  - ../../tests/test_stage2e_workflow.py
  - ../../knowledge/sources/stage-2e-live-agent-experiments.md
  - ../../knowledge/sources/stage-2e-claude-2.1.283-acceptance.md
  - ../../knowledge/sources/stage-2e-codex-0.151.0-acceptance.md
  - ../../knowledge/sources/participant-self-service-rehearsal.md
  - ../../knowledge/sources/kaapi-public-acquisition-validation.md
  - ../../scripts/workshop.py
  - ../../tests/test_workshop.py
tags: [provenance, repository]
---

# Repository source map

This manifest identifies the local documents used to compile the initial wiki.
The files listed here remain the source of truth for their respective claims;
wiki pages should link to them and should not silently diverge from them.

| Source | Role in the knowledge base |
| --- | --- |
| [`README.md`](../../README.md) | Public project purpose, workshop structure, and scope. |
| [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | Contribution, safety, provenance, and review expectations. |
| [`docs/know-before-you-go.md`](../../docs/know-before-you-go.md) | Participant learning goals and participation choices. |
| [`docs/hands-on-setup.md`](../../docs/hands-on-setup.md) | Participant setup, safety boundary, preflight, and synthetic workflow. |
| [`docs/participant-guide.md`](../../docs/participant-guide.md) | Canonical self-service Lab 1-to-Lab 2 journey, platform commands, interpretation, troubleshooting, and safe cleanup. |
| [`docs/stage-2a-validation-report.md`](../../docs/stage-2a-validation-report.md) | Engineering evidence, limitations, status vocabulary, and validation scope. |
| [`docs/stage-2a.1-kaapi-consumer-validation.md`](../../docs/stage-2a.1-kaapi-consumer-validation.md) | Exact-commit Kaapi P2.1 consumer evidence, limitations, and closeout result. |
| [`docs/stage-2b-lab-technical-design.md`](../../docs/stage-2b-lab-technical-design.md) | Accepted design for the Lab 1 experience, Lab 2 verification boundary, scenarios, and implementation deferral. |
| [`docs/lab-1-configuration-assessment.md`](../../docs/lab-1-configuration-assessment.md) | Participant-facing Lab 1 workflow, fixture mapping, output boundary, and interpretation. |
| [`fixtures/lab1/policy.json`](../../fixtures/lab1/policy.json) | Shared policy input for the six synthetic Lab 1 configuration fixtures. |
| [`scripts/lab1.py`](../../scripts/lab1.py) | Lab 1 runner using the accepted Kaapi consumer boundary. |
| [`tests/test_lab1.py`](../../tests/test_lab1.py) | Fast Lab 1 contract tests and optional exact-Kaapi integration coverage. |
| [`docs/stage-2d-lab2-verification-harness.md`](../../docs/stage-2d-lab2-verification-harness.md) | Stage 2D security contract, harness lifecycle, status semantics, evidence boundary, and deferred Stage 2E boundary. |
| [`fixtures/lab2/security-contract.json`](../../fixtures/lab2/security-contract.json) | Trusted synthetic Lab 2 application contract, allowed path, protected paths, and status vocabulary. |
| [`fixtures/lab2/golden-cases.json`](../../fixtures/lab2/golden-cases.json) | Independent expected values for normal, shell-looking, empty, and Unicode lookup cases. |
| [`fixtures/lab2/additional-cases.json`](../../fixtures/lab2/additional-cases.json) | Verifier-owned deterministic cases kept outside the participant-visible case set. |
| [`fixtures/lab2/repo/README.md`](../../fixtures/lab2/repo/README.md) | Synthetic Lab 2 application and protected workspace context copied by `prepare`. |
| [`scripts/lab2_harness.py`](../../scripts/lab2_harness.py) | Standard-library-only prepare, record, verify, and report implementation for Stage 2D. |
| [`tests/test_lab2_harness.py`](../../tests/test_lab2_harness.py) | Stage 2D deterministic and adversarial verifier tests. |
| [`docs/stage-2e-live-agent-workflow-design.md`](../../docs/stage-2e-live-agent-workflow-design.md) | Stage 2E live-agent lifecycle, trust boundary, evidence semantics, participant pathways, manual-validation gates, and deferred automation. |
| [`docs/lab-2-live-agent-workflow.md`](../../docs/lab-2-live-agent-workflow.md) | Participant-facing Stage 2E workflow, stop/checkpoint, pathway procedures, fallback, and evidence interpretation. |
| [`scripts/stage2e_workflow.py`](../../scripts/stage2e_workflow.py) | Standard-library-only Stage 2E preparation, bounded metadata, lifecycle gate, contextual report, and manual pathway plan generation. |
| [`tests/test_stage2e_workflow.py`](../../tests/test_stage2e_workflow.py) | Deterministic Stage 2E wrapper, lifecycle, metadata, report, hygiene, fallback, and conservative-failure tests. |
| [`knowledge/sources/stage-2e-live-agent-experiments.md`](stage-2e-live-agent-experiments.md) | Provisional manually supplied live observations for exact Claude Code and Codex versions/profiles, including the Codex scope-failure example. |
| [`knowledge/sources/stage-2e-claude-2.1.283-acceptance.md`](stage-2e-claude-2.1.283-acceptance.md) | Protected Claude Code 2.1.283 acceptance result, strong local runtime-bookkeeping classification evidence, and strict scope-review interpretation. |
| [`knowledge/sources/stage-2e-codex-0.151.0-acceptance.md`](stage-2e-codex-0.151.0-acceptance.md) | Protected Codex 0.151.0 successful acceptance, exact generated boundary, bytecode hygiene, agent claim, and independent result. |
| [`knowledge/sources/participant-self-service-rehearsal.md`](participant-self-service-rehearsal.md) | Sanitized deterministic self-service rehearsal, participant-output coverage, dependency finding, and explicit non-live limitations. |
| [`knowledge/sources/kaapi-public-acquisition-validation.md`](kaapi-public-acquisition-validation.md) | Credential-disabled public exact-commit acquisition, locked environment, and fresh Codex Lab 1 results. |
| [`scripts/workshop.py`](../../scripts/workshop.py) | Pinned workshop-managed Kaapi acquisition, validation, and Lab 1 launcher. |
| [`tests/test_workshop.py`](../../tests/test_workshop.py) | Fail-closed managed-dependency and platform-path tests. |
| [`scripts/preflight.py`](../../scripts/preflight.py) | Executable behavior for deterministic checks and synthetic artifact verification. |
| [`tests/test_preflight.py`](../../tests/test_preflight.py) | Mocked regression coverage for the preflight contract. |
| [`scripts/kaapi_consumer.py`](../../scripts/kaapi_consumer.py) | Minimal workshop-side consumer contract for Kaapi configuration evidence and grading. |
| [`tests/test_kaapi_consumer.py`](../../tests/test_kaapi_consumer.py) | Consumer-contract tests against the exact Kaapi P2.1 candidate. |

## Provenance rule

Local documentation can establish what this repository intends or what its
tests observed. It does not automatically establish current vendor behavior or
security of a production deployment.
