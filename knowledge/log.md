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
