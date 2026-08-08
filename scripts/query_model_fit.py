#!/usr/bin/env python3
"""Query current informational model-fit projections without activating them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from model_contract import DEFAULT_ROOT, load_json


ACTIVE_REALIZATION_STATES = {"declared", "observed"}


def _validate_query(root: Path, query: dict[str, Any]) -> None:
    schema = load_json(root / "schemas/model-fit-query.schema.json")
    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(query)


def validate_query_result(root: Path, result: dict[str, Any]) -> None:
    query_schema = load_json(root / "schemas/model-fit-query.schema.json")
    result_schema = load_json(root / "schemas/model-fit-query-result.schema.json")
    registry = Registry().with_resource(
        query_schema["$id"], Resource.from_contents(query_schema)
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
    realizations = _load_by_relative_path(root, "source/model-realizations")
    projections = _load_by_relative_path(root, "generated/model-fit-projections")
    candidates: list[dict[str, Any]] = []

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
            item
            for item in projection["task_fit"]
            if item["task_family"] == query["task_family"]
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

        candidates.append(
            {
                "realization_ref": realization_ref,
                "projection_ref": projection_ref,
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
    result = {
        "schema_version": "aoa_model_fit_query_result_v1",
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
        "source_root": str(root),
    }
    validate_query_result(root, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--task-family", required=True)
    parser.add_argument("--runtime-product", default="codex-cli")
    parser.add_argument("--runtime-version", required=True)
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
    result = query_model_fit(args.root, query)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    if args.require_match and result["candidate_count"] == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
