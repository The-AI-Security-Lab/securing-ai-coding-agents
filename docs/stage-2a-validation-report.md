# Stage 2A Engineering Review, Remediation & Validation Report

Checked 2026-09-25. This report covers the local Stage 2A baseline only. It
does not build Lab 1 or Lab 2, publish the setup, modify Kaapi, or establish a
production security guarantee.

## Status vocabulary and readiness semantics

| Status | Meaning |
| --- | --- |
| `PASS` | The stated deterministic check succeeded in the recorded environment. |
| `FAIL` | A required deterministic check did not succeed. |
| `INCONCLUSIVE` | A probe ran or was attempted, but cannot establish the stated property. |
| `NOT TESTED` | The check requires participant action or live behavior and was not automated. |
| `NOT APPLICABLE` | The check is outside the selected pathway or intentionally optional. |

The preflight now exposes three separate concepts:

- `automated_gate`: `CLEAR` or `BLOCKED` for required deterministic checks;
- `exit_code`: `0` only when no required automated check failed; and
- `readiness.state` plus `readiness.hands_on_ready`. The preflight never sets
  `hands_on_ready` to `true`: selected-agent authentication, synthetic action
  provenance, and manual approval evidence must be reviewed outside this
  process.

Therefore, exit code `0` is not an overall workshop `PASS` and must not be
used by downstream automation as proof of hands-on readiness. Instructor-led
participation is reported as `INSTRUCTOR_LED_NOT_HANDS_ON`.

## Repository and scope inspection

### Workshop repository

| Item | Observed value |
| --- | --- |
| Current branch | `stage-2a-technical-baseline` |
| Current base commit | `81995a0` (`Add workshop licensing and contribution guidelines`) |
| Public `main` | `81995a098d5de4374bd8b01263e4bb0840792eb7` |
| `origin/main` | Same commit as public `main` |
| Working tree | Existing Stage 2A files plus this remediation remain uncommitted on the local branch |
| Approved files | `README.md` and `docs/know-before-you-go.md` unchanged |
| Lab fixtures | None existed before this remediation; complete labs remain out of scope |

No push, merge, pull request, public-`main` modification, or publication action
was performed.

### Participant versus maintainer requirements

The preflight now requires only:

- Python 3.11 or newer;
- `scripts/preflight.py`; and
- `docs/hands-on-setup.md`.

Git is checked only for `--acquisition git`. `--acquisition auto` supports both
a Git checkout and an extracted ZIP; `--acquisition zip` does not require Git.
The validation report, README, GitHub authentication, and future lab fixtures
are not participant preflight requirements.

### Current changed files

- `scripts/preflight.py`
- `tests/test_preflight.py`
- `docs/hands-on-setup.md`
- `docs/stage-2a-validation-report.md`

## Exact local validation environment

| Component | Observed value | Evidence/limitation |
| --- | --- | --- |
| Host | macOS Darwin 23.6.0, arm64 | Local maintainer machine only |
| Python | 3.14.4 at `/opt/homebrew/bin/python3` | 3.11 is the implemented minimum; 3.14.4 is not a required participant version |
| Git | 2.39.5 at `/usr/bin/git` | Required only for Git acquisition |
| `uv` | 0.12.5 | Used only for the separate Kaapi source workflow |
| Claude Code | 2.1.282 at `/Users/ashish/.local/bin/claude` | Bounded live session completed on this maintainer machine; no credentials or provider response content retained |
| Codex CLI | `codex-cli 0.151.0` at `/Users/ashish/.local/bin/codex` | Bounded live session completed on this maintainer machine; no credentials or provider response content retained |
| Kaapi | 1.1.0 from the canonical checkout's prepared `.venv` | Local CLI fixture checks only; not a workshop dependency |

These are locally tested configurations, not vendor compatibility claims.

## Official vendor documentation

The following sources were checked on 2026-09-25. They are vendor-documented
requirements and workflows, not locally tested compatibility claims.

