# Securing AI Coding Agents: From Guardrails to Verification

A 90-minute, hands-on workshop from [AI Security Lab](https://www.aisecuritylab.com/).
You will inspect an AI coding-agent configuration, constrain its authority,
let one supported agent attempt a synthetic security fix, and independently
verify both the fix and its change scope.

## Start here

1. Read the [Participant Lab Guide](docs/participant-guide.md).
2. Choose **one** path: Claude Code, Codex, or instructor-led fallback. You do
   not need both agents.
3. From this repository root, prepare the pinned workshop dependency, then run
   preflight:

   ```sh
   python3 scripts/workshop.py setup
   python3 scripts/preflight.py --agent claude
   # or: python3 scripts/preflight.py --agent codex
   # or: python3 scripts/preflight.py --agent none --kaapi skip
   ```

4. Complete [Lab 1](docs/lab-1-configuration-assessment.md), then
   [Lab 2](docs/lab-2-live-agent-workflow.md).
5. Interpret the evidence before cleaning the generated lab state.

Python 3.11 or newer, Git, and `uv` are required for the hands-on path. Setup
uses anonymous public access to obtain the exact validated Kaapi revision into
`.workshop-deps/`; it does not install Kaapi globally. Docker, a VM, a
GitHub account, and both coding agents are not required. Agent authentication
depends on your provider and organization; if it is unavailable, use the
instructor-led path rather than weakening the lab boundary.

The workflow is designed for macOS and Windows/PowerShell. Primary end-to-end
validation for this release was performed on macOS; the PowerShell commands
and generated paths are test-covered but have not received equivalent live
agent acceptance.

## What you will learn

```text
Inspect → Constrain → Run → Observe → Verify → Decide
```

- **Lab 1 — Govern an AI coding agent with configuration analysis** asks:
  “Should we let this agent operate like this?” You use Kaapi, AI Security
  Lab's open-source coding-agent security analysis tool, with supplied
  synthetic configurations.
- **Lab 2 — Verify an AI-generated security fix** asks: “The agent says the
  vulnerability is fixed. How do we know?” You independently check the
  security property and final change scope.

Together: govern what the agent can do, and verify what it actually delivers.
This is not a generic Claude Code or Codex tutorial.

## What you will do

Choose Claude Code **or** Codex and stay on that path:

- Assess risky, hardened, and malformed synthetic configurations in Lab 1.
- Prepare a disposable Lab 2 workspace and generated agent boundary.
- Give the selected agent an exact synthetic remediation task.
- Exit the agent before verification.
- Independently verify the lookup security property and the strict
  `app/lookup.py` change boundary.
- Investigate any scope failure before cleanup.

The other vendor's fixtures are optional exploration. Never use a production
repository, production credentials, real incident data, or a real employee or
customer configuration.

## How to read results

The labs keep four evidence categories separate:

1. configured authority;
2. resolved permitted capabilities;
3. observed runtime behavior; and
4. independently verified runtime outcomes.

Kaapi supplies configuration evidence for categories 1 and 2. It does not
prove runtime enforcement or the delivered result. Agent self-report is not
independent evidence. Lab 2 verifies a bounded final outcome; it does not
provide complete runtime telemetry.

In Lab 2, security and scope are independent. Overall `PASS` requires both
security `PASS` and scope `PASS`. For unexpected paths:

```text
Detect → Explain → Classify → Decide → Fix / Explicitly Allow
```

Do not whitelist what you have not explained, and do not delete unexpected
files before interpreting the evidence.

## Time box

| Activity | Required time |
| --- | ---: |
| Orientation, choose one path, preflight | 10 minutes |
| Lab 1 fixture inspection and assessment | 20 minutes |
| Lab 1 evidence debrief | 10 minutes |
| Lab 2 prepare, agent remediation, and exit | 25 minutes |
| Independent verification and decision | 15 minutes |
| Cleanup and wrap-up | 10 minutes |

Optional other-vendor exploration is outside the required 90-minute path.

## Troubleshooting

Use the [Lab Guide troubleshooting section](docs/participant-guide.md#h-troubleshooting).
Do not bypass the verifier to obtain `PASS`. `NOT TESTED` and `INCONCLUSIVE`
are meaningful outcomes, not failures to hide.

## Cleanup

Cleanup is the final lab step, not a way to erase a scope failure. First exit
the agent, interpret and optionally preserve sanitized evidence, then remove
only the exact generated run and isolated agent-home paths. Local deletion of
an authenticated temporary home is not proof of provider-side token/session
revocation. See [Safe cleanup](docs/participant-guide.md#i-safe-cleanup).

## Instructor and engineering resources

- [Know before you go](docs/know-before-you-go.md)
- [Hands-on setup and preflight](docs/hands-on-setup.md)
- [Participant Lab Guide](docs/participant-guide.md)
- [Project knowledge base](knowledge/index.md)

The knowledge base links engineering design and provenance records. Internal
milestone documents are supporting evidence, not prerequisites for participants.

## Licensing and contributions

See [Contributing](CONTRIBUTING.md), [Workshop materials license](LICENSE),
[Code license](LICENSE-CODE.md), and [Notices](NOTICE.md). The custom license
drafts require confirmation of the legal rights holder and legal review before
being treated as final. Third-party tools retain their own licenses.
