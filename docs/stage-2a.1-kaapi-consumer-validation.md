# Stage 2A.1 Kaapi P2.1 Workshop Consumer Validation

Checked 2026-09-25. This is a consumer-validation record for the Stage 2A
workshop baseline. It does not redesign Stage 2A, modify Kaapi, begin Stage
2B, or implement Lab 1 or Lab 2.

## Candidate identity and boundaries

| Item | Recorded value |
| --- | --- |
| Workshop branch | `stage-2a.1-kaapi-consumer-validation` |
| Kaapi candidate branch | `codex/p2.1-workshop-evaluation` |
| Exact Kaapi commit consumed | `9a0bc6ba34576782675aded9e16b718c24fea9bd` |
| Candidate acquisition | `git archive 9a0bc6ba34576782675aded9e16b718c24fea9bd` into a disposable `/tmp` directory |
| API consumed | Public `kaapi.analyze_text(...)` only |
| Data | Synthetic configuration and synthetic requirement/policy data only |

The Kaapi checkout used to create the archive had pre-existing uncommitted
Wiki changes. No Kaapi files were modified by this validation, and those
changes were not included in the exact-commit archive. No credentials,
provider responses, production configuration, or customer data were used.

Kaapi's supplied candidate brief reports 150 candidate tests passed,
`git diff --check` passed, CLI/Python parity passed, and determinism and
fail-closed handling passed. The candidate test suite was not independently
rerun here because `uv` needed to download `jsonschema` and the environment
could not resolve PyPI. That is a validation limitation, not a candidate test
failure.

## Consumer integration

The workshop did not previously contain a P2.1 consumer contract. The
smallest practical integration adds [`scripts/kaapi_consumer.py`](../scripts/kaapi_consumer.py),
which:

1. passes configuration bytes, runtime, source label, and policy unchanged to
   the public `kaapi.analyze_text(...)` API;
2. reads the structured Kaapi posture and matching policy requirement without
   reimplementing Kaapi's security or policy logic;
3. grades only the configuration requirement as `PASS`, `FAIL`,
   `INCONCLUSIVE`, or `NOT_TESTED`; and
4. exposes four separate evidence categories:
   `configured_authority`, `resolved_permitted_capabilities`,
   `observed_runtime_behavior`, and
   `independently_verified_runtime_outcome`.

The last two categories are always absent from this configuration-only flow.
If either is required by a workshop requirement, the result is
`INCONCLUSIVE`; a Kaapi configuration `PASS` is never promoted to runtime or
outcome evidence.

The adapter catches errors from the public call and returns `NOT_TESTED` for
unassessable input without importing Kaapi's internal exception classes. This
is conservative and safe for malformed configuration, but the public API does
not expose a stable top-level exception contract. That remains an API /
integration limitation for future refinement.

## Baseline before integration

Command:

```console
python3 -m unittest discover -s tests -v && python3 scripts/wiki_check.py
```

Observed result: 33 existing workshop tests passed and the direct Wiki check
reported `WIKI CHECK: PASS (7 source/wiki pages, 1 log entries)`.

## Consumer validation cases

The new contract tests are in
[`tests/test_kaapi_consumer.py`](../tests/test_kaapi_consumer.py). They consume
the four synthetic P2.1 golden configurations from the exact candidate
archive; no Kaapi test code or private internals are copied into this
repository.

| Case | Runtime | Kaapi posture | Policy result | Workshop grade | Runtime/outcome evidence |
| --- | --- | --- | --- | --- | --- |
| Claude insecure | `claude-code` | `FAIL` | `FAIL` | `FAIL` | Not supplied; not inferred |
| Claude hardened | `claude-code` | `PASS` | `PASS` | `PASS` | Not supplied; not inferred |
| Codex insecure | `codex` | `FAIL` | `FAIL` | `FAIL` | Not supplied; not inferred |
| Codex hardened | `codex` | `PASS` | `PASS` | `PASS` | Not supplied; not inferred |

Additional consumer cases:

