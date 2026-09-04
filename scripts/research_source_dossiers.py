#!/usr/bin/env python3
"""Build and validate a fast, generated read model for research sources."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import SplitResult, urlsplit, urlunsplit

from jsonschema import Draft202012Validator, FormatChecker


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ID = "https://schemas.aoa.local/models/research-source-dossier-catalog.schema.json"
SCHEMA_VERSION = "aoa_model_research_source_dossier_catalog_v1"
SCHEMA_PATH = Path("schemas/research-source-dossier-catalog.schema.json")
OUTPUT_PATH = Path("generated/research-source-dossiers.json")
RUN_DIRECTORY = Path("research-intake/recon-runs")
AUTOMATION_DIRECTORIES = (
    Path("research-intake/capture-snapshots"),
    Path("research-intake/change-receipts"),
    Path("research-intake/supersession-proposals"),
)


class ResearchSourceDossierError(ValueError):
    """Raised when dossier inputs cannot produce an honest read model."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def normalized_source_uri(uri: str) -> str:
    """Normalize only URI syntax that cannot change source identity.

    Cross-URI equivalence is intentionally not inferred. In particular, query
    strings, path case, and trailing slashes are preserved.
    """

    parsed = urlsplit(uri)
    if not parsed.scheme or not parsed.netloc:
        raise ResearchSourceDossierError(f"source URI must be absolute: {uri!r}")
    path = parsed.path or "/"
    normalized = SplitResult(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=path,
        query=parsed.query,
        fragment="",
    )
    return urlunsplit(normalized)


def source_dossier_id(canonical_uri: str) -> str:
    digest = hashlib.sha256(canonical_uri.encode("utf-8")).hexdigest()[:20]
    return f"research-source:{digest}"


def _relative_json_records(
    root: Path,
    directory: Path,
) -> Iterable[tuple[Path, dict[str, Any]]]:
    base = root / directory
    if not base.exists():
        return
    for path in sorted(base.glob("*.json")):
        try:
            yield path.relative_to(root), load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            raise ResearchSourceDossierError(
                f"cannot read {path.relative_to(root)}: {exc}"
            ) from exc


def _input_ref(kind: str, record_id: str, ref: Path, digest: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "record_id": record_id,
        "ref": ref.as_posix(),
        "content_digest": digest,
    }


def _new_dossier(canonical_uri: str) -> dict[str, Any]:
    return {
        "dossier_id": source_dossier_id(canonical_uri),
        "canonical_uri": canonical_uri,
        "uri_aliases": set(),
        "titles": set(),
        "publishers": set(),
        "source_classes": set(),
        "origin_groups": set(),
        "propagation_roles": set(),
        "mutable_surface_states": set(),
        "appearances": [],
        "capture_snapshots": [],
        "change_receipts": [],
        "supersession_proposals": [],
    }


def _dossier_for(
    dossiers: dict[str, dict[str, Any]],
    uri: str,
) -> dict[str, Any]:
    canonical_uri = normalized_source_uri(uri)
    if canonical_uri not in dossiers:
        dossiers[canonical_uri] = _new_dossier(canonical_uri)
    dossiers[canonical_uri]["uri_aliases"].add(uri)
    return dossiers[canonical_uri]


def _add_source_metadata(dossier: dict[str, Any], source: dict[str, Any]) -> None:
    for field, target in (
        ("title", "titles"),
        ("publisher", "publishers"),
        ("source_class", "source_classes"),
        ("origin_group", "origin_groups"),
        ("propagation_role", "propagation_roles"),
    ):
        value = source.get(field)
        if isinstance(value, str) and value:
            dossier[target].add(value)
    mutable = source.get("mutable_surface")
    if isinstance(mutable, bool):
        dossier["mutable_surface_states"].add(mutable)


def _segments(source: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "segment_id": segment["segment_id"],
            "locator": segment["locator"],
            "content_digest": segment.get("content_digest"),
            "digest_unavailable_reason": segment.get("digest_unavailable_reason"),
        }
        for segment in source.get("segments", [])
    ]


