# Project knowledge base

This is the maintained, source-backed wiki for **Securing AI Coding Agents:
From Guardrails to Verification**.

Start with the [index](index.md). The project documents and validation report
remain the canonical sources; this directory adds durable cross-references and
evolving synthesis so important conclusions do not live only in chat history.

The wiki is intentionally small at first. Add a source manifest under
`sources/`, update the relevant page under `wiki/`, refresh [index.md](index.md),
append to [log.md](log.md), and run:

```bash
python3 scripts/wiki_check.py
```

See the repository-level [AGENTS.md](../AGENTS.md) for the maintenance schema
and ingest, query, and lint workflows.
