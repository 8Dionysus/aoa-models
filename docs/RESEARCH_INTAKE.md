# External web research intake

`research-intake/` is the pre-canon entry surface for external model
reconnaissance. It preserves useful, incomplete, contradictory, and historical
web evidence before an exact owner fact, study, or claim exists.

A valid packet is not owner truth. It cannot route or activate a model, prove
fit or safety, establish runtime currentness, satisfy an eval verdict, or enter
the model-fit query.

## Why a separate surface exists

The web exposes several different objects under similar language:

- provider identity, interface, price, and product-policy facts;
- benchmark results bound to a task pool, harness, grader, and revision;
- model-behavior observations with incomplete realization identity;
- runtime or transport symptoms reported against one client/build;
- operational pressure from primary issues and forums;
- dependent retellings of one original measurement.

`source/` owns accepted configuration-scoped model meaning. Research intake
keeps the material distinguishable until the normal owner route can decide what,
if anything, should become a realization fact, `ModelStudy`, or `ModelClaim`.

See [AOA-MODELS-D-0006](decisions/AOA-MODELS-D-0006-separate-pre-canon-web-research-intake.md)
for the accepted boundary.

## Packet contour

Each `research-intake/recon-runs/*.json` file is one self-contained `ReconRun`:

```text
ReconRun
  ├─ SourceCapture[]
  │    └─ segment[]
  ├─ ExternalObservation[]
  ├─ ObservationCluster[]
  ├─ tension[]
  ├─ method_pressure[]
  └─ lineage + revisit triggers
```

Local source, observation, cluster, tension, and pressure IDs are unique inside
the packet. A cross-run supersession uses a qualified run plus observation ref.
Old packets remain readable; a newer observation links to history instead of
rewriting it.

When a method or predecessor artifact has a repository-local `ref` and a
`content_digest`, validation resolves it. ReconRun predecessors use the printed
JSON-canonical digest; other local files use the SHA-256 digest of their bytes.
This keeps method and lineage references from silently drifting after review.

The schema is `schemas/recon-run.schema.json`. Semantic rules are implemented
in `scripts/research_intake_contract.py` and exercised through the normal owner
validator.

## Manual authoring flow

### 1. Ask a bounded question

Prefer a question with a transfer boundary:

> Under which product, effort, and verifier conditions does a reported outcome
> recur?

Avoid a brand-level prompt such as “what is this model like?”.

### 2. Declare scope before collecting conclusions

Record:

- subject labels used for discovery, without treating them as exact snapshots;
- target kinds the run actually investigates;
- capture interval;
- inclusion and exclusion criteria;
- whether the run tests another family/provider, another product/instrument, or
  records an evidence-backed deferral.

There is no required source count. Stop when the supported scope, unknowns,
countersearch, and next disposition are reviewable.

### 3. Capture sources by segment and origin

One URL can contain current and historical sections. Capture the exact segment
locator used by an observation. Store a content digest when exact bytes were
retained; otherwise state why the digest is unavailable.

`origin_group` identifies who produced the evidence. `dependency_refs` connect
retellings, derived leaderboards, or pages that consume an earlier measurement.
A hundred links to one table remain one origin.

Source class describes the natural role of evidence; it is not a universal
rank. A forum report can discover a failure mode while remaining unable to
establish incidence or model causality.

### 4. Atomize observations

One observation carries one proposition, target kind, subject, configuration,
outcome, time interval, source segments, confounds, transfer limits, posture,
and disposition.

Separate at least these target kinds:

- `provider_fact`;
- `benchmark_result`;
- `model_behavior`;
- `runtime_behavior`;
- `product_policy`;
- `operational_pressure`;
- `unresolved` when attribution is not yet honest.

Model/provider names are ordinary data. New names require no Python or schema
branch.

### 5. Bind the subject and configuration honestly

Use `exact`, `bounded`, `partial`, or `unresolved` completeness independently
for the subject and configuration. A partial or unresolved observation must
name its configuration gaps.

Keep separate:

- family/model label and exact snapshot;
- provider route and product surface;
- runtime name/version and exact owner runtime-subject ref;
- reasoning effort;
- context policy;
- tools and permissions;
- prompt, scaffold, and runbook;
- harness, instrument revision, and grader.