def _segment_digest_posture(segments: list[dict[str, Any]]) -> str:
    available = sum(segment.get("content_digest") is not None for segment in segments)
    if available == len(segments) and segments:
        return "all_segments_digest_backed"
    if available:
        return "some_segments_digest_backed"
    return "no_segment_digest"


def _observation_refs(run: dict[str, Any], source_id: str) -> list[str]:
    refs: list[str] = []
    for observation in run.get("observations", []):
        if any(
            ref.get("source_id") == source_id for ref in observation.get("source_segment_refs", [])
        ):
            refs.append(observation["observation_id"])
    return sorted(refs)


def _artifact_id(record: dict[str, Any]) -> str:
    value = record.get("capture_id") or record.get("receipt_id") or record.get("proposal_id")
    if not isinstance(value, str):
        raise ResearchSourceDossierError("automation artifact is missing its identity")
    return value


def _qualified_observation_uris(
    qualified: dict[str, Any],
    runs_by_id: dict[str, tuple[Path, dict[str, Any], str]],
) -> set[str]:
    run_id = qualified.get("recon_run_id")
    observation_id = qualified.get("observation_id")
    if run_id not in runs_by_id:
        return set()
    _, run, _ = runs_by_id[run_id]
    source_by_id = {source["source_id"]: source for source in run.get("source_captures", [])}
    observation = next(
        (
            candidate
            for candidate in run.get("observations", [])
            if candidate.get("observation_id") == observation_id
        ),
        None,
    )
    if observation is None:
        return set()
    uris: set[str] = set()
    for source_ref in observation.get("source_segment_refs", []):
        source = source_by_id.get(source_ref.get("source_id"))
        if source and isinstance(source.get("uri"), str):
            uris.add(normalized_source_uri(source["uri"]))
    return uris


def _latest_timestamp(values: Iterable[str]) -> str:
    timestamps = [value for value in values if value]
    if not timestamps:
        raise ResearchSourceDossierError("dossier has no recorded timestamp")
    return max(timestamps)


def _finalize_dossier(dossier: dict[str, Any]) -> dict[str, Any]:
    appearances = sorted(
        dossier["appearances"],
        key=lambda item: (item["captured_at"], item["recon_run_id"], item["source_id"]),
    )
    snapshots = sorted(
        dossier["capture_snapshots"],
        key=lambda item: (item["created_at"], item["capture_id"]),
    )
    receipts = sorted(
        dossier["change_receipts"],
        key=lambda item: (item["created_at"], item["receipt_id"]),
    )
    proposals = sorted(
        dossier["supersession_proposals"],
        key=lambda item: (item["created_at"], item["proposal_id"]),
    )
    mutable_states = dossier["mutable_surface_states"]
    mutable = True in mutable_states
    if len(mutable_states) > 1:
        currentness_posture = "mixed_mutability"
    elif not mutable:
        currentness_posture = "immutable_reference"
    elif not snapshots:
        currentness_posture = "mutable_metadata_only"
    else:
        latest_snapshot = snapshots[-1]
        if (
            latest_snapshot["retrieval_state"] == "captured"
            and latest_snapshot["segment_state"] == "captured"
        ):
            currentness_posture = "mutable_snapshot_backed"
        else:
            currentness_posture = "mutable_snapshot_gap"

    attention: list[str] = []
    if mutable and not snapshots and len(appearances) > 1:
        attention.append("reused_mutable_without_snapshot")
    if len(appearances) > 1 and any(
        item["segment_digest_posture"] != "all_segments_digest_backed" for item in appearances
    ):
        attention.append("reused_segments_without_complete_digest")
    if len(dossier["origin_groups"]) > 1:
        attention.append("origin_group_variation")
    if len(mutable_states) > 1:
        attention.append("mixed_mutability_classification")
    if any(item["review_disposition"] == "review_required" for item in receipts):
        attention.append("change_review_required")
    if proposals:
        attention.append("supersession_review_present")
    if snapshots and snapshots[-1]["segment_state"] != "captured":
        attention.append("latest_snapshot_segment_gap")

    recorded_times = [item["captured_at"] for item in appearances]
    recorded_times.extend(item["created_at"] for item in snapshots)
    recorded_times.extend(item["created_at"] for item in receipts)
    recorded_times.extend(item["created_at"] for item in proposals)

    return {
        "dossier_id": dossier["dossier_id"],
        "canonical_uri": dossier["canonical_uri"],
        "uri_aliases": sorted(dossier["uri_aliases"]),
        "titles": sorted(dossier["titles"]),
        "publishers": sorted(dossier["publishers"]),
        "source_classes": sorted(dossier["source_classes"]),
        "origin_groups": sorted(dossier["origin_groups"]),
        "propagation_roles": sorted(dossier["propagation_roles"]),
        "mutable_surface_states": sorted(mutable_states),
        "first_recorded_at": min(recorded_times),
        "latest_recorded_at": _latest_timestamp(recorded_times),
        "appearance_count": len(appearances),
        "run_count": len({item["recon_run_id"] for item in appearances}),
        "appearances": appearances,
        "capture_snapshots": snapshots,
        "change_receipts": receipts,
        "supersession_proposals": proposals,
        "currentness": {
            "posture": currentness_posture,
            "latest_recorded_at": _latest_timestamp(recorded_times),
            "snapshot_backed": bool(snapshots),
            "change_history_present": bool(receipts),
            "semantic_review_present": bool(proposals),
            "freshness_asserted": False,
        },
        "attention": attention,
    }


