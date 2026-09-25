"""Workshop-side consumer contract for the Kaapi P2.1 public API.

This module deliberately contains no configuration or policy evaluation logic.
Kaapi owns that analysis; the workshop owns requirement grading and the evidence
boundary between configuration and runtime outcomes.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any


PASS = "PASS"
FAIL = "FAIL"
INCONCLUSIVE = "INCONCLUSIVE"
NOT_TESTED = "NOT_TESTED"

CONFIGURED_AUTHORITY = "configured_authority"
RESOLVED_PERMITTED_CAPABILITIES = "resolved_permitted_capabilities"
OBSERVED_RUNTIME_BEHAVIOUR = "observed_runtime_behavior"
INDEPENDENT_RUNTIME_OUTCOME = "independently_verified_runtime_outcome"

EVIDENCE_CATEGORIES = {
    CONFIGURED_AUTHORITY,
    RESOLVED_PERMITTED_CAPABILITIES,
    OBSERVED_RUNTIME_BEHAVIOUR,
    INDEPENDENT_RUNTIME_OUTCOME,
}
CONFIGURATION_CATEGORIES = {
    CONFIGURED_AUTHORITY,
    RESOLVED_PERMITTED_CAPABILITIES,
}

Analyzer = Callable[..., dict[str, Any]]


def _result(
    grade: str,
    *,
    limitations: list[str] | None = None,
    evidence: dict[str, Any] | None = None,
    kaapi: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "grade": grade,
        "limitations": limitations or [],
        "evidence": evidence or {},
        "kaapi": kaapi or {},
    }


def _invalid_requirement(requirement: Mapping[str, Any]) -> str | None:
    control_id = requirement.get("control_id")
    policy = requirement.get("policy")
    required = requirement.get("required_evidence")
    if not isinstance(control_id, str) or not control_id:
        return "The security requirement must declare a control_id."
    if not isinstance(policy, Mapping):
        return "The security requirement must declare a Kaapi policy object."
    if not isinstance(required, list) or any(not isinstance(item, str) for item in required):
        return "The security requirement must declare required_evidence names."
    unknown = sorted(set(required) - EVIDENCE_CATEGORIES)
    if unknown:
        return f"Unsupported evidence categories: {', '.join(unknown)}."
    missing = sorted(CONFIGURATION_CATEGORIES - set(required))
    if missing:
        return f"Configuration evidence is incomplete: {', '.join(missing)}."
    return None


def _matching_requirement(
    document: Mapping[str, Any], control_id: str
) -> Mapping[str, Any] | None:
    policy_result = document.get("organisation_policy")
    if not isinstance(policy_result, Mapping):
        return None
    requirements = policy_result.get("requirements")
    if not isinstance(requirements, list):
        return None
    for item in requirements:
        if isinstance(item, Mapping) and item.get("control_id") == control_id:
            return item
    return None


def _configuration_evidence(
    document: Mapping[str, Any],
    policy_requirement: Mapping[str, Any],
) -> dict[str, Any]:
    resolved = document.get("resolved_capability")
    if not isinstance(resolved, Mapping):
        configured_authority = None
        permitted_capabilities = None
    else:
        configured_authority = {
            name: resolved.get(name)
            for name in (
                "configured_mode",
                "mode_uncertain",
                "bypasses",
                "bypass_locked",
                "permission_counts",
            )
            if name in resolved
        }
        permitted_capabilities = {
            name: resolved.get(name)
            for name in ("capabilities", "sandbox", "network", "mcp")
            if name in resolved
        }
    return {
        CONFIGURED_AUTHORITY: (
            {
                **configured_authority,
                "policy_requirement": dict(policy_requirement),
            }
            if configured_authority is not None
            else None
        ),
        RESOLVED_PERMITTED_CAPABILITIES: permitted_capabilities,
        OBSERVED_RUNTIME_BEHAVIOUR: None,
        INDEPENDENT_RUNTIME_OUTCOME: None,
    }


def assess_configuration(
    config_content: str | bytes,
    *,
    runtime: str,
    security_requirement: Mapping[str, Any],
    source: str | None = None,
    analyzer: Analyzer | None = None,
) -> dict[str, Any]:
    """Consume one configuration through Kaapi's public ``analyze_text`` API.

    A PASS means only that the declared configuration requirement passed with
    the two configuration evidence categories present. Runtime behavior and
    independently verified outcomes are never inferred from Kaapi output.
    ``analyzer`` is an internal test seam; production use leaves it unset.
    """

    invalid = _invalid_requirement(security_requirement)
    if invalid:
        return _result(NOT_TESTED, limitations=[invalid])

    control_id = security_requirement["control_id"]
    policy = security_requirement["policy"]
    required = set(security_requirement["required_evidence"])
    if analyzer is None:
        from kaapi import analyze_text

        analyzer = analyze_text

    try:
        document = analyzer(
            config_content,
            runtime=runtime,
            source=source,
            policy=policy,
        )
    except Exception as exc:  # Kaapi's public API has no exported error type.
        return _result(
            NOT_TESTED,
            limitations=[
                f"Kaapi public API rejected or could not assess the input ({type(exc).__name__})."
            ],
        )

    if not isinstance(document, Mapping):
        return _result(
            INCONCLUSIVE,
            limitations=["Kaapi returned a non-structured assessment result."],
        )

    policy_requirement = _matching_requirement(document, control_id)
    if policy_requirement is None:
        return _result(
            INCONCLUSIVE,
            limitations=["Kaapi returned no matching policy requirement."],
            kaapi={
                "posture": document.get("posture"),
                "policy_verdict": (document.get("organisation_policy") or {}).get("verdict"),
            },
        )

    evidence = _configuration_evidence(document, policy_requirement)
    missing_configuration = [
        name
        for name in sorted(CONFIGURATION_CATEGORIES)
        if evidence.get(name) in (None, {})
    ]
    if missing_configuration:
        return _result(
            INCONCLUSIVE,
            limitations=[
                "Kaapi did not provide required configuration evidence: "
                + ", ".join(missing_configuration)
                + "."
            ],
            evidence=evidence,
        )

    runtime_required = sorted(required - CONFIGURATION_CATEGORIES)
    if runtime_required:
        return _result(
            INCONCLUSIVE,
            limitations=[
                "Required runtime evidence is not supplied by configuration analysis: "
                + ", ".join(runtime_required)
                + "."
            ],
            evidence=evidence,
            kaapi={
                "posture": document.get("posture"),
                "policy_verdict": (document.get("organisation_policy") or {}).get("verdict"),
                "policy_status": policy_requirement.get("status"),
            },
        )

    observed = policy_requirement.get("observed")
    if isinstance(observed, Mapping) and (
        observed.get("policy_runtime_supported") is False
        or observed.get("control_available") is False
    ):
        return _result(
            NOT_TESTED,
            limitations=["The selected policy requirement is unsupported for this runtime."],
            evidence=evidence,
            kaapi={
                "posture": document.get("posture"),
                "policy_verdict": (document.get("organisation_policy") or {}).get("verdict"),
                "policy_status": policy_requirement.get("status"),
            },
        )

    status = policy_requirement.get("status")
    grade = PASS if status == PASS else FAIL if status == FAIL else INCONCLUSIVE
    limitations = []
    if grade in {PASS, FAIL}:
        limitations.append(
            "Configuration analysis establishes configured authority and resolved "
            "permitted capabilities only; it does not verify runtime enforcement "
            "or independently verified runtime outcomes."
        )
    else:
        limitations.append("Kaapi returned no deterministic PASS or FAIL policy status.")
    return _result(
        grade,
        limitations=limitations,
        evidence=evidence,
        kaapi={
            "posture": document.get("posture"),
            "policy_verdict": (document.get("organisation_policy") or {}).get("verdict"),
            "policy_status": status,
        },
    )
