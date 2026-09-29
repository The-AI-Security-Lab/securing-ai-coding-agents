# Lab 1 — Configuration Assessment

Start with the [Participant Lab Guide](participant-guide.md). This page gives
the Lab 1 detail for participants and instructors.

## What you are doing

You are deciding whether a supplied synthetic configuration meets the declared
security baseline. Kaapi assesses configured authority and resolved permitted
capabilities. It does not establish observed runtime behavior or independently
verified runtime outcomes.

## Inspect, then assess

Inspect the three files for the one agent path you selected:

| State | Claude Code | Codex |
| --- | --- | --- |
| Risky | [`fixtures/lab1/claude/risky/settings.json`](../fixtures/lab1/claude/risky/settings.json) | [`fixtures/lab1/codex/risky/config.toml`](../fixtures/lab1/codex/risky/config.toml) |
| Hardened | [`fixtures/lab1/claude/hardened/settings.json`](../fixtures/lab1/claude/hardened/settings.json) | [`fixtures/lab1/codex/hardened/config.toml`](../fixtures/lab1/codex/hardened/config.toml) |
| Malformed | [`fixtures/lab1/claude/malformed/settings.json`](../fixtures/lab1/claude/malformed/settings.json) | [`fixtures/lab1/codex/malformed/config.toml`](../fixtures/lab1/codex/malformed/config.toml) |

After inspection, run from the repository root:

```sh
python3 scripts/workshop.py lab1 --agent codex
```

Use `--agent claude` for Claude Code, or `python` instead of `python3` in
PowerShell. The command assesses all three fixtures for the selected agent.

## Expected participant result

```text
Lab 1 — Configuration Assessment

✗ RISKY — FAIL
  File: fixtures/lab1/codex/risky/config.toml
  Reason: Configuration exceeds the declared security baseline.

✓ HARDENED — PASS
  File: fixtures/lab1/codex/hardened/config.toml
  Reason: Configuration meets the declared security baseline.

○ MALFORMED — NOT TESTED
  File: fixtures/lab1/codex/malformed/config.toml
  Reason: Configuration could not be safely assessed.
```

`PASS` means the configuration meets the declared baseline. It is not proof of
runtime behavior. `FAIL` means the declared baseline was not met. `NOT TESTED`
means the configuration could not be safely assessed. `INCONCLUSIVE` means the
evidence is insufficient for a supported conclusion.

Detailed evidence remains available with:

```sh
python3 scripts/lab1.py --agent codex --format evidence
```

An optional custom configuration assessment is deferred from this bounded pass.
Real configuration files may expose internal paths, URLs, MCP names, or other
sensitive material; the supplied model-free synthetic fixtures remain the safe
participant path.

## Sources and related pages

- [Participant Lab Guide](participant-guide.md)
- [Kaapi consumer](../scripts/kaapi_consumer.py)
- [Lab 1 policy](../fixtures/lab1/policy.json)