def build_catalog(root: Path = DEFAULT_ROOT) -> dict[str, Any]:
    root = root.resolve()
    dossiers: dict[str, dict[str, Any]] = {}
    input_refs: list[dict[str, Any]] = []
    runs_by_id: dict[str, tuple[Path, dict[str, Any], str]] = {}
    generation_times: list[str] = []

    for rel, run in _relative_json_records(root, RUN_DIRECTORY):
        run_id = run["recon_run_id"]
        digest = canonical_digest(run)
        runs_by_id[run_id] = (rel, run, digest)
        input_refs.append(_input_ref("ReconRun", run_id, rel, digest))
        generation_times.append(run["updated_at"])
        for source in run.get("source_captures", []):
            dossier = _dossier_for(dossiers, source["uri"])
            _add_source_metadata(dossier, source)
            segments = _segments(source)
            dossier["appearances"].append(
                {
                    "recon_run_id": run_id,
                    "recon_run_ref": rel.as_posix(),
                    "recon_run_digest": digest,
                    "source_id": source["source_id"],
                    "source_capture_digest": canonical_digest(source),
                    "captured_at": source["captured_at"],
                    "mutable_surface": source["mutable_surface"],
                    "origin_group": source["origin_group"],
                    "propagation_role": source["propagation_role"],
                    "observation_refs": _observation_refs(run, source["source_id"]),
                    "segments": segments,
                    "segment_digest_posture": _segment_digest_posture(segments),
                }
            )

    automation: list[tuple[Path, dict[str, Any]]] = []
    for directory in AUTOMATION_DIRECTORIES:
        automation.extend(_relative_json_records(root, directory))
    automation.sort(key=lambda item: item[0].as_posix())

    snapshots_by_id: dict[str, tuple[str, dict[str, Any]]] = {}
    for rel, artifact in automation:
        artifact_id = _artifact_id(artifact)
        input_refs.append(
            _input_ref(artifact["kind"], artifact_id, rel, canonical_digest(artifact))
        )
        generation_times.append(artifact["created_at"])
        if artifact["kind"] != "ResearchCaptureSnapshot":
            continue
        source = artifact["request"]["source"]
        dossier = _dossier_for(dossiers, source["uri"])
        _add_source_metadata(dossier, source)
        canonical_uri = dossier["canonical_uri"]
        snapshots_by_id[artifact_id] = (canonical_uri, artifact)
        dossier["capture_snapshots"].append(
            {
                "capture_id": artifact_id,
                "ref": rel.as_posix(),
                "content_digest": artifact["artifact_digest"],
                "created_at": artifact["created_at"],
                "source_id": source["source_id"],
                "segment_id": artifact["request"]["segment"]["segment_id"],
                "retrieval_state": artifact["retrieval"]["state"],
                "segment_state": artifact["segment_result"]["state"],
                "segment_content_digest": artifact["segment_result"]["content_digest"],
                "normalized_segment_digest": artifact["segment_result"][
                    "normalized_content_digest"
                ],
                "predecessor_snapshot": (
                    artifact["predecessor_snapshot"]["artifact_id"]
                    if artifact.get("predecessor_snapshot")
                    else None
                ),
            }
        )

    for rel, artifact in automation:
        if artifact["kind"] != "ResearchChangeReceipt":
            continue
        uris = {
            snapshots_by_id[ref["artifact_id"]][0]
            for ref in (artifact["previous_snapshot"], artifact["current_snapshot"])
            if ref["artifact_id"] in snapshots_by_id
        }
        for uri in sorted(uris):
            dossiers[uri]["change_receipts"].append(
                {
                    "receipt_id": artifact["receipt_id"],
                    "ref": rel.as_posix(),
                    "content_digest": artifact["artifact_digest"],
                    "created_at": artifact["created_at"],
                    "previous_capture_id": artifact["previous_snapshot"]["artifact_id"],
                    "current_capture_id": artifact["current_snapshot"]["artifact_id"],
                    "classification": artifact["classification"],
                    "review_disposition": artifact["review_disposition"],
                }
            )

    for rel, artifact in automation:
        if artifact["kind"] != "ResearchSupersessionProposal":
            continue
        roles_by_uri: dict[str, set[str]] = defaultdict(set)
        for role, key in (
            ("prior", "prior_observation"),
            ("candidate", "candidate_observation"),
        ):
            for uri in _qualified_observation_uris(artifact[key], runs_by_id):
                roles_by_uri[uri].add(role)
        for uri, roles in sorted(roles_by_uri.items()):
            dossier = dossiers.get(uri)
            if dossier is None:
                continue
            dossier["supersession_proposals"].append(
                {
                    "proposal_id": artifact["proposal_id"],
                    "ref": rel.as_posix(),
                    "content_digest": artifact["artifact_digest"],
                    "created_at": artifact["created_at"],
                    "status": artifact["status"],
                    "candidate_relation": artifact["candidate_relation"],
                    "roles": sorted(roles),
                    "review_required": artifact["review_required"],
                    "automatic_application": artifact["automatic_application"],
                }
            )

    finalized = [
        _finalize_dossier(dossier)
        for _, dossier in sorted(dossiers.items(), key=lambda item: item[0])
    ]
    generated_from = sorted(
        input_refs,
        key=lambda item: (item["kind"], item["ref"], item["record_id"]),
    )
    return {
        "$schema": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "kind": "ResearchSourceDossierCatalog",
        "authority": {
            "pre_canon": True,
            "generated": True,
            "informational_only": True,
            "automatic_promotion": False,
            "source_mutation_authority": False,
            "routing_authority": False,
            "activation_authority": False,
            "proof_authority": False,
            "acceptance_authority": False,
        },
        "identity_policy": {
            "mode": "normalized_exact_uri",
            "normalization": [
                "lowercase URI scheme and authority",
                "supply slash for an empty path",
                "remove fragment from source-surface identity",
                "preserve path case, trailing slash, and query string",
            ],
            "cross_uri_aliasing": "review_required_not_automatic",
        },
        "generated_from": generated_from,
        "input_fingerprint": canonical_digest(generated_from),
        "counts": {
            "dossiers": len(finalized),
            "source_appearances": sum(item["appearance_count"] for item in finalized),
            "recon_runs": len(runs_by_id),
            "capture_snapshots": sum(len(item["capture_snapshots"]) for item in finalized),
            "change_receipts": sum(len(item["change_receipts"]) for item in finalized),
            "supersession_proposals": len(
                {
                    proposal["proposal_id"]
                    for item in finalized
                    for proposal in item["supersession_proposals"]
                }
            ),
            "attention_dossiers": sum(bool(item["attention"]) for item in finalized),
        },
        "dossiers": finalized,
        "generated_at": _latest_timestamp(generation_times),
    }


