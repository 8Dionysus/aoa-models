# External web research intake

`research-intake/` is the pre-canon entry surface for external model
reconnaissance. It preserves useful, incomplete, contradictory, and historical
web evidence before an exact owner fact, study, or claim exists.

A valid packet is not owner truth. It cannot route or activate a model, prove
fit or safety, establish runtime currentness, satisfy an eval verdict, or enter
the model-fit query.

After the first four materially different runs, the repository also supports
bounded mechanical capture and refresh. The automation creates immutable
pre-canon candidates and review receipts; it does not discover sources,
interpret truth, edit a `ReconRun`, or promote evidence.

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
See [AOA-MODELS-D-0007](decisions/AOA-MODELS-D-0007-bound-research-automation-to-immutable-pre-canon-artifacts.md)
for the bounded automation decision.
See [AOA-MODELS-D-0008](decisions/AOA-MODELS-D-0008-generate-source-dossiers-from-retained-research-history.md)
for the generated cross-run source-history decision.

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
  ├─ search_probe[] (optional coverage and negative-search ledger)
  └─ lineage + revisit triggers
```

Local source, observation, cluster, tension, and pressure IDs are unique inside
the packet. A cross-run supersession uses a qualified run plus observation ref.
Old packets remain readable; a newer observation links to history instead of
rewriting it.

`search_probes` make the search itself inspectable without imposing a source
quota. A probe records one question, query variants, source roles sought,
capture time, retained source and observation refs, limitations, and the next
action. Its result distinguishes qualified or mixed evidence, weak signals,
bounded failure to find a qualified source, access limits, and deliberate
deferral. `no_qualified_source_found` is a statement about the recorded search
scope and time, never proof that evidence does not exist. Older packets do not
need probes.

Mechanical automation uses three separate flat routes:

```text
research-intake/capture-snapshots/       ResearchCaptureSnapshot
research-intake/change-receipts/         ResearchChangeReceipt
research-intake/supersession-proposals/  ResearchSupersessionProposal
```

These artifacts use
`schemas/research-automation-artifact.schema.json`. They remain outside
`source/` and cannot be direct canonical evidence. A repository-retained
receipt resolves both local snapshots by ID and digest; a retained proposal
resolves both local recon runs and observations by digest.

When a method or predecessor artifact has a repository-local `ref` and a
`content_digest`, validation resolves it. ReconRun predecessors use the printed
JSON-canonical digest; other local files use the SHA-256 digest of their bytes.
This keeps method and lineage references from silently drifting after review.

The schema is `schemas/recon-run.schema.json`. Semantic rules are implemented
in `scripts/research_intake_contract.py` and exercised through the normal owner
validator.

## Fast source-dossier loop

Retained `source_captures` are already the source visits. Do not duplicate them
into a manually maintained dossier. The deterministic builder joins their
history with retained capture snapshots, change receipts, and supersession
proposals into `generated/research-source-dossiers.json`.

Before citing or revisiting a source, query by exact URI, dossier ID, title,
publisher, or origin group:

```bash
python -B scripts/query_research_source_dossiers.py \
  https://example.invalid/document

python -B scripts/query_research_source_dossiers.py example-publisher

python -B scripts/query_research_source_dossiers.py --attention
```

The result exposes all retained appearances and observation refs, currentness
posture, segment-digest posture, capture history, change receipts, metadata
variation, and supersession review. It deliberately sets
`freshness_asserted=false`: the newest recorded event is not proof that the
external surface is still current.

The source identity is conservative. Scheme and authority are lowercased, an
empty path becomes `/`, and URI fragments are removed because they select a
location inside one retrieved surface. Path case, trailing slash, and query
remain identity-bearing. Different URIs are not automatically aliased even if
their content or titles match; that equivalence requires review.

For each research pass:

1. Query the likely source before adding it, so earlier segments, observations,
   caveats, and pending review remain visible.
2. Add new evidence to a `ReconRun`; use bounded capture or refresh only when
   the question needs retained currentness/change evidence.
3. Rebuild with `python -B scripts/build_research_source_dossiers.py`.
4. Validate with `python -B scripts/validate_research_intake.py`.

Only touched or question-relevant sources need a live revisit. Rebuilding the
catalog performs no network retrieval and does not expand the source set. The
validator compares the generated bytes to all retained inputs, so a pass cannot
silently leave an edited source dossier stale.

The attention view is intentionally narrow. A single mutable citation without
a snapshot remains visible as `mutable_metadata_only`, but does not flood the
queue. Attention appears when a mutable source is reused without a snapshot,
any reused source has incompletely digested segments, metadata classifications
conflict, a snapshot segment has a gap, a change requires review, or a
supersession proposal exists.

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
countersearch, and next disposition are reviewable. For a materially searched
gap, preserve a `search_probe` so the next pass can continue rather than repeat
an invisible search.

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

When research crosses training, conversion, quantization, serving, or an
accelerated path, preserve the causal artifact chain rather than treating its
last filename as the subject:

```text
training recipe -> checkpoint -> representation -> conversion -> runtime
  -> loaded process/cache policy -> workload outcome
