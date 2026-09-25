# Repository agent instructions

## Project knowledge base

This repository maintains a small, source-backed project wiki in
`knowledge/`. Treat it as a compiled view over the repository's canonical
documents and approved external sources.

The layers are:

- `knowledge/sources/` — source manifests and provenance notes. Source
  material is immutable from the wiki workflow; do not rewrite a source to
  make a claim fit.
- `knowledge/wiki/` — maintained synthesis pages. These are agent-owned and
  may be created or revised when new evidence changes the project picture.
- `knowledge/index.md` — content-oriented catalog of every wiki page.
- `knowledge/log.md` — append-only chronological record of ingests, queries,
  and health checks.

The repository's existing `README.md` and `docs/` files remain canonical
project documentation. Wiki pages should summarize and connect them, not
silently replace them. Keep claims about vendor behavior, live validation,
and security outcomes explicitly scoped to their evidence.

## Wiki page conventions

Every page in `knowledge/wiki/` starts with YAML frontmatter:

```yaml
---
type: concept | overview | evidence | pathway | source-summary | source-manifest
status: current | provisional | needs-review
updated: YYYY-MM-DD
sources:
  - ../sources/...
tags: [security, verification]
---
```

Use relative Markdown links so the wiki works in GitHub, a local editor, and
Obsidian. Add a `Sources and related pages` section to every page. Prefer
small pages with one clear subject over a single large summary.

The `sources:` key is required on every Wiki/source page. Its list may be
empty only when the page genuinely contains no source-backed claim. Any
security-relevant, readiness, compatibility, validation, or other
consequential factual claim must preserve enough provenance to trace it to the
canonical repository document, deterministic test evidence, manually recorded
evidence, or an attributed external source that supports it. A Wiki page,
agent-generated summary, or other synthesized knowledge page is not sufficient
primary evidence for such a claim. Use `provisional` or `needs-review` when
the supporting evidence is incomplete; never manufacture a source to satisfy
the format.

## Operating workflows

### Ingest

When the user provides or identifies a new source:

1. Preserve or record the source in `knowledge/sources/` when permitted.
2. Read the source and identify new claims, entities, controls, evidence, and
   contradictions.
3. Update the relevant wiki pages and create a page only when the concept is
   likely to recur.
4. Update `knowledge/index.md` and append one dated entry to `knowledge/log.md`.
5. Run `python3 scripts/wiki_check.py` and report unresolved uncertainty.

Do not treat an agent's prose as independent security evidence. Distinguish
vendor documentation, repository documentation, deterministic local tests,
and manually observed live behavior.

### Query

Read `knowledge/index.md` first, then the smallest set of relevant pages and
their cited sources. Answer with links and evidence scope. If the answer is a
reusable synthesis, comparison, or decision record, offer to file it as a
new wiki page or do so when the user clearly asks.

### Lint

Run the deterministic checker first. Then inspect for stale claims,
contradictions, orphan pages, missing links, and important concepts that have
no page. Use `needs-review` rather than guessing when evidence is incomplete.

## Safety and provenance

Use synthetic data only in examples and fixtures. Never add credentials,
tokens, personal information, customer or employer code, production
configuration, or exploit steps for third-party systems. External sources
must retain attribution and licensing constraints. Do not claim that a
configuration setting enforces a security property without outcome evidence.
