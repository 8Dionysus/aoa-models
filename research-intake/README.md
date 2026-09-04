# Research intake

This directory contains pre-canon external web-reconnaissance material.

- `recon-runs/` contains schema-validated `ReconRun` packets.
- `reports/` contains bounded human research reports and method notes paired
  with packets.
- `capture-snapshots/` may retain reviewed immutable segment-capture candidates.
- `change-receipts/` may retain classified refresh comparisons that resolve
  both snapshots.
- `supersession-proposals/` may retain review-only relationships that resolve
  both source observations without editing them.

Nothing here is a `ModelClaim`, accepted `ModelStudy`, proof verdict, runtime
currentness fact, fit-query input, route, activation, or owner acceptance.

Cross-run lookup is generated at
[`generated/research-source-dossiers.json`](../generated/research-source-dossiers.json).
It is not another authored source store: each dossier is rebuilt from the
retained routes above and groups only the same exact normalized URI. Query it
before reusing a source:

```bash
python -B scripts/query_research_source_dossiers.py <URI-or-text>
```

After changing a retained run or automation artifact, rebuild the catalog with
`python -B scripts/build_research_source_dossiers.py`. The normal validator
rejects a missing or stale catalog.

Read [`docs/RESEARCH_INTAKE.md`](../docs/RESEARCH_INTAKE.md) before adding a run
and validate with:

```bash
python -B scripts/validate_research_intake.py
python -B scripts/build_research_source_dossiers.py --check
```

Bounded capture and refresh use `python -B scripts/research_intake.py`. Request
manifests, offline inputs, exploratory outputs, and one-off adapter trials are
working material and do not belong in these retained routes by default.

## Current manual corpus

The initial corpus deliberately spans different pressures instead of repeating
one provider-shaped fixture:

- [`GPT-5.6 v0.2 seed`](recon-runs/gpt-5.6-2026-08-29-v0.2.json) normalizes
  the pilot and deep dossier into the first packet.
- [`GPT-5.6 temporal drift`](reports/gpt-5.6-temporal-drift-2026-08-30.md)
  tests segment-level currentness, correction, product-time identity, and
  dependent restatement.
- [`Claude 5 persistence under authority`](reports/claude-5-persistence-under-authority-2026-08-30.md)
  tests a different provider/family plus model, product, runtime, transport,
  observability, and delegated-acceptance boundaries.
- [`Cross-provider outcome economics`](reports/cross-provider-outcome-economics-2026-08-30.md)
  tests common-instrument comparison, effort frontiers, denominators,
  instrument discontinuity, and excluded operational cost.
- [`Gemma 4 E2B/E4B deep dossier`](reports/gemma-4-e2b-e4b-web-recon-deep-dossier-2026-08-30.md)
  pairs a temporal lineage/footprint packet with a separate operating-points
  packet. It tests PLE effective-versus-retained parameter language, memory
  denominators, bounded Gemma 3n inheritance, MTP amortization, energy and
  device Pareto regions, usable-versus-nominal context, runtime attribution,
  and subject-metadata audit without promoting either size.
- [`Gemma 4 E2B/E4B corroboration`](reports/gemma-4-e2b-e4b-corroboration-2026-09-04.md)
  adds independent agentic, clinical, audio, Raspberry Pi, Apple Silicon, and
  MTP evidence. It preserves metric-level E2B inversions inside otherwise
  E4B-favorable instruments, strengthens the recurring E2B resource direction,
  exposes an MTP backend sign flip, and separates nominal, allocated,
  completed, and semantically usable context. Its paired
  [`ReconRun`](recon-runs/gemma-4-2026-09-04-e2b-e4b-corroboration.json) remains
  pre-canon.

The Gemma 4 run also retains nine immutable, locator-bounded capture snapshots
for release-history segments, memory-table/caveat segments, and exact current
E2B/E4B base/IT registry responses. They are refresh anchors, not archived page
bodies, scheduled watches, or canonical evidence.

The later PLE issue state is linked to the earlier open-state observation by a
review-only
[`ResearchSupersessionProposal`](supersession-proposals/gemma4-ple-offload-status-20260904.json).
No `ResearchChangeReceipt` is claimed because the mutable issue did not have a
prior retained locator-bounded snapshot. The proposal neither edits the source
runs nor interprets stale closure as supported PLE offload.

The current lens is
[`External Model Web Recon v0.3`](reports/external-model-web-recon-method-v0.3.md).
These records prove that the contour can preserve materially different web
evidence as data; they do not prove that the ontology is complete.

The bootstrap validation and temporary-surface cleanup are recorded in the
[`execution receipt`](reports/web-recon-bootstrap-execution-2026-08-30.md).
The bounded automation contour, generic demonstrations, and working-surface
cleanup are recorded separately in the
[`automation bootstrap receipt`](reports/research-automation-bootstrap-2026-08-30.md).
