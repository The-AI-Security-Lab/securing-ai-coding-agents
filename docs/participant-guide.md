# Participant Lab Guide

This is the canonical self-service journey for **Securing AI Coding Agents:
From Guardrails to Verification**. Run commands from the repository root. Pick
one coding agent—Claude Code or Codex—for both labs; you do not need both.

The required path is:

```text
Inspect → Constrain → Run → Observe → Verify → Decide
```

Primary end-to-end validation was performed on macOS. Windows/PowerShell
command generation is covered by tests, but a complete Windows live-agent
acceptance has not been independently validated; use the separated Windows
commands below or the instructor-led fallback if your environment differs.

## 1. Before you start

Use only the supplied synthetic fixtures and disposable workspaces. Do not use
production repositories, real credentials, customer or employee data, real
incidents, or real agent configuration files. Inspect terminal output before
sharing it.

You need Python 3.11+, Git, `uv`, this repository, and one supported agent for
the hands-on path. Authentication is checked when the agent is used, not by
the automated preflight.

## 2. Setup and preflight

On macOS or another shell with `python3`:

```sh
python3 scripts/workshop.py setup
python3 scripts/preflight.py --agent codex
```

Use `--agent claude` for Claude Code. For instructor-led participation:

```sh
python3 scripts/preflight.py --agent none --kaapi skip
```

On Windows/PowerShell, use the same sequence with `python`:

```powershell
python scripts/workshop.py setup
python scripts/preflight.py --agent codex
```

The normal preflight is concise. `AUTOMATED CHECKS: PASS` means the required
local checks passed, so you may continue to Lab 1. Authentication is checked
when you use the selected agent, and live agent behavior and approval behavior
are intentionally checked later during Lab 2. The open circles mark those
later checks; they are not a reason to stop. Use `--verbose` for commands,
observations, and limitations, or `--format json` for machine-readable
evidence.

Setup obtains the workshop-managed Kaapi `1.1.0` environment at the pinned
revision `9a0bc6ba34576782675aded9e16b718c24fea9bd` under `.workshop-deps/`.
It does not install Kaapi globally.

If a required check fails, fix that check and rerun preflight. Do not weaken a
boundary to make the check pass.

## 3. Lab 1 — Configuration Assessment

What you are doing: deciding whether a supplied agent configuration meets the
declared security baseline. Kaapi provides configuration evidence only; a
`PASS` is not proof of runtime behavior.

The Lab 1 evidence model separates configured authority, resolved permitted capabilities,
observed runtime behavior, and independently verified outcomes.
Only the first two are expected in this lab.

First inspect the three files for your selected agent:

| Case | Codex | Claude Code |
| --- | --- | --- |
| Risky | `fixtures/lab1/codex/risky/config.toml` | `fixtures/lab1/claude/risky/settings.json` |
| Hardened | `fixtures/lab1/codex/hardened/config.toml` | `fixtures/lab1/claude/hardened/settings.json` |
| Malformed | `fixtures/lab1/codex/malformed/config.toml` | `fixtures/lab1/claude/malformed/settings.json` |

After inspecting them, run one command. macOS/shell:

```sh
python3 scripts/workshop.py lab1 --agent codex
```

PowerShell:

```powershell
python scripts/workshop.py lab1 --agent codex
```

Replace `codex` with `claude` when appropriate. The output shows each exact
fixture path and its assessment:

```text
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

`PASS` means the configuration meets the declared baseline. It is not runtime
proof. `FAIL` means the declared baseline was not met. `NOT TESTED` means the
configuration could not be safely assessed. `INCONCLUSIVE` means the evidence
was insufficient for a supported conclusion.

For detailed Kaapi evidence, run the underlying assessment with its explicit
evidence option:

```sh
python3 scripts/lab1.py --agent codex --format evidence
```

Do not point the required path at your real configuration; it can contain
internal paths, URLs, or MCP names.

## 4. Lab 2 — Agent remediation and independent verification

What you are doing: giving one selected agent a synthetic remediation task,
then checking the final workspace independently. Only `app/lookup.py` may change.

The tested boundaries remain version-specific:

- Codex: `workspace-write` with approval `never`.
- Claude Code: `--restricted`, `--safe-mode`, `--strict-mcp-config`, an empty
  MCP configuration, tools `Bash,Read,Edit,Write`, manual permission mode, and
  the generated fail-closed sandbox/filesystem settings.

Approval is a decision boundary, not automatically hard isolation. Codex's
tested profile does not establish read confidentiality outside the workspace.
Bytecode hygiene is not security isolation.

### Start Lab 2

Run one command from the workshop repository. The wrapper prepares the
disposable workspace, creates the selected agent's tested configuration, starts
the agent in the correct workspace, and keeps the temporary paths out of the
normal participant flow.

macOS/shell:

```sh
python3 scripts/workshop.py lab2 --agent codex
```

Windows/PowerShell:

```powershell
python scripts/workshop.py lab2 --agent codex
```

Replace `codex` with `claude`. The wrapper displays the exact synthetic task
before starting the agent; it does not submit the task to the agent for you.
When the agent starts, paste or type the displayed task into the agent and
submit it. Let the agent attempt the defined remediation, review its
completion message, and exit the agent completely. Do not ask it to claim
that independent verification passed.

The wrapper preserves Codex isolation underneath by copying the generated
configuration into a temporary workshop-owned Codex home. It never changes
your normal Codex configuration, Claude configuration, or authentication
state. For debugging only, add `--verbose` to the start command to see the
exact workspace and launch details.

### Verify Lab 2

After the agent process has exited, run exactly one command:

```sh
python3 scripts/workshop.py lab2 verify
```

PowerShell:

```powershell
python scripts/workshop.py lab2 verify
```

The wrapper remembers the active run and internally performs the required
record, independent verification, and report steps. You do not copy a run ID
or run lower-level workflow commands.

The concise result has three decisions:

```text
Security
✓ PASS
  6 / 6 security cases passed

