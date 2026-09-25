# Hands-on Setup & Preflight

This guide is the Stage 2A technical baseline. It establishes a minimum
participant environment, one selected coding-agent pathway, and a safe
synthetic check. It does not publish or run the complete Lab 1 or Lab 2
exercises.

Choose exactly one pathway:

- **Claude Code hands-on**
- **Codex hands-on**
- **Instructor-led** (no local agent required)

The unselected agent is not a requirement and cannot fail your preflight.

## Safety and readiness boundary

Use a disposable or organization-approved directory. Use synthetic material
only. Never paste API keys, access tokens, credentials, customer data,
production source, or production configuration into an agent or evidence file.

The preflight does not start an agent, inspect authentication state, send a
provider request, change agent permissions, or install Kaapi. Its exit code is
an automated gate only:

- exit code `1` means a required automated check failed;
- exit code `0` means no required automated check failed;
- exit code `0` does **not** mean that authentication, provider access, agent
  execution, or approval behavior has been established; and
- the text and JSON `readiness` summary must be reviewed separately.

The instructor-led pathway is supported participation, not hands-on readiness.
Use it when a local check fails or manual agent evidence cannot be safely
obtained.

## Minimum participant requirements

| Requirement | Hands-on | Instructor-led | Notes |
| --- | --- | --- | --- |
| Python 3.11 or newer | Required | Not required | The preflight uses only the standard library. The minimum is aligned with the inspected Kaapi source; future labs may add dependencies. |
| `scripts/preflight.py` and this guide | Required | Not required | These are the only participant files checked by the preflight. |
| One selected agent | Claude Code **or** Codex | Not required | Do not install both for this workshop. |
| Git | Required only when using a Git checkout | Not required | A downloaded ZIP/extracted directory is supported. |
| GitHub account/authentication | Not required | Not required | A public download does not require GitHub write access. |
| Kaapi | Optional and non-gating | Not required | Integration and participant execution requirements are not yet validated. |

The validation report, approved README, orientation guide, and eventual lab
fixtures are maintainer or later-milestone concerns. Their presence is not a
participant preflight requirement.

## Obtain the workshop materials

Two acquisition methods are supported:

1. **Git checkout** — the repository remote observed for this project is
   `https://github.com/The-AI-Security-Lab/securing-ai-coding-agents.git`.
   A maintainer has not re-run a fresh clone as part of this validation; use
   your approved Git workflow if you choose this method.
2. **Public ZIP download** — download the repository archive from GitHub and
   extract it. Git metadata and GitHub authentication are not needed for the
   Stage 2A preflight.

From the extracted or cloned repository root, use `python3` below. The
preflight auto-detects a Git checkout; use `--acquisition zip` to make the
archive path explicit.

## Prepare the selected agent

The commands and requirements in this section are vendor-documented and were
not treated as local compatibility tests. Local versions actually observed on
the maintainer machine are recorded in the validation report.

### Claude Code

Anthropic's current setup documentation lists macOS 13+, Windows 10 1809+ or
Windows Server 2019+, Ubuntu 20.04+, Debian 10+, and Alpine Linux 3.19+ on x64
or ARM64, with at least 4 GB RAM and network access for authentication and AI
processing. It documents native, Homebrew, WinGet, and Linux package-manager
installation methods; use the method approved for your machine. Start an
interactive session with `claude` from the selected directory.

Anthropic documents Claude Code access through Pro, Max, Team, Enterprise, or
Console accounts, and through supported enterprise providers such as Bedrock
or Google Cloud's Agent Platform. A free claude.ai plan does not include
Claude Code. Usage or provider charges depend on the account and provider;
the workshop does not provide a cost guarantee or budget.

Relevant configuration scopes are:

- user: `~/.claude/settings.json`;
- shared project: `.claude/settings.json`;
- project-local: `.claude/settings.local.json`; and
- organization-managed sources such as `managed-settings.json` or managed
  policy delivery.

Do not edit managed settings. Keep personal settings and sign-in state out of
the workshop evidence. Do not use `--dangerously-skip-permissions` for the
synthetic check.

### Codex

The current OpenAI Codex CLI quickstart documents installation for macOS/Linux
and Windows paths, then starting `codex` from a project directory and choosing
Sign in with ChatGPT or another available sign-in method. Codex is included
across ChatGPT plans, subject to plan-specific usage limits; API-key or
workspace-managed access may follow a different organization path. Usage can
consume plan allowances or credits, so confirm the account's policy before
running a live check.

Codex configuration is distinct from Claude Code. The documented user-level
file is `~/.codex/config.toml`; a trusted project can contain
`.codex/config.toml`, and managed/system configuration may also apply. For a
synthetic action, use the least-privileged approved profile available to you
and keep approval prompts enabled. Do not use full-access or approval-bypass
settings.