| Case | Expected result | Observed result |
| --- | --- | --- |
| Malformed Claude configuration | `NOT_TESTED`; no inferred security result | `NOT_TESTED` |
| Missing resolved-capability evidence | `INCONCLUSIVE` | `INCONCLUSIVE` |
| Requirement that also needs observed runtime behavior | Must not become configuration `PASS` | `INCONCLUSIVE` |
| Unsupported policy runtime | `NOT_TESTED` | `NOT_TESTED` |
| Repeated identical Codex assessment | Byte-equivalent structured result | Passed |
| Public API input forwarding | Original bytes, runtime, source, and policy preserved | Passed with an injected contract spy |

The four evidence categories remained distinct in every result. The
configuration categories contain Kaapi-derived evidence; runtime behavior and
independent runtime outcome remain unset and cannot satisfy a requirement.

## Tests and validation after integration

The exact consumer-validation command was:

```console
KAAPI_P21_SOURCE=/tmp/kaapi-p21-consumer.hBVvYY \
PYTHONPATH=/tmp/kaapi-p21-consumer.hBVvYY:. \
python3 -m unittest discover -s tests -v
```

Observed result: **40 tests passed**. This includes the 33 existing workshop
tests and 7 new consumer-contract tests.

Additional checks:

| Command | Result | Limitation |
| --- | --- | --- |
| `python3 -m py_compile scripts/preflight.py scripts/kaapi_consumer.py tests/test_preflight.py tests/test_kaapi_consumer.py tests/test_wiki_check.py` | Passed | Compilation only |
| `git diff --check` | Passed | Checks tracked diff whitespace; new untracked files were inspected through compilation and tests |
| `python3 scripts/wiki_check.py` | `WIKI CHECK: PASS (7 source/wiki pages, 1 log entries)` | Wiki was validated but not changed |
| `python3 scripts/preflight.py --agent claude` | Exit `0`; automated gate `CLEAR`; readiness unresolved; `hands_on_ready` `NO` | Executable/version only; auth and live action `NOT TESTED` |
| `python3 scripts/preflight.py --agent codex` | Exit `0`; automated gate `CLEAR`; readiness unresolved; `hands_on_ready` `NO` | Executable/version only; auth and live action `NOT TESTED` |
| `python3 scripts/preflight.py --agent none` | Exit `0`; instructor-led, not hands-on | Neither agent is required |

The Stage 2A synthetic negative regression coverage and independent artifact
verification remain unchanged and are included in the 40-test result.

## Failure and gap classification

| Finding | Classification | Disposition |
| --- | --- | --- |
| No mismatch was found for the tested P2.1 public API contract | None | No Kaapi correction required from this consumer run |
| Stage 2A had no workshop-side P2.1 consumer adapter | Expected integration gap; not a Stage 2A defect | Stage 2A was completed before P2.1 integration existed. Stage 2A.1 addressed the gap with the minimal adapter and contract tests; this is candidate infrastructure, not final Lab architecture |
| Kaapi public API does not export a stable top-level exception type for malformed input | `API / INTEGRATION MISMATCH` | Non-blocking limitation; adapter conservatively returns `NOT_TESTED` and does not import private Kaapi modules |
| Candidate dependency installation could not complete because PyPI DNS resolution was unavailable | None; environment limitation | Direct public-API consumer tests still ran from the exact archived source; candidate's reported 150-test result remains vendor-provided evidence |

No Kaapi-owned defect was reproduced. Consequently, no Kaapi minimal
reproduction is being returned as a correction request. The API limitation
above can be reproduced with the public call using malformed JSON, which
raises an internal exception class; the workshop does not depend on that
class name.

## Consumer conclusion

Kaapi P2.1 can be reliably consumed for the tested responsibility: deterministic
analysis of synthetic Claude Code and Codex configuration against a declared
policy, with structured configuration evidence and conservative handling of
malformed, unsupported, or insufficiently evidenced requirements.

It cannot establish runtime enforcement or independently verified runtime
outcomes. Those remain responsibilities for the future workshop harness and
labs. This validation therefore does not establish that a hardened
configuration was enforced by a live agent.

## Integration status

`CONSUMER VALIDATION PASSED WITH WORKSHOP CORRECTIONS`