Change scope
✓ PASS
  Changed: app/lookup.py
  Unexpected files: None
  Protected file changed: No

OVERALL RESULT: PASS
```

For a failure, read the stated failed cases, side effect, unexpected paths,
or inconclusive reason. Security and scope remain independent:

| Security | Scope | Overall | Meaning |
| --- | --- | --- | --- |
| PASS | PASS | PASS | Defined security and final-state scope both passed. |
| PASS | FAIL | FAIL | The fix passed, but final scope needs investigation. |
| FAIL | PASS | FAIL | Scope passed, but the defined security property failed. |
| FAIL | FAIL | FAIL | Both required outcomes failed. |
| INCONCLUSIVE | any | not PASS | Preserve the evidence and investigate. |

Use `python3 scripts/workshop.py lab2 verify --verbose` to print the exact
retained evidence path, or `--evidence` to print machine-readable JSON. The
independent verifier owns the security and final-state outcome. The result is
not complete runtime telemetry.

For any unexpected final-state artifact, follow:

```text
Detect → Explain → Classify → Decide → Fix / Explicitly Allow
```

Do not whitelist unexplained `__pycache__`, `.claude/.cc-writes`, or other
artifacts. Do not whitelist what you have not explained. Do not delete an
unexpected artifact before interpreting it.

## 5. Cleanup — final participant step

What you are doing: removing only workshop-created state whose ownership and
canonical location can be proven.

After verification and evidence review, run:

```sh
python3 scripts/workshop.py cleanup
```

PowerShell:

```powershell
python scripts/workshop.py cleanup
```

This removes verified workshop-managed Kaapi state, the active Lab 2 workspace
and evidence, and the temporary isolated Codex workshop home. It deliberately
preserves your normal Codex configuration, normal Claude configuration, and
authentication/session data. It never searches arbitrary temporary folders or
uses a broad cleanup glob. Local cleanup is not proof of server-side token/session revocation.

To inspect exact ownership decisions without deleting anything:

```sh
python3 scripts/workshop.py cleanup --dry-run --verbose
```

For exact discovered, removed, preserved, and refused paths after the run:

```sh
python3 scripts/workshop.py cleanup --verbose
```

If ownership or safety cannot be established, cleanup refuses that path and
reports it for manual inspection. Repeating cleanup is safe and reports owned
state as already absent. Local cleanup is not proof of provider-side logout,
token revocation, or session revocation.

## 6. What the labs prove—and do not prove

Lab 1 assesses supplied configuration against a declared baseline. Lab 2
independently checks the defined security cases and final filesystem scope for
one disposable run. Overall `PASS` requires both security `PASS` and scope
`PASS`.

The labs do not establish a generally secure environment, complete runtime
telemetry, reverted intermediate writes, detached-process absence, arbitrary
external effects, complete process/network/filesystem telemetry, syscall or
kernel telemetry, or Codex read confidentiality outside the workspace.

## 7. Troubleshooting and recovery

- **Preflight shows `FAIL`:** fix the named local prerequisite and rerun it.
  Do not substitute a global Kaapi or weaken an agent boundary.
- **Authentication is unavailable:** stop the live path and use the
  instructor-led fallback; never place tokens, device codes, or auth files in
  the repository.
- **The agent says it cannot edit:** do not bypass the tested restriction.
  Exit the agent, inspect the lifecycle message, and preserve the independent
  result as `FAIL` or `INCONCLUSIVE` as appropriate.
- **Verification says no active run or the agent is still active:** use the
  exact recovery message; exit the selected agent completely before retrying
  verification.
- **An unexpected final-state path appears:** preserve it and follow
  `Detect → Explain → Classify → Decide → Fix / Explicitly Allow`. Do not
  whitelist or delete it first.
- **Cleanup refuses a path:** use `cleanup --verbose` or
  `cleanup --dry-run --verbose`, inspect the exact reported path, and do not
  broaden the cleanup target.
- **Windows behavior differs:** use the PowerShell command for the current
  step. Complete Windows live-agent acceptance remains a documented
  limitation; use the instructor-led fallback if needed.

## Sources and related pages

- [Lab 1 detail](lab-1-configuration-assessment.md)
- [Lab 2 detail](lab-2-live-agent-workflow.md)
- [Hands-on setup and troubleshooting](hands-on-setup.md)
- [Project knowledge base](../knowledge/index.md)