```

Bind measurements to their semantic namespace and denominator. File bytes,
weight tensors, resident process memory, peak process memory, and full-stack
peak are different memory measures. Cold setup, conversion, repack, warmup,
prefill, decode, time-to-first-token, and end-to-end latency are different time
measures. Throughput needs concurrency, input/output length, batching, and
cache policy; energy needs the integration interval, token count, and whether
idle power was removed.

For a named score whose implementations can differ, retain a metric passport:
reference and candidate, corpus, positions or response unit, direction,
reduction, masking, precision, decoding, and instrument revision. A shared
label such as `KL`, `ASR`, `WER`, or `ROUGE` is not sufficient for cross-study
comparison.

For adapted deployment, inspect parity across the stages that actually exist:
base, adapter, merged artifact, quantized artifact, served path, and accelerated
target/drafter pair. Loader acceptance is not semantic parity. Preserve
release state separately as announced, listed, retrievable, loadable,
executable, semantically accepted, benchmark-retained, and independently
rerun.

Negative research remains bounded. Record the searched question, variants,
source roles, interval, access limits, and next action in a `search_probe`.
Failure to find unseen-schema, privacy, long-context, or another requested
evaluation in that scope is a continuation handle, never evidence of absence.

### 9. Validate

Run from the repository root:

```bash
python -B scripts/validate_research_intake.py
python -B scripts/validate_models.py
python -B scripts/build_research_source_dossiers.py --check
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

## Bounded automation flow

The command entrypoint is `scripts/research_intake.py`. It has three
subcommands and never overwrites an existing output path.

### Capture one source segment

`capture-source` consumes a data request rather than provider-specific flags.
The request carries ordinary source metadata, one locator, media expectation,
timeout, and byte bound. For example:

```json
{
  "schema_version": "aoa_model_research_capture_request_v1",
  "source": {
    "source_id": "source-example",
    "title": "Bounded source title",
    "uri": "https://example.invalid/document",
    "source_class": "primary_documentation",
    "publisher": "example-publisher",
    "published_at": null,
    "updated_at": null,
    "effective_interval": null,
    "temporal_notes": "No separate effective interval is asserted.",
    "mutable_surface": true,
    "origin_group": "example-origin",
    "propagation_role": "origin",
    "dependency_refs": [],
    "access_notes": "Public web surface.",
    "selection_context": "Selected for one bounded research question."
  },
  "segment": {
    "segment_id": "bounded-section",
    "locator": {
      "kind": "html_id",
      "value": "bounded-section"
    }
  },
  "retrieval": {
    "media_type": "auto",
    "max_bytes": 2097152,
    "timeout_seconds": 20
  }
}
```

Run a live bounded retrieval with:

```bash
python -B scripts/research_intake.py capture-source \
  --request work/capture-request.json \
  --output research-intake/capture-snapshots/source-example-20260830.json
```

For deterministic replay from retained input bytes, add both execution-only
arguments:

```bash
--input-file work/source-example.html \
--input-ref external-input:source-example.html
```

The local path is not copied into the artifact. `input_ref` is the portable
provenance label. A missing input, HTTP error, failed locator, duplicate HTML
ID, truncated document, or line range beyond the available document becomes an
explicit unavailable, missing, or partial state. Recording that state is a
successful capture operation; it is not evidence that the segment exists.

The initial generic locator set is:

- `whole_document` with `value: null`;
- `line_range` with one-based inclusive `start` and `end`;
- `json_pointer` using RFC 6901 token escaping;
- `html_id` using one element ID.

