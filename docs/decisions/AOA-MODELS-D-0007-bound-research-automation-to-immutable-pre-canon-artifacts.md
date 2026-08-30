# Bind research automation to immutable pre-canon artifacts

## Status

Accepted for the owner-local experimental repository.

## Index metadata

- Decision ID: AOA-MODELS-D-0007
- Original date: 2026-08-30
- Owner facets: research-intake, provenance, temporal-change, review-boundary
- Posture: accepted-owner-source

## Context

AOA-MODELS-D-0006 admitted external web reconnaissance through manually
authored, pre-canon `ReconRun` packets and deliberately deferred automation
until several materially different runs exposed stable semantics. The GPT-5.6
seed and temporal recheck, Claude persistence run, and cross-provider economics
run now expose repeated mechanical work: retrieve the same bounded segment,
retain its locator and digest, distinguish a changed document from a changed
segment, bind a later snapshot to history, and package a possible observation
relationship for review.

Those operations are repeatable without deciding whether a web assertion is
true. Leaving them entirely manual loses deterministic retrieval limits,
content-addressed history, unavailable and partial states, and reproducible
change classification. Automating discovery, consensus, source ranking, or
promotion at the same time would cross a different boundary: dependent
retellings can resemble recurrence, source usefulness changes by question, and
supersession changes observation history only after semantic review.

A future contributor would lose why bounded capture and refresh are safe to
automate while discovery, truth judgment, promotion, and source mutation are
not if this distinction existed only in command implementation or a bootstrap
report.

## Options considered

- Keep retrieval, segment hashing, temporal comparison, and proposal packaging
  fully manual after the observation contour has stabilized.
- Build a broad crawler or monitor that selects sources and writes observations
  directly into recon packets.
- Add universal source ranking, recurrence thresholds, or automatic consensus
  before independent-origin and question-relative usefulness can be preserved.
- Let refresh overwrite the previous capture or automatically add a qualified
  `supersedes` reference to an observation.
- Add bounded, data-driven commands that create immutable pre-canon capture
  snapshots, change receipts, and review-only supersession proposals.

## Decision

Add one owner-local automation contour beneath manual research judgment:

- `capture-source` consumes source metadata, one structured locator, and
  bounded retrieval parameters, then creates an immutable
  `ResearchCaptureSnapshot` candidate. It records successful, partial,
  missing, and unavailable states instead of filling gaps.
- `refresh-capture` repeats the same request, creates a new snapshot linked to
  its predecessor, and creates a `ResearchChangeReceipt`. It classifies
  retrieval, document, raw-segment, normalized-segment, and locator-state
  change without overwriting either snapshot.
- `suggest-supersession` binds two exact content-addressed observations and
  packages an operator-supplied update, narrowing, contradiction, or
  independence relation with a structural comparison. It creates a proposal;
  it never changes either `ReconRun`.

Keep provider, family, model, source class, URL, publisher, origin, and
retrieval limits as data. Adapter behavior is selected by general locator and
media contracts, not by provider or model identity. Initial locator kinds are
whole document, line range, JSON Pointer, and HTML element ID because the
landed runs and their source strata exercise text, structured, and page
segments; adding another adapter requires a generic extraction pressure rather
than a named site branch.

Every automation artifact is pre-canon, content-addressed, and has no source
mutation, automatic promotion, routing, activation, proof, or acceptance
authority. Repository-retained receipts resolve their exact local snapshots;
repository-retained proposals resolve their exact local runs and observations.
The command route refuses to overwrite an existing output.

## Rationale

This contour automates evidence preservation rather than evidence judgment.
Raw and normalized segment digests allow formatting-only change to remain
different from content change. Document and segment digests allow a mutable
page to change without implying that the cited segment changed. Explicit
missing, partial, unavailable, recovery, and ambiguity states keep failed
retrieval from becoming silence or invented evidence.

Content-addressed observation refs make a proposal reproducible, while the
required review posture preserves D-0006: a structural overlap is not semantic
supersession, and a proposal cannot establish a model fact, study, claim,
runtime condition, proof verdict, route, or acceptance. Bounded HTTP and
offline-input execution permit live capture and deterministic replay without
introducing a crawler or mutable cache as an owner source.

## Consequences

- Repeated source refreshes become deterministic, append-only review objects.
- Text/Markdown line ranges, structured JSON values, HTML element IDs, and
  whole documents share one provider-neutral contract.
- Redirect target, HTTP status, ETag, last-modified value, byte limit,
  truncation, document digest, segment digest, and normalization profile remain
  inspectable without retaining an unbounded page body.
- Normalization is comparison evidence only. It cannot replace the raw segment
  digest or justify semantic equivalence by itself.
- An unavailable capture is a valid artifact state and may still require retry
  or a different access route; successful command execution does not establish
  source availability at another time.
- An `update` or `narrowing` proposal requires the same target kind, a shared
  subject-identity dimension, and a non-earlier candidate interval. This only
  admits review; it does not accept the relation.
- Requests, offline inputs, exploratory outputs, and one-off load checks remain
  working material unless separately reviewed into the declared flat artifact
  routes.
- Broad discovery, scheduling, crawling, source ranking, consensus, automatic
  observation authoring, promotion, and canonical source writes remain outside
  this decision.

## Source surfaces

- `schemas/research-automation-artifact.schema.json`
- `scripts/research_automation.py`
- `scripts/research_automation_contract.py`
- `scripts/research_intake.py`
- `scripts/research_intake_contract.py`
- `scripts/validate_research_intake.py`
- `research-intake/capture-snapshots/`
- `research-intake/change-receipts/`
- `research-intake/supersession-proposals/`
- `docs/RESEARCH_INTAKE.md`
- `tests/test_research_automation.py`

## Follow-up route

Use bounded refreshes to learn actual revisit cadence, locator failure modes,
and review burden. Add a new locator or normalization profile only when a real
source cannot be represented safely by the current generic contour. Consider
scheduling or discovery automation only after reviewed capture history exposes
stable selection and retry policy; consider any promotion bridge only through
a separate owner decision and the normal target-object evidence review.

Accepted supersession still belongs in a later reviewed `ReconRun` edit. Exact
provider or runtime facts route to `ModelRealization`; reproducible protocols
to `ModelStudy`; bounded behavioral claims to `ModelClaim` with appropriate
evidence and independent review; proof to `aoa-evals`; runtime symptoms to the
runtime owner. No automation receipt transfers acceptance.

## Verification

- `python -B scripts/validate_research_intake.py`
- `python -B scripts/validate_models.py`
- `python -B scripts/build_model_fit_projections.py --check`
- `python -B scripts/generate_decision_index.py --check`
- `python -B -m unittest discover -s tests -v`
- `git diff --check`

Live external retrieval, catalog currentness, runtime admission, proof,
deployment, publication, and owner or human acceptance remain separate checks.
