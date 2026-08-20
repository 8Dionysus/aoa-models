# Bind currentness to an exact runtime subject

## Status

Accepted for the owner-local model-fit access plane.

## Index metadata

- Decision ID: AOA-MODELS-D-0004
- Original date: 2026-08-20
- Owner facets: realization-currentness, access-plane, evidence-chain, consumer-boundary
- Posture: accepted-owner-source

## Context

The first currentness repair treated a Codex version and live model catalog as
the runtime identity. That is insufficient for the external actor route: an
ambient installed CLI and a separately bound content-addressed runtime can
report the same version while being different runtime subjects. A version-only
repair therefore creates recurring named-version exceptions and can let one
subject's currentness evidence inform another subject.

## Decision

Represent the exact runtime subject separately from the runtime version. An
active model realization may be current or queryable only when its runtime
configuration carries a `runtime_subject` object with an owner-defined `kind`,
`source`, and immutable SHA-256 `digest`. The fit query must receive the exact
same subject identity and compares the complete object, not just its version.

The live catalog checker treats version, model capabilities, context, and
backend compatibility as facts about the supplied subject. Missing or
mismatched subject identity is an active mismatch even when every version
field agrees. Ambient observations remain valid evidence about the ambient
subject only; they cannot silently establish currentness for a different
content-addressed binding.

Historical realizations and previously emitted result shapes remain readable,
but new active source and query paths fail closed without an exact subject.
The subject identity does not grant routing, activation, process, proof, or
owner-acceptance authority; package admission, runtime binding, and execution
remain with their stronger owners.

## Rationale

Separating subject identity from version preserves model realization meaning
across package rebuilds, companion changes, isolated Codex homes, and external
runtime bindings. It makes the currentness boundary generic and lets a
consumer bind exact evidence without teaching `aoa-models` to launch or route
the runtime.

## Consequences

- Same-version subject drift returns no fit candidate and fails live currentness
  checks closed.
- A runtime subject digest is evidence of identity, not proof of package
  admission or behavioral fit.
- Existing stale history is preserved without renaming or rewriting its
  observations.
- The v2 content-addressed fit result remains the handoff format; its new
  candidates expose the exact subject identity that was matched.

## Source surfaces

- `schemas/runtime-subject.schema.json`
- `schemas/model-realization.schema.json`
- `schemas/model-fit-query.schema.json`
- `schemas/model-fit-query-result.schema.json`
- `scripts/model_contract.py`
- `scripts/query_model_fit.py`
- `scripts/check_live_codex_catalog.py`
- `tests/test_model_contract.py`

## Follow-up route

Hand the exact subject identity to `aoa-sdk` as part of its runtime-neutral
incarnation binding and require `abyss-stack` to admit the corresponding
package/profile. Route behavioral observations to `aoa-evals`; do not promote
catalog or subject compatibility into fit, routing, activation, or acceptance.

## Verification

- `python scripts/validate_models.py`
- `python scripts/build_model_fit_projections.py --check`
- `python scripts/generate_decision_index.py --check`
- `python -m unittest discover -s tests -v`
