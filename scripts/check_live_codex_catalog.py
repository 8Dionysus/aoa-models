#!/usr/bin/env python3
"""Compare active Codex realizations with the live Codex model catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from model_contract import DEFAULT_ROOT, load_json, runtime_subject_validation_errors


ACTIVE_REALIZATION_STATES = {"declared", "observed"}


def _normalized_codex_version(version_output: str) -> str:
    match = re.fullmatch(r"codex-cli\s+([^\s]+)", version_output.strip())
    if not match:
        raise ValueError(f"unsupported Codex version output: {version_output!r}")
    return match.group(1)


def _catalog_models(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    models = catalog.get("models")
    if not isinstance(models, list):
        raise ValueError("Codex model catalog has no models array")
    return {
        model["slug"]: model
        for model in models
        if isinstance(model, dict) and isinstance(model.get("slug"), str)
    }


def assess_realization(
    realization_ref: str,
    realization: dict[str, Any],
    codex_version: str,
    models_by_slug: dict[str, dict[str, Any]],
    runtime_subject: dict[str, Any] | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    configuration = realization["configuration"]
    runtime = configuration["runtime"]
    context = configuration["context"]
    model_slug = runtime["model_slug"]
    model = models_by_slug.get(model_slug)
    mismatches: list[str] = []

    if runtime["product"] != "codex-cli":
        mismatches.append(f"runtime product is {runtime['product']!r}, not 'codex-cli'")
    if runtime["version"] != codex_version:
        mismatches.append(
            f"runtime version {runtime['version']!r} differs from live {codex_version!r}"
        )
    expected_subject = runtime.get("runtime_subject")
    expected_subject_errors = (
        runtime_subject_validation_errors(root, expected_subject)
        if root is not None
        else []
    )
    if expected_subject_errors or not isinstance(expected_subject, dict):
        mismatches.append(
            "realization has no valid exact runtime subject identity"
            + (": " + "; ".join(expected_subject_errors) if expected_subject_errors else "")
        )
    elif runtime_subject is None:
        mismatches.append("live exact runtime subject identity was not supplied")
    elif expected_subject != runtime_subject:
        mismatches.append("live runtime subject identity differs from the realization")
    if model is None:
        mismatches.append(f"model slug {model_slug!r} is absent from the live catalog")
    else:
        supported_efforts = {
            item.get("effort")
            for item in model.get("supported_reasoning_levels", [])
            if isinstance(item, dict)
        }
        if configuration["reasoning_effort"] not in supported_efforts:
            mismatches.append(
                f"reasoning effort {configuration['reasoning_effort']!r} is absent from the live catalog"
            )
        if context["nominal_context_tokens"] != model.get("context_window"):
            mismatches.append(
                "Codex context window differs from the realization record"
            )
        if context["effective_context_percent"] != model.get(
            "effective_context_window_percent"
        ):
            mismatches.append(
                "effective Codex context percentage differs from the realization record"
            )
        if runtime.get("multi_agent_backend_version") != model.get(
            "multi_agent_version"
        ):
            mismatches.append(
                "multi-agent backend version differs from the realization record"
            )
        if configuration["access"]["supported_in_api"] != model.get(
            "supported_in_api"
        ):
            mismatches.append("API support differs from the realization record")

    lifecycle_state = realization["lifecycle_state"]
    if lifecycle_state in ACTIVE_REALIZATION_STATES:
        currentness = "current" if not mismatches else "active_mismatch"
    else:
        currentness = "historical"
    return {
        "realization_ref": realization_ref,
        "model_slug": model_slug,
        "lifecycle_state": lifecycle_state,
        "currentness": currentness,
        "mismatches": mismatches,
    }


def check_catalog(
    root: Path,
    catalog: dict[str, Any],
    codex_version_output: str,
    required_realization_refs: tuple[str, ...] = (),
    runtime_subject: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], bool]:
    root = root.resolve()
    codex_version = _normalized_codex_version(codex_version_output)
    models_by_slug = _catalog_models(catalog)
    subject_errors = (
        runtime_subject_validation_errors(root, runtime_subject)
        if runtime_subject is not None
        else []
    )
    assessments = []
    for path in sorted((root / "source/model-realizations").glob("*.json")):
        realization_ref = path.relative_to(root).as_posix()
        assessments.append(
            assess_realization(
                realization_ref,
                load_json(path),
                codex_version,
                models_by_slug,
                runtime_subject,
                root,
            )
        )

    by_ref = {item["realization_ref"]: item for item in assessments}
    required_failures = [
        ref
        for ref in required_realization_refs
        if ref not in by_ref or by_ref[ref]["currentness"] != "current"
    ]
    active_mismatches = [
        item["realization_ref"]
        for item in assessments
        if item["currentness"] == "active_mismatch"
    ]
    ok = not subject_errors and not required_failures and not active_mismatches
    result = {
        "schema_version": "aoa_models_live_codex_catalog_check_v1",
        "codex_version": codex_version,
        "runtime_subject": runtime_subject,
        "runtime_subject_errors": subject_errors,
        "catalog_model_count": len(models_by_slug),
        "assessment_count": len(assessments),
        "assessments": assessments,
        "required_realization_refs": list(required_realization_refs),
        "required_failures": required_failures,
        "active_mismatches": active_mismatches,
        "ok": ok,
        "claim_limit": (
            "live Codex catalog compatibility only; runtime-profile availability, "
            "model fit, activation, proof, and owner acceptance require separate evidence"
        ),
    }
    return result, ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--codex-version")
    parser.add_argument("--codex-executable", default="codex")
    parser.add_argument("--require-realization-ref", action="append", default=[])
    parser.add_argument("--runtime-subject-source")
    parser.add_argument("--runtime-subject-digest")
    parser.add_argument("--runtime-subject-kind", default="content_addressed_runtime")
    args = parser.parse_args()

    if args.catalog:
        if not args.codex_version:
            parser.error("--codex-version is required with --catalog")
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        version_output = args.codex_version
    else:
        version_output = subprocess.run(
            [args.codex_executable, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        catalog = json.loads(
            subprocess.run(
                [args.codex_executable, "debug", "models"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )

    result, ok = check_catalog(
        args.root,
        catalog,
        version_output,
        tuple(args.require_realization_ref),
        (
            {
                "kind": args.runtime_subject_kind,
                "source": args.runtime_subject_source,
                "digest": args.runtime_subject_digest,
            }
            if args.runtime_subject_source is not None or args.runtime_subject_digest is not None
            else None
        ),
    )
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
