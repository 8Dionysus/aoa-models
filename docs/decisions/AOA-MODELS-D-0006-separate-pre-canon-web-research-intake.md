# Separate pre-canon web research intake from model source truth

## Status

Accepted for the owner-local experimental repository.

## Index metadata

- Decision ID: AOA-MODELS-D-0006
- Original date: 2026-08-30
- Owner facets: research-intake, external-evidence, pre-canon, promotion-boundary
- Posture: accepted-owner-source

## Context

The first GPT-5.6 web-reconnaissance passes found useful evidence in provider
documentation, independent papers and benchmarks, primary issue reports, and
forums. They also found that source URLs, model aliases, benchmark names, and
mention counts are not stable model facts. Product routes change independently,
one page can mix current and historical segments, grader or harness revisions can
change a headline result, and operational symptoms can belong to the runtime or
product rather than the model.

The existing `ModelIdentity`, `ModelRealization`, `ModelClaim`, and `ModelStudy`
contracts deliberately require stronger owner scope. Importing incomplete or
contradictory web observations directly into `source/` would either weaken those
contracts or discard early signals before an exact subject or owned study exists.
Keeping the material only in unstructured reports would preserve prose but lose
origin dependencies, segment currentness, contradictions, and deterministic
reference validation.

A future contributor would lose why external recurrence is retained without
becoming source truth, why web observations do not feed the fit query, and why
manual packet authoring precedes crawling if this boundary existed only in the
initial corpus or implementation commit.

## Options considered

- Import provider facts, papers, issues, and forum reports directly as model
  claims or study results under `source/`.
- Keep web reconnaissance only as human-readable reports outside the owner
  contracts.
- Build a crawler, source-ranking score, or automatic consensus/promotion path
  before the observation semantics have survived several subjects and runs.
- Delay all external intake until a final ontology of model behavior or
  artificial individuality exists.
- Add a separate, validated pre-canon intake that preserves incomplete and
  contradictory observations without granting them claim, proof, routing, or
  activation authority.

## Decision

Add an owner-local `research-intake/` surface, separate from both canonical
`source/` and rebuildable `generated/` model-fit projections. Its first durable
unit is one self-contained `ReconRun` packet containing source captures with
bounded segments, atomic external observations, observation clusters, tensions,
method pressures, lineage, and revisit triggers.

The packet is pre-canon by contract. It has no automatic-promotion, routing,
activation, proof, or acceptance authority. A research-intake record cannot be
used directly as accepted model-source evidence, cannot enter
`query_model_fit.py`, and cannot establish exact runtime currentness. A later
provider or realization fact, `ModelStudy`, or `ModelClaim` requires its normal
owner review and evidence route while retaining the intake provenance.

Keep model and provider identities as ordinary data. Validate structural and
semantic invariants—references, origin dependencies, temporal history,
configuration gaps, outcome decomposition, and authority—but do not compute one
confidence score, rank source classes universally, count dependent retellings as
independent evidence, or turn a mention threshold into a claim.

Use a reproducible manual packet-authoring and check route first. Reconsider
crawling, monitoring, or other discovery automation only after multiple real
runs and subjects expose stable semantics that warrant it.

## Rationale

This boundary lets `aoa-models` receive valuable external pressure without
turning the web into a second source of model truth. A self-contained run keeps
the smallest useful review object and avoids multiplying top-level owner kinds
before a consumer requires separate identity. Segment-level capture, origin
groups, exact instrument context, counterevidence, and explicit transfer limits
preserve what a flat bibliography or scalar score would erase.

Integrating research validation into the normal owner validator makes packet
integrity durable, while the direct-promotion prohibition preserves the stronger
claim/study lifecycle. Manual authoring is an accepted early cost: premature
automation would hard-code the first family, source strata, and current web
measurement mistakes into infrastructure.

## Consequences

- Weak, partial, contradictory, stale, and no-fit observations can remain
  addressable without being promoted or deleted.
- One model family, provider, URL, benchmark revision, score, or source count is
  never a validator special case.
- Source-segment capture and origin dependencies add authoring work and require
  explicit configuration gaps when the external subject is incomplete.
- A valid packet proves only pre-canon structural and semantic integrity. It
  does not prove a source claim, production prevalence, behavioral fit, runtime
  health, or owner acceptance.
- `ModelRealization`, `ModelClaim`, `ModelStudy`, model-fit projection, and exact
  runtime-subject laws remain unchanged and stronger for their objects.
- `aoa-evals` still owns proof and verdicts; `aoa-sdk` routing and incarnation
  binding; `abyss-stack` process truth; `abyss-machine` host/runtime admission;
  `aoa-memo` reviewed durable memory; and the Operator final authority.
- A future promotion bridge or automated discovery contour requires new
  evidence and a separate owner decision rather than silently extending this
  packet validator.

## Source surfaces

- `schemas/recon-run.schema.json`
- `research-intake/recon-runs/`
- `research-intake/reports/`
- `scripts/research_intake_contract.py`
- `scripts/validate_research_intake.py`
- `scripts/validate_models.py`
- `tests/test_research_intake_contract.py`
- `docs/RESEARCH_INTAKE.md`

## Follow-up route

Use several bounded recon runs to test temporal drift, persistence under
authority, outcome economics, and at least one different family, provider, or
instrument surface. Let their method pressure justify any schema evolution or
automation.

Route an exact provider/runtime fact through a separate `ModelRealization`
review; a reproducible protocol through `ModelStudy`; behavioral promotion
through appropriate owned evidence and independent review; runtime/product
symptoms to their runtime owner; proof to `aoa-evals`; and reviewed durable
memory to `aoa-memo`. No handoff transfers acceptance automatically.

## Verification

- `python scripts/validate_research_intake.py`
- `python scripts/validate_models.py`
- `python scripts/build_model_fit_projections.py --check`
- `python scripts/generate_decision_index.py --check`
- `python -m unittest discover -s tests -v`
- `git diff --check`

Live catalog compatibility, runtime admission, external retrieval freshness,
proof, deployment, publication, and owner/human acceptance remain separate
checks and are not established by this decision.
