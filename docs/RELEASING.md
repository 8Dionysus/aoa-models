# aoa-models release route

## Scope

`aoa-models` publishes owner-authored source and its read-only access-plane
contract. The repository does not launch models, choose routes, admit runtime
packages, issue proof verdicts, or accept work.

`v0.1.0` is a source-only GitHub Release. This route does not publish a Python
package, model weights, runtime bundle, package-registry record, SBOM,
signature, or artifact-registry promotion. GitHub's generated source archives
are views of the exact tag, not owner attestations.

## Version and source authority

- `pyproject.toml` is the package metadata version marker.
- The dated `## [0.1.0]` section in `CHANGELOG.md` is the canonical release
  prose and reconciliation ledger.
- `README.md` carries the exact current-release banner.
- `source/`, `schemas/`, and `docs/decisions/` remain owner-authored; generated
  projections and the decision index are rebuilt by their builders.

## Preflight

Run from a clean `main` checkout synchronized with the public `origin/main`:

```bash
GIT_SSH_COMMAND='ssh -F /dev/null' python scripts/release_check.py
```

The exact-subject catalog check is intentionally explicit. It verifies
compatibility of the declared runtime subject only; it does not prove package
admission, process health, fit, routing, proof, or acceptance.

The current SDK federation helper is also checked, but `aoa-models` is not in
its admitted owner list as of this release. The expected result is the
bounded non-admission error `Unknown owner repo 'aoa-models'`. Do not pass
`--all-due` and do not mutate `aoa-sdk` to force this repository into a
federation list. The owner-local route below is the authorized publication
route until a separate federation decision admits this repository.

## Owner-local dry-run and publication

The helper below binds the release to clean `main`, the exact remote main
commit, the approved tag, the canonical changelog body, and an empty uploaded
asset set:

```bash
GIT_SSH_COMMAND='ssh -F /dev/null' python scripts/release_publish.py --dry-run
```

After the release-prep PR is merged and local `main` is fast-forwarded to the
exact landed commit, rerun the owner gate and dry-run. Then publish once:

```bash
GIT_SSH_COMMAND='ssh -F /dev/null' python scripts/release_check.py
GIT_SSH_COMMAND='ssh -F /dev/null' python scripts/release_publish.py --confirm
```

`--confirm` creates the annotated `v0.1.0` tag at the already-verified HEAD,
pushes only that tag, and creates a non-draft, non-prerelease GitHub Release
with notes derived from `CHANGELOG.md`. It never creates a tag from a moving
branch and never generates prose from GitHub's automatic notes.

## Postpublish audit

```bash
GIT_SSH_COMMAND='ssh -F /dev/null' python scripts/release_publish.py --postpublish
```

The audit requires the remote peeled tag to resolve to the exact landed main
commit, a published latest GitHub Release with matching body and tag, no
uploaded assets for this source-only release, and a clean local tree. A
successful audit proves publication identity and release-surface integrity;
it does not prove runtime health, model fit, proof, deployment, rollback
execution, or human acceptance.

## Recovery and rollback

Do not move or recreate `v0.1.0`. If publication fails after the tag is pushed,
preserve the tag and resume with `--postpublish` after resolving the GitHub
Release operation. Any future correction requires a new owner-approved
version. Runtime rollback and consumer admission belong to stronger owners.
