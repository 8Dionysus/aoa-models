# Changelog

All notable owner-source changes are recorded here. Release notes describe
the source and read-only access-plane contour owned by `aoa-models`; they do
not promote model knowledge into routing, runtime, proof, or acceptance.

## [Unreleased]

- Reserved for changes after `v0.1.0`.

## [0.1.0] - 2026-08-22

### Summary

- First public owner-source slice for configuration-scoped, lifecycle-aware
  model knowledge in AoA. This experimental 0.x release establishes validated
  model identity, realization, claim, study, projection, and read-only fit
  query contours for GPT-5.6 Luna/Sol while preserving stale runtime history.

### Added

- `ModelIdentity`, `ModelRealization`, `ModelClaim`, `ModelStudy`, and
  generated `ModelFitProjection` source and schema surfaces.
- Configuration-scoped provenance across provider, access regime, runtime
  version and exact subject, reasoning effort, context, tools, environment,
  permissions, and observation interval.
- The read-only `scripts/query_model_fit.py` access plane and the
  content-addressed `aoa_model_fit_query_result_v2` evidence return. Results
  bind the exact query, clean owner source, realization/projection catalog,
  candidate realization and projection bytes, matched runtime subject, and
  generating fit claims or studies.
- Live Codex catalog compatibility checking, exact
  `runtime_subject={kind,source,digest}` identity, and a pinned GitHub Repo
  Validation workflow with `contents: read` permissions.
- Bounded Luna `eval`, `stats`, `memo`, evaluator-review, and structured
  owner-duty hypotheses with fixed studies and explicit attribution limits.
- The current 0.148.0 Luna max structured-owner-duty declaration bound to the
  content-addressed runtime package subject
  `codex-cli-standalone/x86_64-unknown-linux-musl+codex-code-mode-host` with
  digest `sha256:35cc6b0e4e5c527569807be8017b705f410f0c6c2b7a3fa1c6a5407d65889041`.
- Four accepted owner decisions covering separate model ownership, live
  realization currentness, content-addressed query returns, and exact
  runtime-subject currentness.

### Changed

- Currentness now binds to the complete exact realization and live catalog
  subject rather than a model nickname, calendar review date, or runtime
  version alone.
- Query returns carry immutable source, catalog, candidate, projection, query,
  and result provenance instead of informal candidate paths.
- Generated projections and the decision index are explicitly rebuildable,
  checkable consumer views; they cannot authorize routing, activation, proof,
  or acceptance.
- Provider facts, runtime observations, behavioral claims, study results,
  economics, and external-owner responsibilities remain separate.
- A narrow owner-local source-release route is now documented. This release is
  source-only: no Python package-index publication, runtime bundle, model
  weights, or artifact-registry promotion is promised.

### Fixed

- Closed stale Codex 0.146 and 0.147 realization paths without rewriting
  history; lifecycle transitions preserve why they became stale.
- Scoped landing counterevidence to the landing claim instead of allowing
  unrelated evidence to weaken the wrong hypothesis.
- Rejected same-version/different-subject matches and missing exact subject
  identity; negative paths are covered by contract tests.
- Kept generated projections and the decision index synchronized with owner
  source across currentness and lifecycle transitions.

### Deprecated

- Version-only or ambient-catalog currentness is deprecated as a sufficient
  active/runtime identity.
- Stale 0.146 and 0.147 realizations remain readable historical records but
  are not current activation inputs.

### Removed

- No capability was removed from a prior public release because no prior
  release existed. Seven generated 0.147 projections were removed from the
  current consumer view only because their source realizations became
  explicitly stale; historical source records remain.

### Security

- No credential, secret, private key, or new external-effect surface is added.
  CI grants `contents: read`; the declared workspace-write realization has
  `external_effects=false` and network disabled.
- This is not a security audit, package-signing attestation, SBOM, or
  supply-chain proof. No package artifact, SBOM, signature, or publication
  attestation is emitted by this source-only release route.

### Validation

The release-prep source was validated against the clean campaign baseline
`538ec4158bed914d6dcd80249c88fbd3b55617d9`; the same gate is required again
on the exact landed release commit:

- `PYTHONDONTWRITEBYTECODE=1 python -B scripts/validate_models.py` — OK:
  `ModelClaim=8`, `ModelFitProjection=1`, `ModelIdentity=2`,
  `ModelRealization=13`, `ModelStudy=16`.
- `PYTHONDONTWRITEBYTECODE=1 python -B scripts/build_model_fit_projections.py --check`
  — one current generated projection.
- `PYTHONDONTWRITEBYTECODE=1 python -B scripts/generate_decision_index.py --check`
  — five accepted decision records; generated index current.
- Exact-subject catalog check with the 0.148.0 runtime subject and
  `--require-realization-ref` — passed; catalog compatibility only.
- Exact-subject `scripts/query_model_fit.py --require-match` — passed; the
  result remains an informational handoff aid.
- `PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s tests -v` —
  all contract tests passed.
- `git diff --check` — passed.
- Release-prep and landed-main GitHub Repo Validation run identities are
  recorded in the execution report; CI is validation evidence, not
  publication, runtime health, proof, or acceptance.

