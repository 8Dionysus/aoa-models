#!/usr/bin/env python3
"""Publish and audit the exact owner-local aoa-models source release."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess

from release_check import RELEASE_TAG, RELEASE_VERSION, ROOT, extract_release_section, load_version, run


SLUG = "8Dionysus/aoa-models"


def fail(message: str) -> None:
    raise SystemExit(f"release_publish: FAIL: {message}")


def output(command: list[str]) -> str:
    result = run(command)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no command output"
        fail(f"{' '.join(command)}\n{detail}")
    return result.stdout.strip()


def release_body() -> tuple[str, str]:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = extract_release_section(changelog)
    summary = section.split("### Summary", 1)[1].split("### Added", 1)[0].strip()
    body = (
        "Released\n\n"
        "Canonical changelog: https://github.com/8Dionysus/aoa-models/blob/main/CHANGELOG.md\n\n"
        "## Highlights\n\n"
        f"{summary}\n\n"
        "## Full Release Notes\n\n"
        f"{section}\n"
    )
    return body, hashlib.sha256(body.encode("utf-8")).hexdigest()


def remote_ref(ref: str) -> str | None:
    result = run(["git", "ls-remote", "origin", ref])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no command output"
        fail(f"remote inspection failed for {ref}: {detail}")
    line = next((line for line in result.stdout.splitlines() if line.endswith(f"\t{ref}")), None)
    return line.split("\t", 1)[0] if line else None


def assert_release_surfaces() -> tuple[str, str, str]:
    version = load_version()
    if version != RELEASE_VERSION:
        fail(f"pyproject version {version!r} does not match {RELEASE_VERSION!r}")
    branch = output(["git", "branch", "--show-current"])
    if branch != "main":
        fail(f"publication requires main, found {branch!r}")
    status = output(["git", "status", "--porcelain", "--untracked-files=all"])
    if status:
        fail(f"publication requires a clean tree:\n{status}")
    head = output(["git", "rev-parse", "HEAD"])
    remote_main = remote_ref("refs/heads/main")
    if remote_main != head:
        fail(f"local main is not the exact remote main: {head} != {remote_main}")
    body, body_sha = release_body()
    return head, body, body_sha


def tag_identity(head: str) -> dict[str, str | None]:
    tag_object = remote_ref(f"refs/tags/{RELEASE_TAG}")
    peeled = remote_ref(f"refs/tags/{RELEASE_TAG}^{{}}")
    return {"tag_object": tag_object, "peeled_commit": peeled, "expected_commit": head}


def gh_release() -> dict:
    result = run(["gh", "api", f"repos/{SLUG}/releases/tags/{RELEASE_TAG}"])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no command output"
        fail(f"GitHub Release lookup failed\n{detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"GitHub Release response was not JSON: {exc}")


def latest_release_tag() -> str | None:
    result = run(["gh", "release", "list", "--repo", SLUG, "--limit", "100", "--json", "tagName,isLatest"])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no command output"
        fail(f"GitHub latest marker lookup failed\n{detail}")
    try:
        rows = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"GitHub release list response was not JSON: {exc}")
    return next((row.get("tagName") for row in rows if row.get("isLatest")), None)


def postpublish(head: str | None = None) -> dict:
    local_head, body, body_sha = assert_release_surfaces()
    if head is not None and local_head != head:
        fail(f"HEAD changed during postpublish audit: {local_head} != {head}")
    head = local_head
    identity = tag_identity(head)
    if identity["peeled_commit"] != head:
        fail(f"remote tag does not point to landed main: {identity}")
    release = gh_release()
    latest = latest_release_tag()
    checks = {
        "tag_name": release.get("tag_name") == RELEASE_TAG,
        "published": bool(release.get("published_at")) and not release.get("draft") and not release.get("prerelease"),
        "latest": latest == RELEASE_TAG,
        "body_matches_canonical": release.get("body") == body,
        "assets_empty": release.get("assets") == [],
    }
    if not all(checks.values()):
        fail(
            json.dumps(
                {
                    "checks": checks,
                    "release_url": release.get("html_url"),
                    "latest": latest,
                    "body_sha256": body_sha,
                    "assets": release.get("assets"),
                },
                sort_keys=True,
            )
        )
    return {
        "schema_version": "aoa_models_postpublish_v1",
        "repo": "aoa-models",
        "version": RELEASE_VERSION,
        "tag": RELEASE_TAG,
        "head": head,
        "tag_identity": identity,
        "release_url": release.get("html_url"),
        "published_at": release.get("published_at"),
        "latest_marker": latest,
        "body_sha256": body_sha,
        "assets": [],
        "attestation": {"status": "not_applicable", "reason": "source-only GitHub Release; no package artifact is published"},
        "checks": checks,
        "runtime_health": False,
        "proof": False,
        "acceptance": False,
        "passed": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--confirm", action="store_true")
    mode.add_argument("--postpublish", action="store_true")
    args = parser.parse_args()

    head, body, body_sha = assert_release_surfaces()
    if args.postpublish:
        print(json.dumps(postpublish(head), sort_keys=True))
        return 0

    existing_tag = tag_identity(head)
    if existing_tag["tag_object"] or existing_tag["peeled_commit"]:
        fail(f"approved tag already exists; refusing to move or recreate it: {existing_tag}")

    plan = {
        "schema_version": "aoa_models_release_publish_plan_v1",
        "repo": "aoa-models",
        "version": RELEASE_VERSION,
        "tag": RELEASE_TAG,
        "head": head,
        "body_sha256": body_sha,
        "source_only": True,
        "uploaded_assets": [],
        "actions": [
            "create annotated tag at exact verified main",
            "push only the approved tag",
            "create a non-draft latest GitHub Release from canonical changelog",
        ],
    }
    if args.dry_run:
        print(json.dumps(plan, sort_keys=True))
        return 0

    tag = run(["git", "tag", "-a", RELEASE_TAG, "-m", f"aoa-models {RELEASE_TAG}", head])
    if tag.returncode != 0:
        detail = tag.stderr.strip() or tag.stdout.strip() or "no command output"
        fail(f"annotated tag creation failed\n{detail}")
    push = run(["git", "push", "origin", f"refs/tags/{RELEASE_TAG}"])
    if push.returncode != 0:
        detail = push.stderr.strip() or push.stdout.strip() or "no command output"
        fail(f"tag push failed after local tag creation\n{detail}")
    release = run(
        [
            "gh",
            "release",
            "create",
            RELEASE_TAG,
            "--repo",
            SLUG,
            "--verify-tag",
            "--title",
            f"aoa-models {RELEASE_TAG}",
            "--notes-file",
            "-",
            "--latest",
        ],
        input_text=body,
    )
    if release.returncode != 0:
        detail = release.stderr.strip() or release.stdout.strip() or "no command output"
        fail(f"GitHub Release publication failed after tag push; preserve tag and retry postpublish\n{detail}")
    print(json.dumps(postpublish(head), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
