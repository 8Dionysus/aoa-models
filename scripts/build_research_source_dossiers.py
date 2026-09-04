#!/usr/bin/env python3
"""Build the generated, pre-canon research-source dossier catalog."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from research_source_dossiers import (
    DEFAULT_ROOT,
    OUTPUT_PATH,
    ResearchSourceDossierError,
    build_catalog,
    render_catalog,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    output_path = root / OUTPUT_PATH
    try:
        catalog = build_catalog(root)
    except (OSError, KeyError, TypeError, ResearchSourceDossierError) as exc:
        print(f"ERROR: cannot build source dossier catalog: {exc}", file=sys.stderr)
        return 1
    expected = render_catalog(catalog)
    if args.check:
        if not output_path.is_file() or output_path.read_text(encoding="utf-8") != expected:
            print(f"ERROR: {OUTPUT_PATH} is missing or stale", file=sys.stderr)
            return 1
        print(
            "OK: "
            f"{catalog['counts']['dossiers']} research-source dossier(s) are current "
            f"from {catalog['counts']['source_appearances']} source appearance(s)"
        )
        return 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(expected, encoding="utf-8")
    print(
        f"wrote {OUTPUT_PATH} with {catalog['counts']['dossiers']} dossier(s) "
        f"from {catalog['counts']['source_appearances']} source appearance(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
