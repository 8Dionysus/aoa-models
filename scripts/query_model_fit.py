#!/usr/bin/env python3
"""Query current informational model-fit projections without activating them."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from model_contract import (
    DEFAULT_ROOT,
    load_json,
    runtime_subject_validation_errors,
)


ACTIVE_REALIZATION_STATES = {"declared", "observed"}
ZERO_DIGEST = "sha256:" + "0" * 64
PROVENANCE_SCHEMAS = {
    "realization": ("schemas/model-realization.schema.json", "aoa_model_realization_v1"),
    "projection": (
        "schemas/model-fit-projection.schema.json",
        "aoa_model_fit_projection_v1",
    ),
    "claim": ("schemas/model-claim.schema.json", "aoa_model_claim_v1"),
    "study": ("schemas/model-study.schema.json", "aoa_model_study_v1"),
}


class ModelFitQueryError(ValueError):
    """The read-only fit query cannot produce exact owner evidence."""


def canonical_digest(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ModelFitQueryError(f"cannot verify aoa-models Git source: {' '.join(args)}") from exc
    return result.stdout.strip()


def _owner_source_ref(root: Path) -> str:
    top = Path(_git(root, "rev-parse", "--show-toplevel")).resolve(strict=True)
    if top != root:
        raise ModelFitQueryError("query root must name the exact aoa-models worktree")
    source_ref = _git(root, "rev-parse", "HEAD")
    if re.fullmatch(r"[0-9a-f]{40}", source_ref) is None:
        raise ModelFitQueryError("aoa-models HEAD is not a full SHA-1 source ref")
    return source_ref


def _artifact_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _provenance_ref(
    root: Path,
    relative: str,
    *,
    source_ref: str,
    kind: str,
) -> dict[str, str]:
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise ModelFitQueryError(f"model-fit evidence is unavailable: {relative}")
    schema_ref, schema_version = PROVENANCE_SCHEMAS[kind]
    return {
        "owner_repo": "aoa-models",
        "artifact_ref": relative,
        "source_ref": source_ref,
        "artifact_digest": _artifact_digest(path),
        "schema_ref": schema_ref,
        "schema_version": schema_version,
    }


def _assert_clean_evidence(root: Path, paths: set[str]) -> None:
    if not paths:
        return
    status = _git(root, "status", "--porcelain=v1", "--", *sorted(paths))
    if status:
        raise ModelFitQueryError(
            "selected aoa-models fit evidence is dirty relative to owner_source_ref"
        )


def _catalog_digest(root: Path, directories: tuple[str, ...]) -> str:
    inventory = []
    for directory in directories:
        for path in sorted((root / directory).glob("*.json")):
            inventory.append(
                {
                    "artifact_ref": path.relative_to(root).as_posix(),
                    "artifact_digest": _artifact_digest(path),
                }
            )
    return canonical_digest(inventory)


def _catalog_paths(root: Path, directories: tuple[str, ...]) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for directory in directories
        for path in (root / directory).glob("*.json")
    }


def _validate_query(root: Path, query: dict[str, Any]) -> None:
    schema = load_json(root / "schemas/model-fit-query.schema.json")
    runtime_subject_schema = load_json(root / "schemas/runtime-subject.schema.json")
    Draft202012Validator(
        schema,
        registry=Registry().with_resource(
            runtime_subject_schema["$id"], Resource.from_contents(runtime_subject_schema)
        ),
        format_checker=FormatChecker(),
    ).validate(query)


def validate_query_result(root: Path, result: dict[str, Any]) -> None:
    query_schema = load_json(root / "schemas/model-fit-query.schema.json")
    result_schema = load_json(root / "schemas/model-fit-query-result.schema.json")
    runtime_subject_schema = load_json(root / "schemas/runtime-subject.schema.json")
    registry = (
        Registry()
        .with_resource(query_schema["$id"], Resource.from_contents(query_schema))
        .with_resource(runtime_subject_schema["$id"], Resource.from_contents(runtime_subject_schema))
    )
    Draft202012Validator(
        result_schema,
        registry=registry,
        format_checker=FormatChecker(),
    ).validate(result)


def _load_by_relative_path(root: Path, directory: str) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(root).as_posix(): load_json(path)
        for path in sorted((root / directory).glob("*.json"))
    }


def query_model_fit(root: Path, query: dict[str, Any]) -> dict[str, Any]:
    root = root.resolve()
    _validate_query(root, query)
    subject_errors = runtime_subject_validation_errors(root, query.get("runtime_subject"))
    if subject_errors:
        raise ModelFitQueryError(
            "exact runtime subject identity is required: " + "; ".join(subject_errors)
        )
    source_ref = _owner_source_ref(root)
    realizations = _load_by_relative_path(root, "source/model-realizations")
    projections = _load_by_relative_path(root, "generated/model-fit-projections")
    candidates: list[dict[str, Any]] = []
    selected_evidence_paths: set[str] = set()

    required_tools = set(query["required_tools"])
    required_mcp_servers = set(query["required_mcp_servers"])
    requested_effort = query.get("reasoning_effort")

    for projection_ref, projection in sorted(projections.items()):
        realization_ref = projection["subject_realization_ref"]
        realization = realizations.get(realization_ref)
        if realization is None:
            continue
        if realization["lifecycle_state"] not in ACTIVE_REALIZATION_STATES:
            continue
        if projection["freshness"]["status"] not in {"current", "unknown"}:
            continue

        configuration = realization["configuration"]
        runtime = configuration["runtime"]
        tools = configuration["tools"]
        permissions = configuration["permissions"]

        realization_subject = runtime.get("runtime_subject")
        if realization_subject != query["runtime_subject"]:
            continue
        if runtime["product"] != query["runtime_product"]:
            continue
        if runtime["version"] != query["runtime_version"]:
            continue
        if requested_effort and configuration["reasoning_effort"] != requested_effort:
            continue
        if permissions["sandbox_mode"] != query["sandbox_mode"]:
            continue
        if not required_tools.issubset(set(tools["required_tools"])):
            continue
        if not required_mcp_servers.issubset(set(tools["required_mcp_servers"])):
            continue

        task_fit = [
            item for item in projection["task_fit"] if item["task_family"] == query["task_family"]
        ]
        if not task_fit:
            continue

        limitations: list[str] = []
        if realization["lifecycle_state"] == "declared":
            limitations.append(
                "realization is declared from current owner inputs but is not yet observed in an external actor run"
            )
        if any(item.get("escalation_required") for item in task_fit):
            limitations.append(
                "source claim is not reviewed; stronger-owner escalation remains required"
            )
        limitations.append(
            "candidate is informational and cannot activate, route, prove, or accept work"
        )

        claim_refs = list(projection["generated_from_claim_refs"])
        study_refs = list(projection["study_refs"])
        fit_evidence_refs = [
            *(
                _provenance_ref(
                    root,
                    claim_ref,
                    source_ref=source_ref,
                    kind="claim",
                )
                for claim_ref in claim_refs
            ),
            *(
                _provenance_ref(
                    root,
                    study_ref,
                    source_ref=source_ref,
                    kind="study",
                )
                for study_ref in study_refs
            ),
        ]
        selected_evidence_paths.update({realization_ref, projection_ref, *claim_refs, *study_refs})

        candidates.append(
            {
                "realization_ref": realization_ref,
                "projection_ref": projection_ref,
                "runtime_subject": realization_subject,
                "realization_provenance": _provenance_ref(
                    root,
                    realization_ref,
                    source_ref=source_ref,
                    kind="realization",
                ),
                "projection_provenance": _provenance_ref(
                    root,
                    projection_ref,
                    source_ref=source_ref,
                    kind="projection",
                ),
                "fit_evidence_refs": fit_evidence_refs,
                "model_slug": runtime["model_slug"],
                "reasoning_effort": configuration["reasoning_effort"],
                "sandbox_mode": permissions["sandbox_mode"],
                "lifecycle_state": realization["lifecycle_state"],
                "projection_posture": projection["posture"],
                "freshness": projection["freshness"]["status"],
                "task_fit": task_fit,
                "limitations": limitations,
            }
        )

    candidates.sort(key=lambda item: item["realization_ref"])
    catalog_directories = (
        "source/model-realizations",
        "generated/model-fit-projections",
    )
    _assert_clean_evidence(
        root,
        selected_evidence_paths | _catalog_paths(root, catalog_directories),
    )
    query_digest = canonical_digest(query)
    result = {
        "schema_version": "aoa_model_fit_query_result_v2",
        "result_id": f"model-fit-query-result:{query_digest.removeprefix('sha256:')[:32]}",
        "query_digest": query_digest,
        "query": query,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "authority": {
            "informational_only": True,
            "activation_authority": False,
            "routing_authority": False,
            "proof_authority": False,
            "acceptance_authority": False,
        },
        "owner_source_ref": source_ref,
        "catalog_digest": _catalog_digest(root, catalog_directories),
        "result_digest": ZERO_DIGEST,
    }
    result["result_digest"] = canonical_digest(result)
    validate_query_result(root, result)
    assert_query_result_digest(result)
    return result


def assert_query_result_digest(result: dict[str, Any]) -> None:
    expected = canonical_digest(result | {"result_digest": ZERO_DIGEST})
    if result.get("result_digest") != expected:
        raise ModelFitQueryError(f"model-fit query result digest mismatch: expected {expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--task-family", required=True)
    parser.add_argument("--runtime-product", default="codex-cli")
    parser.add_argument("--runtime-version", required=True)
    parser.add_argument("--runtime-subject-source")
    parser.add_argument("--runtime-subject-digest")
    parser.add_argument("--runtime-subject-kind", default="content_addressed_runtime")
    parser.add_argument(
        "--reasoning-effort",
        choices=("low", "medium", "high", "xhigh", "max"),
    )
    parser.add_argument(
        "--sandbox-mode",
        required=True,
        choices=("read-only", "workspace-write", "danger-full-access"),
    )
    parser.add_argument("--required-tool", action="append", default=[])
    parser.add_argument("--required-mcp-server", action="append", default=[])
    parser.add_argument("--require-match", action="store_true")
    args = parser.parse_args()

    query = {
        "schema_version": "aoa_model_fit_query_v1",
        "task_family": args.task_family,
        "runtime_product": args.runtime_product,
        "runtime_version": args.runtime_version,
        "reasoning_effort": args.reasoning_effort,
        "sandbox_mode": args.sandbox_mode,
        "required_tools": sorted(set(args.required_tool)),
        "required_mcp_servers": sorted(set(args.required_mcp_server)),
    }
    if args.runtime_subject_source is not None or args.runtime_subject_digest is not None:
        query["runtime_subject"] = {
            "kind": args.runtime_subject_kind,
            "source": args.runtime_subject_source,
            "digest": args.runtime_subject_digest,
        }
    result = query_model_fit(args.root, query)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    if args.require_match and result["candidate_count"] == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
