---
type: source-summary
status: current
updated: 2026-09-29
sources:
  - ../../docs/stage-2a.1-kaapi-consumer-validation.md
  - ../../scripts/workshop.py
  - ../../tests/test_workshop.py
tags: [provenance, Kaapi, supply-chain, lab-1, participant-setup]
---

# Kaapi public acquisition validation

With terminal prompting and credential helpers disabled, a fresh temporary Git
repository anonymously fetched exact commit
`9a0bc6ba34576782675aded9e16b718c24fea9bd` from
`https://github.com/The-AI-Security-Lab/kaapi.git` and resolved it as a commit.
The observed acquisition status is `PUBLIC_AND_ACCESSIBLE`.

A separate fresh temporary workshop context, independent of the developer's
existing Kaapi checkout, ran the revision's documented locked setup,
`uv sync --frozen --group dev`. It reported Kaapi `1.1.0`, exposed
`kaapi.analyze_text(...)`, and produced Codex Lab 1 results `FAIL` for risky,
`PASS` for hardened, and `NOT TESTED` for malformed.

The implemented workshop abstraction was then rehearsed against a second fresh
managed dependency directory: `workshop.py setup` reported `READY`, preflight
reported the exact revision/version/API as `PASS`, and `workshop.py lab1`
reproduced the same three Codex fixture results. No live coding agent or agent
authentication was involved.

This validates public acquisition and the tested macOS setup path. It does not
establish permanent availability, equivalent Windows execution, agent runtime
behavior, or independently verified runtime outcomes. The workshop pins the
commit and never trusts a moving branch or arbitrary global Kaapi.

## Sources and related pages

- [Kaapi consumer validation](../../docs/stage-2a.1-kaapi-consumer-validation.md)
- [Workshop dependency manager](../../scripts/workshop.py)
- [Workshop dependency tests](../../tests/test_workshop.py)
- [Participant pathways](../wiki/participant-pathways.md)
