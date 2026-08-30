from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from research_automation import (  # noqa: E402
    ResearchAutomationError,
    assert_output_paths_absent,
    build_capture_snapshot,
    build_change_receipt,
    build_refreshed_snapshot,
    build_supersession_proposal,
    write_immutable_json,
)
from research_automation_contract import (  # noqa: E402
    finalize_artifact,
    load_json,
    validate_automation_artifact,
    validate_research_automation,
)
from test_research_intake_contract import minimal_packet  # noqa: E402


def capture_request(
    locator: dict,
    *,
    source_id: str = "source-example",
    source_class: str = "independent_document",
    media_type: str = "auto",
) -> dict:
    return {
        "schema_version": "aoa_model_research_capture_request_v1",
        "source": {
            "source_id": source_id,
            "title": "Bounded external source",
            "uri": "https://example.invalid/source",
            "source_class": source_class,
            "publisher": "example-publisher",
            "published_at": None,
            "updated_at": None,
            "effective_interval": None,
            "temporal_notes": "No separate effective interval is asserted.",
            "mutable_surface": True,
            "origin_group": "example-origin",
            "propagation_role": "origin",
            "dependency_refs": [],
            "access_notes": "Captured from a bounded offline input in this test.",
            "selection_context": "Exercises a generic source adapter and locator.",
        },
        "segment": {
            "segment_id": "bounded-segment",
            "locator": locator,
        },
        "retrieval": {
            "media_type": media_type,
            "max_bytes": 4096,
            "timeout_seconds": 5,
        },
    }