## Run the deterministic preflight

From the workshop root, run exactly one command:

```bash
python3 scripts/preflight.py --agent claude
python3 scripts/preflight.py --agent codex
python3 scripts/preflight.py --agent none
```

For an extracted ZIP, make the acquisition mode explicit:

```bash
python3 scripts/preflight.py --agent codex --acquisition zip
```

The output reports `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT TESTED`, and `NOT
APPLICABLE` without collapsing them into an unsupported overall pass. Use JSON
for local evidence if desired:

```bash
python3 scripts/preflight.py --agent codex --format json > /tmp/stage-2a-preflight.json
```

Inspect the file before sharing. The preflight does not dump environment
variables or credentials, but executable paths can still identify a machine.

### Interpret failures

- A required `FAIL` blocks the automated gate. Fix the stated issue and rerun.
- A selected-agent executable `FAIL` means that pathway is unavailable; do not
  install the other agent unless you choose to switch pathways.
- `NOT TESTED` means a participant or live-agent action remains outstanding.
- `INCONCLUSIVE` means a probe cannot establish the claimed property; this is
  the expected outcome for an unavailable or incompatible optional Kaapi CLI
  availability probe.
- `NOT APPLICABLE` means the check is outside the selected pathway.

## Safe synthetic agent check

This is the smallest supported live validation. It uses one known synthetic
input and one bounded output in a directory outside the workshop checkout.
The agent must read the input and write only its SHA-256 digest. The verifier
independently computes the digest and rejects extra files. It does not accept a
natural-language claim as evidence.

### 1. Prepare the disposable fixture

Choose a new path outside the repository:

```bash
python3 scripts/preflight.py \
  --agent claude \
  --synthetic prepare \
  --synthetic-dir /tmp/stage2a-synthetic
```

Use `codex` in place of `claude` for the Codex pathway. The path must be new or
empty. Preparation will not modify an existing non-empty directory and will
refuse any path inside the workshop checkout.

### 2. Authenticate and perform the bounded action manually

Authenticate using the selected vendor flow. Keep provider prompts and agent
approval controls enabled. Start the agent from the synthetic directory, not
from the workshop repository, and ask it to:

> Read `stage2a-input.txt` and write only `stage2a-output.sha256` containing the
> SHA-256 hexadecimal digest of that input. Do not access paths outside this
> directory, use the network, or modify any other file. Stop for approval before
> writing.

Review the proposed action. Approve it only if it is bounded to this directory.
Record locally, without credentials or prompt transcripts:

- selected agent and exact `--version` output;
- authentication/provider result;
- the action proposed and whether approval was requested;
- whether the output file was created; and
- any limitation or unexpected behavior.

This is manual evidence. The preflight does not mark authentication or
approval behavior as passed from the agent's prose.

### 3. Verify the artifact independently

After the agent stops, run:

```bash
python3 scripts/preflight.py \
  --agent claude \
  --synthetic verify \
  --synthetic-dir /tmp/stage2a-synthetic
```

The artifact check is `PASS` only when the digest matches and the directory
contains exactly the two expected regular files. The output still reports
agent provenance and approval review as `NOT TESTED`; filesystem contents alone
cannot establish who created the file or how an approval was handled.

## Optional Kaapi path

Kaapi is not a participant prerequisite. Do not install it solely for this
milestone. The canonical local Kaapi source inspected for this review is a
separate checkout and is not part of this workshop repository.

If a maintainer provides an approved Kaapi checkout, probe CLI availability
without changing it:

```bash
python3 scripts/preflight.py \
  --agent codex \
  --kaapi check \
  --kaapi-project /path/to/kaapi
```

The supported source workflow observed in that checkout is labeled vendor/
project-local documentation, not a workshop participant guarantee:

```bash
uv sync --frozen --group dev
uv run kaapi version
uv run kaapi check path/to/config.toml --runtime codex --format json
```

The result is informational and non-gating. A successful version result proves
only that the Kaapi CLI is available in that prepared environment; it is not
proof of workshop integration. Configuration-analysis evidence is separate and
must come from a synthetic `kaapi check ... --format json` run.

## Official documentation checked

Checked 2026-09-25. These sources describe vendor-documented behavior; they do
not replace local validation:

- [Claude Code advanced setup](https://code.claude.com/docs/en/getting-started)
- [Claude Code settings and precedence](https://code.claude.com/docs/en/settings)
- [Codex CLI quickstart](https://learn.chatgpt.com/docs/codex/cli)
- [Using Codex with a ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)
- [Codex configuration basics](https://learn.chatgpt.com/docs/config-file/config-basic)

When local setup is unavailable, incompatible, unaffordable, or blocked by
organizational policy, use the instructor-led pathway rather than weakening
the boundary or exposing real data.
