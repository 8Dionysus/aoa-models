from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_model_fit_projections import build_expected  # noqa: E402
from check_live_codex_catalog import check_catalog  # noqa: E402
from model_contract import validate_repo  # noqa: E402
from query_model_fit import query_model_fit, validate_query_result  # noqa: E402


class ModelContractTests(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        fixture = Path(temporary.name) / "aoa-models"
        shutil.copytree(
            ROOT,
            fixture,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".ruff_cache"),
        )
        return temporary, fixture

    def test_repository_is_valid(self) -> None:
        self.assertEqual(validate_repo(ROOT), [])

    def test_projection_builder_matches_files(self) -> None:
        expected = build_expected(ROOT)
        self.assertTrue(expected)
        for relative, content in expected.items():
            self.assertEqual((ROOT / relative).read_text(encoding="utf-8"), content)

    def test_configuration_fingerprint_is_enforced(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = next((fixture / "source/model-realizations").glob("*luna*max*.json"))
        record = json.loads(path.read_text(encoding="utf-8"))
        record["configuration"]["context"]["nominal_context_tokens"] += 1
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(fixture)
        self.assertTrue(any("configuration fingerprint mismatch" in issue for issue in issues))

    def test_reviewed_claim_requires_independent_review(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = fixture / "source/model-claims/luna-bounded-landing-fit-transfer-hypothesis-v2.json"
        claim = json.loads(path.read_text(encoding="utf-8"))
        claim["confidence_posture"] = "reviewed"
        claim["lifecycle"]["state"] = "reviewed"
        claim["independent_review_refs"] = []
        claim["lifecycle"]["history"].append(
            {
                "from": "hypothesis",
                "to": "reviewed",
                "at": "2026-08-02T00:00:00Z",
                "reason": "unsupported direct promotion",
                "evidence_refs": [],
            }
        )
        path.write_text(json.dumps(claim, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(fixture)
        self.assertTrue(any("unsupported lifecycle transition hypothesis -> reviewed" in issue for issue in issues))
        self.assertTrue(any("requires an independent review" in issue for issue in issues))

    def test_lifecycle_history_must_be_contiguous(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = fixture / "source/model-claims/luna-bounded-landing-fit-transfer-hypothesis-v2.json"
        claim = json.loads(path.read_text(encoding="utf-8"))
        claim["lifecycle"]["state"] = "stale"
        claim["freshness"]["status"] = "stale"
        claim["lifecycle"]["history"].append(
            {
                "from": "observed",
                "to": "stale",
                "at": "2026-08-15T00:00:00Z",
                "reason": "broken history fixture",
                "evidence_refs": [],
            }
        )
        path.write_text(json.dumps(claim, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(fixture)
        self.assertTrue(any("does not continue from hypothesis" in issue for issue in issues))

    def test_generated_projection_has_no_activation_or_acceptance_authority(self) -> None:
        for path in (ROOT / "generated/model-fit-projections").glob("*.json"):
            projection = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(projection["authority"]["informational_only"])
            self.assertFalse(projection["authority"]["activation_authority"])
            self.assertFalse(projection["authority"]["proof_authority"])
            self.assertFalse(projection["authority"]["acceptance_authority"])
            self.assertEqual(projection["effect_family"], "read")

    def test_v2_study_requires_observe_only_usage_metering(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = fixture / "source/model-studies/external-codex-landing-readiness-2026-08-01.json"
        study = json.loads(path.read_text(encoding="utf-8"))
        study["schema_version"] = "aoa_model_study_v2"
        path.write_text(json.dumps(study, indent=2) + "\n", encoding="utf-8")

        issues = validate_repo(fixture)

        self.assertTrue(
            any("usage_metering" in issue and "required property" in issue for issue in issues)
        )

    def test_current_claim_cannot_reference_stale_realization(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = fixture / "source/model-claims/luna-bounded-landing-fit-transfer-hypothesis-v2.json"
        claim = json.loads(path.read_text(encoding="utf-8"))
        claim["subject_realization_refs"][0] = (
            "source/model-realizations/"
            "openai-gpt-5.6-luna-codex-0.146.0-chatgpt-max-readonly.json"
        )
        path.write_text(json.dumps(claim, indent=2) + "\n", encoding="utf-8")

        issues = validate_repo(fixture)

        self.assertTrue(
            any("current claim references non-current realization" in issue for issue in issues)
        )

    def test_live_codex_catalog_accepts_exact_current_realization(self) -> None:
        realization_ref = (
            "source/model-realizations/"
            "openai-gpt-5.6-luna-codex-0.147.0-chatgpt-xhigh-workspace-write.json"
        )
        catalog = {
            "models": [
                {
                    "slug": "gpt-5.6-luna",
                    "supported_reasoning_levels": [
                        {"effort": effort}
                        for effort in ("low", "medium", "high", "xhigh", "max")
                    ],
                    "context_window": 272000,
                    "effective_context_window_percent": 95,
                    "multi_agent_version": "v1",
                    "supported_in_api": True,
                }
            ]
        }

        result, ok = check_catalog(
            ROOT,
            catalog,
            "codex-cli 0.147.0",
            (realization_ref,),
        )

        self.assertTrue(ok)
        self.assertEqual(result["required_failures"], [])
        assessment = next(
            item for item in result["assessments"] if item["realization_ref"] == realization_ref
        )
        self.assertEqual(assessment["currentness"], "current")

    def test_live_codex_catalog_rejects_active_version_drift(self) -> None:
        catalog = {
            "models": [
                {
                    "slug": "gpt-5.6-luna",
                    "supported_reasoning_levels": [
                        {"effort": effort}
                        for effort in ("low", "medium", "high", "xhigh", "max")
                    ],
                    "context_window": 272000,
                    "effective_context_window_percent": 95,
                    "multi_agent_version": "v1",
                    "supported_in_api": True,
                }
            ]
        }

        result, ok = check_catalog(ROOT, catalog, "codex-cli 0.148.0")

        self.assertFalse(ok)
        self.assertEqual(len(result["active_mismatches"]), 4)

    def test_property_query_returns_informational_current_candidate(self) -> None:
        query = {
            "schema_version": "aoa_model_fit_query_v1",
            "task_family": "landing",
            "runtime_product": "codex-cli",
            "runtime_version": "0.147.0",
            "reasoning_effort": "xhigh",
            "sandbox_mode": "workspace-write",
            "required_tools": ["shell-read", "workspace-write"],
            "required_mcp_servers": [],
        }

        result = query_model_fit(ROOT, query)

        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["candidates"][0]["model_slug"], "gpt-5.6-luna")
        self.assertTrue(result["authority"]["informational_only"])
        self.assertFalse(result["authority"]["activation_authority"])
        self.assertFalse(result["authority"]["routing_authority"])
        self.assertFalse(result["authority"]["proof_authority"])
        self.assertFalse(result["authority"]["acceptance_authority"])
        validate_query_result(ROOT, result)


if __name__ == "__main__":
    unittest.main()