def render_catalog(catalog: dict[str, Any]) -> str:
    return json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def expected_content(root: Path = DEFAULT_ROOT) -> str:
    return render_catalog(build_catalog(root))


def validate_research_source_dossiers(root: Path = DEFAULT_ROOT) -> list[str]:
    root = root.resolve()
    issues: list[str] = []
    schema_path = root / SCHEMA_PATH
    output_path = root / OUTPUT_PATH
    if not schema_path.is_file():
        return [f"{SCHEMA_PATH}: required schema is missing"]
    try:
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"{SCHEMA_PATH}: {exc}"]
    if not output_path.is_file():
        return [f"{OUTPUT_PATH}: generated source dossier catalog is missing"]
    try:
        catalog = load_json(output_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{OUTPUT_PATH}: invalid JSON: {exc}"]
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(catalog), key=lambda item: list(item.path)):
        location = "/".join(str(part) for part in error.path)
        suffix = f" at {location}" if location else ""
        issues.append(f"{OUTPUT_PATH}: schema error{suffix}: {error.message}")
    dossier_ids = [item.get("dossier_id") for item in catalog.get("dossiers", [])]
    canonical_uris = [item.get("canonical_uri") for item in catalog.get("dossiers", [])]
    if len(dossier_ids) != len(set(dossier_ids)):
        issues.append(f"{OUTPUT_PATH}: duplicate dossier ID")
    if len(canonical_uris) != len(set(canonical_uris)):
        issues.append(f"{OUTPUT_PATH}: duplicate canonical URI")
    for dossier in catalog.get("dossiers", []):
        canonical_uri = dossier.get("canonical_uri")
        if isinstance(canonical_uri, str):
            expected_id = source_dossier_id(canonical_uri)
            if dossier.get("dossier_id") != expected_id:
                issues.append(
                    f"{OUTPUT_PATH}: dossier ID mismatch for {canonical_uri!r}; "
                    f"expected {expected_id}"
                )
    try:
        expected = expected_content(root)
    except (OSError, KeyError, TypeError, ResearchSourceDossierError) as exc:
        issues.append(f"{OUTPUT_PATH}: cannot rebuild catalog: {exc}")
    else:
        if output_path.read_text(encoding="utf-8") != expected:
            issues.append(f"{OUTPUT_PATH}: generated source dossier catalog is stale")
    return issues