An external source digest or version string never establishes the exact
`ModelRealization.runtime_subject` owned by canonical source.

### 6. Decompose agent outcomes

Keep these fields independent even when some are unknown:

```text
requested
executed
artifact
verified
reported
termination
```

A valid artifact with missing protocol completion and a confident completion
claim with no tool execution are different observations. Measurements retain
their metric, value, unit, denominator, and notes. Price, quota, tokens, turns,
wall time, retries, and accepted outcome are not interchangeable denominators.

### 7. Cluster by mechanism, not sentiment

A cluster names its supported scope, referenced observations, independent
origin groups, counterevidence, transfer limits, unresolved gaps, posture, and
next action. Preserve tensions before averaging. A tension may be resolved by
scope, instrument, time, product, segment, origin, or axis split; unresolved is
a valid result.

Evidence posture describes what exists. Disposition describes the next action.
They are not one confidence score.

### 8. Record method pressure and revisit events

Add a method pressure only when the run exposed a real ambiguity or missing
dimension. Do not add schema fields merely because they might become useful.

Useful revisit triggers include:

- alias, snapshot, product, runtime, price, or quota change;
- benchmark task-pool, grader, harness, or scoring revision;
- controlled reproduction or counterexample for an operational symptom;
- a later observation that narrows or supersedes an earlier one.

### 9. Validate

Run from the repository root:

```bash
python -B scripts/validate_research_intake.py
python -B scripts/validate_models.py
python -B -m unittest discover -s tests -v
```

The intake validator prints a canonical digest for each run. That digest binds
packet bytes after JSON canonicalization; it does not promote the packet or
prove its external sources.

Repository-local method and predecessor digests are also checked. An
`external-input:` ref remains preserved provenance that this repository cannot
recompute; it is not silently treated as a local file or proof.

Errors name the run file and missing record/ref/segment. Fix source records
before any derived documentation. Do not weaken source, claim, or runtime
validators to admit a web packet.

## Minimal authoring outline

The exact schema is authoritative; this is a contour, not copy-ready JSON:

```json
{
  "$schema": "https://schemas.aoa.local/models/recon-run.schema.json",
  "schema_version": "aoa_model_recon_run_v1",
  "kind": "ReconRun",
  "recon_run_id": "recon-run:family/date-question",
  "authority": {
    "pre_canon": true,
    "automatic_promotion": false,
    "routing_authority": false,
    "activation_authority": false,
    "proof_authority": false,
    "acceptance_authority": false
  },
  "promotion_policy": "pre_canon_no_automatic_promotion",
  "source_captures": [],
  "observations": [],
  "clusters": [],
  "tensions": [],
  "method_pressures": []
}
```

Use the smallest existing run as a field-complete example. Do not copy its
model names, source counts, URLs, scores, or currentness claims into a new run.

## Promotion and handoff

```text
pre-canon observation/cluster
  ├─ exact provider/runtime fact → separate ModelRealization review
  ├─ exact subject + reproducible method → ModelStudy candidate
  ├─ bounded behavior + appropriate owned evidence → ModelClaim candidate
  ├─ runtime/product symptom → runtime or product owner
  └─ weak/stale/contradictory → preserve, watch, replicate, or no-fit
```

No research-intake path can be direct accepted evidence in canonical model
source. A later record cites the original external sources and its explicit
owner review/proof route; it may preserve the intake packet as provenance, but
the packet does not satisfy acceptance.

## Validation that stays versus working checks

Permanent tests protect generic structure and semantic boundaries: refs,
history, origin dependencies, authority, outcome decomposition, and
multi-provider data acceptance.

Do not retain permanent tests for:

- one migration's exact record counts or filenames;
- current external URLs, prices, scores, aliases, or leaderboard positions;
- one-off extraction scripts or browser snapshots;
- temporary downloads, dedup tables, or corpus-specific assertions.

If a working check reveals a recurring invariant, rewrite it as a small generic
test and remove the one-off helper before closing the goal that created it.

## Why there is no crawler yet

The first packets are authored manually so real runs can pressure-test subject
binding, segment capture, origin semantics, outcome shape, and contradiction
handling. A crawler, monitor, source ranking, or consensus engine would freeze
those choices prematurely. Automation requires separate evidence and owner
review after several materially different runs.
