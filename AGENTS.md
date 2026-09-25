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

## Engineering workflow and Git provenance

Before engineering work, inspect the current repository/worktree path, branch,
full `HEAD` SHA, working-tree status, and active worktrees. Every milestone or
task must name its exact accepted base commit and required ancestor milestone
SHAs. **Branch name is not provenance. Verify commit ancestry.**

- If required ancestry is missing, stop and report. Do not silently merge,
  cherry-pick, rebase, reset, or otherwise repair history.
- Use the explicitly assigned feature branch and worktree. Do not create or
  switch branches without authorization. Preserve unrelated dirty/untracked
  files and other worktrees.
- Before implementation, record the accepted base SHA, required ancestor SHAs,
  feature branch, worktree, allowed scope, protected/out-of-scope files or
  areas, required validation, and whether commit/push/merge/rebase/tag actions
  are authorized.
- Stay within the assigned milestone. Finishing early does not authorize the
  next stage.
- Before completion, run the required validation, review the final diff and
  status, re-check ancestry, and confirm protected branches and worktrees were
  not modified.
- Commit and push only when explicitly authorized. Preserve accepted milestone
  history; integrate forward rather than rewrite it unless explicitly directed.

For substantial engineering milestones, report the worktree path, branch,
starting/base SHA, final/commit SHA, required-ancestor verification, changed
files, validation results, push status, clean/dirty/untracked status, protected
branches confirmed unchanged, and known limitations or unresolved issues.

## Safety and provenance

Use synthetic data only in examples and fixtures. Never add credentials,
tokens, personal information, customer or employer code, production
configuration, or exploit steps for third-party systems. External sources
must retain attribution and licensing constraints. Do not claim that a
configuration setting enforces a security property without outcome evidence.
