from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from research_intake_contract import (  # noqa: E402
    canonical_digest,
    validate_research_intake,
)
from research_source_dossiers import expected_content as expected_dossier_content  # noqa: E402


def minimal_packet(
    run_id: str = "recon-run:example/provider-a",
    *,
    provider: str = "provider-a",
    family: str = "family-a",
    source_class: str = "independent_benchmark",
) -> dict:
    return {
        "$schema": "https://schemas.aoa.local/models/recon-run.schema.json",
        "schema_version": "aoa_model_recon_run_v1",
        "kind": "ReconRun",
        "recon_run_id": run_id,
        "title": f"Bounded external recon for {provider}",
        "status": "captured",
        "intake_owner": "aoa-models",
        "authority": {
            "pre_canon": True,
            "automatic_promotion": False,
            "routing_authority": False,
            "activation_authority": False,
            "proof_authority": False,
            "acceptance_authority": False,
        },
        "question": "Which bounded observation survives the stated configuration limits?",
        "scope": {
            "subject_labels": [provider, family],
            "target_kinds": ["benchmark_result"],
            "capture_interval": {
                "start": "2026-08-30T00:00:00Z",
                "end": "2026-08-30T01:00:00Z",
            },
            "inclusion_criteria": ["Primary result with an exposed method"],
            "exclusion_criteria": ["Dependent retelling without new evidence"],
            "generality_probe": {
                "mode": "different_family_or_provider",
                "subject_labels": [provider, family],
                "rationale": "Provider, family, and source class are ordinary packet data.",
            },
        },
        "method": {
            "name": "External Model Web Recon Lens",
            "version": "test",
            "artifacts": [
                {
                    "relation": "method",
                    "ref": "docs/RESEARCH_INTAKE.md",
                    "content_digest": None,
                }
            ],
        },
        "lineage": {
            "predecessor_artifacts": [],
            "supersedes_recon_run_refs": [],
        },
        "promotion_policy": "pre_canon_no_automatic_promotion",
        "source_captures": [
            {
                "source_id": "source-a",
                "title": "Primary benchmark report",
                "uri": "https://example.invalid/benchmark",
                "source_class": source_class,
                "publisher": provider,
                "captured_at": "2026-08-30T00:05:00Z",
                "published_at": "2026-08-29T00:00:00Z",
                "updated_at": None,
                "effective_interval": None,
                "temporal_notes": "No separate effective interval was published.",
                "mutable_surface": True,
                "origin_group": "origin-a",
                "propagation_role": "origin",
                "dependency_refs": [],
                "segments": [
                    {
                        "segment_id": "result-table",
                        "locator": "Result table under the benchmark heading",
                        "content_digest": None,
                        "digest_unavailable_reason": "Fixture does not archive page bytes.",
                    }
                ],
                "access_notes": "Public page.",
                "selection_context": "Selected as a primary method-backed source.",
            }
        ],
        "observations": [
            {
                "observation_id": "observation-a",
                "statement": "The named configuration produced one bounded benchmark result.",
                "target_kind": "benchmark_result",
                "subject": {
                    "completeness": "partial",
                    "family": family,
                    "models": [f"{family}-model"],
                    "provider": provider,
                    "product": "api",
                    "snapshot": None,
                    "runtime": None,
                    "owner_realization_refs": [],
                    "additional_dimensions": {},
                },
                "configuration": {
                    "completeness": "partial",
                    "route": None,
                    "reasoning_effort": "medium",
                    "context_policy": None,
                    "tools": [],
                    "permissions": [],
                    "prompt": None,
                    "scaffold": None,
                    "runbook": None,
                    "harness": "benchmark-harness",
                    "instrument_revision": "v1",
                    "grader": "deterministic-tests",
                    "additional_dimensions": {},
                },
                "outcome": {
                    "requested": "Complete the bounded benchmark task.",
                    "executed": "A task attempt was recorded.",
                    "artifact": "A candidate artifact was produced.",
                    "verified": "The benchmark verifier returned a result.",
                    "reported": "The report published the aggregate result.",
                    "termination": "clean",
                    "measurements": [
                        {
                            "metric": "success",
                            "value": True,
                            "unit": None,
                            "denominator": "one bounded task attempt",
                            "notes": "Fixture value, not a model claim.",
                        }
                    ],
                    "additional_dimensions": {},
                },
                "source_segment_refs": [
                    {"source_id": "source-a", "segment_id": "result-table"}
                ],
                "confounds": ["The exact provider snapshot was not disclosed."],
                "configuration_gaps": ["Snapshot and route are unknown."],
                "transfer_limits": ["Bounded to the cited task and harness revision."],
                "counterevidence_refs": [],
                "supersedes": [],
                "evidence_posture": "method_backed_observation",
                "disposition": "cluster",
                "observed_interval": {
                    "start": "2026-08-29T00:00:00Z",
                    "end": "2026-08-29T01:00:00Z",
                },
            }
        ],
        "clusters": [
            {
                "cluster_id": "cluster-a",
                "label": "One bounded method-backed result",
                "observation_refs": ["observation-a"],
                "counterevidence_refs": [],
                "independent_origin_groups": ["origin-a"],
                "supported_scope": "The result applies only to the cited task and harness revision.",
                "transfer_limits": ["No cross-task or cross-snapshot transfer is established."],
                "unresolved_configuration_gaps": ["The exact snapshot is unknown."],
                "posture": "method_backed_observation",
                "disposition": "watch",
                "next_action": "Seek an independent origin or exact-subject replication.",
            }
        ],
        "tensions": [],
        "method_pressures": [],
        "revisit_triggers": ["The provider publishes an exact snapshot identifier."],
        "created_at": "2026-08-30T02:00:00Z",
        "updated_at": "2026-08-30T02:00:00Z",
    }


