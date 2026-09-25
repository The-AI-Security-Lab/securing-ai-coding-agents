# Lab 1 — Configuration assessment

Lab 1 teaches participants to inspect an agent configuration and decide what
the declared policy evidence supports. It does not claim that a setting was
enforced at runtime. The participant workflow is **Demonstrate → Choose →
Practice**:

1. The instructor demonstrates the three fixture states for the other vendor
   where practical, choosing the demonstration path based on the predominant
   participant path.
2. Each participant chooses Claude Code or Codex and remains on that path.
3. Each participant practices with the three fixtures for the selected path.

All six synthetic fixtures remain available. A participant with both agents,
or with time to compare configuration models, may optionally run the other
vendor's three fixtures. Running both vendors is not a workshop prerequisite.
Participants stay on their selected path for Lab 2.

| Agent path | Risky | Hardened | Malformed |
| --- | --- | --- | --- |
| Claude Code | [`fixtures/lab1/claude/risky/settings.json`](../fixtures/lab1/claude/risky/settings.json) | [`fixtures/lab1/claude/hardened/settings.json`](../fixtures/lab1/claude/hardened/settings.json) | [`fixtures/lab1/claude/malformed/settings.json`](../fixtures/lab1/claude/malformed/settings.json) |
| Codex | [`fixtures/lab1/codex/risky/config.toml`](../fixtures/lab1/codex/risky/config.toml) | [`fixtures/lab1/codex/hardened/config.toml`](../fixtures/lab1/codex/hardened/config.toml) | [`fixtures/lab1/codex/malformed/config.toml`](../fixtures/lab1/codex/malformed/config.toml) |

The three cases have distinct teaching questions:

- **Risky:** Can the participant identify the concerning authority/capability before seeing the assessment?
- **Hardened:** Does the candidate now meet the declared configuration baseline?
- **Malformed:** What should we conclude when the evidence cannot be safely assessed?

The runner consumes each fixture through the accepted public Kaapi consumer
adapter and uses Kaapi for configuration/policy evidence only:

```sh
python3 scripts/lab1.py --agent claude
python3 scripts/lab1.py --agent codex
python3 scripts/lab1.py --agent claude --case risky --format json
```

The fixtures are synthetic and are not copied into a participant's real
configuration. The examples correspond to the relevant configuration models:
Claude Code uses JSON settings, while Codex uses TOML configuration. A common
organisational security requirement can therefore map to different vendor
configuration controls and evidence.

The declared Lab 1 baseline is intentionally narrower than the full inspection:

- Claude Code's decision is gated by `AGENT-SBOX-001`: sandbox enablement must
  be present.
- Codex's decision is gated by `AGENT-MCP-001`: the configured MCP server count
  must be zero.

The other visible settings provide useful authority and capability context for
the participant's inspection, but they are not separate pass/fail requirements
in this Lab 1 policy.

For orientation only, the corresponding real configuration locations are
Claude Code's user `~/.claude/settings.json`, shared project
`.claude/settings.json`, project-local `.claude/settings.local.json`, and
managed settings; and Codex's user `~/.codex/config.toml`, trusted project
`.codex/config.toml`, and possible managed/system layers. Lab 1 does not read
or modify any of those locations.

The participant-facing result is deliberately simple:

- `PASS`, `FAIL`, `INCONCLUSIVE`, or `NOT TESTED` for the configuration baseline;
- `NOT APPLICABLE` for Lab 1's task-scope and independently verified outcome rows;
- which of the four formal evidence categories are present or missing; and
- a plain-English conclusion and limitation.

The four evidence categories remain separate: configured authority, resolved
permitted capabilities, observed runtime behaviour, and independently verified
runtime outcome. Lab 1 supplies only the first two. `PASS` therefore means that
the declared configuration requirement passed; it is not proof of runtime
enforcement or of a security outcome. The bridge question is: “Kaapi says the
configuration passes. Are we done?” No. Lab 2 remains responsible for bounded
write scope, the small synthetic command-injection-style security fix, and
independent verification of both task/write scope and security outcome.
