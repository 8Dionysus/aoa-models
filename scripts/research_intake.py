#!/usr/bin/env python3
"""Bounded mechanical automation for pre-canon research intake."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from research_automation import (
    ResearchAutomationError,
    assert_output_paths_absent,
    build_capture_snapshot,
    build_change_receipt,
    build_refreshed_snapshot,
    build_supersession_proposal,
    load_snapshot,
    write_immutable_json,
)
from research_automation_contract import DEFAULT_ROOT


def _capture_source(args: argparse.Namespace) -> int:
    assert_output_paths_absent([args.output])
    request = json.loads(args.request.read_text(encoding="utf-8"))
    snapshot = build_capture_snapshot(
        request,
        root=args.root,
        input_path=args.input_file,
        input_ref=args.input_ref,
        captured_at=args.captured_at,
    )
    write_immutable_json(args.output, snapshot)
    print(
        f"SNAPSHOT {snapshot['capture_id']} {snapshot['artifact_digest']} "
        f"retrieval={snapshot['retrieval']['state']} "
        f"segment={snapshot['segment_result']['state']} {args.output}"
    )
    return 0


def _refresh_capture(args: argparse.Namespace) -> int:
    assert_output_paths_absent([args.snapshot_output, args.receipt_output])
    previous = load_snapshot(args.previous, args.root)
    current = build_refreshed_snapshot(
        previous,
        args.previous,
        root=args.root,
        input_path=args.input_file,
        input_ref=args.input_ref,
        captured_at=args.captured_at,
    )
    receipt = build_change_receipt(
        previous,
        args.previous,
        current,
        args.snapshot_output,
        root=args.root,
    )
    write_immutable_json(args.snapshot_output, current)
    write_immutable_json(args.receipt_output, receipt)
    print(
        f"REFRESH {receipt['receipt_id']} {receipt['artifact_digest']} "
        f"classification={receipt['classification']} "
        f"review={receipt['review_disposition']}"
    )
    print(f"SNAPSHOT {current['capture_id']} {current['artifact_digest']} {args.snapshot_output}")
    print(f"RECEIPT {args.receipt_output}")
    return 0


def _suggest_supersession(args: argparse.Namespace) -> int:
    assert_output_paths_absent([args.output])
    proposal = build_supersession_proposal(
        args.prior_run,
        args.prior_observation,
        args.candidate_run,
        args.candidate_observation,
        relation=args.relation,
        scope_dimensions=args.scope_dimension,
        rationale=args.rationale,
        ambiguities=args.ambiguity,
        root=args.root,
        created_at=args.created_at,
    )
    write_immutable_json(args.output, proposal)
    comparison = proposal["structural_comparison"]
    print(
        f"PROPOSAL {proposal['proposal_id']} {proposal['artifact_digest']} "
        f"relation={proposal['candidate_relation']} "
        f"temporal={comparison['temporal_relation']} review_required=true {args.output}"
    )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create immutable pre-canon capture, change, and supersession-review candidates."
        )
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser(
        "capture-source",
        help="capture one bounded source segment into an immutable candidate",
    )
    capture.add_argument("--request", type=Path, required=True)
    capture.add_argument("--output", type=Path, required=True)
    capture.add_argument("--input-file", type=Path)
    capture.add_argument("--input-ref")
    capture.add_argument("--captured-at")
    capture.set_defaults(handler=_capture_source)

    refresh = subparsers.add_parser(
        "refresh-capture",
        help="create a new snapshot and classified change receipt",
    )
    refresh.add_argument("--previous", type=Path, required=True)
    refresh.add_argument("--snapshot-output", type=Path, required=True)
    refresh.add_argument("--receipt-output", type=Path, required=True)
    refresh.add_argument("--input-file", type=Path)
    refresh.add_argument("--input-ref")
    refresh.add_argument("--captured-at")
    refresh.set_defaults(handler=_refresh_capture)

    supersession = subparsers.add_parser(
        "suggest-supersession",
        help="package a review-only relationship proposal between two observations",
    )
    supersession.add_argument("--prior-run", type=Path, required=True)
    supersession.add_argument("--prior-observation", required=True)
    supersession.add_argument("--candidate-run", type=Path, required=True)
    supersession.add_argument("--candidate-observation", required=True)
    supersession.add_argument(
        "--relation",
        choices=("update", "narrowing", "contradiction", "independent"),
        required=True,
    )
    supersession.add_argument(
        "--scope-dimension",
        action="append",
        required=True,
        help="repeat for each bounded scope dimension under review",
    )
    supersession.add_argument("--rationale", required=True)
    supersession.add_argument("--ambiguity", action="append", default=[])
    supersession.add_argument("--created-at")
    supersession.add_argument("--output", type=Path, required=True)
    supersession.set_defaults(handler=_suggest_supersession)
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    args.root = args.root.resolve()
    if args.command in {"capture-source", "refresh-capture"} and (
        (args.input_file is None) != (args.input_ref is None)
    ):
        parser.error("--input-file and --input-ref must be supplied together")
    try:
        return args.handler(args)
    except (OSError, json.JSONDecodeError, ResearchAutomationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
