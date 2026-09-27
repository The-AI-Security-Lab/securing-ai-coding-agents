# Wiki change log

Entries are append-only. Use the format `## [YYYY-MM-DD] operation | subject`
so recent activity can be found with simple text tools.

## [2026-09-25] ingest | Existing workshop documentation

- Created the initial project wiki from `README.md`, `CONTRIBUTING.md`, and
  the validated documents in `docs/`.
- Recorded the distinction between deterministic preflight results and
  hands-on readiness.
- Added source manifests, cross-linked synthesis pages, and the deterministic
  wiki health check.

## [2026-09-25] update | Stage 2A.1 Kaapi consumer validation

- Recorded consumer validation of Kaapi P2.1 commit
  `9a0bc6ba34576782675aded9e16b718c24fea9bd` through the public
  `kaapi.analyze_text(...)` API.
- Preserved the boundary between configuration evidence, runtime behavior, and
  independently verified runtime outcomes.
- Recorded the non-blocking public exception-contract limitation and the fact
  that Stage 2B has not started.

## [2026-09-25] closeout | Accepted Stage 2B lab technical design

- Recorded acceptance of `docs/stage-2b-lab-technical-design.md`.
- Recorded the Demonstrate → Choose → Practice Lab 1 flow, selected-agent
  continuity, the six configuration fixtures, and the Lab 2 bounded-scope plus
  independent-verification design.
- Preserved the four evidence categories and existing status semantics; Lab 1
  and Lab 2 implementation remain deferred.

## [2026-09-25] closeout | Stage 2C Lab 1 implementation

- Recorded the six-fixture Demonstrate → Choose → Practice implementation.
- Recorded real validation through the public Kaapi API at exact P2.1 commit
  `9a0bc6ba34576782675aded9e16b718c24fea9bd`.
- Recorded independent results: risky `FAIL`, hardened `PASS`, and malformed
  `NOT TESTED` for both Claude Code and Codex.
- Preserved the boundary that configuration evidence does not establish
  runtime behavior or an independently verified outcome; Lab 2 remains
  unimplemented.

## [2026-09-26] update | Stage 2D Lab 2 verification harness

- Recorded the standard-library-only synthetic Lab 2 security fixture and
  independent verification harness.
- Recorded final-state scope verification, external golden cases, existing
  status semantics, and the four separate evidence categories.
- Recorded that Stage 2D does not execute an agent or establish complete
  runtime telemetry; Stage 2E remains deferred.

## [2026-09-27] design | Stage 2E live coding-agent workflow

- Added the canonical design for wrapping the accepted Stage 2D verifier with
  one selected live coding-agent pathway and explicit prepare → launch → exit
  → record → verify → report → decide sequencing.
- Preserved the distinction between execution metadata, observed runtime
  behavior, and independently verified outcome evidence.
- Recorded provisional, version-scoped Claude Code and Codex boundary
  observations, including the Codex security-pass/scope-fail `__pycache__`
  example, without weakening the Stage 2D allowlist.
- Added the Stage 2E wiki synthesis and source-map navigation; implementation,
  participant commands, and verifier changes remain deferred.

## [2026-09-27] correction | Stage 2E live coding-agent workflow design

- Clarified that Stage 2E validates manual Claude Code and Codex participant
  launch procedures while automated/programmatic launch adapters remain
  deferred.
- Bounded the tested Codex non-disclosure claim as a workflow property rather
  than enforced read confidentiality.
- Removed AppSec evidence arbitration from Stage 2E and split unresolved items
  into acceptance blockers versus documented limitations/future research.
- Added explicit Claude/Codex normal-path and preserved Codex bytecode-failure
  acceptance cases without changing the Stage 2D allowlist.

## [2026-09-27] correction | Stage 2E runtime-observability requirement

- Removed independent runtime-observability evidence from the Stage 2E
  acceptance blockers.
- Classified richer independent evidence beyond bounded manual observations as
  documented future research; participant observations and agent output remain
  non-comprehensive evidence.
