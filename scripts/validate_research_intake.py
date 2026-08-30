#!/usr/bin/env python3
"""Validate pre-canon external research-intake packets."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from research_intake_contract import (
    DEFAULT_ROOT,
    canonical_digest,
    collect_recon_runs,
    research_intake_summary,
    validate_research_intake,
)
from research_automation_contract import collect_research_automation_artifacts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    issues = validate_research_intake(root)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1
    records, _ = collect_recon_runs(root)
    for path, record in records:
        print(
            f"RUN {record['recon_run_id']} {canonical_digest(record)} "
            f"{path.relative_to(root)}"
        )
    automation_records, _ = collect_research_automation_artifacts(root)
    for path, record in automation_records:
        artifact_id = (
            record.get("capture_id")
            or record.get("receipt_id")
            or record.get("proposal_id")
        )
        print(
            f"ARTIFACT {artifact_id} {record['artifact_digest']} "
            f"{path.relative_to(root)}"
        )
    counts = ", ".join(
        f"{kind}={count}" for kind, count in research_intake_summary(root).items()
    )
    print(f"OK: pre-canon research intake is valid ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