class ResearchAutomationTests(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        fixture = Path(temporary.name) / "aoa-models"
        (fixture / "schemas").mkdir(parents=True)
        for name in (
            "recon-run.schema.json",
            "research-automation-artifact.schema.json",
        ):
            shutil.copy2(ROOT / "schemas" / name, fixture / "schemas" / name)
        return temporary, fixture

    def test_text_line_capture_is_content_addressed_and_copy_ready(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        source = fixture / "source.md"
        source.write_text("heading\nfirst result\nsecond result\nend\n", encoding="utf-8")
        request = capture_request(
            {"kind": "line_range", "value": {"start": 2, "end": 3}},
            source_class="research_note",
            media_type="text/markdown",
        )

        snapshot = build_capture_snapshot(
            request,
            root=fixture,
            input_path=source,
            input_ref="external-input:source.md",
            captured_at="2026-08-30T08:00:00Z",
        )

        self.assertEqual(snapshot["retrieval"]["state"], "captured")
        self.assertEqual(snapshot["segment_result"]["state"], "captured")
        self.assertEqual(snapshot["gap_reasons"], [])
        self.assertEqual(
            snapshot["source_capture_candidate"]["segments"][0]["content_digest"],
            snapshot["segment_result"]["content_digest"],
        )
        self.assertEqual(validate_automation_artifact(snapshot, fixture), [])

    def test_http_capture_records_effective_uri_and_transport_metadata(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        request = capture_request(
            {"kind": "json_pointer", "value": "/result"},
            source_class="structured_endpoint",
            media_type="application/json",
        )

        class Response:
            status = 200
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "ETag": '"revision-a"',
            }

            def __enter__(self) -> Response:
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def geturl(self) -> str:
                return "https://example.invalid/effective-source"

            def read(self, size: int) -> bytes:
                return b'{"result":"bounded"}'[:size]

        with patch("research_automation.urlopen", return_value=Response()):
            snapshot = build_capture_snapshot(
                request,
                root=fixture,
                captured_at="2026-08-30T08:00:00Z",
            )

        self.assertEqual(snapshot["retrieval"]["transport"], "http")
        self.assertEqual(snapshot["retrieval"]["http_status"], 200)
        self.assertEqual(
            snapshot["retrieval"]["final_uri"],
            "https://example.invalid/effective-source",
        )
        self.assertEqual(snapshot["segment_result"]["state"], "captured")

    def test_json_pointer_refresh_classifies_content_change(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        first_input = fixture / "first.json"
        second_input = fixture / "second.json"
        first_input.write_text('{"result":{"value":1}}\n', encoding="utf-8")
        second_input.write_text('{"result":{"value":2}}\n', encoding="utf-8")
        request = capture_request(
            {"kind": "json_pointer", "value": "/result/value"},
            source_class="structured_api",
            media_type="application/json",
        )
        previous_path = fixture / "research-intake/capture-snapshots/first.json"
        previous = build_capture_snapshot(
            request,
            root=fixture,
            input_path=first_input,
            input_ref="external-input:first.json",
            captured_at="2026-08-30T08:00:00Z",
        )
        write_immutable_json(previous_path, previous)
        current_path = fixture / "research-intake/capture-snapshots/second.json"

        current = build_refreshed_snapshot(
            previous,
            previous_path,
            root=fixture,
            input_path=second_input,
            input_ref="external-input:second.json",
            captured_at="2026-08-30T09:00:00Z",
        )
        receipt = build_change_receipt(
            previous,
            previous_path,
            current,
            current_path,
            root=fixture,
        )

        self.assertEqual(receipt["classification"], "content_changed")
        self.assertEqual(receipt["review_disposition"], "review_required")
        self.assertEqual(current["predecessor_snapshot"], receipt["previous_snapshot"])
        self.assertFalse(receipt["automatic_supersession"])

    def test_html_id_refresh_records_missing_segment(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        first_input = fixture / "first.html"
        second_input = fixture / "second.html"
        first_input.write_text(
            '<main><section id="result"><strong>Bounded</strong> result</section></main>',
            encoding="utf-8",
        )
        second_input.write_text("<main><section>Moved result</section></main>", encoding="utf-8")
        request = capture_request(
            {"kind": "html_id", "value": "result"},
            source_class="web_page",
            media_type="text/html",
        )
        previous_path = fixture / "previous.json"
        previous = build_capture_snapshot(
            request,
            root=fixture,
            input_path=first_input,
            input_ref="external-input:first.html",
            captured_at="2026-08-30T08:00:00Z",
        )
        current = build_refreshed_snapshot(
            previous,
            previous_path,
            root=fixture,
            input_path=second_input,
            input_ref="external-input:second.html",
            captured_at="2026-08-30T09:00:00Z",
        )
        receipt = build_change_receipt(
            previous,
            previous_path,
            current,
            fixture / "current.json",
            root=fixture,
        )

        self.assertEqual(current["segment_result"]["state"], "missing")
        self.assertIn("html_id_not_found", current["gap_reasons"])
        self.assertEqual(receipt["classification"], "segment_became_missing")

    def test_unavailable_input_is_preserved_as_a_valid_state(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        request = capture_request(
            {"kind": "whole_document", "value": None},
            source_class="unavailable_archive",
        )

        snapshot = build_capture_snapshot(
            request,
            root=fixture,
            input_path=fixture / "missing.txt",
            input_ref="external-input:missing.txt",
            captured_at="2026-08-30T08:00:00Z",
        )

        self.assertEqual(snapshot["retrieval"]["state"], "unavailable")
        self.assertEqual(snapshot["segment_result"]["state"], "unavailable")
        self.assertIsNone(snapshot["segment_result"]["content_digest"])
        self.assertTrue(snapshot["gap_reasons"])
        self.assertEqual(validate_automation_artifact(snapshot, fixture), [])

    def test_capture_request_enforces_generic_resource_and_locator_bounds(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        oversized = capture_request({"kind": "whole_document", "value": None})
        automation_schema = load_json(
            fixture / "schemas/research-automation-artifact.schema.json"
        )
        maximum = automation_schema["$defs"]["capture_request"]["properties"][
            "retrieval"
        ]["properties"]["max_bytes"]["maximum"]
        oversized["retrieval"]["max_bytes"] = maximum + 1
        with self.assertRaisesRegex(ResearchAutomationError, "greater than the maximum"):
            build_capture_snapshot(
                oversized,
                root=fixture,
                captured_at="2026-08-30T08:00:00Z",
            )

        invalid_pointer = capture_request(
            {"kind": "json_pointer", "value": "/invalid~2escape"},
            media_type="application/json",
        )
        with self.assertRaisesRegex(ResearchAutomationError, "invalid escape"):
            build_capture_snapshot(
                invalid_pointer,
                root=fixture,
                captured_at="2026-08-30T08:00:00Z",
            )

    def test_presentation_only_change_does_not_imply_content_change(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        first_input = fixture / "first.txt"
        second_input = fixture / "second.txt"
        first_input.write_text("Alpha  \n", encoding="utf-8")
        second_input.write_text("Alpha\n", encoding="utf-8")
        request = capture_request(
            {"kind": "line_range", "value": {"start": 1, "end": 1}},
            media_type="text/plain",
        )
        previous_path = fixture / "previous.json"
        previous = build_capture_snapshot(
            request,
            root=fixture,
            input_path=first_input,
            input_ref="external-input:first.txt",
            captured_at="2026-08-30T08:00:00Z",
        )
        current = build_refreshed_snapshot(
            previous,
            previous_path,
            root=fixture,
            input_path=second_input,
            input_ref="external-input:second.txt",
            captured_at="2026-08-30T09:00:00Z",
        )
        receipt = build_change_receipt(
            previous,
            previous_path,
            current,
            fixture / "current.json",
            root=fixture,
        )

        self.assertEqual(receipt["classification"], "presentation_changed")
        self.assertEqual(receipt["review_disposition"], "review_optional")

    def test_immutable_writer_refuses_overwrite(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        target = fixture / "artifact.json"
        target.write_text("existing\n", encoding="utf-8")

        with self.assertRaisesRegex(ResearchAutomationError, "refusing to overwrite"):
            write_immutable_json(target, {"kind": "candidate"})

        self.assertEqual(target.read_text(encoding="utf-8"), "existing\n")
        with self.assertRaisesRegex(ResearchAutomationError, "must be distinct"):
            assert_output_paths_absent([fixture / "same.json", fixture / "same.json"])

    def test_cli_capture_and_refresh_are_end_to_end_and_append_only(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        request_path = fixture / "request.json"
        first_input = fixture / "first.json"
        second_input = fixture / "second.json"
        request_path.write_text(
            json.dumps(
                capture_request(
                    {"kind": "json_pointer", "value": "/value"},
                    media_type="application/json",
                )
            ),
            encoding="utf-8",
        )
        first_input.write_text('{"value":1}\n', encoding="utf-8")
        second_input.write_text('{"value":2}\n', encoding="utf-8")
        first_snapshot = fixture / "research-intake/capture-snapshots/first.json"
        second_snapshot = fixture / "research-intake/capture-snapshots/second.json"
        receipt_path = fixture / "research-intake/change-receipts/change.json"
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        capture_command = [
            sys.executable,
            "-B",
            str(ROOT / "scripts/research_intake.py"),
            "--root",
            str(fixture),
            "capture-source",
            "--request",
            str(request_path),
            "--output",
            str(first_snapshot),
            "--input-file",
            str(first_input),
            "--input-ref",
            "external-input:first.json",
            "--captured-at",
            "2026-08-30T08:00:00Z",
        ]

        captured = subprocess.run(
            capture_command,
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(captured.returncode, 0, captured.stderr)
        first_bytes = first_snapshot.read_bytes()
        refreshed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "scripts/research_intake.py"),
                "--root",
                str(fixture),
                "refresh-capture",
                "--previous",
                str(first_snapshot),
                "--snapshot-output",
                str(second_snapshot),
                "--receipt-output",
                str(receipt_path),
                "--input-file",
                str(second_input),
                "--input-ref",
                "external-input:second.json",
                "--captured-at",
                "2026-08-30T09:00:00Z",
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(refreshed.returncode, 0, refreshed.stderr)
        self.assertEqual(load_json(receipt_path)["classification"], "content_changed")

        refused = subprocess.run(
            capture_command,
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(refused.returncode, 1)
        self.assertIn("refusing to overwrite", refused.stderr)
        self.assertEqual(first_snapshot.read_bytes(), first_bytes)

    def test_repository_validator_recomputes_change_receipt(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        first_input = fixture / "first.json"
        second_input = fixture / "second.json"
        first_input.write_text('{"value":1}\n', encoding="utf-8")
        second_input.write_text('{"value":2}\n', encoding="utf-8")
        request = capture_request(
            {"kind": "json_pointer", "value": "/value"},
            media_type="application/json",
        )
        previous_path = fixture / "research-intake/capture-snapshots/first.json"
        current_path = fixture / "research-intake/capture-snapshots/second.json"
        receipt_path = fixture / "research-intake/change-receipts/change.json"
        previous = build_capture_snapshot(
            request,
            root=fixture,
            input_path=first_input,
            input_ref="external-input:first.json",
            captured_at="2026-08-30T08:00:00Z",
        )
        write_immutable_json(previous_path, previous)
        current = build_refreshed_snapshot(
            previous,
            previous_path,
            root=fixture,
            input_path=second_input,
            input_ref="external-input:second.json",
            captured_at="2026-08-30T09:00:00Z",
        )
        write_immutable_json(current_path, current)
        receipt = build_change_receipt(
            previous,
            previous_path,
            current,
            current_path,
            root=fixture,
        )
        write_immutable_json(receipt_path, receipt)
        self.assertEqual(validate_research_automation(fixture), [])

        tampered = copy.deepcopy(receipt)
        tampered["classification"] = "unchanged"
        tampered = finalize_artifact(tampered)
        receipt_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")

        issues = validate_research_automation(fixture)
        self.assertTrue(any("classification does not match" in issue for issue in issues))

    def test_repository_validator_reports_malformed_artifact_without_crashing(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        path = fixture / "research-intake/capture-snapshots/malformed.json"
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps({"kind": "ResearchCaptureSnapshot", "request": []}),
            encoding="utf-8",
        )

        issues = validate_research_automation(fixture)

        self.assertTrue(any("schema error" in issue for issue in issues))

    def test_supersession_proposal_is_review_only_and_does_not_mutate_runs(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        run_directory = fixture / "research-intake/recon-runs"
        run_directory.mkdir(parents=True)
        prior = minimal_packet("recon-run:example/prior")
        candidate = minimal_packet("recon-run:example/candidate")
        candidate["observations"][0]["observed_interval"] = {
            "start": "2026-08-30T00:00:00Z",
            "end": "2026-08-30T01:00:00Z",
        }
        prior_path = run_directory / "prior.json"
        candidate_path = run_directory / "candidate.json"
        prior_path.write_text(json.dumps(prior, indent=2) + "\n", encoding="utf-8")
        candidate_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
        before = (prior_path.read_bytes(), candidate_path.read_bytes())

        proposal = build_supersession_proposal(
            prior_path,
            "observation-a",
            candidate_path,
            "observation-a",
            relation="update",
            scope_dimensions=["observed_interval", "instrument_revision"],
            rationale=(
                "The later observation is reviewable as a bounded temporal update "
                "under the same target and subject dimensions."
            ),
            ambiguities=["The exact provider snapshot remains unavailable."],
            root=fixture,
            created_at="2026-08-30T10:00:00Z",
        )

        self.assertEqual(proposal["status"], "proposed")
        self.assertTrue(proposal["review_required"])
        self.assertFalse(proposal["automatic_application"])
        self.assertFalse(proposal["authority"]["source_mutation_authority"])
        self.assertEqual(before, (prior_path.read_bytes(), candidate_path.read_bytes()))
        proposal_path = fixture / "research-intake/supersession-proposals/proposal.json"
        write_immutable_json(proposal_path, proposal)
        self.assertEqual(validate_research_automation(fixture), [])

        cli_path = fixture / "research-intake/supersession-proposals/cli-proposal.json"
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "scripts/research_intake.py"),
                "--root",
                str(fixture),
                "suggest-supersession",
                "--prior-run",
                str(prior_path),
                "--prior-observation",
                "observation-a",
                "--candidate-run",
                str(candidate_path),
                "--candidate-observation",
                "observation-a",
                "--relation",
                "update",
                "--scope-dimension",
                "observed_interval",
                "--rationale",
                "The later bounded observation is packaged only for review.",
                "--created-at",
                "2026-08-30T10:01:00Z",
                "--output",
                str(cli_path),
            ],
            cwd=ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(load_json(cli_path)["status"], "proposed")
        self.assertEqual(before, (prior_path.read_bytes(), candidate_path.read_bytes()))
        self.assertEqual(validate_research_automation(fixture), [])

    def test_update_proposal_requires_shared_subject_scope(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        run_directory = fixture / "research-intake/recon-runs"
        run_directory.mkdir(parents=True)
        prior = minimal_packet("recon-run:example/prior")
        candidate = minimal_packet(
            "recon-run:example/candidate",
            provider="provider-b",
            family="family-b",
        )
        candidate["observations"][0]["observed_interval"] = {
            "start": "2026-08-30T00:00:00Z",
            "end": "2026-08-30T01:00:00Z",
        }
        prior_path = run_directory / "prior.json"
        candidate_path = run_directory / "candidate.json"
        prior_path.write_text(json.dumps(prior), encoding="utf-8")
        candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

        with self.assertRaisesRegex(
            ResearchAutomationError,
            "shared subject identity dimension",
        ):
            build_supersession_proposal(
                prior_path,
                "observation-a",
                candidate_path,
                "observation-a",
                relation="update",
                scope_dimensions=["provider"],
                rationale=(
                    "This intentionally unsafe update attempts to cross unrelated subjects "
                    "and must be rejected by the generic boundary."
                ),
                ambiguities=[],
                root=fixture,
                created_at="2026-08-30T10:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
