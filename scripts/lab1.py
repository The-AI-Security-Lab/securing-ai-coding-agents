"""Run the Stage 2C Lab 1 configuration-assessment practice.

Lab 1 deliberately consumes only configuration and policy evidence.  Runtime
behavior and independently verified runtime outcomes remain absent until Lab 2.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.kaapi_consumer import (
        CONFIGURED_AUTHORITY,
        EVIDENCE_CATEGORIES,
        FAIL,
        INCONCLUSIVE,
        INDEPENDENT_RUNTIME_OUTCOME,
        NOT_TESTED,
        OBSERVED_RUNTIME_BEHAVIOUR,
        PASS,
        RESOLVED_PERMITTED_CAPABILITIES,
        assess_configuration,
    )
except ModuleNotFoundError as exc:  # Support direct `python3 scripts/lab1.py`.
    if exc.name != "scripts":
        raise
    from kaapi_consumer import (
        CONFIGURED_AUTHORITY,
        EVIDENCE_CATEGORIES,
        FAIL,
        INCONCLUSIVE,
        INDEPENDENT_RUNTIME_OUTCOME,
        NOT_TESTED,
        OBSERVED_RUNTIME_BEHAVIOUR,
        PASS,
        RESOLVED_PERMITTED_CAPABILITIES,
        assess_configuration,
    )


NOT_APPLICABLE = "NOT APPLICABLE"
REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "fixtures" / "lab1"
POLICY_PATH = FIXTURE_ROOT / "policy.json"
CASES = ("risky", "hardened", "malformed")
RUNTIMES = {"claude": "claude-code", "codex": "codex"}
FIXTURE_FILES = {
    "claude": "settings.json",
    "codex": "config.toml",
}
TEACHING_QUESTIONS = {
    "risky": "Can you identify the concerning authority/capability before seeing the assessment?",
    "hardened": "Does the candidate now meet the declared configuration baseline?",
    "malformed": "What should we conclude when the evidence cannot be safely assessed?",
}


def _load_policy(policy_path: Path) -> dict[str, Any]:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("Lab 1 policy must be a JSON object.")
    if policy.get("required_evidence") != [
        CONFIGURED_AUTHORITY,
        RESOLVED_PERMITTED_CAPABILITIES,
    ]:
        raise ValueError("Lab 1 requires configuration evidence only.")
    runtimes = policy.get("runtimes")
    if not isinstance(runtimes, dict) or set(runtimes) != set(RUNTIMES.values()):
        raise ValueError("Lab 1 policy must define Claude Code and Codex requirements.")
    return policy


def fixture_path(agent: str, case: str, fixture_root: Path = FIXTURE_ROOT) -> Path:
    if agent not in RUNTIMES:
        raise ValueError(f"Unknown agent path: {agent}")
    if case not in CASES:
        raise ValueError(f"Unknown Lab 1 case: {case}")
    return fixture_root / agent / case / FIXTURE_FILES[agent]


def selected_cases(agent: str) -> tuple[str, ...]:
    if agent not in RUNTIMES:
        raise ValueError(f"Unknown agent path: {agent}")
    return CASES


def _security_requirement(runtime: str, policy: dict[str, Any]) -> dict[str, Any]:
    runtime_policy = policy["runtimes"][runtime]
    return {
        "control_id": runtime_policy["control_id"],
        "policy": runtime_policy["policy"],
        "required_evidence": policy["required_evidence"],
    }


def _evidence_presence(evidence: dict[str, Any]) -> dict[str, str]:
    return {
        category: "PRESENT" if evidence.get(category) not in (None, {}) else "MISSING"
        for category in sorted(EVIDENCE_CATEGORIES)
    }


def _conclusion(grade: str) -> str:
    if grade == PASS:
        return "The declared configuration baseline passes, subject to runtime verification."
    if grade == FAIL:
        return "The declared configuration baseline does not pass."
    if grade == INCONCLUSIVE:
        return "The available evidence is insufficient for a pass/fail conclusion."
    if grade == NOT_TESTED:
        return "The configuration could not be safely assessed."
    return "No conclusion is available."


def _display_status(grade: str) -> str:
    return "NOT TESTED" if grade == NOT_TESTED else grade


def participant_result(
    agent: str,
    case: str,
    *,
    fixture_root: Path = FIXTURE_ROOT,
    policy_path: Path = POLICY_PATH,
    analyzer: Any = None,
) -> dict[str, Any]:
    runtime = RUNTIMES[agent]
    policy = _load_policy(policy_path)
    path = fixture_path(agent, case, fixture_root)
    try:
        result = assess_configuration(
            path.read_bytes(),
            runtime=runtime,
            security_requirement=_security_requirement(runtime, policy),
            source=f"synthetic:lab1:{runtime}:{case}",
            analyzer=analyzer,
        )
    except ModuleNotFoundError as exc:
        if exc.name != "kaapi" or analyzer is not None:
            raise
        result = {
            "grade": NOT_TESTED,
            "limitations": [
                "Kaapi's public API is unavailable in this environment; no configuration assessment was run."
            ],
            "evidence": {},
            "kaapi": {},
        }
    try:
        fixture_display = str(path.relative_to(REPO_ROOT))
    except ValueError:
        fixture_display = str(path)
    return {
        "agent": agent,
        "runtime": runtime,
        "case": case,
        "fixture": fixture_display,
        "teaching_question": TEACHING_QUESTIONS[case],
        "configuration_baseline": _display_status(result["grade"]),
        "within_task_scope": NOT_APPLICABLE,
        "independently_verified_security_outcome": NOT_APPLICABLE,
        "kaapi_posture": result["kaapi"].get("posture", "MISSING"),
        "policy_status": result["kaapi"].get("policy_status", "MISSING"),
        "evidence_presence": _evidence_presence(result["evidence"]),
        "conclusion": _conclusion(result["grade"]),
        "formal_result": result,
    }


def assess_selected_agent(
    agent: str,
    case: str | None = None,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    cases = (case,) if case is not None else selected_cases(agent)
    return [participant_result(agent, item, **kwargs) for item in cases]


def _human_result(result: dict[str, Any]) -> str:
    presence = result["evidence_presence"]
    lines = [
        f"{result['case'].title()} — {result['runtime']}",
        f"Teaching question: {result['teaching_question']}",
        f"Configuration meets baseline: {result['configuration_baseline']}",
        f"Kaapi posture: {result['kaapi_posture']}",
        f"Policy status: {result['policy_status']}",
        f"Stayed within task scope: {result['within_task_scope']}",
        f"Independently verified security outcome: {result['independently_verified_security_outcome']}",
        "Evidence: "
        + "; ".join(f"{name}={presence[name]}" for name in sorted(presence)),
        f"Conclusion: {result['conclusion']}",
    ]
    limitations = result["formal_result"]["limitations"]
    if limitations:
        lines.append("Evidence note: " + " ".join(limitations))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=sorted(RUNTIMES), required=True)
    parser.add_argument("--case", choices=CASES)
    parser.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args()
    results = assess_selected_agent(args.agent, args.case)
    if args.format == "json":
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print("\n\n".join(_human_result(result) for result in results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
