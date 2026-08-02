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
from model_contract import validate_repo  # noqa: E402


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
        path = fixture / "source/model-claims/luna-bounded-landing-fit-hypothesis.json"
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
        path = fixture / "source/model-claims/luna-bounded-landing-fit-hypothesis.json"
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


if __name__ == "__main__":
    unittest.main()
