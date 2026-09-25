import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

from scripts.kaapi_consumer import (
    CONFIGURED_AUTHORITY,
    FAIL,
    INDEPENDENT_RUNTIME_OUTCOME,
    OBSERVED_RUNTIME_BEHAVIOUR,
    PASS,
    RESOLVED_PERMITTED_CAPABILITIES,
)
from scripts.lab1 import (
    CASES,
    POLICY_PATH,
    assess_selected_agent,
    participant_result,
    fixture_path,
    selected_cases,
)


KAAPI_P21_SOURCE = os.environ.get("KAAPI_P21_SOURCE")


class Lab1Tests(unittest.TestCase):
    def analyzer(self, content: bytes, **kwargs: Any) -> dict[str, Any]:
        if content.count(b"[") != content.count(b"]"):
            raise ValueError("malformed synthetic configuration")
        requirement = kwargs["policy"]["requirements"][0]
        if kwargs["runtime"] == "claude-code":
            status = FAIL if b'"enabled": false' in content else PASS
        else:
            status = FAIL if b"[mcp_servers.demo]" in content else PASS
        return {
            "posture": status,
            "organisation_policy": {
                "verdict": status,
                "requirements": [
                    {
                        "control_id": requirement["control_id"],
                        "status": status,
                        "observed": {"synthetic": True},
                    }
                ],
            },
            "resolved_capability": {
                "configured_mode": "synthetic",
                "capabilities": ["synthetic.read"],
                "sandbox": "synthetic",
                "network": "synthetic",
                "mcp": [],
            },
        }

    def test_policy_is_configuration_only_and_covers_both_runtimes(self) -> None:
        policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            policy["required_evidence"],
            [CONFIGURED_AUTHORITY, RESOLVED_PERMITTED_CAPABILITIES],
        )
        self.assertEqual(set(policy["runtimes"]), {"claude-code", "codex"})

    def test_each_selected_path_has_exactly_three_cases(self) -> None:
        self.assertEqual(selected_cases("claude"), CASES)
        self.assertEqual(selected_cases("codex"), CASES)
        for agent in ("claude", "codex"):
            results = assess_selected_agent(agent, analyzer=self.analyzer)
            self.assertEqual([result["case"] for result in results], list(CASES))

    def test_selected_path_does_not_require_other_vendor_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copy(POLICY_PATH, root / "policy.json")
            for case in CASES:
                destination = root / "claude" / case
                destination.mkdir(parents=True)
                shutil.copy(
                    fixture_path("claude", case),
                    destination / "settings.json",
                )
            results = assess_selected_agent(
                "claude",
                fixture_root=root,
                policy_path=root / "policy.json",
                analyzer=self.analyzer,
            )
            self.assertEqual([result["case"] for result in results], list(CASES))
            self.assertFalse((root / "codex").exists())

    def test_both_agent_fixtures_are_available(self) -> None:
        expected = {"risky": FAIL, "hardened": PASS, "malformed": "NOT TESTED"}
        for agent in ("claude", "codex"):
            for case in CASES:
                result = participant_result(agent, case, analyzer=self.analyzer)
                self.assertEqual(result["configuration_baseline"], expected[case])

    def test_result_preserves_missing_runtime_and_outcome_evidence(self) -> None:
        result = participant_result("claude", "hardened", analyzer=self.analyzer)
        self.assertEqual(result["evidence_presence"][OBSERVED_RUNTIME_BEHAVIOUR], "MISSING")
        self.assertEqual(result["evidence_presence"][INDEPENDENT_RUNTIME_OUTCOME], "MISSING")
        self.assertEqual(result["within_task_scope"], "NOT APPLICABLE")
        self.assertEqual(result["independently_verified_security_outcome"], "NOT APPLICABLE")

    def test_malformed_fixture_is_not_promoted_to_a_pass(self) -> None:
        for agent in ("claude", "codex"):
            result = participant_result(agent, "malformed", analyzer=self.analyzer)
            self.assertEqual(result["configuration_baseline"], "NOT TESTED")
            self.assertIn("could not be safely assessed", result["conclusion"])

    def test_repeated_assessment_is_deterministic(self) -> None:
        first = participant_result("codex", "hardened", analyzer=self.analyzer)
        second = participant_result("codex", "hardened", analyzer=self.analyzer)
        self.assertEqual(first, second)

    @unittest.skipUnless(
        KAAPI_P21_SOURCE,
        "set KAAPI_P21_SOURCE to the exact Kaapi P2.1 source snapshot",
    )
    def test_real_kaapi_assesses_all_lab1_fixtures(self) -> None:
        expected = {"risky": "FAIL", "hardened": "PASS", "malformed": "NOT_TESTED"}
        for agent in ("claude", "codex"):
            for case in CASES:
                with self.subTest(agent=agent, case=case):
                    result = participant_result(agent, case)
                    formal = result["formal_result"]
                    self.assertEqual(formal["grade"], expected[case])
                    if case == "malformed":
                        self.assertIsNone(
                            formal["evidence"].get("configured_authority")
                        )
                        self.assertIsNone(
                            formal["evidence"].get(
                                "resolved_permitted_capabilities"
                            )
                        )
                    else:
                        self.assertIn("configured_authority", formal["evidence"])
                        self.assertIn(
                            "resolved_permitted_capabilities", formal["evidence"]
                        )
                        self.assertIsNotNone(formal["kaapi"].get("policy_status"))
                    self.assertIsNone(
                        formal["evidence"].get("observed_runtime_behavior")
                    )
                    self.assertIsNone(
                        formal["evidence"].get(
                            "independently_verified_runtime_outcome"
                        )
                    )


if __name__ == "__main__":
    unittest.main()
