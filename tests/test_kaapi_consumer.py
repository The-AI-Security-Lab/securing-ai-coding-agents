import json
import os
import unittest
from pathlib import Path
from typing import Any

from scripts.kaapi_consumer import (
    CONFIGURED_AUTHORITY,
    INDEPENDENT_RUNTIME_OUTCOME,
    INCONCLUSIVE,
    NOT_TESTED,
    OBSERVED_RUNTIME_BEHAVIOUR,
    PASS,
    RESOLVED_PERMITTED_CAPABILITIES,
    assess_configuration,
)


KAAPI_SOURCE = os.environ.get("KAAPI_P21_SOURCE")


@unittest.skipUnless(
    KAAPI_SOURCE,
    "set KAAPI_P21_SOURCE to the exact Kaapi P2.1 source checkout/archive",
)
class KaapiConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        assert KAAPI_SOURCE is not None
        cls.root = Path(KAAPI_SOURCE)
        cls.golden = cls.root / "evaluation" / "p2_1" / "golden"

    def case(self, name: str) -> tuple[dict[str, Any], bytes]:
        case_dir = self.golden / name
        manifest = json.loads(
            (case_dir / "evaluation.json").read_text(encoding="utf-8")
        )
        return manifest, (case_dir / manifest["config"]).read_bytes()

    def requirement(
        self,
        manifest: dict[str, Any],
        evidence: list[str] | None = None,
    ) -> dict[str, Any]:
        requirement = json.loads(
            json.dumps(manifest["security_requirement"])
        )
        requirement["required_evidence"] = evidence or [
            CONFIGURED_AUTHORITY,
            RESOLVED_PERMITTED_CAPABILITIES,
        ]
        return requirement

    def test_claude_and_codex_insecure_and_hardened_cases(self) -> None:
        for case_name in (
            "claude-insecure",
            "claude-hardened",
            "codex-insecure",
            "codex-hardened",
        ):
            with self.subTest(case=case_name):
                manifest, config = self.case(case_name)
                result = assess_configuration(
                    config,
                    runtime=manifest["runtime"],
                    security_requirement=self.requirement(manifest),
                    source=f"synthetic:{case_name}",
                )
                self.assertEqual(result["grade"], manifest["expected"]["grade"])
                self.assertEqual(
                    result["kaapi"]["posture"],
                    manifest["expected"]["security_posture"],
                )
                self.assertIn(CONFIGURED_AUTHORITY, result["evidence"])
                self.assertIn(
                    RESOLVED_PERMITTED_CAPABILITIES, result["evidence"]
                )
                self.assertIsNone(
                    result["evidence"][OBSERVED_RUNTIME_BEHAVIOUR]
                )
                self.assertIsNone(
                    result["evidence"][INDEPENDENT_RUNTIME_OUTCOME]
                )

    def test_malformed_configuration_is_not_tested(self) -> None:
        manifest, _ = self.case("claude-hardened")
        result = assess_configuration(
            '{"permissions": [}',
            runtime="claude-code",
            security_requirement=self.requirement(manifest),
        )
        self.assertEqual(result["grade"], NOT_TESTED)
        self.assertIn("could not assess", result["limitations"][0])

    def test_missing_configuration_evidence_is_inconclusive(self) -> None:
        manifest, config = self.case("claude-hardened")

        def incomplete_analyzer(*args: Any, **kwargs: Any) -> dict[str, Any]:
            return {
                "posture": "PASS",
                "organisation_policy": {
                    "requirements": [
                        {
                            "control_id": manifest["security_requirement"]["control_id"],
                            "status": "PASS",
                            "observed": {"sandbox_enabled": True},
                        }
                    ]
                },
                "resolved_capability": None,
            }

        result = assess_configuration(
            config,
            runtime="claude-code",
            security_requirement=self.requirement(manifest),
            analyzer=incomplete_analyzer,
        )
        self.assertEqual(result["grade"], INCONCLUSIVE)
        self.assertIn("resolved_permitted_capabilities", result["limitations"][0])

    def test_runtime_evidence_requirement_cannot_become_configuration_pass(self) -> None:
        manifest, config = self.case("claude-hardened")
        result = assess_configuration(
            config,
            runtime="claude-code",
            security_requirement=self.requirement(
                manifest,
                [
                    CONFIGURED_AUTHORITY,
                    RESOLVED_PERMITTED_CAPABILITIES,
                    OBSERVED_RUNTIME_BEHAVIOUR,
                ],
            ),
        )
        self.assertEqual(result["grade"], INCONCLUSIVE)
        self.assertIn("observed_runtime_behavior", result["limitations"][0])

    def test_unsupported_runtime_requirement_is_not_tested(self) -> None:
        manifest, config = self.case("claude-hardened")
        requirement = self.requirement(manifest)
        requirement["policy"]["runtimes"] = ["codex"]
        result = assess_configuration(
            config,
            runtime="claude-code",
            security_requirement=requirement,
        )
        self.assertEqual(result["grade"], NOT_TESTED)

    def test_repeated_assessment_is_deterministic(self) -> None:
        manifest, config = self.case("codex-insecure")
        requirement = self.requirement(manifest)
        first = assess_configuration(
            config,
            runtime="codex",
            security_requirement=requirement,
            source="synthetic:codex-insecure",
        )
        second = assess_configuration(
            config,
            runtime="codex",
            security_requirement=requirement,
            source="synthetic:codex-insecure",
        )
        self.assertEqual(first, second)

    def test_public_api_receives_unchanged_consumer_inputs(self) -> None:
        manifest, config = self.case("claude-hardened")
        requirement = self.requirement(manifest)
        calls: dict[str, Any] = {}

        def fake_analyzer(content: bytes, **kwargs: Any) -> dict[str, Any]:
            calls["content"] = content
            calls["kwargs"] = kwargs
            return {
                "posture": "PASS",
                "organisation_policy": {
                    "verdict": "PASS",
                    "requirements": [
                        {
                            "control_id": requirement["control_id"],
                            "status": "PASS",
                            "observed": {"sandbox_enabled": True},
                        }
                    ],
                },
                "resolved_capability": {
                    "configured_mode": "dontAsk",
                    "capabilities": ["tool.Read"],
                },
            }

        result = assess_configuration(
            config,
            runtime="claude-code",
            security_requirement=requirement,
            source="synthetic:consumer-contract",
            analyzer=fake_analyzer,
        )
        self.assertEqual(result["grade"], PASS)
        self.assertEqual(calls["content"], config)
        self.assertEqual(calls["kwargs"]["runtime"], "claude-code")
        self.assertEqual(calls["kwargs"]["source"], "synthetic:consumer-contract")
        self.assertEqual(calls["kwargs"]["policy"], requirement["policy"])


if __name__ == "__main__":
    unittest.main()
