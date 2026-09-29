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

For additional human-readable configuration detail, use:

```sh
python3 scripts/workshop.py lab1 --agent codex --verbose
```

For detailed machine-readable evidence, use the participant interface:

```sh
python3 scripts/workshop.py lab1 --agent codex --evidence
```

Replace `codex` with `claude` as needed. The lower-level `scripts/lab1.py`
runner is an implementation detail; normal participants should use
`scripts/workshop.py`.

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
and submits it automatically as the selected agent's first prompt. When the
agent opens, review that task, let the agent attempt the defined remediation,
review its completion message, and exit the agent completely. You do not need
to know `task.txt`, `participant/`, the temporary run ID, or any internal
path. Do not ask it to claim that independent verification passed.

### What the workshop configures for you

The wrapper does more than launch your normal coding-agent session. It creates
the workshop-controlled Lab 2 workspace and invokes the selected agent with
the tested workshop boundary. Choose one participant path:

```sh
python3 scripts/workshop.py lab2 --agent codex
python3 scripts/workshop.py lab2 --agent claude
```

Do not manually recreate the invocation. Under the hood, the implementation
backs these controls:

- **Codex:** workspace-write sandboxing, workshop-defined approval behavior
  (`--ask-for-approval never`), an isolated temporary `CODEX_HOME` containing
  the workshop configuration, and `web_search = "disabled"` for the exercise.
- **Claude Code:** the generated Lab 2 workspace as the working directory,
  `--restricted`, `--safe-mode`, `--strict-mcp-config`, an empty generated MCP
  configuration, the bounded `Bash,Read,Edit,Write` tool set, manual permission
  mode, and generated fail-closed sandbox/filesystem settings.

Configured authority tells us what authority we intended to give the agent. It
does not prove observed runtime behavior or an independently verified outcome;
that is why Lab 2 still performs independent verification. The generated
workshop configuration does not replace or modify your normal Codex/Claude
configuration or authentication state. For debugging only, add `--verbose` to
the wrapper command to see launch details.

### Verify Lab 2

After the agent process has exited, run exactly one command:

```sh
python3 scripts/workshop.py lab2 verify
```

PowerShell:

```powershell
python scripts/workshop.py lab2 verify
```

The wrapper remembers the retained run and internally performs the required
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

### Optional: try Lab 2 with the other agent

The normal one-agent path is:

```text
lab2 → complete/exit agent → lab2 verify → review → final workshop cleanup
```

You do not need `lab2 cleanup` on that path. If you want to try the other
coding agent, retry Lab 2, or recover a retained Lab 2 run, first run:

```sh
python3 scripts/workshop.py lab2 cleanup
```

Then start Lab 2 again with the other `--agent` value. This removes the
retained workshop-owned Lab 2 run state, workspace, and evidence, plus any
isolated workshop-owned Codex configuration for that run; it does not remove
Kaapi or normal Claude/Codex configuration or authentication.

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

This removes verified workshop-managed Kaapi state, the retained Lab 2 workspace
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
- **A Lab 2 run already exists:** a previous run or its verification evidence
  may intentionally be retained. To retry, test the other agent, or start
  another Lab 2 attempt, run:

  ```sh
  python3 scripts/workshop.py lab2 cleanup
  python3 scripts/workshop.py lab2 --agent claude
  ```

  Replace `claude` with `codex` as needed. Lab 2 cleanup removes only safely
  identified Lab 2 workshop state; it does not remove Kaapi or normal agent
  configuration/authentication. It is not required on the normal path.
- **Verification says no Lab 2 run exists:** no retained run is available to
  verify. Start one with `python3 scripts/workshop.py lab2 --agent claude` or
  `--agent codex`.
- **The agent is still active:** exit the selected agent completely, then run
  `python3 scripts/workshop.py lab2 verify`. Verification is never run while
  the lifecycle is active.
- **The agent did not complete the task:** if it refuses the edit, encounters
  a restriction, reports failure, exits without the remediation, or claims
  success and you are unsure, still exit it completely and run
  `python3 scripts/workshop.py lab2 verify`. Do not manually repair the
  workspace or bypass the tested restriction; independent verification owns
  the defined security and scope result.
- **No Lab 2 state exists for cleanup:**
  `python3 scripts/workshop.py lab2 cleanup` reports that no retained run was
  found and removes nothing. Start Lab 2 normally if you want another attempt.
- **Difference between cleanup commands:**
  `python3 scripts/workshop.py lab2 cleanup` resets only retained Lab 2 state
  so Lab 2 can be retried or another agent can be used. The final
  `python3 scripts/workshop.py cleanup` removes all safely attributable
  workshop-managed state, including Kaapi and Lab 2 state, after you are
  finished. The two commands are not both mandatory.
- **An unexpected final-state path appears:** preserve it and follow
  `Detect → Explain → Classify → Decide → Fix / Explicitly Allow`. Do not
  whitelist or delete it first.
- **Cleanup refuses a path:** use `cleanup --verbose` or
  `cleanup --dry-run --verbose`, inspect the exact reported path, and do not
  broaden the cleanup target. If `lab2 cleanup` refuses a path, preserve it
  and inspect the exact ownership/safety message; do not use broad `rm` or
  glob commands to force cleanup.
- **Windows behavior differs:** use the PowerShell command for the current
  step. Complete Windows live-agent acceptance remains a documented
  limitation; use the instructor-led fallback if needed.

## Sources and related pages

- [Lab 1 detail](lab-1-configuration-assessment.md)
- [Lab 2 detail](lab-2-live-agent-workflow.md)
- [Hands-on setup and troubleshooting](hands-on-setup.md)
- [Project knowledge base](../knowledge/index.md)
