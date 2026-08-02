#!/usr/bin/env python3
"""Build informational model-fit projections from owner-authored claims."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Any

from model_contract import DEFAULT_ROOT, load_json


OUTPUT_DIR = Path("generated/model-fit-projections")
CLAIM_DIR = Path("source/model-claims")
REALIZATION_DIR = Path("source/model-realizations")
STUDY_DIR = Path("source/model-studies")


def _path_map(root: Path, directory: Path) -> dict[str, dict[str, Any]]:
    return {
        path.relative_to(root).as_posix(): load_json(path)
        for path in sorted((root / directory).glob("*.json"))
    }


def _projection_filename(realization_ref: str) -> str:
    return Path(realization_ref).name


def build_expected(root: Path = DEFAULT_ROOT) -> dict[str, str]:
    root = root.resolve()
    claims = _path_map(root, CLAIM_DIR)
    realizations = _path_map(root, REALIZATION_DIR)
    studies = _path_map(root, STUDY_DIR)
    claims_by_realization: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for claim_ref, claim in claims.items():
        state = claim.get("lifecycle", {}).get("state")
        if state in {"stale", "superseded", "retracted"}:
            continue
        for realization_ref in claim.get("subject_realization_refs", []):
            claims_by_realization[realization_ref].append((claim_ref, claim))

    studies_by_realization: dict[str, list[str]] = defaultdict(list)
    for study_ref, study in studies.items():
        for arm in study.get("comparison_arms", []):
            for realization_ref in arm.get("realization_refs", []):
                studies_by_realization[realization_ref].append(study_ref)

    expected: dict[str, str] = {}
    for realization_ref, claim_entries in sorted(claims_by_realization.items()):
        if realization_ref not in realizations:
            continue
        realization = realizations[realization_ref]
        states = [claim.get("lifecycle", {}).get("state") for _, claim in claim_entries]
        reviewed_task_outcome = any(
            claim.get("lifecycle", {}).get("state") == "reviewed"
            and claim.get("evidence_modality") == "task_outcome_evidence"
            for _, claim in claim_entries
        )
        posture = "candidate" if reviewed_task_outcome else "declared"
        task_fit = []
        for _, claim in sorted(claim_entries):
            state = claim.get("lifecycle", {}).get("state", "hypothesis")
            task_fit.append(
                {
                    "task_family": claim["scope"]["task_family"],
                    "claim_posture": state,
                    "conditions": claim["scope"]["conditions"],
                    "exclusions": claim["scope"]["exclusions"],
                    "escalation_required": state != "reviewed",
                }
            )
        review_dates = [
            claim.get("freshness", {}).get("review_by")
            for _, claim in claim_entries
            if claim.get("freshness", {}).get("review_by")
        ]
        freshness_states = {
            claim.get("freshness", {}).get("status", "unknown")
            for _, claim in claim_entries
        }
        freshness_status = (
            "stale" if "stale" in freshness_states else "unknown" if "unknown" in freshness_states else "current"
        )
        timestamps = [realization["updated_at"]]
        timestamps.extend(claim["updated_at"] for _, claim in claim_entries)
        timestamps.extend(
            studies[study_ref]["updated_at"]
            for study_ref in studies_by_realization.get(realization_ref, [])
        )
        stem = Path(realization_ref).stem
        projection = {
            "$schema": "https://schemas.aoa.local/models/model-fit-projection.schema.json",
            "schema_version": "aoa_model_fit_projection_v1",
            "kind": "ModelFitProjection",
            "model_fit_projection_id": f"model-fit-projection:{stem}",
            "subject_realization_ref": realization_ref,
            "consumers": ["aoa-agents", "aoa-sdk", "abyss-stack"],
            "generated_from_claim_refs": sorted(ref for ref, _ in claim_entries),
            "study_refs": sorted(set(studies_by_realization.get(realization_ref, []))),
            "posture": posture,
            "effect_family": "read",
            "task_fit": task_fit,
            "authority": {
                "informational_only": True,
                "activation_authority": False,
                "proof_authority": False,
                "acceptance_authority": False,
            },
            "freshness": {
                "status": freshness_status,
                "review_by": min(review_dates) if review_dates else None,
            },
            "must_not_claim": [
                "routing or activation authority",
                "proof or owner acceptance",
                "landing completion",
                "internal geometry or training lineage from behavior alone",
            ],
            "generated_at": max(timestamps),
        }
        relative = (OUTPUT_DIR / _projection_filename(realization_ref)).as_posix()
        expected[relative] = json.dumps(
            projection,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
    return expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    expected = build_expected(root)
    output_dir = root / OUTPUT_DIR
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in output_dir.glob("*.json")
    } if output_dir.exists() else set()
    expected_paths = set(expected)
    stale_paths = sorted(actual_paths - expected_paths)
    if stale_paths:
        for path in stale_paths:
            print(f"ERROR: stale generated projection requires source-aware removal: {path}", file=sys.stderr)
        return 1
    if args.check:
        mismatches = []
        for relative, content in expected.items():
            path = root / relative
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                mismatches.append(relative)
        if mismatches:
            for relative in mismatches:
                print(f"ERROR: missing or stale generated projection: {relative}", file=sys.stderr)
            return 1
        print(f"OK: {len(expected)} generated model-fit projection(s) are current")
        return 0
    output_dir.mkdir(parents=True, exist_ok=True)
    for relative, content in expected.items():
        (root / relative).write_text(content, encoding="utf-8")
        print(f"wrote {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
