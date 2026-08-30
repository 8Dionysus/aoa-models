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

Read [`docs/RESEARCH_INTAKE.md`](../docs/RESEARCH_INTAKE.md) before adding a run
and validate with:

```bash
python -B scripts/validate_research_intake.py
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

The current lens is
[`External Model Web Recon v0.3`](reports/external-model-web-recon-method-v0.3.md).
These records prove that the contour can preserve materially different web
evidence as data; they do not prove that the ontology is complete.

The bootstrap validation and temporary-surface cleanup are recorded in the
[`execution receipt`](reports/web-recon-bootstrap-execution-2026-08-30.md).
The bounded automation contour, generic demonstrations, and working-surface
cleanup are recorded separately in the
[`automation bootstrap receipt`](reports/research-automation-bootstrap-2026-08-30.md).