### Notes

- This is an initial 0.x source release, not a stable 1.0 API. No prior public
  compatibility promise exists. The existing `pyproject.toml` marker already
  selected `0.1.0`; the version does not derive from commit count.
- New active/current query paths require exact `runtime_subject` identity.
  Historical v1/source shapes remain readable where owner law permits; no
  migration script exists, so consumers must preserve source refs, result
  digests, and exact subject identity rather than reconstructing them from a
  nickname or version.
- The 0.148.0 realization is declared and catalog-compatible, not observed in
  a fresh external actor run. This release does not prove package admission,
  process health, behavioral fit, reliability, wake/resume delivery,
  routing, activation, proof, owner acceptance, or human acceptance.
- Deployment, observability, recovery, rollback, runtime admission, and
  provider/consumer activation remain stronger-owner concerns. A consumer
  must bind the exact published source/query evidence through `aoa-sdk`, use
  `abyss-machine`/`abyss-stack` admission and receipts, and obtain independent
  `aoa-evals` evidence before any fit claim is strengthened.
- The source-only release route does not publish a package or upload release
  assets. GitHub source archives are platform-generated views of the exact
  tag and are not an attestation or runtime artifact.
- `aoa-session-memory`, `aoa-routing`, and `abyss-stack_old` are outside this
  release and were not mutated.

### First-Parent Reconciliation

The repository had no prior release tag. Every first-parent commit from the
root to `v0.1.0` is covered below; generated files are grouped with the
source/contract change that gives them meaning.

| First-parent commit | PR / landing | Reconciled public change | Classification |
|---|---|---|---|
| `36b0bd134566d088090d3ec7a16affccffc4300a` | root | Initial owner organ: AGENTS, README, DIRECTION, HANDOFFS, CHANGELOG, D-0001, v1 schemas, validators/builders, Luna/Sol identities and realizations, studies, tests, and package metadata. | Changelog-worthy: initial owner surface. |
| `40bfebfaf5b52a095c85cc76c42f9493152b63ce` | PR #1 | Live Codex 0.147 realization refresh and 0.146 closure; read-only fit query/result schema; catalog checker; D-0002; handoff docs; CI; install metadata; generated projection refresh. | Changelog-worthy: currentness/access-plane foundation; generated renames grouped. |
| `d5dbdd06cf18147abe7baa505fed1146cef99f7a` | PR #2 | Content-addressed `aoa_model_fit_query_result_v2`, exact owner/source/catalog/claim/study provenance, query/result digests, D-0003, and tests. | Changelog-worthy: evidence-bound query ABI. |
| `a66625ac6ae22823cecc11c2581bccf9e50b958c` | PR #3 | Bounded Luna eval/stats/memo hypotheses; xhigh structured-owner-duty realization; provider/economics provenance; Unreleased hints; projection and tests. | Changelog-worthy: operational canary hypotheses; economics/projection churn grouped. |
| `3cb16a29fcc584972b57064a41c315e2ef1ae67b` | PR #4 | Separate Luna eval-review canary claim and projection plus negative/contract tests. | Changelog-worthy: eval-review canary. |
| `5df78821be6edbe439df452d7bcde75e1c453b91` | PR #5 | Dedicated xhigh eval-reader read-only realization, projection, and claim update. | Changelog-worthy: evaluator realization; replacement projection deletion is generated churn. |
| `e1ede88f248019ed40dae8d0632b5181100a0b87` | PR #6 | Max structured-owner-duty hypothesis and realization; transfer-hypothesis update; projection refresh and tests. | Changelog-worthy: structured owner-duty canary. |
| `9f97e30a172084b203ea23436171a0290b3a4f39` | PR #7 | Landing counterevidence restricted to landing scope; lifecycle and test repair. | Changelog-worthy: bounded-counterevidence fix. |
| `ffed04f5b1f7686f2123ba7daf3d165a63859e2e` | PR #8 | All 0.147 realizations/projections closed as stale with explicit history; stale claims and generated consumers removed; lifecycle tests updated. | Changelog-worthy: stale-runtime closure; seven projection removals are generated churn. |
| `538ec4158bed914d6dcd80249c88fbd3b55617d9` | PR #9 | Exact runtime-subject schema; 0.148 Luna declaration/currentness hypothesis; exact subject in query/result/catalog checker; D-0004; boundary docs; projection and tests. | Changelog-worthy: exact-subject currentness; two branch commits grouped into one logical item. |

### Non-first-parent reconciliation

All branch commits were grouped into their landed PR item rather than silently
omitted: PR #1 (`63a3eaa`, `7b4dcc1`, `f3242a3`), PR #2 (`3cdc8d5`), PR #3
(`e789ebb`, `7a37aa4`), PR #4 (`2208b2e1`), PR #5 (`0e868a8`), PR #6
(`2db0bb1`), PR #7 (`f27401f`), PR #8 (`68d0e0b`), and PR #9
(`6760e41`, `0df9033`). None is a second public release note, duplicate,
unrelated noise, or intentional exclusion.
