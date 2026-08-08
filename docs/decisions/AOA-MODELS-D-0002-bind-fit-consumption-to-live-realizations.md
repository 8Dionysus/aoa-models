# Bind fit consumption to live realizations

## Status

Accepted.

## Index metadata

- Decision ID: AOA-MODELS-D-0002
- Original date: 2026-08-08
- Owner facets: realization-currentness, access-plane, consumer-boundary, lifecycle
- Posture: accepted-owner-source

## Context

The first Luna landing studies produced exact Codex 0.146.0 realizations and
informational fit projections. The host later moved to Codex 0.147.0 while the
claim remained calendar-current, so a consumer could still discover a fit
projection whose exact runtime no longer matched the machine. At the same time,
`aoa-agents-skills` became a real bounded consumer that needs to ask for
configurations satisfying role properties without reading the whole model
repository or turning a model name into the start of an actor route.

If only the source records and a calendar `review_by` remained, future
consumers would lose the stronger rule that runtime version and catalog
capabilities are part of realization identity. If each consumer read generated
JSON directly, the owner could not provide one checked, authority-limited query
contract or distinguish an informational candidate from activation.

## Options considered

- Keep Codex 0.146.0 realizations current until their claim review date. This
  would make calendar freshness stronger than exact runtime identity.
- Let `aoa-agents`, `aoa-sdk`, or `abyss-stack` parse model source and choose a
  realization independently. This would duplicate fit interpretation and move
  model-knowledge meaning into consumers.
- Publish a model-first launcher or registry that activates Luna directly. This
  would conflate an informational fit candidate with a role, route, binding,
  permission, and runtime decision.
- Preserve old realizations as stale history, add exact current declarations,
  validate them against the live Codex catalog, and expose one read-only
  property query whose result carries no activation authority.

## Decision

Treat every material Codex version or model-catalog capability change as a
realization-currentness event. An active claim may not remain `current` when it
references a stale, suspended, retired, or missing realization. Historical
realizations close their observation interval and retain an explicit transition
reason instead of being rewritten.

Provide one owner-governed read-only fit query over current generated
projections and exact realization source. Its input describes task family,
runtime, effort when already required, permission posture, tools, and MCP
requirements. Its output returns zero or more informational candidates plus
their limitations. The query cannot route, activate, prove, accept, or grant an
effect, and deterministic ordering is not a ranking or model choice.

Codex product context and native API context remain distinct. API prices,
cache-write cost, and long-context multipliers are stored as reference
economics when the active realization uses ChatGPT quota; no per-run USD cost
is invented.

The public `8Dionysus/aoa-models` repository is now the canonical remote for
this owner. Ecosystem registration and runtime admission remain separate
stronger-owner actions.

## Rationale

This keeps volatile compatibility in the object that actually changes—the
exact realization—while preserving stable role identity outside the model
organ. A checked query gives the first real consumer a narrow access plane
without making `aoa-models` a launcher, route planner, proof system, or runtime.
The transfer hypothesis from Codex 0.146.0 to 0.147.0 remains visibly weaker
than a new real-work observation.

## Consequences

- Codex upgrades can immediately stale incompatible source and claims even
  when a calendar review date has not passed.
- Historical studies and receipts remain addressable through their original
  realization rather than being relabelled as current evidence.
- Consumers gain a compact property-based query but must still obtain a role
  mandate, SDK binding, runtime admission, domain procedure, and return route.
- A newly declared realization may appear only with an explicit limitation
  until an external actor run observes it.
- `abyss-stack` must implement and admit every referenced runtime/tool profile
  before the corresponding declaration becomes callable.
- `aoa-evals` still owns any claim that the new realization provides net
  benefit or performs its role adequately.

## Source surfaces

- `schemas/model-realization.schema.json`
- `schemas/model-fit-query.schema.json`
- `schemas/model-fit-query-result.schema.json`
- `source/model-realizations/`
- `source/model-claims/`
- `generated/model-fit-projections/`
- `scripts/check_live_codex_catalog.py`
- `scripts/query_model_fit.py`

## Follow-up route

Hand the exact current realization reference to `aoa-sdk` for binding and the
declared runtime/tool profile to `abyss-stack` for implementation and live
admission. After a real Codex 0.147.0 landing regression, route evidence to
`aoa-evals`; then strengthen, narrow, weaken, or stale the transfer hypothesis
from reviewed owner evidence.

Register the read-only query through the current organ-access fabric without
letting that transport acquire model-fit or activation authority.

## Verification

- `python scripts/generate_decision_index.py --check`
- `python scripts/validate_models.py`
- `python scripts/build_model_fit_projections.py --check`
- `python scripts/check_live_codex_catalog.py`
- schema-backed fit query tests and `python -m unittest discover -s tests -v`