def source_dossier_summary(root: Path = DEFAULT_ROOT) -> dict[str, int]:
    path = root.resolve() / OUTPUT_PATH
    if not path.is_file():
        return {"ResearchSourceDossier": 0}
    try:
        catalog = load_json(path)
    except (OSError, json.JSONDecodeError):
        return {"ResearchSourceDossier": 0}
    return {"ResearchSourceDossier": len(catalog.get("dossiers", []))}


def find_dossiers(
    catalog: dict[str, Any],
    query: str | None = None,
    *,
    attention_only: bool = False,
) -> list[dict[str, Any]]:
    dossiers = catalog.get("dossiers", [])
    if attention_only:
        dossiers = [item for item in dossiers if item.get("attention")]
    if not query:
        return list(dossiers)
    normalized_query: str | None = None
    try:
        normalized_query = normalized_source_uri(query)
    except ResearchSourceDossierError:
        pass
    exact = [
        item
        for item in dossiers
        if query == item.get("dossier_id")
        or normalized_query == item.get("canonical_uri")
        or query in item.get("uri_aliases", [])
    ]
    if exact:
        return exact
    needle = query.casefold()
    return [
        item
        for item in dossiers
        if any(
            needle in value.casefold()
            for value in (
                item.get("canonical_uri", ""),
                *item.get("titles", []),
                *item.get("publishers", []),
                *item.get("origin_groups", []),
            )
        )
    ]


__all__ = [
    "DEFAULT_ROOT",
    "OUTPUT_PATH",
    "ResearchSourceDossierError",
    "build_catalog",
    "expected_content",
    "find_dossiers",
    "normalized_source_uri",
    "render_catalog",
    "source_dossier_id",
    "source_dossier_summary",
    "validate_research_source_dossiers",
]
