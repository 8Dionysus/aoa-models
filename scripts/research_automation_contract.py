#!/usr/bin/env python3
"""Contracts for bounded, non-authoritative research-intake automation."""

from __future__ import annotations

from collections.abc import Iterable
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_SCHEMA = Path("schemas/research-automation-artifact.schema.json")
RECON_RUN_SCHEMA = Path("schemas/recon-run.schema.json")
AUTOMATION_ROUTES = {
    "ResearchCaptureSnapshot": Path("research-intake/capture-snapshots"),
    "ResearchChangeReceipt": Path("research-intake/change-receipts"),
    "ResearchSupersessionProposal": Path("research-intake/supersession-proposals"),
}


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


def artifact_digest(record: dict[str, Any]) -> str:
    payload = copy.deepcopy(record)
    payload.pop("artifact_digest", None)
    return canonical_digest(payload)


def finalize_artifact(record: dict[str, Any]) -> dict[str, Any]:
    finalized = copy.deepcopy(record)
    finalized["artifact_digest"] = artifact_digest(finalized)
    return finalized


def _validator_bundle(
    root: Path,
) -> tuple[Draft202012Validator, dict[str, Any]]:
    automation_schema = load_json(root / AUTOMATION_SCHEMA)
    recon_schema = load_json(root / RECON_RUN_SCHEMA)
    Draft202012Validator.check_schema(automation_schema)
    registry = Registry().with_resource(
        recon_schema["$id"],
        Resource.from_contents(recon_schema),
    )
    return (
        Draft202012Validator(
            automation_schema,
            registry=registry,
            format_checker=FormatChecker(),
        ),
        automation_schema,
    )


def _schema_issues(
    validator: Draft202012Validator,
    record: dict[str, Any],
    label: str,
) -> list[str]:
    issues: list[str] = []
    for error in sorted(
        validator.iter_errors(record),
        key=lambda item: tuple(str(part) for part in item.path),
    ):
        location = "/".join(str(part) for part in error.path)
        suffix = f" at {location}" if location else ""
        issues.append(f"{label}: schema error{suffix}: {error.message}")
    return issues


def validate_capture_request(
    request: dict[str, Any],
    root: Path = DEFAULT_ROOT,
) -> list[str]:
    root = root.resolve()
    try:
        _, schema = _validator_bundle(root)
        request_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": schema["$defs"],
            "$ref": "#/$defs/capture_request",
        }
        validator = Draft202012Validator(
            request_schema,
            format_checker=FormatChecker(),
        )
    except (OSError, KeyError, ValueError, SchemaError, json.JSONDecodeError) as exc:
        return [f"capture request schema is unavailable: {exc}"]
    issues = _schema_issues(validator, request, "capture request")
    locator = request.get("segment", {}).get("locator", {})
    if locator.get("kind") == "line_range":
        value = locator.get("value", {})
        if value.get("end", 0) < value.get("start", 1):
            issues.append("capture request: line_range end precedes start")
    if locator.get("kind") == "json_pointer":
        pointer = locator.get("value", "")
        if any(re.search(r"~(?![01])", token) for token in pointer.split("/")[1:]):
            issues.append("capture request: JSON Pointer contains an invalid escape")
    source = request.get("source", {})
    if source.get("propagation_role") == "dependent" and not source.get("dependency_refs"):
        issues.append("capture request: dependent source requires a dependency ref")
    if source.get("source_id") in source.get("dependency_refs", []):
        issues.append("capture request: source cannot depend on itself")
    interval = source.get("effective_interval")
    if isinstance(interval, dict):
        try:
            start = _parse_datetime(interval["start"])
            end_value = interval.get("end")
            end = _parse_datetime(end_value) if end_value else None
        except (KeyError, TypeError, ValueError):
            pass
        else:
            if end is not None and end < start:
                issues.append("capture request: effective interval ends before it starts")
    return issues


