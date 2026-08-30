#!/usr/bin/env python3
"""Validate aoa-models schemas, sources, lifecycle, and derived authority."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from model_contract import DEFAULT_ROOT, collect_records, validate_repo
from research_intake_contract import research_intake_summary, validate_research_intake


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    issues = [*validate_repo(args.root), *validate_research_intake(args.root)]
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1
    records, _ = collect_records(args.root.resolve())
    model_counts = [
        f"{kind}={len(entries)}" for kind, entries in sorted(records.items())
    ]
    research_counts = [
        f"{kind}={count}"
        for kind, count in research_intake_summary(args.root.resolve()).items()
    ]
    counts = ", ".join([*model_counts, *research_counts])
    print(f"OK: aoa-models source and derived contracts are valid ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
