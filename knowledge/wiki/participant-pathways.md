---
type: pathway
status: current
updated: 2026-09-29
sources:
  - ../sources/repository-source-map.md
  - ../sources/external-source-map.md
  - ../../docs/hands-on-setup.md
  - ../../docs/know-before-you-go.md
  - ../../docs/participant-guide.md
  - ../sources/kaapi-public-acquisition-validation.md
tags: [participants, Claude-Code, Codex, setup]
---

# Participant pathways

The workshop supports exactly one selected hands-on agent pathway or an
instructor-led path.

| Path | What is required | What the preflight can establish |
| --- | --- | --- |
| Claude Code hands-on | Python 3.11+, Git, `uv`, workshop-managed Kaapi, Claude executable, and separate manual authentication/action review. | Local deterministic checks for the selected executable, required files, and exact managed Kaapi revision/version/API. |
| Codex hands-on | Python 3.11+, Git, `uv`, workshop-managed Kaapi, Codex executable, and separate manual authentication/action review. | Local deterministic checks for the selected executable, required files, and exact managed Kaapi revision/version/API. |
| Instructor-led | No local agent or Python requirement. | The supported participation mode; not hands-on readiness. |

The unselected agent is not a requirement and cannot fail the selected
pathway. Hands-on setup anonymously obtains exact Kaapi commit
`9a0bc6ba34576782675aded9e16b718c24fea9bd` into ignored workshop-managed state
and prepares its locked environment. Preflight fails closed if that checkout,
Kaapi `1.1.0`, or its public API differs; it never substitutes a global Kaapi.
Instructor-led participation may skip this hands-on dependency.

The self-service path runs a concise preflight, one vendor's three Lab 1
fixtures, and one generated Lab 2 pathway through `scripts/workshop.py`. The
wrapper starts the selected agent in the generated workspace, automatically
copies Codex's generated configuration into an isolated workshop-owned home,
remembers the active run, and performs lifecycle bookkeeping before independent
verification. It does not treat process exit or an agent claim as task success.
PowerShell commands are platform-separated and test-covered; primary
end-to-end live validation remains macOS.

Cleanup removes only provenance-verified workshop state: managed Kaapi, the
active Lab 2 run, and any marked isolated Codex home. It refuses paths whose
canonical location, ownership marker, or symlink safety cannot be established,
and never removes normal agent configuration or authentication state.

## Sources and related pages

- [Hands-on setup and preflight](../../docs/hands-on-setup.md)
- [Participant Lab Guide](../../docs/participant-guide.md)
- [Project overview](project-overview.md)
- [Readiness and status semantics](readiness-and-status-semantics.md)
- [Kaapi public acquisition validation](../sources/kaapi-public-acquisition-validation.md)
