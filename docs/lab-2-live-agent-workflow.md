# Lab 2 — Verify an AI-generated security fix

Use the [Participant Lab Guide](participant-guide.md) for the executable
journey. This page records the Lab 2 contract and interpretation rules.

## Task

The wrapper displays and automatically submits a synthetic command-injection
remediation task as the selected agent's first prompt. When the selected agent
starts, review the task, let it work, and exit the agent completely. The agent must preserve
`lookup(name)` behavior and change only `app/lookup.py`. The participant exits
the agent before independent verification.

Start the lab from the repository root:

```sh
python3 scripts/workshop.py lab2 --agent codex
```

Use `claude` for Claude Code, or `python` in PowerShell. The wrapper prepares
the disposable workspace, displays the task, starts the agent with the tested
boundary, and remembers the retained Lab 2 run. Temporary paths stay hidden
from the normal participant flow.

## What the workshop configures for you

The wrapper creates the workshop-controlled Lab 2 environment; it does not
simply launch the user's normal coding-agent session. These implementation-
backed controls are shown here to explain the boundary, not as a second
manual execution path. Use the `workshop.py` command above.

Codex receives an automatically copied configuration in an isolated temporary
`CODEX_HOME`, including `sandbox_mode = "workspace-write"`,
`approval_policy = "never"`, and `web_search = "disabled"`. Its tested
invocation also uses:

```text
--strict-config --sandbox workspace-write --ask-for-approval never --cd <generated Lab 2 workspace>
```

Claude starts with the generated workspace as its actual working directory and
uses:

```text
--restricted --safe-mode --strict-mcp-config
--tools Bash,Read,Edit,Write --permission-mode manual
```

The generated MCP configuration is empty, and the generated settings retain
the tested fail-closed sandbox/filesystem boundary. Configured authority tells
us what authority we intended to give the agent; it does not prove observed
runtime behavior or an independently verified outcome. Lab 2 therefore still
performs independent verification. Do not weaken these settings.

After the agent exits:

```sh
python3 scripts/workshop.py lab2 verify
```

The wrapper handles lifecycle bookkeeping, independent verification, and the
participant report in the correct order. It never treats process exit or an
agent completion message as proof that the task succeeded.

If a completed or abandoned run is retained and you want to retry or switch
agents, clear only that run with:

```sh
python3 scripts/workshop.py lab2 cleanup
```

This does not remove Kaapi or normal Claude/Codex configuration or
authentication. It is optional recovery/reset; it is not part of the normal
one-agent path. Final workshop cleanup remains:

```sh
python3 scripts/workshop.py cleanup
```

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

## Optional: try Lab 2 with the other agent

The normal one-agent path is:

```text
lab2 → complete/exit agent → lab2 verify → review → final workshop cleanup
```

This does not require `lab2 cleanup`. If you want to try the other coding
agent, retry Lab 2, or recover a retained Lab 2 run, first run:

```sh
python3 scripts/workshop.py lab2 cleanup
```

Then start Lab 2 again with the other `--agent` value. This removes the
retained workshop-owned Lab 2 run state, workspace, and evidence, plus any
isolated workshop-owned Codex configuration for that run; it does not remove
Kaapi or normal Claude/Codex configuration or authentication.

## Cleanup

After reviewing the result, run `python3 scripts/workshop.py cleanup`. Use
`--dry-run --verbose` to inspect exact owned paths without deleting anything.
Cleanup never removes normal Claude/Codex configuration or authentication state.

## Sources and related pages

- [Participant Lab Guide](participant-guide.md)
- [Independent verifier](../scripts/lab2_harness.py)
- [Security contract](../fixtures/lab2/security-contract.json)
- [Lab 2 harness detail](stage2d-lab2-verification-harness.md)