| Agent | Documented facts relevant to this workshop | Cost/access limitation | Configuration locations/scopes |
| --- | --- | --- | --- |
| Claude Code | Current setup docs list macOS 13+, Windows 10 1809+/Server 2019+, Ubuntu 20.04+, Debian 10+, and Alpine 3.19+ on x64/ARM64; 4 GB+ RAM and internet access are listed. Native, Homebrew, WinGet, and Linux package-manager methods are documented. | Requires a Pro, Max, Team, Enterprise, or Console account; supported enterprise providers are also documented. Usage/provider charges depend on the account and provider. | User `~/.claude/settings.json`; shared project `.claude/settings.json`; project-local `.claude/settings.local.json`; managed sources such as `managed-settings.json`. |
| Codex CLI | Current quickstart documents installation for macOS/Linux and Windows paths, starting `codex` in a project directory, and signing in with ChatGPT or another available method. | Codex is included across ChatGPT plans, subject to plan-specific limits; API/workspace access can follow different organization controls. Usage may consume allowances or credits. | User `~/.codex/config.toml`; trusted project `.codex/config.toml`; managed/system layers may also apply. |

Sources:

- [Claude Code advanced setup](https://code.claude.com/docs/en/getting-started)
- [Claude Code settings and precedence](https://code.claude.com/docs/en/settings)
- [Codex CLI quickstart](https://learn.chatgpt.com/docs/codex/cli)
- [Using Codex with a ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)
- [Codex configuration basics](https://learn.chatgpt.com/docs/config-file/config-basic)

The agents are not treated as security-equivalent. Their account models,
configuration files, approval controls, sandbox behavior, and managed policy
surfaces remain distinct.

## Deterministic local tests

### Repository and preflight commands

| Status | Exact command/action | Expected outcome | Observed outcome | Evidence/limitation |
| --- | --- | --- | --- | --- |
| `PASS` | `python3 -m py_compile scripts/preflight.py tests/test_preflight.py` | Both files compile | Completed without output | Syntax only |
| `PASS` | `python3 -m unittest discover -s tests -v` | Focused test suite passes | 23 tests passed | Mocked/unit tests; no provider calls |
| `PASS` | `python3 scripts/preflight.py --agent claude` | Claude-only deterministic checks run; Codex is not required | Selected executable passed; auth, synthetic provenance, and approval were `NOT TESTED`; exit `0`; readiness unresolved | Local Claude version only |
| `PASS` | `python3 scripts/preflight.py --agent codex` | Codex-only deterministic checks run; Claude is not required | Selected executable passed; auth, synthetic provenance, and approval were `NOT TESTED`; exit `0`; readiness unresolved | Local Codex version only |
| `PASS` | `python3 scripts/preflight.py --agent none` | Instructor-led path does not require either agent | Both agent paths `NOT APPLICABLE`; exit `0`; readiness `INSTRUCTOR_LED_NOT_HANDS_ON` | Not hands-on readiness |
| `PASS` | `python3 scripts/preflight.py --agent codex --acquisition zip` | Extracted-directory path runs without Git | ZIP acquisition accepted; Git `NOT APPLICABLE` | ZIP path was exercised in the local checkout without Git metadata being required by the check |
| `PASS` | `python3 scripts/preflight.py --agent claude --kaapi check` | Absent optional Kaapi is non-gating | Kaapi `INCONCLUSIVE`; exit `0`; readiness still unresolved | No Kaapi was on PATH |
| `PASS` | `python3 scripts/preflight.py --agent codex --format json` | JSON contains checks and readiness separately | JSON emitted with `automated_gate`, `exit_code`, `readiness`, and individual statuses | Do not share local paths or sensitive evidence without review |

The negative regression test also confirmed that a selected missing agent is a
required `FAIL` and exits `1`, while an unselected missing agent is not tested
and cannot fail the pathway.

### Safe synthetic validation

The implementation provides:

1. `--synthetic prepare` to create a new/empty disposable directory containing
   only the original known `stage2a-input.txt`;
2. a documented manual agent action that writes only
   `stage2a-output.sha256`, with approval prompts left enabled; and
3. `--synthetic verify` to independently confirm the input bytes equal the
   original fixture, compare the output digest against that original input,
   reject missing/extra files and symlinks, and report provenance/approval
   separately.

| Status | Exact command/action | Observed outcome | Limitation |
| --- | --- | --- | --- |
| `PASS` | Unit test `test_synthetic_prepare_and_independent_verify` | Prepared fixture, wrote expected digest in the test fixture, and independently verified it | Mocked/local filesystem action; no live agent |
| `PASS` | Unit test `test_synthetic_workspace_cannot_be_inside_checkout` | In-checkout target rejected | Does not validate every platform filesystem edge case |
| `PASS` | Negative synthetic tests for modified input, incorrect digest, extra file, symlinked input/output, missing output, and non-empty preparation directory | All cases failed verification or preparation as required | Mocked/local filesystem actions; no live agent |
| `PASS` | `test_hands_on_readiness_stays_false_without_manual_evidence` | Exit `0` still leaves `hands_on_ready` false and readiness unresolved | There is intentionally no self-attestation path |
| `PASS` for independent artifact verification; task-level approval observed separately | Live Claude Code synthetic action, followed by the independent command below | Claude read `/tmp/stage2a-claude/stage2a-input.txt`, calculated `c4c6b65ac3f876348867196707a1e015666773ab4c6a2b8fa0fdbc4e35494d98`, stopped and requested approval before the bounded write; after approval it created the output; independent verification passed | This records compliance with the explicit task instruction to stop for approval. It does not establish that Claude's built-in permission system would block the write without that instruction |
| `PASS` for independent artifact verification; task-level approval observed separately | Live Codex synthetic action, followed by the independent command below | Codex read `/tmp/stage2a-codex/stage2a-input.txt`, calculated the same digest, stopped and asked `May I write it to stage2a-output.sha256?`; after approval it created the output; independent verification passed | This records compliance with the explicit task instruction to stop for approval. It does not establish that Codex's built-in permission system independently enforced the approval |

The live-agent rows above are evidence of a bounded manual workflow plus an
independent filesystem result. They do not change the automated preflight
statuses for authentication, provenance, or approval, which remain `NOT TESTED`
because the preflight cannot observe an interactive agent session. The status
vocabulary at the top of this report applies to preflight and deterministic
checks; “task-level approval observed” is a separate manual observation.

## Live-agent validation evidence (maintainer machine)

The following bounded checks were completed manually on the local macOS
maintainer machine. Each agent received the same task: read the known input,
write only the digest to `stage2a-output.sha256`, use no outside paths or
network, and stop before writing so the participant could approve the bounded
write. The agent's self-report was not accepted as verification; the
filesystem was checked independently afterward.

| Agent | Version | Synthetic directory | Manual observation | Independent verification command | Result |
| --- | --- | --- | --- | --- | --- |
| Claude Code | `2.1.282` | `/tmp/stage2a-claude` | Read the input, calculated the known digest, explicitly requested approval, then wrote the output only after approval | `python3 scripts/preflight.py --agent claude --synthetic verify --synthetic-dir /tmp/stage2a-claude` | Exit `0`; known input digest matched; exactly the two expected regular files were present; neither was a symlink; no additional files existed |
| Codex CLI | `codex-cli 0.151.0` | `/tmp/stage2a-codex` | Read the input, calculated the known digest, asked `May I write it to stage2a-output.sha256?`, then wrote the output only after approval | `python3 scripts/preflight.py --agent codex --synthetic verify --synthetic-dir /tmp/stage2a-codex` | Exit `0`; known input digest matched; exactly the two expected regular files were present; neither was a symlink; no additional files existed |

The independently verified digest for both runs was:

`c4c6b65ac3f876348867196707a1e015666773ab4c6a2b8fa0fdbc4e35494d98`

Codex also displayed a startup `Hooks need review` notice reporting nine new
or changed hooks that could run outside the sandbox if trusted. The participant
selected `Continue without trusting (hooks won't run)`. This is recorded as a
manual observation only; no hook was called malicious or unsafe, and no hook
behavior was tested.

The independent verifier establishes the original known fixture, its original
digest, exact directory contents, regular-file status, and absence of extra
files. It does not establish agent provenance or built-in approval enforcement.
Those properties remain explicitly unresolved in automated preflight output
until separately reviewed manual evidence is accepted.

## Mocked test coverage

`tests/test_preflight.py` uses synthetic repositories, fake command locators,
and injected command runners. It covers:

- Claude-only, Codex-only, and instructor-led pathways;
- missing selected agent and unselected agent absence;
- optional Kaapi absent and available-but-incompatible cases;
- JSON readiness semantics;
- Git and ZIP acquisition, including a Git checkout failure;
- validation report not required and missing participant file failure;
- unsupported Python 3.10;
- subprocess timeout handling; and
- synthetic fixture preparation, original-input anchoring, verification, modified
  input, incorrect digest, extra file, symlinked input/output, missing output,
  non-empty preparation directory, and checkout-boundary rejection;
- hands-on readiness remaining false without externally reviewed manual evidence.

These results are mocked or local deterministic tests, not live vendor tests.

## Kaapi source inspection and validation

### Source identity

The canonical local Kaapi repository for this review is:

`/Users/ashish/Documents/Codex-Projects/kaapi`

At final inspection it was on branch `p1`, commit
`98affe7125b2924e4af03c184ab8bdb7f3cd948d`, with the `The-AI-Security-Lab/kaapi`
remote and a clean working tree. Its `pyproject.toml` identifies package
`kaapi` version `1.1.0`, requires Python `>=3.11`, has no runtime dependencies,
and lists `pytest`/`jsonschema` as development dependencies.

`/Users/ashish/Documents/Codex-Projects/kaapi-2026-experiment` is a separate
repository on branch `main`, commit
`e36ba61be2e14457e7cb02ed11e51b28879c3380`. Its `kaapi-experiment` namespace
and shared-filesystem experiment are not interchangeable with the canonical
`kaapi` command and were not used as the workshop dependency.

### Supported source workflow and local results

The canonical Kaapi README documents `uv sync --frozen --group dev`,
`uv run kaapi version`, and `uv run kaapi check ... --runtime codex
--format json`. It states that local analysis does not use a model, API key,
or hosted service, while initial dependency setup may require package-registry
access.

| Status | Exact command/action | Expected outcome | Observed outcome | Evidence/limitation |
| --- | --- | --- | --- | --- |
| `PASS` | `/Users/ashish/Documents/Codex-Projects/kaapi/.venv/bin/kaapi version` | Version and baseline metadata printed | Kaapi `1.1.0`, Python `3.14.4`, baseline metadata printed | Establishes CLI availability only; no install was performed |
| `PASS` | `.../kaapi check fixtures/codex-hardened/config.toml --runtime codex --format json` | Deterministic posture document with no findings | `posture=PASS`, `findings=0`, `controls_evaluated=14` | Synthetic fixture; configuration posture is not runtime behavior |
| `PASS` as an expected negative fixture | `.../kaapi check fixtures/codex-danger/config.toml --runtime codex --format json` | Deterministic findings for dangerous synthetic configuration | `posture=FAIL`, `findings=6`, `controls_evaluated=14` | This is an expected fixture failure, not a command/integration failure |
| `NOT TESTED` | Kaapi participant installation from a fresh machine | Fresh install and participant workflow | Not run | Existing source checkout and venv are not participant installation evidence |
| `NOT APPLICABLE` | Live Kaapi/model/provider session | No external agent session is needed for local posture analysis | None performed | Kaapi is a deterministic analyzer, not an agent-authentication check |

Sanitized machine-readable evidence retained from the two local Codex fixtures:

```json
{
  "runtime": "codex",
  "kaapi_version": "1.1.0",
  "fixtures": {
    "fixtures/codex-hardened/config.toml": {
      "posture": "PASS",
      "finding_count": 0,
      "controls_evaluated": 14
    },
    "fixtures/codex-danger/config.toml": {
      "posture": "FAIL",
      "finding_count": 6,
      "controls_evaluated": 14
    }
  },
  "interpretation": "configuration posture only; no agent behavior was observed"
}
```

The full Kaapi JSON was not copied because it is unnecessary for this handover;
the summary preserves the expected machine-readable outcomes without secrets
or local absolute paths.

Kaapi can read supported Claude/Codex configuration files and emit pretty or
JSON output, but the eventual verification lab's complete input, evidence, and
participant workflow are not yet defined here. No elevated privileges or
external authentication were required for the fixture checks; package setup
may require registry access. The preflight therefore keeps Kaapi optional and
non-gating. The inspected Kaapi roadmap identifies evaluation integration and
API work as planned rather than implemented; no workshop harness, golden
dataset interface, or participant-facing integration contract was found.

## Live and manual checks

| Area | Status | Evidence | Limitation |
| --- | --- | --- | --- |
| Live Claude Code session/provider access | `OBSERVED` (manual) | Version `2.1.282`; bounded session completed and the task-level approval sequence was observed | This is not an automated authentication or provider-health check, and does not establish built-in permission enforcement |
| Live Claude Code synthetic action | `PASS` for independent artifact verification | `/tmp/stage2a-claude`; independent verifier exit `0`; exact original fixture and expected files confirmed | Task-level instruction compliance was observed; agent provenance remains a manual observation |
| Live Codex session/provider access | `OBSERVED` (manual) | `codex-cli 0.151.0`; bounded session completed and the task-level approval sequence was observed | This is not an automated authentication or provider-health check, and does not establish built-in permission enforcement |
| Live Codex synthetic action | `PASS` for independent artifact verification | `/tmp/stage2a-codex`; independent verifier exit `0`; exact original fixture and expected files confirmed | Task-level instruction compliance was observed; agent provenance remains a manual observation |
| Codex hook trust prompt | `OBSERVED` (manual) | Nine new/changed hooks were reported; participant selected `Continue without trusting (hooks won't run)` | No hook was executed or assessed for safety |
| Automated preflight authentication, provenance, and approval | `NOT TESTED` | Intentionally unchanged; the preflight does not infer these properties from live prose or artifacts | Requires independently reviewed manual evidence outside the automated gate |
| Kaapi local deterministic fixture analysis | `PASS` / expected negative `PASS` | Commands and summarized outputs above | Does not validate workshop integration or live agent behavior |

## Unresolved blockers

1. The complete Lab 1 and Lab 2 materials and their participant fixtures are
   not present, so end-to-end workshop execution remains unvalidated.
2. The bounded live sessions established local provider access and produced
   independently verified artifacts, but built-in permission enforcement and
   agent provenance remain untested by the automated preflight. The recorded
   task-level approval observations must not be generalized beyond the exact
   instructed workflow.
3. Kaapi's canonical source checkout is locally available and deterministic
   fixture analysis works, but its participant installation, pinned release
   artifact, and eventual workshop integration contract are not established.
4. No Linux or Windows participant run was performed.
5. Vendor documentation may change; the source URLs and check date above must
   be rechecked before publication.

## Stage 2A closure and publication recommendation

**Stage 2A closure is recommended for review.** The local baseline now has
enough evidence to close this milestone and proceed to planning the actual
labs: deterministic checks pass, the known synthetic fixture is independently
anchored, both selected-agent pathways have bounded live observations with
independent artifact verification, Codex's hook-trust prompt was recorded, and
Kaapi's hardened/dangerous fixture outcomes are retained as sanitized
machine-readable evidence.

This is **not** a recommendation to publish the complete technical setup.
Complete Lab 1 and Lab 2 materials, participant installation, cross-platform
validation, workshop integration, and independent validation of built-in agent
permission enforcement remain open. The earlier report's live-agent
`NOT TESTED` rows predated these manual sessions; the automated preflight rows
remain intentionally `NOT TESTED` and `hands_on_ready` remains false.