def locator_label(locator: dict[str, Any]) -> str:
    kind = locator["kind"]
    value = locator["value"]
    if kind == "whole_document":
        return "whole-document"
    if kind == "line_range":
        return f"line-range:{value['start']}-{value['end']}"
    if kind == "json_pointer":
        return f"json-pointer:{value}"
    if kind == "html_id":
        return f"html-id:{value}"
    raise ValueError(f"unsupported locator kind: {kind!r}")


def _validate_snapshot(record: dict[str, Any], label: str, issues: list[str]) -> None:
    request = record.get("request", {})
    source = request.get("source", {})
    segment_request = request.get("segment", {})
    retrieval = record.get("retrieval", {})
    segment = record.get("segment_result", {})
    candidate = record.get("source_capture_candidate", {})

    source_id = source.get("source_id")
    created_at = record.get("created_at")
    if isinstance(source_id, str) and isinstance(created_at, str):
        try:
            expected_id = f"research-capture:{source_id}/{_timestamp_token(created_at)}"
        except ValueError:
            expected_id = None
        if expected_id and record.get("capture_id") != expected_id:
            issues.append(f"{label}: capture ID does not match source and timestamp")

    for key, value in source.items():
        if candidate.get(key) != value:
            issues.append(f"{label}: source_capture_candidate disagrees with request source {key}")
    if candidate.get("captured_at") != record.get("created_at"):
        issues.append(f"{label}: source_capture_candidate captured_at differs from created_at")
    if retrieval.get("attempted_at") != record.get("created_at"):
        issues.append(f"{label}: retrieval attempted_at differs from created_at")
    candidate_segments = candidate.get("segments", [])
    if len(candidate_segments) == 1:
        candidate_segment = candidate_segments[0]
        if candidate_segment.get("segment_id") != segment_request.get("segment_id"):
            issues.append(f"{label}: candidate segment ID differs from request")
        locator = segment_request.get("locator")
        if isinstance(locator, dict):
            try:
                expected_locator = locator_label(locator)
            except (KeyError, TypeError, ValueError):
                expected_locator = None
            if expected_locator and candidate_segment.get("locator") != expected_locator:
                issues.append(f"{label}: candidate locator differs from structured locator")
        if candidate_segment.get("content_digest") != segment.get("content_digest"):
            issues.append(f"{label}: candidate segment digest differs from segment result")
        if (
            candidate_segment.get("digest_unavailable_reason")
            != segment.get("digest_unavailable_reason")
        ):
            issues.append(f"{label}: candidate digest gap differs from segment result")

    retrieval_state = retrieval.get("state")
    if retrieval_state == "unavailable":
        if retrieval.get("document_digest") is not None:
            issues.append(f"{label}: unavailable retrieval cannot have a document digest")
        if retrieval.get("document_size_bytes") is not None:
            issues.append(f"{label}: unavailable retrieval cannot have a document size")
        if not retrieval.get("error"):
            issues.append(f"{label}: unavailable retrieval requires an error")
        if segment.get("state") != "unavailable":
            issues.append(f"{label}: unavailable retrieval requires unavailable segment")
    elif retrieval_state in {"captured", "partial"}:
        if retrieval.get("document_digest") is None:
            issues.append(f"{label}: retrieved document requires a digest")
        if retrieval.get("document_size_bytes") is None:
            issues.append(f"{label}: retrieved document requires a byte size")
        document_size = retrieval.get("document_size_bytes")
        max_bytes = request.get("retrieval", {}).get("max_bytes")
        if (
            isinstance(document_size, int)
            and isinstance(max_bytes, int)
            and document_size > max_bytes
        ):
            issues.append(f"{label}: retrieved document exceeds declared byte bound")
    if retrieval_state == "captured":
        if retrieval.get("truncated"):
            issues.append(f"{label}: captured retrieval cannot be truncated")
        if retrieval.get("error") is not None:
            issues.append(f"{label}: captured retrieval cannot retain an error")
    if retrieval_state == "partial":
        if not retrieval.get("truncated"):
            issues.append(f"{label}: partial retrieval requires truncation evidence")
        if not retrieval.get("error"):
            issues.append(f"{label}: partial retrieval requires an error or gap reason")
    transport = retrieval.get("transport")
    if transport == "local_input":
        if not retrieval.get("input_ref"):
            issues.append(f"{label}: local input retrieval requires input_ref")
        if retrieval.get("final_uri") is not None or retrieval.get("http_status") is not None:
            issues.append(f"{label}: local input cannot claim HTTP result metadata")
    if transport == "http":
        if retrieval.get("input_ref") is not None:
            issues.append(f"{label}: HTTP retrieval cannot claim a local input ref")
        if retrieval_state in {"captured", "partial"}:
            if retrieval.get("final_uri") is None:
                issues.append(f"{label}: successful HTTP retrieval requires final_uri")
            status = retrieval.get("http_status")
            if not isinstance(status, int) or not 200 <= status < 300:
                issues.append(f"{label}: successful HTTP retrieval requires a 2xx status")
    requested_media_type = request.get("retrieval", {}).get("media_type")
    if (
        requested_media_type not in {None, "auto"}
        and retrieval.get("media_type") != requested_media_type
    ):
        issues.append(f"{label}: retrieval media type differs from explicit request")

    segment_state = segment.get("state")
    if segment_state in {"captured", "partial"}:
        for key in ("content_digest", "normalized_content_digest", "byte_length"):
            if segment.get(key) is None:
                issues.append(f"{label}: {segment_state} segment requires {key}")
        if segment.get("digest_unavailable_reason") is not None:
            issues.append(f"{label}: captured segment cannot have a digest gap")
    elif segment_state in {"missing", "unavailable"}:
        for key in ("content_digest", "normalized_content_digest", "byte_length"):
            if segment.get(key) is not None:
                issues.append(f"{label}: {segment_state} segment cannot have {key}")
        if not segment.get("digest_unavailable_reason"):
            issues.append(f"{label}: {segment_state} segment requires a digest gap")

    gap_reasons = record.get("gap_reasons", [])
    fully_captured = retrieval_state == "captured" and segment_state == "captured"
    if fully_captured and gap_reasons:
        issues.append(f"{label}: fully captured snapshot cannot retain gap reasons")
    if not fully_captured and not gap_reasons:
        issues.append(f"{label}: incomplete snapshot requires gap reasons")
    predecessor = record.get("predecessor_snapshot")
    if predecessor and predecessor.get("artifact_id") == record.get("capture_id"):
        issues.append(f"{label}: capture snapshot cannot be its own predecessor")


