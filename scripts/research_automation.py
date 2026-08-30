#!/usr/bin/env python3
"""Build immutable candidates for bounded research-intake automation."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import mimetypes
from pathlib import Path
import re
from typing import Any
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from research_automation_contract import (
    DEFAULT_ROOT,
    artifact_digest,
    candidate_action,
    canonical_digest,
    classify_change,
    compare_observations,
    finalize_artifact,
    load_json,
    locator_label,
    validate_automation_artifact,
    validate_capture_request,
)


ARTIFACT_SCHEMA_ID = (
    "https://schemas.aoa.local/models/research-automation-artifact.schema.json"
)
ARTIFACT_SCHEMA_VERSION = "aoa_model_research_automation_artifact_v1"
AUTHORITY = {
    "pre_canon": True,
    "automatic_promotion": False,
    "source_mutation_authority": False,
    "routing_authority": False,
    "activation_authority": False,
    "proof_authority": False,
    "acceptance_authority": False,
}


class ResearchAutomationError(ValueError):
    """Raised when an automation candidate cannot be built safely."""


def _timestamp(value: str | None = None) -> str:
    if value is None:
        moment = datetime.now(timezone.utc)
    else:
        try:
            moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ResearchAutomationError(f"invalid timestamp {value!r}: {exc}") from exc
        if moment.tzinfo is None:
            raise ResearchAutomationError("timestamp requires an explicit timezone")
        moment = moment.astimezone(timezone.utc)
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_token(value: str) -> str:
    return (
        value.lower()
        .replace("-", "")
        .replace(":", "")
        .replace("+", "")
    )


def _sha256(data: bytes) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(data).hexdigest()


def _media_type_from_header(value: str | None) -> str | None:
    if not value:
        return None
    media_type = value.split(";", 1)[0].strip().lower()
    return media_type or None


def _resolved_media_type(
    requested: str,
    detected: str | None,
    input_path: Path | None,
) -> str | None:
    if requested != "auto":
        return requested
    if detected:
        return detected
    if input_path:
        guessed, _ = mimetypes.guess_type(input_path.name)
        if guessed:
            return guessed.lower()
    return "application/octet-stream"


def _bounded_local_read(path: Path, max_bytes: int) -> tuple[bytes, bool]:
    with path.open("rb") as handle:
        payload = handle.read(max_bytes + 1)
    return payload[:max_bytes], len(payload) > max_bytes


def _retrieve(
    request: dict[str, Any],
    attempted_at: str,
    *,
    input_path: Path | None,
    input_ref: str | None,
) -> tuple[dict[str, Any], bytes | None, list[str]]:
    retrieval_request = request["retrieval"]
    source_uri = request["source"]["uri"]
    max_bytes = retrieval_request["max_bytes"]
    timeout = retrieval_request["timeout_seconds"]
    gaps: list[str] = []
    if input_path is not None:
        transport = "local_input"
        if not input_ref:
            raise ResearchAutomationError("local input requires a portable --input-ref")
        try:
            payload, truncated = _bounded_local_read(input_path, max_bytes)
        except OSError as exc:
            error = f"local_input_unavailable:{exc.__class__.__name__}"
            return (
                {
                    "state": "unavailable",
                    "transport": transport,
                    "attempted_at": attempted_at,
                    "input_ref": input_ref,
                    "final_uri": None,
                    "media_type": _resolved_media_type(
                        retrieval_request["media_type"], None, input_path
                    ),
                    "http_status": None,
                    "etag": None,
                    "last_modified": None,
                    "document_digest": None,
                    "document_size_bytes": None,
                    "truncated": False,
                    "error": error,
                },
                None,
                [error],
            )
        media_type = _resolved_media_type(
            retrieval_request["media_type"], None, input_path
        )
        error = "document_truncated_at_max_bytes" if truncated else None
        if error:
            gaps.append(error)
        return (
            {
                "state": "partial" if truncated else "captured",
                "transport": transport,
                "attempted_at": attempted_at,
                "input_ref": input_ref,
                "final_uri": None,
                "media_type": media_type,
                "http_status": None,
                "etag": None,
                "last_modified": None,
                "document_digest": _sha256(payload),
                "document_size_bytes": len(payload),
                "truncated": truncated,
                "error": error,
            },
            payload,
            gaps,
        )

    scheme = urlparse(source_uri).scheme.lower()
    if scheme not in {"http", "https"}:
        error = f"unsupported_uri_scheme:{scheme or 'missing'}"
        return (
            {
                "state": "unavailable",
                "transport": "http",
                "attempted_at": attempted_at,
                "input_ref": None,
                "final_uri": None,
                "media_type": None,
                "http_status": None,
                "etag": None,
                "last_modified": None,
                "document_digest": None,
                "document_size_bytes": None,
                "truncated": False,
                "error": error,
            },
            None,
            [error],
        )
    http_status: int | None = None
    etag: str | None = None
    last_modified: str | None = None
    detected_media_type: str | None = None
    final_uri: str | None = None
    try:
        http_request = Request(
            source_uri,
            headers={"User-Agent": "aoa-models-research-intake/0.1"},
        )
        with urlopen(http_request, timeout=timeout) as response:  # noqa: S310
            http_status = response.status
            final_uri = response.geturl()
            etag = response.headers.get("ETag")
            last_modified = response.headers.get("Last-Modified")
            detected_media_type = _media_type_from_header(
                response.headers.get("Content-Type")
            )
            payload = response.read(max_bytes + 1)
    except HTTPError as exc:
        error = f"http_error:{exc.code}"
        error_headers = exc.headers or {}
        return (
            {
                "state": "unavailable",
                "transport": "http",
                "attempted_at": attempted_at,
                "input_ref": None,
                "final_uri": exc.geturl(),
                "media_type": _resolved_media_type(
                    retrieval_request["media_type"],
                    _media_type_from_header(error_headers.get("Content-Type")),
                    None,
                ),
                "http_status": exc.code,
                "etag": error_headers.get("ETag"),
                "last_modified": error_headers.get("Last-Modified"),
                "document_digest": None,
                "document_size_bytes": None,
                "truncated": False,
                "error": error,
            },
            None,
            [error],
        )
    except (OSError, URLError, TimeoutError) as exc:
        error = f"retrieval_unavailable:{exc.__class__.__name__}"
        return (
            {
                "state": "unavailable",
                "transport": "http",
                "attempted_at": attempted_at,
                "input_ref": None,
                "final_uri": None,
                "media_type": None,
                "http_status": None,
                "etag": None,
                "last_modified": None,
                "document_digest": None,
                "document_size_bytes": None,
                "truncated": False,
                "error": error,
            },
            None,
            [error],
        )
    truncated = len(payload) > max_bytes
    payload = payload[:max_bytes]
    error = "document_truncated_at_max_bytes" if truncated else None
    if error:
        gaps.append(error)
    return (
        {
            "state": "partial" if truncated else "captured",
            "transport": "http",
            "attempted_at": attempted_at,
            "input_ref": None,
            "final_uri": final_uri,
            "media_type": _resolved_media_type(
                retrieval_request["media_type"], detected_media_type, None
            ),
            "http_status": http_status,
            "etag": etag,
            "last_modified": last_modified,
            "document_digest": _sha256(payload),
            "document_size_bytes": len(payload),
            "truncated": truncated,
            "error": error,
        },
        payload,
        gaps,
    )


def _canonical_text(text: str) -> bytes:
    normalized = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    normalized = "\n".join(line.rstrip() for line in normalized.split("\n")).strip()
    return normalized.encode("utf-8")


class _HTMLIDExtractor(HTMLParser):
    _VOID_ELEMENTS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self, target_id: str) -> None:
        super().__init__(convert_charrefs=True)
        self.target_id = target_id
        self.matches: list[str] = []
        self._active: list[str] | None = None
        self._depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._active is not None:
            if tag not in self._VOID_ELEMENTS:
                self._depth += 1
            return
        if dict(attrs).get("id") == self.target_id:
            if tag in self._VOID_ELEMENTS:
                self.matches.append("")
            else:
                self._active = []
                self._depth = 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        if self._active is None and dict(attrs).get("id") == self.target_id:
            self.matches.append("")

    def handle_endtag(self, tag: str) -> None:
        del tag
        if self._active is None:
            return
        self._depth -= 1
        if self._depth == 0:
            self.matches.append("".join(self._active))
            self._active = None

    def handle_data(self, data: str) -> None:
        if self._active is not None:
            self._active.append(data)


def _json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    current = document
    for raw_token in pointer.split("/")[1:]:
        if re.search(r"~(?![01])", raw_token):
            raise ValueError("invalid JSON Pointer escape")
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", token):
                raise KeyError(token)
            current = current[int(token)]
        elif isinstance(current, dict):
            current = current[token]
        else:
            raise KeyError(token)
    return current


def _normalize_whitespace(text: str) -> bytes:
    normalized = unicodedata.normalize("NFC", re.sub(r"\s+", " ", text).strip())
    return normalized.encode("utf-8")


def _extracted_result(
    payload: bytes,
    normalized: bytes,
    profile: str,
    *,
    partial: bool,
) -> dict[str, Any]:
    return {
        "state": "partial" if partial else "captured",
        "content_digest": _sha256(payload),
        "normalized_content_digest": _sha256(normalized),
        "byte_length": len(payload),
        "normalization_profile": profile,
        "digest_unavailable_reason": None,
    }


def _unavailable_segment(state: str, reason: str) -> dict[str, Any]:
    return {
        "state": state,
        "content_digest": None,
        "normalized_content_digest": None,
        "byte_length": None,
        "normalization_profile": None,
        "digest_unavailable_reason": reason,
    }


def _extract_segment(
    payload: bytes | None,
    retrieval: dict[str, Any],
    locator: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if payload is None:
        reason = retrieval.get("error") or "source_unavailable"
        return _unavailable_segment("unavailable", reason), [reason]
    partial = retrieval["state"] == "partial"
    gaps: list[str] = []
    if partial:
        gaps.append("segment_derived_from_partial_document")
    kind = locator["kind"]
    media_type = retrieval.get("media_type") or "application/octet-stream"
    if kind == "whole_document":
        if media_type == "application/json" or media_type.endswith("+json"):
            try:
                value = json.loads(payload.decode("utf-8"))
                normalized = json.dumps(
                    value,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
                profile = "canonical_json_v1"
            except (UnicodeDecodeError, json.JSONDecodeError):
                normalized = payload
                profile = "raw_bytes_v1"
                partial = True
                gaps.append("declared_json_could_not_be_normalized")
        elif media_type in {"text/html", "application/xhtml+xml"}:
            try:
                normalized = _normalize_whitespace(payload.decode("utf-8"))
                profile = "html_document_text_v1"
            except UnicodeDecodeError:
                normalized = payload
                profile = "raw_bytes_v1"
                partial = True
                gaps.append("html_document_could_not_be_decoded_as_utf8")
        elif media_type.startswith("text/"):
            try:
                normalized = _canonical_text(payload.decode("utf-8"))
                profile = "canonical_text_v1"
            except UnicodeDecodeError:
                normalized = payload
                profile = "raw_bytes_v1"
                partial = True
                gaps.append("text_document_could_not_be_decoded_as_utf8")
        else:
            normalized = payload
            profile = "raw_bytes_v1"
        return _extracted_result(payload, normalized, profile, partial=partial), gaps

    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        reason = "locator_requires_utf8_document"
        return _unavailable_segment("missing", reason), [reason]
    if kind == "line_range":
        value = locator["value"]
        lines = text.splitlines(keepends=True)
        start = value["start"]
        end = value["end"]
        if start > len(lines):
            reason = "line_range_start_exceeds_document"
            return _unavailable_segment("missing", reason), [reason]
        selected_text = "".join(lines[start - 1 : end])
        if end > len(lines):
            partial = True
            gaps.append("line_range_end_exceeds_document")
        selected = selected_text.encode("utf-8")
        return (
            _extracted_result(
                selected,
                _canonical_text(selected_text),
                "canonical_text_v1",
                partial=partial,
            ),
            gaps,
        )
    if kind == "json_pointer":
        try:
            value = _json_pointer(json.loads(text), locator["value"])
        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
            reason = f"json_pointer_unresolved:{exc.__class__.__name__}"
            return _unavailable_segment("missing", reason), [reason]
        selected = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return (
            _extracted_result(
                selected,
                selected,
                "canonical_json_v1",
                partial=partial,
            ),
            gaps,
        )
    if kind == "html_id":
        parser = _HTMLIDExtractor(locator["value"])
        try:
            parser.feed(text)
            parser.close()
        except ValueError as exc:
            reason = f"html_parse_failed:{exc.__class__.__name__}"
            return _unavailable_segment("missing", reason), [reason]
        if not parser.matches:
            reason = "html_id_not_found"
            return _unavailable_segment("missing", reason), [reason]
        if len(parser.matches) > 1:
            partial = True
            gaps.append("html_id_not_unique")
        selected_text = parser.matches[0]
        selected = selected_text.encode("utf-8")
        return (
            _extracted_result(
                selected,
                _normalize_whitespace(selected_text),
                "html_element_text_v1",
                partial=partial,
            ),
            gaps,
        )
    raise ResearchAutomationError(f"unsupported locator kind: {kind!r}")


def _source_capture_candidate(
    request: dict[str, Any],
    captured_at: str,
    segment_result: dict[str, Any],
) -> dict[str, Any]:
    candidate = copy.deepcopy(request["source"])
    candidate["captured_at"] = captured_at
    candidate["segments"] = [
        {
            "segment_id": request["segment"]["segment_id"],
            "locator": locator_label(request["segment"]["locator"]),
            "content_digest": segment_result["content_digest"],
            "digest_unavailable_reason": segment_result["digest_unavailable_reason"],
        }
    ]
    return candidate


def _capture_artifact_id(request: dict[str, Any], captured_at: str) -> str:
    return (
        f"research-capture:{request['source']['source_id']}/"
        f"{_timestamp_token(captured_at)}"
    )


def build_capture_snapshot(
    request: dict[str, Any],
    *,
    root: Path = DEFAULT_ROOT,
    input_path: Path | None = None,
    input_ref: str | None = None,
    captured_at: str | None = None,
    predecessor_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request_issues = validate_capture_request(request, root)
    if request_issues:
        raise ResearchAutomationError("; ".join(request_issues))
    created_at = _timestamp(captured_at)
    retrieval, payload, retrieval_gaps = _retrieve(
        request,
        created_at,
        input_path=input_path,
        input_ref=input_ref,
    )
    segment_result, segment_gaps = _extract_segment(
        payload,
        retrieval,
        request["segment"]["locator"],
    )
    gaps = list(dict.fromkeys([*retrieval_gaps, *segment_gaps]))
    record = finalize_artifact(
        {
            "$schema": ARTIFACT_SCHEMA_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "kind": "ResearchCaptureSnapshot",
            "capture_id": _capture_artifact_id(request, created_at),
            "created_at": created_at,
            "authority": copy.deepcopy(AUTHORITY),
            "promotion_policy": "pre_canon_no_automatic_promotion",
            "request": copy.deepcopy(request),
            "retrieval": retrieval,
            "segment_result": segment_result,
            "source_capture_candidate": _source_capture_candidate(
                request,
                created_at,
                segment_result,
            ),
            "predecessor_snapshot": copy.deepcopy(predecessor_snapshot),
            "gap_reasons": gaps,
        }
    )
    issues = validate_automation_artifact(record, root)
    if issues:
        raise ResearchAutomationError("; ".join(issues))
    return record


def portable_ref(path: Path, root: Path, *, external_prefix: str) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return f"{external_prefix}:{resolved.name}"


def snapshot_ref(
    snapshot: dict[str, Any],
    path: Path,
    root: Path,
    *,
    external_prefix: str,
) -> dict[str, Any]:
    return {
        "artifact_id": snapshot["capture_id"],
        "ref": portable_ref(path, root, external_prefix=external_prefix),
        "content_digest": snapshot["artifact_digest"],
    }


def build_refreshed_snapshot(
    previous: dict[str, Any],
    previous_path: Path,
    *,
    root: Path = DEFAULT_ROOT,
    input_path: Path | None = None,
    input_ref: str | None = None,
    captured_at: str | None = None,
) -> dict[str, Any]:
    issues = validate_automation_artifact(previous, root, label=str(previous_path))
    if issues:
        raise ResearchAutomationError("; ".join(issues))
    if previous.get("kind") != "ResearchCaptureSnapshot":
        raise ResearchAutomationError("refresh input must be a ResearchCaptureSnapshot")
    timestamp = _timestamp(captured_at)
    previous_timestamp = _timestamp(previous["created_at"])
    if datetime.fromisoformat(timestamp.replace("Z", "+00:00")) <= datetime.fromisoformat(
        previous_timestamp.replace("Z", "+00:00")
    ):
        raise ResearchAutomationError("refreshed capture timestamp must follow predecessor")
    predecessor = snapshot_ref(
        previous,
        previous_path,
        root,
        external_prefix="external-input",
    )
    return build_capture_snapshot(
        previous["request"],
        root=root,
        input_path=input_path,
        input_ref=input_ref,
        captured_at=timestamp,
        predecessor_snapshot=predecessor,
    )


def build_change_receipt(
    previous: dict[str, Any],
    previous_path: Path,
    current: dict[str, Any],
    current_path: Path,
    *,
    root: Path = DEFAULT_ROOT,
) -> dict[str, Any]:
    if previous.get("request") != current.get("request"):
        raise ResearchAutomationError("refresh snapshots must preserve the same capture request")
    classification, basis, disposition = classify_change(previous, current)
    previous_ref = snapshot_ref(
        previous,
        previous_path,
        root,
        external_prefix="external-input",
    )
    current_ref = snapshot_ref(
        current,
        current_path,
        root,
        external_prefix="external-output",
    )
    if current.get("predecessor_snapshot") != previous_ref:
        raise ResearchAutomationError("current snapshot does not bind the supplied predecessor")
    record = finalize_artifact(
        {
            "$schema": ARTIFACT_SCHEMA_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "kind": "ResearchChangeReceipt",
            "receipt_id": (
                f"research-change:{current['request']['source']['source_id']}/"
                f"{_timestamp_token(current['created_at'])}"
            ),
            "created_at": current["created_at"],
            "authority": copy.deepcopy(AUTHORITY),
            "previous_snapshot": previous_ref,
            "current_snapshot": current_ref,
            "classification": classification,
            "basis": basis,
            "review_disposition": disposition,
            "automatic_supersession": False,
        }
    )
    issues = validate_automation_artifact(record, root)
    if issues:
        raise ResearchAutomationError("; ".join(issues))
    return record


def _repo_relative_run(path: Path, root: Path) -> tuple[str, dict[str, Any]]:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ResearchAutomationError("recon run must be inside the owner repository") from exc
    if not relative.startswith("research-intake/recon-runs/"):
        raise ResearchAutomationError("recon run must use research-intake/recon-runs/")
    return relative, load_json(resolved)


def _observation(run: dict[str, Any], observation_id: str) -> dict[str, Any]:
    matches = [
        observation
        for observation in run.get("observations", [])
        if observation.get("observation_id") == observation_id
    ]
    if len(matches) != 1:
        raise ResearchAutomationError(
            f"expected one observation {observation_id!r}, found {len(matches)}"
        )
    return matches[0]


def _qualified_observation_ref(
    run_ref: str,
    run: dict[str, Any],
    observation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "recon_run_id": run["recon_run_id"],
        "recon_run_ref": run_ref,
        "recon_run_digest": canonical_digest(run),
        "observation_id": observation["observation_id"],
        "observation_digest": canonical_digest(observation),
        "target_kind": observation["target_kind"],
        "observed_interval": copy.deepcopy(observation["observed_interval"]),
        "source_segment_refs": copy.deepcopy(observation["source_segment_refs"]),
        "counterevidence_refs": copy.deepcopy(observation["counterevidence_refs"]),
    }


def build_supersession_proposal(
    prior_run_path: Path,
    prior_observation_id: str,
    candidate_run_path: Path,
    candidate_observation_id: str,
    *,
    relation: str,
    scope_dimensions: list[str],
    rationale: str,
    ambiguities: list[str],
    root: Path = DEFAULT_ROOT,
    created_at: str | None = None,
) -> dict[str, Any]:
    prior_run_ref, prior_run = _repo_relative_run(prior_run_path, root)
    candidate_run_ref, candidate_run = _repo_relative_run(candidate_run_path, root)
    prior_observation = _observation(prior_run, prior_observation_id)
    candidate_observation = _observation(candidate_run, candidate_observation_id)
    comparison = compare_observations(prior_observation, candidate_observation)
    timestamp = _timestamp(created_at)
    identity_seed = {
        "prior": [prior_run["recon_run_id"], prior_observation_id],
        "candidate": [candidate_run["recon_run_id"], candidate_observation_id],
        "relation": relation,
        "created_at": timestamp,
    }
    identity_digest = canonical_digest(identity_seed).removeprefix("sha256:")[:16]
    record = finalize_artifact(
        {
            "$schema": ARTIFACT_SCHEMA_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "kind": "ResearchSupersessionProposal",
            "proposal_id": (
                f"research-supersession:{identity_digest}/{_timestamp_token(timestamp)}"
            ),
            "created_at": timestamp,
            "status": "proposed",
            "authority": copy.deepcopy(AUTHORITY),
            "prior_observation": _qualified_observation_ref(
                prior_run_ref,
                prior_run,
                prior_observation,
            ),
            "candidate_observation": _qualified_observation_ref(
                candidate_run_ref,
                candidate_run,
                candidate_observation,
            ),
            "candidate_relation": relation,
            "scope_dimensions": list(dict.fromkeys(scope_dimensions)),
            "rationale": rationale,
            "ambiguities": list(dict.fromkeys(ambiguities)),
            "structural_comparison": comparison,
            "candidate_action": candidate_action(relation),
            "review_required": True,
            "automatic_application": False,
            "mutation_policy": "no_source_or_recon_run_mutation",
        }
    )
    issues = validate_automation_artifact(record, root)
    if issues:
        raise ResearchAutomationError("; ".join(issues))
    return record


def write_immutable_json(path: Path, record: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    except FileExistsError as exc:
        raise ResearchAutomationError(f"refusing to overwrite existing artifact: {path}") from exc


def load_snapshot(path: Path, root: Path = DEFAULT_ROOT) -> dict[str, Any]:
    try:
        snapshot = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchAutomationError(f"cannot read snapshot {path}: {exc}") from exc
    issues = validate_automation_artifact(snapshot, root, label=str(path))
    if issues:
        raise ResearchAutomationError("; ".join(issues))
    if snapshot.get("kind") != "ResearchCaptureSnapshot":
        raise ResearchAutomationError(f"not a capture snapshot: {path}")
    return snapshot


def assert_output_paths_absent(paths: list[Path]) -> None:
    resolved_paths = [path.resolve() for path in paths]
    if len(set(resolved_paths)) != len(resolved_paths):
        raise ResearchAutomationError("output artifact paths must be distinct")
    existing = [str(path) for path in resolved_paths if path.exists()]
    if existing:
        raise ResearchAutomationError(
            "refusing to overwrite existing artifact(s): " + ", ".join(existing)
        )


__all__ = [
    "ResearchAutomationError",
    "artifact_digest",
    "assert_output_paths_absent",
    "build_capture_snapshot",
    "build_change_receipt",
    "build_refreshed_snapshot",
    "build_supersession_proposal",
    "load_snapshot",
    "write_immutable_json",
]
