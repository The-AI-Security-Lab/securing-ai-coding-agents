# Lab 2 — Verify an AI-generated security fix

Use the [Participant Lab Guide](participant-guide.md) for the executable
journey. This page records the Lab 2 contract and interpretation rules.

## Task

The wrapper displays, but does not automatically submit, a synthetic
command-injection remediation task. When the selected agent starts, paste or
type the displayed task into the agent and submit it. The agent must preserve
`lookup(name)` behavior and change only `app/lookup.py`. The participant exits
the agent before independent verification.

Start the lab from the repository root:

```sh
python3 scripts/workshop.py lab2 --agent codex
```

Use `claude` for Claude Code, or `python` in PowerShell. The wrapper prepares
the disposable workspace, displays the task, starts the agent with the tested
boundary, and remembers the active run. After the agent starts, paste or type
the displayed task into it and submit it. Temporary paths stay hidden from the
normal participant flow. Codex receives an automatically copied config in an
isolated workshop-owned home. Claude starts with the generated workspace as
its actual working directory while retaining:

```text
--restricted --safe-mode --strict-mcp-config
--tools Bash,Read,Edit,Write --permission-mode manual
```

The generated MCP configuration is empty and the generated settings retain the
tested sandbox/filesystem boundary. Do not weaken these settings.

After the agent exits:

```sh
python3 scripts/workshop.py lab2 verify
```

The wrapper handles lifecycle bookkeeping, independent verification, and the
participant report in the correct order. It never treats process exit or an
agent completion message as proof that the task succeeded.

## Outcome model

Security and final-state scope are independent. Overall `PASS` requires both:

| Security | Scope | Overall |
| --- | --- | --- |
| PASS | PASS | PASS |
| PASS | FAIL | FAIL |
| FAIL | PASS | FAIL |
| FAIL | FAIL | FAIL |
| INCONCLUSIVE | any | not PASS |

The verifier owns the defined security result and final filesystem result. A
security `PASS` does not excuse scope `FAIL`; scope `FAIL` does not prove the
remediation failed. Unexpected artifacts remain failures until explained:

```text
Detect → Explain → Classify → Decide → Fix / Explicitly Allow
```

Final-state verification is not complete runtime telemetry. The tested Codex
boundary does not establish read confidentiality outside the workspace.

## Evidence

Normal output is concise. Use `python3 scripts/workshop.py lab2 verify
--verbose` for the exact retained evidence path, or `--evidence` for JSON.
Machine-readable evidence retains case results, hashes, inventories, scope
review, workflow metadata, and limitations. Do not share sensitive paths or
authentication material.

## Cleanup

After reviewing the result, run `python3 scripts/workshop.py cleanup`. Use
`--dry-run --verbose` to inspect exact owned paths without deleting anything.
Cleanup never removes normal Claude/Codex configuration or authentication state.

## Sources and related pages

- [Participant Lab Guide](participant-guide.md)
- [Independent verifier](../scripts/lab2_harness.py)
- [Security contract](../fixtures/lab2/security-contract.json)
- [Lab 2 harness detail](stage2d-lab2-verification-harness.md)
