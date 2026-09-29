# Securing AI Coding Agents: From Guardrails to Verification

A hands-on workshop from [AI Security Lab](https://www.aisecuritylab.com/).
The complete participant journey is in the [Participant Lab Guide](docs/participant-guide.md).

## Start here

From this repository root, choose one agent and run:

```sh
python3 scripts/workshop.py setup
python3 scripts/preflight.py --agent codex
```

Use `--agent claude` for Claude Code, or `--agent none --kaapi skip` for the
instructor-led path. Then follow the guide through Lab 1, Lab 2, independent
verification, and cleanup.

The workshop uses synthetic fixtures and disposable workspaces. Python 3.11+,
Git, and `uv` are required for the hands-on path. Primary end-to-end validation
was performed on macOS; PowerShell command generation is test-covered but the
complete Windows live-agent path has not been independently validated.

## What the labs teach

- Lab 1 assesses supplied configuration evidence against a declared baseline.
  It is not runtime proof.
- Lab 2 gives one selected agent a bounded remediation task, then independently
  verifies both the defined security property and final change scope.

Overall Lab 2 `PASS` requires both security `PASS` and scope `PASS`. Unexpected
artifacts follow `Detect → Explain → Classify → Decide → Fix / Explicitly Allow`;
do not whitelist unexplained files.

## Help

Use the [Participant Guide](docs/participant-guide.md), its
[troubleshooting section](docs/participant-guide.md#7-troubleshooting-and-recovery),
and [hands-on setup notes](docs/hands-on-setup.md). Engineering provenance is
available from the [project knowledge base](knowledge/index.md).

## Cleanup

Finish with the cleanup command in the [Participant Guide](docs/participant-guide.md).

## Troubleshooting

Use the troubleshooting and recovery guidance in the [Participant Guide](docs/participant-guide.md).

See [Contributing](CONTRIBUTING.md), [Workshop materials license](LICENSE),
[Code license](LICENSE-CODE.md), and [Notices](NOTICE.md) for project details.
