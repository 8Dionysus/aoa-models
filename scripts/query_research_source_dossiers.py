#!/usr/bin/env python3
"""Query the generated source-dossier read model without changing research source."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from research_source_dossiers import (
    DEFAULT_ROOT,
    OUTPUT_PATH,
    find_dossiers,
    load_json,
    validate_research_source_dossiers,
)


def _compact_row(dossier: dict[str, Any]) -> str:
    attention = ",".join(dossier["attention"]) or "none"
    return (
        f"{dossier['dossier_id']} {dossier['canonical_uri']} "
        f"appearances={dossier['appearance_count']} runs={dossier['run_count']} "
        f"posture={dossier['currentness']['posture']} attention={attention}"
    )


def _detail(dossier: dict[str, Any]) -> str:
    lines = [
        f"DOSSIER {dossier['dossier_id']}",
        f"URI {dossier['canonical_uri']}",
        f"RECORDED {dossier['first_recorded_at']} .. {dossier['latest_recorded_at']}",
        f"APPEARANCES {dossier['appearance_count']} across {dossier['run_count']} run(s)",
        (
            "CURRENTNESS "
            f"{dossier['currentness']['posture']} "
            f"freshness_asserted={str(dossier['currentness']['freshness_asserted']).lower()}"
        ),
        f"ATTENTION {', '.join(dossier['attention']) or 'none'}",
        (
            "HISTORY "
            f"snapshots={len(dossier['capture_snapshots'])} "
            f"receipts={len(dossier['change_receipts'])} "
            f"supersession_proposals={len(dossier['supersession_proposals'])}"
        ),
    ]
    if dossier["titles"]:
        lines.append(f"TITLES {' | '.join(dossier['titles'])}")
    if dossier["publishers"]:
        lines.append(f"PUBLISHERS {', '.join(dossier['publishers'])}")
    if dossier["origin_groups"]:
        lines.append(f"ORIGINS {', '.join(dossier['origin_groups'])}")
    for appearance in dossier["appearances"]:
        segment_ids = ",".join(item["segment_id"] for item in appearance["segments"])
        lines.append(
            "RUN "
            f"{appearance['captured_at']} {appearance['recon_run_id']} "
            f"source={appearance['source_id']} "
            f"segments={segment_ids} digest={appearance['segment_digest_posture']} "
            f"observations={','.join(appearance['observation_refs']) or 'none'} "
            f"ref={appearance['recon_run_ref']}"
        )
    for snapshot in dossier["capture_snapshots"]:
        lines.append(
            "SNAPSHOT "
            f"{snapshot['created_at']} {snapshot['capture_id']} "
            f"retrieval={snapshot['retrieval_state']} segment={snapshot['segment_state']} "
            f"ref={snapshot['ref']}"
        )
    for proposal in dossier["supersession_proposals"]:
        lines.append(
            "PROPOSAL "
            f"{proposal['created_at']} {proposal['proposal_id']} "
            f"relation={proposal['candidate_relation']} roles={','.join(proposal['roles'])} "
            f"ref={proposal['ref']}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", help="URI, dossier ID, title, publisher, or origin")
    parser.add_argument(
        "--attention", action="store_true", help="show actionable dossier flags only"
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable result")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    issues = validate_research_source_dossiers(root)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 2
    catalog = load_json(root / OUTPUT_PATH)
    matches = find_dossiers(catalog, args.query, attention_only=args.attention)
    if args.json:
        print(
            json.dumps(
                {"query": args.query, "count": len(matches), "dossiers": matches},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
    elif len(matches) == 1:
        print(_detail(matches[0]))
    else:
        for dossier in matches:
            print(_compact_row(dossier))
        print(f"MATCHES {len(matches)}")
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