Media type, source class, publisher, provider, family, and model remain request
data. Do not add a named-site or named-model branch when a generic locator or
media distinction is missing. One capture is contract-bounded to at most 16
MiB and a timeout no longer than 120 seconds; lower per-source values remain
ordinary request data.

### Refresh without overwriting history

`refresh-capture` reuses the exact request stored in the previous snapshot. It
requires a later capture timestamp, creates a new snapshot, and separately
creates a change receipt:

```bash
python -B scripts/research_intake.py refresh-capture \
  --previous research-intake/capture-snapshots/source-example-20260830.json \
  --snapshot-output research-intake/capture-snapshots/source-example-20260902.json \
  --receipt-output research-intake/change-receipts/source-example-20260902.json
```

The classifier retains these distinctions:

| Classification | Meaning | Automatic semantic effect |
| --- | --- | --- |
| `unchanged` | document and selected segment are stable | none |
| `document_changed_segment_stable` | surrounding document changed; selected segment did not | none |
| `presentation_changed` | raw segment changed; normalized segment stayed stable | none |
| `content_changed` | normalized selected content changed | none; review required |
| `segment_became_missing` / `segment_restored` | locator availability changed | none; review required |
| `source_unavailable` / `source_recovered` / `unavailable_persists` | retrieval availability changed or remained absent | none; retry or review |
| `incomparable` | available evidence cannot support a narrower class | none |

Normalization is a comparison aid, never a replacement for the raw digest or
a claim of semantic equivalence. The receipt always sets
`automatic_supersession=false`.

### Package a supersession review proposal

`suggest-supersession` consumes two exact observations already present in
local `ReconRun` packets. It does not edit either packet:

```bash
python -B scripts/research_intake.py suggest-supersession \
  --prior-run research-intake/recon-runs/prior-run.json \
  --prior-observation observation-prior \
  --candidate-run research-intake/recon-runs/candidate-run.json \
  --candidate-observation observation-candidate \
  --relation narrowing \
  --scope-dimension observed_interval \
  --scope-dimension product \
  --rationale "The later observation narrows the supported product and time scope." \
  --ambiguity "The exact runtime subject remains unavailable." \
  --output research-intake/supersession-proposals/candidate-vs-prior.json
```

Relations are `update`, `narrowing`, `contradiction`, or `independent`.
`update` and `narrowing` require the same target kind, at least one shared
subject-identity dimension, and a candidate interval that does not predate the
prior observation. These are admission checks for review, not acceptance. The
proposal records structural overlap, conflicts, temporal relation, source
segments, counterevidence refs, rationale, and ambiguities with
`review_required=true`, `automatic_application=false`, and
`mutation_policy=no_source_or_recon_run_mutation`.

If review accepts a qualified supersession, edit the later `ReconRun` through
the normal owner-source route and validate it. Do not treat the proposal file
as the accepted edit.

### What stays temporary

Request manifests, offline input files, trial outputs, browser snapshots,
adapter experiments, corpus-specific dedup tables, and one-off load checks are
working material by default. Keep them outside the three flat retained routes
and remove them when the run or goal closes.

Only generic contracts stay permanent: output immutability, content digests,
locator behavior, partial and unavailable states, predecessor history, change
classification, qualified observation refs, authority denial, and
non-mutation. Current URLs, page text, prices, model names, source counts, and
one campaign's filenames are not durable test assertions.

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
multi-provider data acceptance. Source-dossier tests protect deterministic URI
identity, cross-run joining, freshness denial, automation-history joining, and
generated-currentness. They do not freeze today's corpus.

Do not retain permanent tests for:

- one migration's exact record counts or filenames;
- current external URLs, prices, scores, aliases, or leaderboard positions;
- one-off extraction scripts or browser snapshots;
- temporary downloads, dedup tables, or corpus-specific assertions.

If a working check reveals a recurring invariant, rewrite it as a small generic
test and remove the one-off helper before closing the goal that created it.

## Why bounded automation is not a crawler

The first packets stabilized enough mechanical semantics to automate bounded
capture, refresh, and proposal packaging. Source discovery and selection remain
researcher-owned. No scheduler chooses revisit cadence, no crawler expands the
source set, no scalar ranks source classes, no recurrence threshold creates
consensus, and no proposal writes an observation. Those later contours require
their own evidence and owner decision.
