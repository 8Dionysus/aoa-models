# Content-address fit query returns

## Status

Accepted.

## Index metadata

- Decision ID: AOA-MODELS-D-0003
- Original date: 2026-08-10
- Owner facets: access-plane, consumer-boundary, evidence-chain, realization-currentness
- Posture: accepted-owner-source

## Context

The first property query returned realization and projection paths plus an
informational candidate list. That was enough for human inspection but not for
the external actor chain. `aoa-sdk` and `aoa-summon` need to preserve the exact
fit evidence that informed a replaceable incarnation. A path alone does not
bind bytes, source revision, originating claim, or the exact query result.

## Options considered

- Let every consumer reopen paths and construct its own digests.
- Copy fit meaning into `aoa-sdk` or the runtime request.
- Evolve the read-only query result so `aoa-models` emits exact owner-qualified
  evidence while retaining no selection or activation authority.

## Decision

Evolve the fit-query result to `aoa_model_fit_query_result_v2`. Preserve the
human-readable realization and projection paths, and add:

- one full clean `aoa-models` Git source ref;
- exact provenance refs for the realization, projection, and every generating
  fit claim or study used by each candidate;
- a digest of the exact query;
- a digest of the realization/projection catalog, including no-match returns;
- a canonical result ID and result digest.

The query fails closed when any catalog artifact or selected claim/study is
dirty relative to the declared owner source ref. It still returns zero or more
informational candidates and never emits a selected candidate, route,
permission, runtime activation, proof verdict, or owner acceptance.

## Rationale

The model organ should be able to answer not only “which current
configurations might fit?” but also “which exact owner evidence produced this
answer?”. Content addressing lets downstream owners bind that answer without
reinterpreting model claims or trusting machine-local paths.

## Consequences

- `aoa-sdk` can bind one exact model-fit query result and candidate projection
  beside the realization ref.
- An empty result remains reviewable evidence over one exact catalog.
- Branch trials with dirty realization or projection inputs must first create
  an exact proof commit or other clean owner source.
- `aoa-models` still does not decide which candidate an actor uses.

## Source surfaces

- `schemas/model-fit-query-result.schema.json`
- `scripts/query_model_fit.py`
- `tests/test_model_contract.py`

## Follow-up route

Add the exact query-result and projection refs to the `aoa-sdk` incarnation
binding, then require the same model-fit ref in the external `aoa-summon`
packet. Candidate selection and runtime admission remain with their existing
owners.

## Verification

- `python scripts/validate_models.py`
- `python scripts/build_model_fit_projections.py --check`
- `python scripts/generate_decision_index.py --check`
- `python -m unittest discover -s tests -v`
