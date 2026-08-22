#!/usr/bin/env python3
"""Owner-local release gate for the source-only aoa-models release route."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = "0.1.0"
RELEASE_TAG = f"v{RELEASE_VERSION}"
RUNTIME_SUBJECT = {
    "kind": "content_addressed_runtime_package",
    "source": "codex-cli-standalone/x86_64-unknown-linux-musl+codex-code-mode-host",
    "digest": "sha256:35cc6b0e4e5c527569807be8017b705f410f0c6c2b7a3fa1c6a5407d65889041",
}
RECONCILIATION_COMMITS = (
    "36b0bd134566d088090d3ec7a16affccffc4300a",
    "40bfebfaf5b52a095c85cc76c42f9493152b63ce",
    "d5dbdd06cf18147abe7baa505fed1146cef99f7a",
    "a66625ac6ae22823cecc11c2581bccf9e50b958c",
    "3cb16a29fcc584972b57064a41c315e2ef1ae67b",
    "5df78821be6edbe439df452d7bcde75e1c453b91",
    "e1ede88f248019ed40dae8d0632b5181100a0b87",
    "9f97e30a172084b203ea23436171a0290b3a4f39",
    "ffed04f5b1f7686f2123ba7daf3d165a63859e2e",
    "538ec4158bed914d6dcd80249c88fbd3b55617d9",
)


def run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        input=input_text,
        capture_output=True,
        text=True,
    )


def fail(message: str) -> None:
    raise SystemExit(f"release_check: FAIL: {message}")


def output(command: list[str]) -> str:
    result = run(command)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no command output"
        fail(f"{' '.join(command)}\n{detail}")
    return result.stdout.strip()


def load_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def extract_release_section(changelog: str, version: str = RELEASE_VERSION) -> str:
    pattern = re.compile(rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}\s*$", re.M)
    match = pattern.search(changelog)
    if match is None:
        fail(f"CHANGELOG.md is missing a dated [{version}] section")
    next_heading = re.search(r"^## \[", changelog[match.end() :], re.M)
    end = match.end() + next_heading.start() if next_heading else len(changelog)
    return changelog[match.start() : end].strip()


def verify_release_surfaces() -> str:
    version = load_version()
    if version != RELEASE_VERSION:
        fail(f"pyproject.toml version is {version!r}, expected {RELEASE_VERSION!r}")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if "## [Unreleased]" not in changelog:
        fail("CHANGELOG.md must retain [Unreleased]")
    section = extract_release_section(changelog)
    for heading in (
        "### Summary",
        "### Added",
        "### Changed",
        "### Fixed",
        "### Deprecated",
        "### Removed",
        "### Security",
        "### Validation",
        "### Notes",
        "### First-Parent Reconciliation",
    ):
        if heading not in section:
            fail(f"release section is missing {heading}")
    if not re.search(r"^### Summary\s*\n\s*- \S", section, re.M):
        fail("release section must contain a Summary bullet")
    for commit in RECONCILIATION_COMMITS:
        if commit not in section:
            fail(f"release section does not reconcile first-parent commit {commit}")
    banner = f"> Current release: `{RELEASE_TAG}`. See [CHANGELOG](CHANGELOG.md) for release notes."
    if banner not in (ROOT / "README.md").read_text(encoding="utf-8"):
        fail("README.md is missing the exact current-release banner")
    releasing = (ROOT / "docs" / "RELEASING.md").read_text(encoding="utf-8")
    if "source-only GitHub Release" not in releasing:
        fail("docs/RELEASING.md must declare the source-only route")
    return section


def run_owner_validators() -> None:
    commands = [
        [sys.executable, "-B", "scripts/validate_models.py"],
        [sys.executable, "-B", "scripts/build_model_fit_projections.py", "--check"],
        [sys.executable, "-B", "scripts/generate_decision_index.py", "--check"],
        [
            sys.executable,
            "-B",
            "scripts/check_live_codex_catalog.py",
            "--runtime-subject-kind",
            RUNTIME_SUBJECT["kind"],
            "--runtime-subject-source",
            RUNTIME_SUBJECT["source"],
            "--runtime-subject-digest",
            RUNTIME_SUBJECT["digest"],
            "--require-realization-ref",
            "source/model-realizations/openai-gpt-5.6-luna-codex-0.148.0-chatgpt-max-structured-owner-duty-workspace-write.json",
        ],
        [
            sys.executable,
            "-B",
            "scripts/query_model_fit.py",
            "--task-family",
            "structured-owner-duty-currentness",
            "--runtime-product",
            "codex-cli",
            "--runtime-version",
            "0.148.0",
            "--runtime-subject-kind",
            RUNTIME_SUBJECT["kind"],
            "--runtime-subject-source",
            RUNTIME_SUBJECT["source"],
            "--runtime-subject-digest",
            RUNTIME_SUBJECT["digest"],
            "--reasoning-effort",
            "max",
            "--sandbox-mode",
            "workspace-write",
            "--required-tool",
            "shell-read",
            "--required-tool",
            "workspace-write",
            "--require-match",
        ],
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        ["git", "diff", "--check"],
    ]
    for command in commands:
        result = run(command)
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "no command output"
            fail(f"{' '.join(command)}\n{detail}")


def verify_clean_synced_main() -> str:
    status = output(["git", "status", "--porcelain", "--untracked-files=all"])
    if status:
        fail(f"tracked or untracked worktree changes remain:\n{status}")
    branch = output(["git", "branch", "--show-current"])
    if branch != "main":
        fail(f"release gate must run on main, found {branch!r}")
    fetch = run(["git", "fetch", "--tags", "origin"])
    if fetch.returncode != 0:
        detail = fetch.stderr.strip() or fetch.stdout.strip() or "no command output"
        fail(f"origin fetch failed\n{detail}")
    head = output(["git", "rev-parse", "HEAD"])
    origin_main = output(["git", "rev-parse", "refs/remotes/origin/main"])
    if head != origin_main:
        fail(f"main is not synchronized with origin/main: {head} != {origin_main}")
    return head


def main() -> int:
    section = verify_release_surfaces()
    head = verify_clean_synced_main()
    run_owner_validators()
    final_status = output(["git", "status", "--porcelain", "--untracked-files=all"])
    if final_status:
        fail(f"owner validators left worktree drift:\n{final_status}")
    print(
        json.dumps(
            {
                "schema_version": "aoa_models_release_check_v1",
                "repo": "aoa-models",
                "version": RELEASE_VERSION,
                "tag": RELEASE_TAG,
                "head": head,
                "changelog_section_sha256": hashlib.sha256(section.encode()).hexdigest(),
                "source_only": True,
                "artifact_registry_promotion": False,
                "runtime_health": False,
                "proof": False,
                "acceptance": False,
                "passed": True,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
