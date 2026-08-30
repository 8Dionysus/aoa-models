# Research-intake automation bootstrap

- Date: 2026-08-30
- Owner: `aoa-models`
- Baseline: `8fc785ee86a9207c920aeaa928b8c6a05a10b4de`

Posture: implementation and local-validation receipt; not proof, deployment,
external-currentness, or owner acceptance

## Objective

Automate the repeated mechanical work exposed by the first four web-recon runs
without automating source discovery, semantic judgment, consensus, promotion,
or source mutation.

The resulting contour has three commands:

```text
capture-source       -> immutable ResearchCaptureSnapshot
refresh-capture      -> new snapshot + ResearchChangeReceipt
suggest-supersession -> ResearchSupersessionProposal requiring review
```

AOA-MODELS-D-0007 records why these effects are admissible beneath the
pre-canon boundary established by AOA-MODELS-D-0006.

## Generality demonstrations

The permanent contract suite uses temporary inputs and output roots so the
repository does not retain fabricated web evidence or campaign-specific
fixtures.

| Source/locator class | Temporal or failure outcome | Durable invariant exercised |
| --- | --- | --- |
| text/Markdown `line_range` | captured; raw whitespace change with normalized content stable | exact extracted digest remains separate from `presentation_changed` normalization evidence |
| structured JSON `json_pointer` | selected value changes | refresh binds predecessor and emits `content_changed` with review required |
| HTML `html_id` | selected element disappears | new snapshot preserves `missing`; receipt emits `segment_became_missing` |
| bounded HTTP response | redirected effective URI and response metadata retained | transport, status, media type, ETag, final URI, and document digest remain reviewable |
| unavailable offline input | retrieval and segment unavailable | absence is an explicit valid candidate state rather than silence |
| two content-addressed recon observations | update proposal admitted or unrelated-subject update rejected | proposal cannot mutate either run and cannot cross subject identity on product overlap alone |

An end-to-end subprocess test invokes `capture-source`, then
`refresh-capture`, verifies a content-change receipt, invokes the first command
again against the same output, and proves overwrite refusal leaves the original
bytes unchanged.

## Durable checks retained

Permanent tests protect:

- request resource bounds and structured-locator validity;
- generic text, JSON, HTML, HTTP, partial, missing, and unavailable behavior;
- raw and normalized digest separation;
- artifact self-digests and copy-ready `SourceCapture` candidates;
- append-only output and predecessor history;
- recomputation of change classification from exact snapshots;
- qualified run and observation digests;
- update/narrowing subject and temporal admission;
- review-only, no-mutation, and no-automatic-application authority.

No permanent test names a real provider, model, current URL, price, score,
leaderboard position, source count, or one campaign artifact.

## Working checks removed by construction

Adapter inputs, request manifests, generated snapshots, receipts, proposals,
and CLI trial directories are created under `tempfile` roots and removed by the
test harness. No migration helper, downloaded page, browser cache, corpus
deduplication table, or task-local generated artifact is retained.

The declared repository routes therefore contain zero automation artifacts at
bootstrap. This is intentional: the implementation is landed without
pretending its synthetic contract trials are web evidence. A future real
capture enters a retained route only after source selection and review.

## Local validation

The implementation branch passed:

- `python -B scripts/validate_research_intake.py`;
- `python -B scripts/validate_models.py`;
- `python -B scripts/build_model_fit_projections.py --check`;
- `python -B scripts/generate_decision_index.py --check`;
- `python -B -m unittest discover -s tests -v` — 50 tests;
- Ruff on every changed Python and test path;
- `git diff --check`.

The owner validator reports the original four runs, 83 source captures, 77
observations, and 25 clusters, plus zero retained capture snapshots, change
receipts, and supersession proposals. The zero counts do not mean the commands
were untested; they preserve the distinction between contract proof and real
research evidence.

Repository-wide Ruff still exposes the pre-existing unused `subprocess` import
in `scripts/release_publish.py`; that unchanged release path is outside this
goal and was not silently repaired.

## Claim limits

This receipt establishes only the implemented source contract and local test
result. It does not establish live external retrieval at another time, model or
runtime currentness, a semantic supersession, a canonical model claim, an eval
verdict, routing, activation, deployment, publication, or human acceptance.

Normal GitHub review, CI, source landing, and landed-commit validation are
separate closure evidence and are not asserted by this pre-landing receipt.
