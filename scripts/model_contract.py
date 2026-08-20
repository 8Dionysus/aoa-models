#!/usr/bin/env python3
"""Shared validation and deterministic projection helpers for aoa-models."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


DEFAULT_ROOT = Path(__file__).resolve().parents[1]

RECORD_ROUTES = {
    Path("source/model-identities"): "model-identity.schema.json",
    Path("source/model-realizations"): "model-realization.schema.json",
    Path("source/model-claims"): "model-claim.schema.json",
    Path("source/model-studies"): "model-study.schema.json",
    Path("generated/model-fit-projections"): "model-fit-projection.schema.json",
}

REQUIRED_SCHEMA_FILES = {*RECORD_ROUTES.values(), "runtime-subject.schema.json"}

ID_FIELDS = {
    "ModelIdentity": "model_identity_id",
    "ModelRealization": "model_realization_id",
    "ModelClaim": "model_claim_id",
    "ModelStudy": "model_study_id",
    "ModelFitProjection": "model_fit_projection_id",
}

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "hypothesis": {"observed", "stale", "retracted"},
    "observed": {"reviewed", "weakened", "stale", "superseded", "retracted"},
    "reviewed": {"weakened", "stale", "superseded", "retracted"},
    "weakened": {"observed", "stale", "superseded", "retracted"},
    "stale": {"observed", "superseded", "retracted"},
    "superseded": set(),
    "retracted": set(),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def runtime_subject_validation_errors(root: Path, subject: Any) -> list[str]:
    """Return schema errors for one exact runtime subject identity."""
    if not isinstance(subject, dict):
        return ["runtime subject must be an object"]
    schema_path = root / "schemas/runtime-subject.schema.json"
    if not schema_path.is_file():
        return ["runtime subject schema is missing"]
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        error.message
        for error in sorted(validator.iter_errors(subject), key=lambda item: list(item.path))
    ]


def canonical_fingerprint(configuration: dict[str, Any]) -> str:
    payload = json.dumps(
        configuration,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _schema_registry(root: Path) -> tuple[dict[str, dict[str, Any]], Registry]:
    schemas: dict[str, dict[str, Any]] = {}
    registry = Registry()
    for path in sorted((root / "schemas").glob("*.json")):
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        schema_id = schema.get("$id")
        if not schema_id:
            raise ValueError(f"{path.relative_to(root)}: schema has no $id")
        schemas[path.name] = schema
        registry = registry.with_resource(schema_id, Resource.from_contents(schema))
    return schemas, registry


def _record_paths(root: Path, route: Path) -> list[Path]:
    directory = root / route
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def collect_records(root: Path) -> tuple[dict[str, list[tuple[Path, dict[str, Any]]]], list[str]]:
    records: dict[str, list[tuple[Path, dict[str, Any]]]] = defaultdict(list)
    issues: list[str] = []
    for route in RECORD_ROUTES:
        for path in _record_paths(root, route):
            try:
                record = load_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                issues.append(f"{path.relative_to(root)}: invalid JSON: {exc}")
                continue
            records[record.get("kind", "unknown")].append((path, record))

    known_roots = {route.parts[0:2] for route in RECORD_ROUTES}
    for base_name in ("source", "generated"):
        base = root / base_name
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.json")):
            rel = path.relative_to(root)
            if rel.parts[0:2] not in known_roots:
                issues.append(f"{rel}: JSON record is outside a declared source/derived route")
    return records, issues


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _validate_interval(record: dict[str, Any], rel: Path, issues: list[str]) -> None:
    interval = record.get("observation_interval")
    if not isinstance(interval, dict):
        return
    try:
        start = _parse_datetime(interval["start"])
        end_value = interval.get("end")
        end = _parse_datetime(end_value) if end_value else None
    except (KeyError, TypeError, ValueError) as exc:
        issues.append(f"{rel}: invalid observation interval: {exc}")
        return
    if end is not None and end < start:
        issues.append(f"{rel}: observation interval ends before it starts")


def _validate_timestamps(record: dict[str, Any], rel: Path, issues: list[str]) -> None:
    if "created_at" not in record or "updated_at" not in record:
        return
    try:
        created = _parse_datetime(record["created_at"])
        updated = _parse_datetime(record["updated_at"])
    except (TypeError, ValueError) as exc:
        issues.append(f"{rel}: invalid created/updated timestamp: {exc}")
        return
    if updated < created:
        issues.append(f"{rel}: updated_at precedes created_at")


def _all_source_refs(record: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for key in ("source_refs", "evidence_refs", "known_counterevidence", "independent_review_refs", "result_refs"):
        value = record.get(key, [])
        if isinstance(value, list):
            yield from (item for item in value if isinstance(item, dict))


def _validate_source_refs(record: dict[str, Any], rel: Path, issues: list[str]) -> None:
    seen: set[str] = set()
    for ref in _all_source_refs(record):
        source_id = ref.get("source_id")
        if source_id in seen:
            issues.append(f"{rel}: duplicate source_id {source_id!r}")
        if source_id:
            seen.add(source_id)
        uri = ref.get("uri", "")
        if isinstance(uri, str) and uri.startswith("generated/"):
            issues.append(f"{rel}: generated projection cannot be used as source evidence: {uri}")


def _validate_claim(
    root: Path,
    rel: Path,
    claim: dict[str, Any],
    realization_paths: set[str],
    realizations_by_path: dict[str, dict[str, Any]],
    issues: list[str],
) -> None:
    for ref in claim.get("subject_realization_refs", []):
        if ref not in realization_paths:
            issues.append(f"{rel}: subject realization does not exist: {ref}")

    lifecycle = claim.get("lifecycle", {})
    history = lifecycle.get("history", [])
    previous: str | None = None
    for index, transition in enumerate(history):
        source = transition.get("from")
        target = transition.get("to")
        if index == 0:
            if source is not None or target not in {"hypothesis", "observed"}:
                issues.append(
                    f"{rel}: first lifecycle transition must start at null and enter hypothesis or observed"
                )
        else:
            if source != previous:
                issues.append(f"{rel}: lifecycle transition {index} does not continue from {previous}")
            if source in ALLOWED_TRANSITIONS and target not in ALLOWED_TRANSITIONS[source]:
                issues.append(f"{rel}: unsupported lifecycle transition {source} -> {target}")
        previous = target
    state = lifecycle.get("state")
    if history and previous != state:
        issues.append(f"{rel}: lifecycle state {state!r} does not match final transition {previous!r}")

    evidence_refs = claim.get("evidence_refs", [])
    independent_refs = claim.get("independent_review_refs", [])
    if state in {"observed", "reviewed", "weakened"} and not evidence_refs:
        issues.append(f"{rel}: {state} claim requires evidence_refs")
    if state == "reviewed":
        review_kinds = {item.get("kind") for item in independent_refs if isinstance(item, dict)}
        if not independent_refs or not review_kinds.intersection({"eval_verdict", "independent_review"}):
            issues.append(f"{rel}: reviewed claim requires an independent review or eval verdict ref")
        if claim.get("confidence_posture") != "reviewed":
            issues.append(f"{rel}: reviewed lifecycle requires reviewed confidence_posture")
    elif claim.get("confidence_posture") == "reviewed":
        issues.append(f"{rel}: reviewed confidence_posture is unsupported before reviewed lifecycle")
    if state == "hypothesis" and claim.get("confidence_posture") != "hypothesis":
        issues.append(f"{rel}: hypothesis lifecycle requires hypothesis confidence_posture")
    if state == "stale" and claim.get("freshness", {}).get("status") != "stale":
        issues.append(f"{rel}: stale lifecycle requires stale freshness")
    if state == "superseded" and not lifecycle.get("superseded_by"):
        issues.append(f"{rel}: superseded claim requires superseded_by")
    if state != "superseded" and lifecycle.get("superseded_by"):
        issues.append(f"{rel}: superseded_by is only valid for a superseded claim")
    if state == "retracted" and not claim.get("known_counterevidence"):
        issues.append(f"{rel}: retracted claim requires preserved counterevidence")

    freshness = claim.get("freshness", {})
    if freshness.get("status") == "current":
        for ref in claim.get("subject_realization_refs", []):
            realization_state = realizations_by_path.get(ref, {}).get("lifecycle_state")
            if realization_state not in {"declared", "observed"}:
                issues.append(
                    f"{rel}: current claim references non-current realization {ref} ({realization_state})"
                )
    review_by = freshness.get("review_by")
    if freshness.get("status") == "current" and review_by:
        try:
            if _parse_datetime(review_by) < datetime.now(timezone.utc):
                issues.append(f"{rel}: current claim passed review_by and must become stale or be reviewed")
        except (TypeError, ValueError):
            pass


def _validate_study(
    rel: Path,
    study: dict[str, Any],
    realization_paths: set[str],
    issues: list[str],
) -> None:
    seen_arms: set[str] = set()
    for arm in study.get("comparison_arms", []):
        arm_id = arm.get("arm_id")
        if arm_id in seen_arms:
            issues.append(f"{rel}: duplicate comparison arm {arm_id!r}")
        if arm_id:
            seen_arms.add(arm_id)
        for ref in arm.get("realization_refs", []):
            if ref not in realization_paths:
                issues.append(f"{rel}: comparison realization does not exist: {ref}")
    if study.get("status") == "reviewed":
        result_refs = study.get("result_refs", [])
        if not result_refs or not any(ref.get("kind") == "eval_verdict" for ref in result_refs):
            issues.append(f"{rel}: reviewed study requires an aoa-evals verdict reference")


def _validate_projection(
    rel: Path,
    projection: dict[str, Any],
    realization_paths: set[str],
    claim_paths: set[str],
    study_paths: set[str],
    claims_by_path: dict[str, dict[str, Any]],
    issues: list[str],
) -> None:
    subject = projection.get("subject_realization_ref")
    if subject not in realization_paths:
        issues.append(f"{rel}: projected realization does not exist: {subject}")
    for ref in projection.get("generated_from_claim_refs", []):
        if ref not in claim_paths:
            issues.append(f"{rel}: projected claim does not exist: {ref}")
    for ref in projection.get("study_refs", []):
        if ref not in study_paths:
            issues.append(f"{rel}: projected study does not exist: {ref}")
    if projection.get("posture") in {"shadow", "admitted"}:
        source_claims = [claims_by_path.get(ref, {}) for ref in projection.get("generated_from_claim_refs", [])]
        if not source_claims or any(claim.get("lifecycle", {}).get("state") != "reviewed" for claim in source_claims):
            issues.append(f"{rel}: {projection.get('posture')} projection requires reviewed source claims")
    if projection.get("effect_family") != "read":
        issues.append(f"{rel}: initial model-fit projections may expose read effects only")


def validate_repo(root: Path = DEFAULT_ROOT) -> list[str]:
    root = root.resolve()
    issues: list[str] = []
    try:
        schemas, registry = _schema_registry(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"schemas: {exc}"]
    for required_schema in sorted(REQUIRED_SCHEMA_FILES):
        if required_schema not in schemas:
            issues.append(f"schemas/{required_schema}: required schema is missing")

    records, collect_issues = collect_records(root)
    issues.extend(collect_issues)
    expected_kinds = {
        "ModelIdentity",
        "ModelRealization",
        "ModelClaim",
        "ModelStudy",
        "ModelFitProjection",
    }
    for kind in records:
        if kind not in expected_kinds:
            for path, _ in records[kind]:
                issues.append(f"{path.relative_to(root)}: unknown record kind {kind!r}")

    schema_by_kind = {
        "ModelIdentity": "model-identity.schema.json",
        "ModelRealization": "model-realization.schema.json",
        "ModelClaim": "model-claim.schema.json",
        "ModelStudy": "model-study.schema.json",
        "ModelFitProjection": "model-fit-projection.schema.json",
    }
    format_checker = FormatChecker()
    seen_ids: dict[str, Path] = {}
    for kind, entries in records.items():
        if kind not in schema_by_kind:
            continue
        validator = Draft202012Validator(
            schemas[schema_by_kind[kind]],
            registry=registry,
            format_checker=format_checker,
        )
        for path, record in entries:
            rel = path.relative_to(root)
            for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
                location = "/".join(str(part) for part in error.path)
                suffix = f" at {location}" if location else ""
                issues.append(f"{rel}: schema error{suffix}: {error.message}")
            id_field = ID_FIELDS[kind]
            record_id = record.get(id_field)
            if record_id in seen_ids:
                issues.append(f"{rel}: duplicate record ID also used by {seen_ids[record_id]}")
            elif record_id:
                seen_ids[record_id] = rel
            _validate_interval(record, rel, issues)
            _validate_timestamps(record, rel, issues)
            _validate_source_refs(record, rel, issues)

    identity_paths = {
        path.relative_to(root).as_posix()
        for path, _ in records.get("ModelIdentity", [])
    }
    realization_paths = {
        path.relative_to(root).as_posix()
        for path, _ in records.get("ModelRealization", [])
    }
    claim_paths = {
        path.relative_to(root).as_posix()
        for path, _ in records.get("ModelClaim", [])
    }
    study_paths = {
        path.relative_to(root).as_posix()
        for path, _ in records.get("ModelStudy", [])
    }
    claims_by_path = {
        path.relative_to(root).as_posix(): record
        for path, record in records.get("ModelClaim", [])
    }
    realizations_by_path = {
        path.relative_to(root).as_posix(): record
        for path, record in records.get("ModelRealization", [])
    }

    for path, realization in records.get("ModelRealization", []):
        rel = path.relative_to(root)
        if realization.get("model_identity_ref") not in identity_paths:
            issues.append(f"{rel}: model identity does not exist: {realization.get('model_identity_ref')}")
        actual = canonical_fingerprint(realization.get("configuration", {}))
        if realization.get("configuration_fingerprint") != actual:
            issues.append(f"{rel}: configuration fingerprint mismatch; expected {actual}")
        access_regime = realization.get("configuration", {}).get("access", {}).get("billing_regime")
        economics_regime = realization.get("configuration", {}).get("economics", {}).get("active_regime")
        if access_regime != economics_regime:
            issues.append(f"{rel}: access billing regime and economics active regime differ")
        if access_regime == "chatgpt_quota":
            prices = realization.get("configuration", {}).get("economics", {}).get("reference_prices", [])
            if any(not item.get("not_active_for_this_realization") for item in prices):
                issues.append(f"{rel}: API reference price must not be represented as active ChatGPT quota cost")
        context = realization.get("configuration", {}).get("context", {})
        native_api = context.get("native_api")
        if isinstance(native_api, dict) and native_api.get(
            "context_window_tokens", 0
        ) < context.get("nominal_context_tokens", 0):
            issues.append(
                f"{rel}: native API context cannot be smaller than the recorded Codex context"
            )
        lifecycle_state = realization.get("lifecycle_state")
        runtime_subject = (
            realization.get("configuration", {})
            .get("runtime", {})
            .get("runtime_subject")
        )
        if lifecycle_state in {"declared", "observed"}:
            subject_errors = runtime_subject_validation_errors(root, runtime_subject)
            if subject_errors:
                issues.append(
                    f"{rel}: active realization requires an exact runtime_subject identity: "
                    + "; ".join(subject_errors)
                )
            else:
                evidence_digests = {
                    ref.get("content_digest")
                    for ref in realization.get("source_refs", [])
                    if isinstance(ref, dict)
                }
                if runtime_subject["digest"] not in evidence_digests:
                    issues.append(
                        f"{rel}: runtime_subject digest is not backed by a source_ref content_digest"
                    )
        transition = realization.get("lifecycle_transition")
        if lifecycle_state in {"suspended", "stale", "retired"}:
            if not isinstance(transition, dict):
                issues.append(f"{rel}: inactive realization requires lifecycle_transition")
            else:
                if transition.get("to") != lifecycle_state:
                    issues.append(
                        f"{rel}: lifecycle transition target does not match {lifecycle_state}"
                    )
                source_ids = {
                    item.get("source_id")
                    for item in realization.get("source_refs", [])
                    if isinstance(item, dict)
                }
                for evidence_ref in transition.get("evidence_refs", []):
                    if evidence_ref not in source_ids:
                        issues.append(
                            f"{rel}: lifecycle transition evidence ref is not a source_ref: {evidence_ref}"
                        )
            if realization.get("observation_interval", {}).get("end") is None:
                issues.append(f"{rel}: inactive realization requires a closed observation interval")
        elif transition is not None:
            issues.append(
                f"{rel}: active realization must not carry an inactive lifecycle transition"
            )

    for path, claim in records.get("ModelClaim", []):
        _validate_claim(
            root,
            path.relative_to(root),
            claim,
            realization_paths,
            realizations_by_path,
            issues,
        )
    for path, study in records.get("ModelStudy", []):
        _validate_study(path.relative_to(root), study, realization_paths, issues)
    for path, projection in records.get("ModelFitProjection", []):
        _validate_projection(
            path.relative_to(root),
            projection,
            realization_paths,
            claim_paths,
            study_paths,
            claims_by_path,
            issues,
        )

    if not records.get("ModelIdentity"):
        issues.append("source/model-identities: at least one ModelIdentity is required")
    if not records.get("ModelRealization"):
        issues.append("source/model-realizations: at least one ModelRealization is required")
    if not records.get("ModelClaim"):
        issues.append("source/model-claims: at least one ModelClaim is required")
    return sorted(set(issues))
