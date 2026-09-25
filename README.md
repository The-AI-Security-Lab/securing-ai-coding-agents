# Securing AI Coding Agents: From Guardrails to Verification

A hands-on workshop from **[AI Security Lab](https://www.aisecuritylab.com/)**.

This 90-minute virtual workshop explores how to govern the capabilities of AI coding agents and verify that security controls work as intended. We cover both Claude Code and Codex. You can complete the exercises on your own machine or follow the instructor without installing the tools.

## Start here

**Attending the workshop?** Read the [Know Before You Go guide](docs/know-before-you-go.md) for the learning goals, participation options, and preparation advice.

**Planning to work hands-on?** The validated Hands-on Setup & Preflight guide will be published in this repository before the workshop. Please complete setup and authentication before the event. You need only one supported coding agent, not both.

**Bookmark this repository.** Return here for the setup guide, lab materials, and supporting resources as they become available. Links will be added when those materials are validated and published.

## Workshop labs

### Lab 1 — Govern and harden AI coding agents

Explore Claude Code and Codex architecture, security-relevant configurations, permissions, tools, and execution boundaries. Apply practical controls to reduce unnecessary agent authority.

### Lab 2 — Verify security controls

Define basic security evals and a small golden dataset. Use AI Security Lab's open-source tools and a deterministic Python harness to assess supported agent configurations, collect evidence, and distinguish configured restrictions from verified outcomes.

## Continue learning

Explore [AI Security Lab](https://www.aisecuritylab.com/) for open-source tools, research, learning resources, and future hands-on workshops.

## Project knowledge base

The repository includes a maintained, source-backed [project knowledge base](knowledge/index.md).
It links the canonical workshop documents into durable pages covering scope,
readiness semantics, participant pathways, and evidence boundaries. Run
`python3 scripts/wiki_check.py` after updating it.

*Validated technical setup instructions and lab materials will be published separately. This repository currently contains participant orientation materials only.*

## Licensing and contributions

We welcome contributions of synthetic labs, security evals, and verification workflows. See [Contributing](CONTRIBUTING.md) before submitting changes.

Workshop teaching materials and reusable code have **different proposed license terms**: see [Workshop materials license](LICENSE), [Code license](LICENSE-CODE.md), and [Notices](NOTICE.md). Personal learning, internal enterprise use of the harness, and attributed internal colleague-to-colleague teaching are intended to be permitted. Distributing the harness in a commercial product or using workshop materials for paid training or consulting requires separate written approval.

**Publication note:** These custom license drafts require confirmation of the legal rights holder and legal review before they are treated as final. Third-party tools retain their own licenses. This workshop repository should be described as publicly available or source-available, not universally OSI open source.
