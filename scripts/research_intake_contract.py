#!/usr/bin/env python3
"""Schema and semantic validation for pre-canon external recon packets."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

from research_automation_contract import (
    research_automation_summary,
    validate_research_automation,
)
from research_source_dossiers import (
    source_dossier_summary,
    validate_research_source_dossiers,
)


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
RECON_RUN_DIRECTORY = Path("research-intake/recon-runs")
RECON_RUN_SCHEMA = Path("schemas/recon-run.schema.json")


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


def collect_recon_runs(
    root: Path = DEFAULT_ROOT,
) -> tuple[list[tuple[Path, dict[str, Any]]], list[str]]:
    root = root.resolve()
    directory = root / RECON_RUN_DIRECTORY
    records: list[tuple[Path, dict[str, Any]]] = []
    issues: list[str] = []
    if not directory.exists():
        return records, issues
    for path in sorted(directory.glob("*.json")):
        try:
            records.append((path, load_json(path)))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(f"{path.relative_to(root)}: invalid JSON: {exc}")
    for path in sorted(directory.rglob("*.json")):
        if path.parent != directory:
            issues.append(
                f"{path.relative_to(root)}: recon packet is outside the declared flat run route"
            )
    return records, issues


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _validate_interval(
    interval: Any,
    label: str,
    rel: Path,
    issues: list[str],
) -> None:
    if not isinstance(interval, dict):
        return
    try:
        start = _parse_datetime(interval["start"])
        end_value = interval.get("end")
        end = _parse_datetime(end_value) if end_value else None
    except (KeyError, TypeError, ValueError) as exc:
        issues.append(f"{rel}: invalid {label} interval: {exc}")
        return
    if end is not None and end < start:
        issues.append(f"{rel}: {label} interval ends before it starts")


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicate: set[str] = set()
    for value in values:
        if value in seen:
            duplicate.add(value)
        seen.add(value)
    return duplicate


def _validate_no_direct_promotion(root: Path, issues: list[str]) -> None:
    for directory in (
        root / "source/model-identities",
        root / "source/model-realizations",
        root / "source/model-claims",
        root / "source/model-studies",
    ):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            try:
                record = load_json(path)
            except (OSError, json.JSONDecodeError):
                continue
            for key in (
                "source_refs",
                "evidence_refs",
                "known_counterevidence",
                "independent_review_refs",
                "result_refs",
            ):
                for ref in record.get(key, []):
                    uri = ref.get("uri", "") if isinstance(ref, dict) else ""
                    if isinstance(uri, str) and uri.startswith("research-intake/"):
                        issues.append(
                            f"{path.relative_to(root)}: pre-canon research-intake record "
                            "cannot be direct owner evidence or an accepted source reference"
                        )


def _validate_dependency_graph(
    dependencies: dict[str, list[str]],
    rel: Path,
    issues: list[str],
) -> None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(source_id: str) -> None:
        marker = state.get(source_id, 0)
        if marker == 2:
            return
        if marker == 1:
            start = stack.index(source_id)
            cycle = " -> ".join([*stack[start:], source_id])
            issues.append(f"{rel}: source dependency cycle: {cycle}")
            return
        state[source_id] = 1
        stack.append(source_id)
        for dependency in dependencies.get(source_id, []):
            if dependency in dependencies:
                visit(dependency)
        stack.pop()
        state[source_id] = 2

    for source_id in dependencies:
        if state.get(source_id, 0) == 0:
            visit(source_id)


def _validate_local_artifact_digests(
    root: Path,
    rel: Path,
    packet: dict[str, Any],
    issues: list[str],
) -> None:
    artifacts = [
        *(packet.get("method", {}).get("artifacts", [])),
        *(packet.get("lineage", {}).get("predecessor_artifacts", [])),
    ]
    recon_directory = (root / RECON_RUN_DIRECTORY).resolve()
    for artifact in artifacts:
        ref = artifact.get("ref")
        declared_digest = artifact.get("content_digest")
        if not isinstance(ref, str) or not isinstance(declared_digest, str):
            continue
        if urlparse(ref).scheme:
            continue
        ref_path = Path(ref)
        if ref_path.is_absolute():
            issues.append(f"{rel}: local artifact ref must be repository-relative: {ref!r}")
            continue
        artifact_path = (root / ref_path).resolve()
        try:
            artifact_path.relative_to(root)
        except ValueError:
            issues.append(f"{rel}: local artifact ref escapes repository: {ref!r}")
            continue
        if not artifact_path.is_file():
            issues.append(f"{rel}: local artifact does not exist: {ref!r}")
            continue
        try:
            if artifact_path.parent == recon_directory and artifact_path.suffix == ".json":
                actual_digest = canonical_digest(load_json(artifact_path))
            else:
                actual_digest = "sha256:" + hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(f"{rel}: cannot digest local artifact {ref!r}: {exc}")
            continue
        if declared_digest != actual_digest:
            issues.append(
                f"{rel}: local artifact digest mismatch for {ref!r}: "
                f"declared {declared_digest}, actual {actual_digest}"
            )


def _validate_packet(
    root: Path,
    rel: Path,
    packet: dict[str, Any],
    runs_by_id: dict[str, dict[str, Any]],
    observations_by_run: dict[str, set[str]],
    realization_paths: set[str],
    issues: list[str],
) -> None:
    run_id = packet.get("recon_run_id")
    source_captures = packet.get("source_captures", [])
    observations = packet.get("observations", [])
    clusters = packet.get("clusters", [])
    tensions = packet.get("tensions", [])
    method_pressures = packet.get("method_pressures", [])
    search_probes = packet.get("search_probes", [])

    source_ids = [item.get("source_id") for item in source_captures if item.get("source_id")]
    observation_ids = [
        item.get("observation_id") for item in observations if item.get("observation_id")
    ]
    cluster_ids = [item.get("cluster_id") for item in clusters if item.get("cluster_id")]
    tension_ids = [item.get("tension_id") for item in tensions if item.get("tension_id")]
    pressure_ids = [
        item.get("pressure_id") for item in method_pressures if item.get("pressure_id")
    ]
    probe_ids = [item.get("probe_id") for item in search_probes if item.get("probe_id")]
    record_ids = [
        *source_ids,
        *observation_ids,
        *cluster_ids,
        *tension_ids,
        *pressure_ids,
        *probe_ids,
    ]
    for duplicate in sorted(_duplicates(record_ids)):
        issues.append(f"{rel}: duplicate packet-local record ID {duplicate!r}")

    source_id_set = set(source_ids)
    observation_id_set = set(observation_ids)
    source_by_id = {
        source["source_id"]: source
        for source in source_captures
        if isinstance(source, dict) and source.get("source_id")
    }
    segment_refs: set[tuple[str, str]] = set()
    dependencies: dict[str, list[str]] = {}
    for source in source_captures:
        source_id = source.get("source_id")
        if not source_id:
            continue
        segment_ids = [
            segment.get("segment_id")
            for segment in source.get("segments", [])
            if segment.get("segment_id")
        ]
        for duplicate in sorted(_duplicates(segment_ids)):
            issues.append(f"{rel}: source {source_id!r} repeats segment ID {duplicate!r}")
        segment_refs.update((source_id, segment_id) for segment_id in segment_ids)
        dependency_refs = source.get("dependency_refs", [])
        dependencies[source_id] = list(dependency_refs)
        for dependency in dependency_refs:
            if dependency not in source_id_set:
                issues.append(
                    f"{rel}: source {source_id!r} dependency does not exist: {dependency!r}"
                )
            if dependency == source_id:
                issues.append(f"{rel}: source {source_id!r} cannot depend on itself")
        if source.get("propagation_role") == "dependent" and not dependency_refs:
            issues.append(
                f"{rel}: dependent source {source_id!r} requires at least one dependency ref"
            )
        _validate_interval(source.get("effective_interval"), f"source {source_id}", rel, issues)
    _validate_dependency_graph(dependencies, rel, issues)

    independent_origins_by_source: dict[str, set[str]] = {}

    def independent_origins(source_id: str, visiting: set[str]) -> set[str]:
        if source_id in independent_origins_by_source:
            return independent_origins_by_source[source_id]
        if source_id in visiting:
            return set()
        source = source_by_id.get(source_id, {})
        role = source.get("propagation_role")
        origins: set[str] = set()
        if role in {"origin", "mixed"} and source.get("origin_group"):
            origins.add(source["origin_group"])
        if role in {"dependent", "mixed", "unresolved"}:
            for dependency in dependencies.get(source_id, []):
                origins.update(independent_origins(dependency, {*visiting, source_id}))
        independent_origins_by_source[source_id] = origins
        return origins

    for source_id in source_id_set:
        independent_origins(source_id, set())

    origin_groups_by_observation: dict[str, set[str]] = defaultdict(set)
    target_kinds = set(packet.get("scope", {}).get("target_kinds", []))
    for observation in observations:
        observation_id = observation.get("observation_id")
        if not observation_id:
            continue
        if observation.get("target_kind") not in target_kinds:
            issues.append(
                f"{rel}: observation {observation_id!r} target kind is absent from run scope"
            )
        seen_source_refs: set[tuple[str, str]] = set()
        for source_ref in observation.get("source_segment_refs", []):
            key = (source_ref.get("source_id"), source_ref.get("segment_id"))
            if key in seen_source_refs:
                issues.append(
                    f"{rel}: observation {observation_id!r} repeats source segment {key!r}"
                )
            seen_source_refs.add(key)
            if key not in segment_refs:
                issues.append(
                    f"{rel}: observation {observation_id!r} source segment does not exist: "
                    f"{key!r}"
                )
            source = source_by_id.get(key[0], {})
            if source:
                origin_groups_by_observation[observation_id].update(
                    independent_origins_by_source.get(key[0], set())
                )
        for counterevidence_ref in observation.get("counterevidence_refs", []):
            if counterevidence_ref not in observation_id_set:
                issues.append(
                    f"{rel}: observation {observation_id!r} counterevidence does not exist: "
                    f"{counterevidence_ref!r}"
                )
            if counterevidence_ref == observation_id:
                issues.append(
                    f"{rel}: observation {observation_id!r} cannot be its own counterevidence"
                )
        subject = observation.get("subject", {})
        configuration = observation.get("configuration", {})
        if (
            subject.get("completeness") in {"partial", "unresolved"}
            or configuration.get("completeness") in {"partial", "unresolved"}
        ) and not observation.get("configuration_gaps"):
            issues.append(
                f"{rel}: partial observation {observation_id!r} requires configuration_gaps"
            )
        for realization_ref in subject.get("owner_realization_refs", []):
            if realization_ref not in realization_paths:
                issues.append(
                    f"{rel}: observation {observation_id!r} owner realization does not exist: "
                    f"{realization_ref}"
                )
        for superseded_ref in observation.get("supersedes", []):
            target_run = superseded_ref.get("recon_run_id")
            target_observation = superseded_ref.get("observation_id")
            if target_run not in runs_by_id:
                issues.append(
                    f"{rel}: observation {observation_id!r} supersedes missing run "
                    f"{target_run!r}"
                )
            elif target_observation not in observations_by_run.get(target_run, set()):
                issues.append(
                    f"{rel}: observation {observation_id!r} supersedes missing observation "
                    f"{target_run!r}/{target_observation!r}"
                )
            if target_run == run_id and target_observation == observation_id:
                issues.append(f"{rel}: observation {observation_id!r} cannot supersede itself")
        _validate_interval(
            observation.get("observed_interval"),
            f"observation {observation_id}",
            rel,
            issues,
        )

    for cluster in clusters:
        cluster_id = cluster.get("cluster_id")
        if not cluster_id:
            continue
        refs = cluster.get("observation_refs", [])
        counterevidence_refs = cluster.get("counterevidence_refs", [])
        for observation_ref in [*refs, *counterevidence_refs]:
            if observation_ref not in observation_id_set:
                issues.append(
                    f"{rel}: cluster {cluster_id!r} observation does not exist: "
                    f"{observation_ref!r}"
                )
        supported_origins: set[str] = set()
        for observation_ref in [*refs, *counterevidence_refs]:
            supported_origins.update(origin_groups_by_observation.get(observation_ref, set()))
        for origin_group in cluster.get("independent_origin_groups", []):
            if origin_group not in supported_origins:
                issues.append(
                    f"{rel}: cluster {cluster_id!r} origin group is not supported by its "
                    f"observations: {origin_group!r}"
                )

    for tension in tensions:
        tension_id = tension.get("tension_id")
        for observation_ref in [
            *tension.get("side_a_refs", []),
            *tension.get("side_b_refs", []),
        ]:
            if observation_ref not in observation_id_set:
                issues.append(
                    f"{rel}: tension {tension_id!r} observation does not exist: "
                    f"{observation_ref!r}"
                )

    for pressure in method_pressures:
        pressure_id = pressure.get("pressure_id")
        for observation_ref in pressure.get("trigger_refs", []):
            if observation_ref not in observation_id_set:
                issues.append(
                    f"{rel}: method pressure {pressure_id!r} observation does not exist: "
                    f"{observation_ref!r}"
                )

    for probe in search_probes:
        probe_id = probe.get("probe_id")
        source_refs = probe.get("source_refs", [])
        observation_refs = probe.get("observation_refs", [])
        result_state = probe.get("result_state")
        for source_ref in source_refs:
            if source_ref not in source_id_set:
                issues.append(
                    f"{rel}: search probe {probe_id!r} source does not exist: {source_ref!r}"
                )
        for observation_ref in observation_refs:
            if observation_ref not in observation_id_set:
                issues.append(
                    f"{rel}: search probe {probe_id!r} observation does not exist: "
                    f"{observation_ref!r}"
                )
        if result_state in {"qualified_evidence_found", "mixed_evidence_found"}:
            if not source_refs or not observation_refs:
                issues.append(
                    f"{rel}: search probe {probe_id!r} with result {result_state!r} "
                    "requires source and observation refs"
                )
        if result_state in {"no_qualified_source_found", "access_limited"}:
            if not probe.get("limitations"):
                issues.append(
                    f"{rel}: search probe {probe_id!r} with result {result_state!r} "
                    "requires limitations"
                )

    for predecessor in packet.get("lineage", {}).get("supersedes_recon_run_refs", []):
        if predecessor == run_id:
            issues.append(f"{rel}: recon run cannot supersede itself")
        elif predecessor not in runs_by_id:
            issues.append(f"{rel}: superseded recon run does not exist: {predecessor!r}")

    _validate_local_artifact_digests(root, rel, packet, issues)

    _validate_interval(packet.get("scope", {}).get("capture_interval"), "capture", rel, issues)
    try:
        created_at = _parse_datetime(packet["created_at"])
        updated_at = _parse_datetime(packet["updated_at"])
        if updated_at < created_at:
            issues.append(f"{rel}: updated_at precedes created_at")
    except (KeyError, TypeError, ValueError):
        pass


def validate_research_intake(root: Path = DEFAULT_ROOT) -> list[str]:
    root = root.resolve()
    issues: list[str] = []
    schema_path = root / RECON_RUN_SCHEMA
    if not schema_path.is_file():
        return [f"{RECON_RUN_SCHEMA}: required schema is missing"]
    try:
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"{RECON_RUN_SCHEMA}: {exc}"]
    records, collect_issues = collect_recon_runs(root)
    issues.extend(collect_issues)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    runs_by_id: dict[str, dict[str, Any]] = {}
    run_paths: dict[str, Path] = {}
    observations_by_run: dict[str, set[str]] = {}
    for path, record in records:
        rel = path.relative_to(root)
        for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
            location = "/".join(str(part) for part in error.path)
            suffix = f" at {location}" if location else ""
            issues.append(f"{rel}: schema error{suffix}: {error.message}")
        run_id = record.get("recon_run_id")
        if run_id in runs_by_id:
            issues.append(f"{rel}: duplicate recon run ID also used by {run_paths[run_id]}")
        elif run_id:
            runs_by_id[run_id] = record
            run_paths[run_id] = rel
            observations_by_run[run_id] = {
                item.get("observation_id")
                for item in record.get("observations", [])
                if item.get("observation_id")
            }

    realization_paths = {
        path.relative_to(root).as_posix()
        for path in (root / "source/model-realizations").glob("*.json")
    }
    for path, packet in records:
        _validate_packet(
            root,
            path.relative_to(root),
            packet,
            runs_by_id,
            observations_by_run,
            realization_paths,
            issues,
        )
    _validate_no_direct_promotion(root, issues)
    issues.extend(validate_research_automation(root))
    issues.extend(validate_research_source_dossiers(root))
    return issues


def research_intake_summary(root: Path = DEFAULT_ROOT) -> dict[str, int]:
    records, _ = collect_recon_runs(root.resolve())
    return {
        "ReconRun": len(records),
        "SourceCapture": sum(len(record.get("source_captures", [])) for _, record in records),
        "ExternalObservation": sum(len(record.get("observations", [])) for _, record in records),
        "ObservationCluster": sum(len(record.get("clusters", [])) for _, record in records),
        **research_automation_summary(root.resolve()),
        **source_dossier_summary(root.resolve()),
    }
