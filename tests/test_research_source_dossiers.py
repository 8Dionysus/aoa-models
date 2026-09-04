from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from research_automation import build_capture_snapshot, write_immutable_json  # noqa: E402
from research_source_dossiers import (  # noqa: E402
    OUTPUT_PATH,
    build_catalog,
    find_dossiers,
    render_catalog,
    validate_research_source_dossiers,
)
from test_research_automation import capture_request  # noqa: E402
from test_research_intake_contract import minimal_packet  # noqa: E402


class ResearchSourceDossierTests(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        fixture = Path(temporary.name) / "aoa-models"
        (fixture / "schemas").mkdir(parents=True)
        for name in (
            "recon-run.schema.json",
            "research-automation-artifact.schema.json",
            "research-source-dossier-catalog.schema.json",
        ):
            shutil.copy2(ROOT / "schemas" / name, fixture / "schemas" / name)
        (fixture / "research-intake/recon-runs").mkdir(parents=True)
        return temporary, fixture

    def write_run(self, fixture: Path, name: str, packet: dict) -> None:
        path = fixture / "research-intake/recon-runs" / name
        path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    def write_catalog(self, fixture: Path) -> None:
        path = fixture / OUTPUT_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_catalog(build_catalog(fixture)), encoding="utf-8")

    def test_normalized_exact_uri_groups_appearances_without_cross_uri_aliasing(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        first = minimal_packet()
        first["source_captures"][0]["uri"] = "HTTPS://EXAMPLE.INVALID/source#first"
        second = minimal_packet("recon-run:example/provider-b", provider="provider-b")
        second["source_captures"][0]["uri"] = "https://example.invalid/source#second"
        self.write_run(fixture, "first.json", first)
        self.write_run(fixture, "second.json", second)

        catalog = build_catalog(fixture)

        self.assertEqual(catalog["counts"]["dossiers"], 1)
        self.assertEqual(catalog["dossiers"][0]["appearance_count"], 2)
        self.assertEqual(catalog["dossiers"][0]["run_count"], 2)
        self.assertEqual(
            catalog["dossiers"][0]["canonical_uri"],
            "https://example.invalid/source",
        )
        self.assertEqual(
            catalog["identity_policy"]["cross_uri_aliasing"],
            "review_required_not_automatic",
        )

    def test_single_mutable_source_is_visible_without_noisy_attention(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        self.write_run(fixture, "one.json", minimal_packet())

        dossier = build_catalog(fixture)["dossiers"][0]

        self.assertEqual(dossier["currentness"]["posture"], "mutable_metadata_only")
        self.assertFalse(dossier["currentness"]["freshness_asserted"])
        self.assertEqual(dossier["attention"], [])

    def test_snapshot_history_is_joined_but_does_not_assert_freshness(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        self.write_run(fixture, "one.json", packet)
        source_input = fixture / "source.txt"
        source_input.write_text("bounded source\n", encoding="utf-8")
        request = capture_request(
            {"kind": "whole_document", "value": None},
            source_id="source-a",
            media_type="text/plain",
        )
        request["source"]["uri"] = packet["source_captures"][0]["uri"]
        snapshot = build_capture_snapshot(
            request,
            root=fixture,
            input_path=source_input,
            input_ref="external-input:source.txt",
            captured_at="2026-08-30T03:00:00Z",
        )
        write_immutable_json(
            fixture / "research-intake/capture-snapshots/source.json",
            snapshot,
        )

        dossier = build_catalog(fixture)["dossiers"][0]

        self.assertEqual(dossier["currentness"]["posture"], "mutable_snapshot_backed")
        self.assertTrue(dossier["currentness"]["snapshot_backed"])
        self.assertFalse(dossier["currentness"]["freshness_asserted"])
        self.assertEqual(len(dossier["capture_snapshots"]), 1)

    def test_validator_detects_source_change_without_rebuild(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        self.write_run(fixture, "one.json", packet)
        self.write_catalog(fixture)
        packet["source_captures"][0]["title"] = "Changed source title"
        self.write_run(fixture, "one.json", packet)

        issues = validate_research_source_dossiers(fixture)

        self.assertTrue(any("catalog is stale" in issue for issue in issues))

    def test_query_resolves_uri_dossier_id_and_text(self) -> None:
        catalog = build_catalog(ROOT)
        example = catalog["dossiers"][0]

        self.assertEqual(find_dossiers(catalog, example["canonical_uri"]), [example])
        self.assertEqual(find_dossiers(catalog, example["dossier_id"]), [example])
        self.assertIn(example, find_dossiers(catalog, example["publishers"][0]))

    def test_repository_catalog_is_current(self) -> None:
        self.assertEqual(validate_research_source_dossiers(ROOT), [])


if __name__ == "__main__":
    unittest.main()
