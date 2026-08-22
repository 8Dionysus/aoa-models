# Establish a source-only initial release route

## Status

Accepted.

## Index metadata

- Decision ID: AOA-MODELS-D-0005
- Original date: 2026-08-22
- Owner facets: release-route, publication-boundary, artifact-boundary, owner-authority
- Posture: accepted-owner-source

## Context

`aoa-models` has a coherent public source contour and an existing package
metadata version of `0.1.0`, but it had no prior release, no release tag, no
`RELEASING` contract, no release verifier, and no package or artifact
publication contract. The current `aoa-sdk` federation helper does not admit
`aoa-models` as an owner release target. Adding this repository to that sibling
allowlist would widen another owner's source and release policy during this
owner-local task.

## Options considered

- Hold the source release until federation admission and package-trust routes
  exist.
- Modify `aoa-sdk` so the repository appears in the federation allowlist.
- Establish an owner-local source-only GitHub Release route and leave future
  federation/package admission as a separate decision.

## Decision

Publish `aoa-models` `v0.1.0` as an owner-local, source-only GitHub Release.
The route requires a clean exact landed `main`, the owner validator battery,
an annotated `v0.1.0` tag pointing to that commit, and a release body derived
from the canonical changelog. It does not publish a package, model/runtime
bundle, artifact-registry record, SBOM, signature, or attestation. The
repository is not added to `aoa-sdk` or any sibling release list by this
decision.

## Rationale

This preserves the complete source owner boundary while making the existing
0.1.0 public contour reproducibly discoverable. It keeps release publication,
artifact trust, runtime admission, proof, and acceptance as separate claims,
and avoids turning a sibling helper's missing federation admission into a
silent policy mutation.

## Consequences

- The public baseline becomes the exact `v0.1.0` tag and GitHub Release over
  landed `main`.
- `scripts/release_check.py`, `scripts/release_publish.py`, and
  `docs/RELEASING.md` provide a narrow, repeatable local route.
- Consumers still need exact source/query binding, runtime/artifact admission,
  external execution receipts, and independent proof before operational use.
- A future federation or package release must be separately admitted by the
  stronger owner and must not infer trust from this source release.

## Source surfaces

- `README.md`
- `CHANGELOG.md`
- `docs/RELEASING.md`
- `scripts/release_check.py`
- `scripts/release_publish.py`
- `pyproject.toml`

## Follow-up route

Route future federation admission to `aoa-sdk`; route any package, bundle,
SBOM, signature, or trust-gate requirement to `abyss-machine` and its artifact
owner; route runtime use to `abyss-stack`; route proof to `aoa-evals`.

## Verification

- Owner validator and projection/decision builders.
- Exact-subject catalog and query checks.
- Release-prep Repo Validation CI.
- Owner-local dry-run and postpublish identity audit.
- Current `aoa release audit --repo aoa-models` non-admission is recorded as a
  boundary fact, not a green federation result.