class ResearchIntakeContractTests(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        fixture = Path(temporary.name) / "aoa-models"
        (fixture / "schemas").mkdir(parents=True)
        shutil.copy2(ROOT / "schemas/recon-run.schema.json", fixture / "schemas")
        shutil.copy2(
            ROOT / "schemas/research-automation-artifact.schema.json",
            fixture / "schemas",
        )
        shutil.copy2(
            ROOT / "schemas/research-source-dossier-catalog.schema.json",
            fixture / "schemas",
        )
        (fixture / "research-intake/recon-runs").mkdir(parents=True)
        return temporary, fixture

    def write_packet(self, fixture: Path, name: str, packet: dict) -> None:
        path = fixture / "research-intake/recon-runs" / name
        path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        dossier_path = fixture / "generated/research-source-dossiers.json"
        dossier_path.parent.mkdir(parents=True, exist_ok=True)
        dossier_path.write_text(expected_dossier_content(fixture), encoding="utf-8")

    def test_repository_research_intake_is_valid(self) -> None:
        self.assertEqual(validate_research_intake(ROOT), [])

    def test_new_providers_are_data_not_code_branches(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        self.write_packet(fixture, "provider-a.json", minimal_packet())
        self.write_packet(
            fixture,
            "provider-b.json",
            minimal_packet(
                "recon-run:example/provider-b",
                provider="provider-b",
                family="family-b",
                source_class="primary_issue",
            ),
        )

        self.assertEqual(validate_research_intake(fixture), [])

    def test_missing_source_segment_is_rejected(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        packet["observations"][0]["source_segment_refs"][0]["segment_id"] = "missing"
        self.write_packet(fixture, "broken.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(any("source segment does not exist" in issue for issue in issues))

    def test_partial_subject_requires_configuration_gap(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        packet["observations"][0]["configuration_gaps"] = []
        self.write_packet(fixture, "broken.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(any("requires configuration_gaps" in issue for issue in issues))

    def test_source_dependency_cycle_is_rejected(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        second = copy.deepcopy(packet["source_captures"][0])
        second["source_id"] = "source-b"
        second["origin_group"] = "origin-b"
        second["dependency_refs"] = ["source-a"]
        second["propagation_role"] = "dependent"
        packet["source_captures"][0]["dependency_refs"] = ["source-b"]
        packet["source_captures"][0]["propagation_role"] = "dependent"
        packet["source_captures"].append(second)
        self.write_packet(fixture, "cycle.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(any("source dependency cycle" in issue for issue in issues))

    def test_cluster_cannot_invent_independent_origin(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        packet["clusters"][0]["independent_origin_groups"] = ["invented-origin"]
        self.write_packet(fixture, "broken.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(any("origin group is not supported" in issue for issue in issues))

    def test_cluster_counterevidence_supports_its_independent_origin(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        counter_source = copy.deepcopy(packet["source_captures"][0])
        counter_source["source_id"] = "source-b"
        counter_source["origin_group"] = "origin-b"
        packet["source_captures"].append(counter_source)
        counter_observation = copy.deepcopy(packet["observations"][0])
        counter_observation["observation_id"] = "observation-b"
        counter_observation["source_segment_refs"] = [
            {"source_id": "source-b", "segment_id": "result-table"}
        ]
        packet["observations"].append(counter_observation)
        packet["clusters"][0]["counterevidence_refs"] = ["observation-b"]
        packet["clusters"][0]["independent_origin_groups"] = [
            "origin-a",
            "origin-b",
        ]
        self.write_packet(fixture, "valid.json", packet)

        self.assertEqual(validate_research_intake(fixture), [])

    def test_dependent_restatement_does_not_add_independent_origin(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        dependent_source = copy.deepcopy(packet["source_captures"][0])
        dependent_source["source_id"] = "source-b"
        dependent_source["origin_group"] = "retelling-publisher"
        dependent_source["propagation_role"] = "dependent"
        dependent_source["dependency_refs"] = ["source-a"]
        packet["source_captures"].append(dependent_source)
        retelling = copy.deepcopy(packet["observations"][0])
        retelling["observation_id"] = "observation-b"
        retelling["source_segment_refs"] = [
            {"source_id": "source-b", "segment_id": "result-table"}
        ]
        packet["observations"].append(retelling)
        packet["clusters"][0]["observation_refs"].append("observation-b")
        packet["clusters"][0]["independent_origin_groups"].append(
            "retelling-publisher"
        )
        self.write_packet(fixture, "broken.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(any("origin group is not supported" in issue for issue in issues))

    def test_stale_local_artifact_digest_is_rejected(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        method_path = fixture / "docs/method.md"
        method_path.parent.mkdir(parents=True)
        method_path.write_text("bounded method\n", encoding="utf-8")
        packet = minimal_packet()
        packet["method"]["artifacts"] = [
            {
                "relation": "method",
                "ref": "docs/method.md",
                "content_digest": "sha256:" + ("0" * 64),
            }
        ]
        self.write_packet(fixture, "broken.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(any("local artifact digest mismatch" in issue for issue in issues))

    def test_outcome_decomposition_is_structural(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        del packet["observations"][0]["outcome"]["verified"]
        self.write_packet(fixture, "broken.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(
            any("verified" in issue and "required property" in issue for issue in issues)
        )

    def test_outcome_axes_may_diverge_without_implied_completion(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        packet["observations"][0]["outcome"].update(
            {
                "artifact": "A partial artifact exists.",
                "verified": None,
                "reported": "The external report nevertheless claimed completion.",
                "termination": "Runtime ended before verification.",
            }
        )
        self.write_packet(fixture, "valid.json", packet)

        self.assertEqual(validate_research_intake(fixture), [])

    def test_search_probe_resolves_retained_evidence(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        packet["search_probes"] = [
            {
                "probe_id": "probe-a",
                "question": "Does the bounded result have qualified retained evidence?",
                "searched_at": "2026-08-30T01:30:00Z",
                "query_variants": ["bounded benchmark primary source"],
                "source_roles_sought": ["primary method-backed report"],
                "result_state": "qualified_evidence_found",
                "source_refs": ["source-a"],
                "observation_refs": ["observation-a"],
                "limitations": [],
                "next_action": "Seek an independent replication.",
            }
        ]
        self.write_packet(fixture, "valid.json", packet)

        self.assertEqual(validate_research_intake(fixture), [])

    def test_qualified_search_probe_cannot_point_to_unretained_result(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        packet["search_probes"] = [
            {
                "probe_id": "probe-a",
                "question": "Does the bounded result have qualified retained evidence?",
                "searched_at": "2026-08-30T01:30:00Z",
                "query_variants": ["bounded benchmark primary source"],
                "source_roles_sought": ["primary method-backed report"],
                "result_state": "qualified_evidence_found",
                "source_refs": [],
                "observation_refs": [],
                "limitations": [],
                "next_action": "Retain the source and observation before claiming coverage.",
            }
        ]
        self.write_packet(fixture, "broken.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(any("requires source and observation refs" in issue for issue in issues))

    def test_negative_search_probe_requires_a_limit_statement(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        packet["search_probes"] = [
            {
                "probe_id": "probe-a",
                "question": "Was a qualified cross-configuration replication located?",
                "searched_at": "2026-08-30T01:30:00Z",
                "query_variants": ["cross configuration replication"],
                "source_roles_sought": ["independent benchmark"],
                "result_state": "no_qualified_source_found",
                "source_refs": [],
                "observation_refs": [],
                "limitations": [],
                "next_action": "Repeat the search after the next release cycle.",
            }
        ]
        self.write_packet(fixture, "broken.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(any("requires limitations" in issue for issue in issues))

    def test_missing_cross_run_supersession_is_rejected(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packet = minimal_packet()
        packet["observations"][0]["supersedes"] = [
            {
                "recon_run_id": "recon-run:missing/run",
                "observation_id": "observation-a",
            }
        ]
        self.write_packet(fixture, "broken.json", packet)

        issues = validate_research_intake(fixture)

        self.assertTrue(any("supersedes missing run" in issue for issue in issues))

    def test_pre_canon_path_cannot_be_direct_owner_evidence(self) -> None:
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        self.write_packet(fixture, "valid.json", minimal_packet())
        claim_directory = fixture / "source/model-claims"
        claim_directory.mkdir(parents=True)
        (claim_directory / "invalid.json").write_text(
            json.dumps(
                {
                    "kind": "ModelClaim",
                    "evidence_refs": [
                        {"uri": "research-intake/recon-runs/provider-a.json"}
                    ],
                }
            ),
            encoding="utf-8",
        )

        issues = validate_research_intake(fixture)

        self.assertTrue(any("cannot be direct owner evidence" in issue for issue in issues))

    def test_canonical_digest_is_order_independent(self) -> None:
        packet = minimal_packet()
        reordered = {key: packet[key] for key in reversed(packet)}

        self.assertEqual(canonical_digest(packet), canonical_digest(reordered))


if __name__ == "__main__":
    unittest.main()