def _digest_changed(previous: Any, current: Any) -> bool | None:
    if previous is None or current is None:
        return None
    return previous != current


def classify_change(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> tuple[str, dict[str, bool | None], str]:
    previous_retrieval = previous["retrieval"]
    current_retrieval = current["retrieval"]
    previous_segment = previous["segment_result"]
    current_segment = current["segment_result"]
    basis: dict[str, bool | None] = {
        "retrieval_state_changed": previous_retrieval["state"] != current_retrieval["state"],
        "document_digest_changed": _digest_changed(
            previous_retrieval.get("document_digest"),
            current_retrieval.get("document_digest"),
        ),
        "segment_state_changed": previous_segment["state"] != current_segment["state"],
        "segment_digest_changed": _digest_changed(
            previous_segment.get("content_digest"),
            current_segment.get("content_digest"),
        ),
        "normalized_segment_digest_changed": _digest_changed(
            previous_segment.get("normalized_content_digest"),
            current_segment.get("normalized_content_digest"),
        ),
    }
    previous_unavailable = previous_retrieval["state"] == "unavailable"
    current_unavailable = current_retrieval["state"] == "unavailable"
    if current_unavailable and previous_unavailable:
        return "unavailable_persists", basis, "retry_or_revisit"
    if current_unavailable:
        return "source_unavailable", basis, "retry_or_revisit"
    if previous_unavailable:
        return "source_recovered", basis, "review_required"

    previous_state = previous_segment["state"]
    current_state = current_segment["state"]
    captured_states = {"captured", "partial"}
    if previous_state in captured_states and current_state == "missing":
        return "segment_became_missing", basis, "review_required"
    if previous_state == "missing" and current_state in captured_states:
        return "segment_restored", basis, "review_required"
    if previous_state not in captured_states or current_state not in captured_states:
        return "incomparable", basis, "retry_or_revisit"
    if basis["segment_digest_changed"] is False:
        if basis["document_digest_changed"] is True:
            return "document_changed_segment_stable", basis, "no_change"
        return "unchanged", basis, "no_change"
    if (
        basis["segment_digest_changed"] is True
        and basis["normalized_segment_digest_changed"] is False
    ):
        return "presentation_changed", basis, "review_optional"
    if basis["normalized_segment_digest_changed"] is True:
        return "content_changed", basis, "review_required"
    return "incomparable", basis, "retry_or_revisit"


def _compare_scalar_dimensions(
    previous: dict[str, Any],
    current: dict[str, Any],
    fields: Iterable[str],
) -> tuple[list[str], list[str]]:
    shared: list[str] = []
    conflicting: list[str] = []
    for field in fields:
        previous_value = previous.get(field)
        current_value = current.get(field)
        if previous_value is None or current_value is None:
            continue
        if previous_value == current_value:
            shared.append(field)
        else:
            conflicting.append(field)
    return shared, conflicting


def _compare_list_dimension(
    previous: dict[str, Any],
    current: dict[str, Any],
    field: str,
) -> tuple[bool, bool]:
    previous_values = set(previous.get(field, []))
    current_values = set(current.get(field, []))
    if not previous_values or not current_values:
        return False, False
    return bool(previous_values & current_values), not bool(previous_values & current_values)


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _timestamp_token(value: str) -> str:
    moment = _parse_datetime(value)
    if moment.tzinfo is None:
        raise ValueError("timestamp requires timezone")
    canonical = moment.astimezone(timezone.utc)
    rendered = canonical.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return rendered.lower().replace("-", "").replace(":", "").replace("+", "")


def _temporal_relation(
    previous_interval: dict[str, Any],
    current_interval: dict[str, Any],
) -> str:
    try:
        previous_start = _parse_datetime(previous_interval["start"])
        previous_end_value = previous_interval.get("end")
        previous_end = _parse_datetime(previous_end_value) if previous_end_value else None
        current_start = _parse_datetime(current_interval["start"])
        current_end_value = current_interval.get("end")
        current_end = _parse_datetime(current_end_value) if current_end_value else None
    except (KeyError, TypeError, ValueError):
        return "unknown"
    if previous_end is not None and current_start > previous_end:
        return "after"
    if current_end is not None and current_end < previous_start:
        return "before"
    return "overlap"


def compare_observations(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    previous_subject = previous.get("subject", {})
    current_subject = current.get("subject", {})
    subject_shared, subject_conflicting = _compare_scalar_dimensions(
        previous_subject,
        current_subject,
        ("family", "provider", "product", "snapshot"),
    )
    models_shared, models_conflicting = _compare_list_dimension(
        previous_subject,
        current_subject,
        "models",
    )
    if models_shared:
        subject_shared.append("models")
    if models_conflicting:
        subject_conflicting.append("models")
    previous_runtime = previous_subject.get("runtime") or {}
    current_runtime = current_subject.get("runtime") or {}
    runtime_shared, runtime_conflicting = _compare_scalar_dimensions(
        previous_runtime,
        current_runtime,
        ("name", "version", "subject_ref"),
    )
    subject_shared.extend(f"runtime.{field}" for field in runtime_shared)
    subject_conflicting.extend(f"runtime.{field}" for field in runtime_conflicting)

    previous_configuration = previous.get("configuration", {})
    current_configuration = current.get("configuration", {})
    configuration_shared, configuration_conflicting = _compare_scalar_dimensions(
        previous_configuration,
        current_configuration,
        (
            "route",
            "reasoning_effort",
            "context_policy",
            "harness",
            "instrument_revision",
            "grader",
        ),
    )
    for field in ("tools", "permissions"):
        shared, conflicting = _compare_list_dimension(
            previous_configuration,
            current_configuration,
            field,
        )
        if shared:
            configuration_shared.append(field)
        if conflicting:
            configuration_conflicting.append(field)
    return {
        "same_target_kind": previous.get("target_kind") == current.get("target_kind"),
        "shared_subject_dimensions": sorted(subject_shared),
        "conflicting_subject_dimensions": sorted(subject_conflicting),
        "shared_configuration_dimensions": sorted(configuration_shared),
        "conflicting_configuration_dimensions": sorted(configuration_conflicting),
        "temporal_relation": _temporal_relation(
            previous.get("observed_interval", {}),
            current.get("observed_interval", {}),
        ),
    }


def candidate_action(relation: str) -> str:
    if relation in {"update", "narrowing"}:
        return "review_add_qualified_supersedes_ref"
    if relation == "contradiction":
        return "review_as_tension"
    if relation == "independent":
        return "preserve_independent"
    raise ValueError(f"unsupported candidate relation: {relation!r}")


def _validate_proposal(record: dict[str, Any], label: str, issues: list[str]) -> None:
    prior = record.get("prior_observation", {})
    candidate = record.get("candidate_observation", {})
    if (
        prior.get("recon_run_id") == candidate.get("recon_run_id")
        and prior.get("observation_id") == candidate.get("observation_id")
    ):
        issues.append(f"{label}: proposal cannot compare an observation with itself")
    relation = record.get("candidate_relation")
    if relation:
        try:
            expected_action = candidate_action(relation)
        except ValueError as exc:
            issues.append(f"{label}: {exc}")
        else:
            if record.get("candidate_action") != expected_action:
                issues.append(f"{label}: candidate action disagrees with relation")
    comparison = record.get("structural_comparison", {})
    if relation in {"update", "narrowing"}:
        if not comparison.get("same_target_kind"):
            issues.append(f"{label}: update or narrowing requires the same target kind")
        identity_dimensions = {
            "family",
            "models",
            "snapshot",
            "runtime.subject_ref",
        }
        if not identity_dimensions.intersection(
            comparison.get("shared_subject_dimensions", [])
        ):
            issues.append(
                f"{label}: update or narrowing requires a shared subject identity dimension"
            )
        if comparison.get("temporal_relation") == "before":
            issues.append(f"{label}: update or narrowing candidate predates prior observation")


def validate_automation_artifact(
    record: dict[str, Any],
    root: Path = DEFAULT_ROOT,
    *,
    label: str = "research automation artifact",
) -> list[str]:
    root = root.resolve()
    try:
        validator, _ = _validator_bundle(root)
    except (OSError, KeyError, ValueError, SchemaError, json.JSONDecodeError) as exc:
        return [f"{label}: automation schema is unavailable: {exc}"]
    schema_issues = _schema_issues(validator, record, label)
    issues = list(schema_issues)
    declared_digest = record.get("artifact_digest")
    if isinstance(declared_digest, str):
        actual_digest = artifact_digest(record)
        if declared_digest != actual_digest:
            issues.append(
                f"{label}: artifact digest mismatch: declared {declared_digest}, "
                f"actual {actual_digest}"
            )
    kind = record.get("kind")
    if not schema_issues and kind == "ResearchCaptureSnapshot":
        _validate_snapshot(record, label, issues)
    elif not schema_issues and kind == "ResearchSupersessionProposal":
        _validate_proposal(record, label, issues)
    return issues


def collect_research_automation_artifacts(
    root: Path = DEFAULT_ROOT,
) -> tuple[list[tuple[Path, dict[str, Any]]], list[str]]:
    root = root.resolve()
    records: list[tuple[Path, dict[str, Any]]] = []
    issues: list[str] = []
    for expected_kind, route in AUTOMATION_ROUTES.items():
        directory = root / route
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            try:
                record = load_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                issues.append(f"{path.relative_to(root)}: invalid JSON: {exc}")
                continue
            if record.get("kind") != expected_kind:
                issues.append(
                    f"{path.relative_to(root)}: route expects {expected_kind}, "
                    f"found {record.get('kind')!r}"
                )
            records.append((path, record))
        for path in sorted(directory.rglob("*.json")):
            if path.parent != directory:
                issues.append(
                    f"{path.relative_to(root)}: automation artifact is outside its flat route"
                )
    return records, issues


def _resolve_artifact_ref(
    root: Path,
    label: str,
    ref: dict[str, Any],
    records_by_path: dict[str, dict[str, Any]],
    valid_paths: set[str],
    issues: list[str],
) -> dict[str, Any] | None:
    path_ref = ref.get("ref")
    if not isinstance(path_ref, str) or not path_ref.startswith("research-intake/"):
        issues.append(f"{label}: repository artifact ref must be owner-relative")
        return None
    target = records_by_path.get(path_ref)
    if target is None:
        issues.append(f"{label}: referenced automation artifact does not exist: {path_ref!r}")
        return None
    if path_ref not in valid_paths:
        issues.append(f"{label}: referenced automation artifact is invalid: {path_ref!r}")
        return None
    if target.get("capture_id") != ref.get("artifact_id"):
        issues.append(f"{label}: referenced artifact ID does not match {path_ref!r}")
    if target.get("artifact_digest") != ref.get("content_digest"):
        issues.append(f"{label}: referenced artifact digest does not match {path_ref!r}")
    return target


def _observation_by_id(run: dict[str, Any], observation_id: str) -> dict[str, Any] | None:
    return next(
        (
            observation
            for observation in run.get("observations", [])
            if observation.get("observation_id") == observation_id
        ),
        None,
    )


def _validate_qualified_observation(
    root: Path,
    label: str,
    ref: dict[str, Any],
    issues: list[str],
) -> dict[str, Any] | None:
    run_ref = ref.get("recon_run_ref")
    if not isinstance(run_ref, str):
        return None
    run_path = root / run_ref
    if not run_path.is_file():
        issues.append(f"{label}: recon run does not exist: {run_ref!r}")
        return None
    try:
        run = load_json(run_path)
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(f"{label}: cannot read recon run {run_ref!r}: {exc}")
        return None
    if run.get("recon_run_id") != ref.get("recon_run_id"):
        issues.append(f"{label}: recon run ID does not match {run_ref!r}")
    if canonical_digest(run) != ref.get("recon_run_digest"):
        issues.append(f"{label}: recon run digest does not match {run_ref!r}")
    observation = _observation_by_id(run, ref.get("observation_id"))
    if observation is None:
        issues.append(
            f"{label}: observation {ref.get('observation_id')!r} is absent from {run_ref!r}"
        )
        return None
    if canonical_digest(observation) != ref.get("observation_digest"):
        issues.append(f"{label}: observation digest does not match {run_ref!r}")
    for key in ("target_kind", "observed_interval", "source_segment_refs", "counterevidence_refs"):
        if ref.get(key) != observation.get(key):
            issues.append(f"{label}: qualified observation field {key} does not match source")
    return observation


def validate_research_automation(root: Path = DEFAULT_ROOT) -> list[str]:
    root = root.resolve()
    if not (root / AUTOMATION_SCHEMA).is_file():
        return [f"{AUTOMATION_SCHEMA}: required schema is missing"]
    if not (root / RECON_RUN_SCHEMA).is_file():
        return [f"{RECON_RUN_SCHEMA}: required schema is missing"]
    records, collect_issues = collect_research_automation_artifacts(root)
    issues = list(collect_issues)
    records_by_path = {path.relative_to(root).as_posix(): record for path, record in records}
    ids: dict[str, Path] = {}
    valid_paths: set[str] = set()
    for path, record in records:
        rel = path.relative_to(root)
        artifact_issues = validate_automation_artifact(record, root, label=str(rel))
        issues.extend(artifact_issues)
        if not artifact_issues:
            valid_paths.add(rel.as_posix())
        artifact_id = (
            record.get("capture_id")
            or record.get("receipt_id")
            or record.get("proposal_id")
        )
        if artifact_id in ids:
            issues.append(f"{rel}: duplicate automation artifact ID also used by {ids[artifact_id]}")
        elif artifact_id:
            ids[artifact_id] = rel

    for path, record in records:
        rel = path.relative_to(root)
        label = str(rel)
        if rel.as_posix() not in valid_paths:
            continue
        kind = record.get("kind")
        if kind == "ResearchCaptureSnapshot":
            predecessor_ref = record.get("predecessor_snapshot")
            if predecessor_ref:
                predecessor = _resolve_artifact_ref(
                    root,
                    label,
                    predecessor_ref,
                    records_by_path,
                    valid_paths,
                    issues,
                )
                if predecessor:
                    if record.get("request") != predecessor.get("request"):
                        issues.append(
                            f"{label}: refreshed snapshot must preserve predecessor request"
                        )
                    try:
                        if _parse_datetime(record["created_at"]) <= _parse_datetime(
                            predecessor["created_at"]
                        ):
                            issues.append(f"{label}: refreshed snapshot must follow predecessor")
                    except (KeyError, TypeError, ValueError):
                        pass
        elif kind == "ResearchChangeReceipt":
            previous = _resolve_artifact_ref(
                root,
                label,
                record.get("previous_snapshot", {}),
                records_by_path,
                valid_paths,
                issues,
            )
            current = _resolve_artifact_ref(
                root,
                label,
                record.get("current_snapshot", {}),
                records_by_path,
                valid_paths,
                issues,
            )
            if previous and current:
                if previous.get("capture_id") == current.get("capture_id"):
                    issues.append(f"{label}: change receipt requires two snapshots")
                if previous.get("request") != current.get("request"):
                    issues.append(f"{label}: change receipt snapshots use different requests")
                if record.get("created_at") != current.get("created_at"):
                    issues.append(f"{label}: receipt created_at must match current snapshot")
                try:
                    expected_receipt_id = (
                        f"research-change:{current['request']['source']['source_id']}/"
                        f"{_timestamp_token(current['created_at'])}"
                    )
                except (KeyError, TypeError, ValueError):
                    expected_receipt_id = None
                if expected_receipt_id and record.get("receipt_id") != expected_receipt_id:
                    issues.append(f"{label}: receipt ID does not match current snapshot")
                classification, basis, disposition = classify_change(previous, current)
                if record.get("classification") != classification:
                    issues.append(f"{label}: change classification does not match snapshots")
                if record.get("basis") != basis:
                    issues.append(f"{label}: change basis does not match snapshots")
                if record.get("review_disposition") != disposition:
                    issues.append(f"{label}: review disposition does not match classification")
                predecessor = current.get("predecessor_snapshot") or {}
                if predecessor != record.get("previous_snapshot"):
                    issues.append(f"{label}: current snapshot does not bind receipt predecessor")
        elif kind == "ResearchSupersessionProposal":
            prior = _validate_qualified_observation(
                root,
                f"{label} prior",
                record.get("prior_observation", {}),
                issues,
            )
            candidate = _validate_qualified_observation(
                root,
                f"{label} candidate",
                record.get("candidate_observation", {}),
                issues,
            )
            if prior and candidate:
                expected = compare_observations(prior, candidate)
                if record.get("structural_comparison") != expected:
                    issues.append(f"{label}: structural comparison does not match observations")
    return issues


def research_automation_summary(root: Path = DEFAULT_ROOT) -> dict[str, int]:
    records, _ = collect_research_automation_artifacts(root.resolve())
    counts = {kind: 0 for kind in AUTOMATION_ROUTES}
    for _, record in records:
        kind = record.get("kind")
        if kind in counts:
            counts[kind] += 1
    return counts
