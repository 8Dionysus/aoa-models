# Web-recon intake bootstrap execution and cleanup receipt

Статус: owner-local implementation validated; review, CI and source landing
recorded below as separate claims

Baseline: `main@5bcbea1` = `origin/main@5bcbea1`, clean before mutation

Рабочая ветвь: `feat/external-web-recon-intake`

## Landed contour under review

Намеренная долговечная поверхность:

- accepted owner decision `AOA-MODELS-D-0006` and generated decision index;
- `ReconRun` schema plus generic semantic contract/check CLI;
- integration into the normal `validate_models.py` contour;
- direct-evidence guard between `research-intake/` and canonical model source;
- manual authoring, promotion/handoff, mutable-source and no-crawler guidance;
- normalized GPT-5.6 v0.2 seed with precursor/input digests;
- temporal drift, persistence under authority and outcome-economics runs;
- evidence-derived method v0.3 and bounded human reports;
- synthetic generic tests plus validation of the real corpus.

No `ModelIdentity`, `ModelRealization`, `ModelClaim`, `ModelStudy`, generated
fit projection or fit-query input was created or changed from web evidence.

## Current packet receipt

| ReconRun | Canonical digest |
|---|---|
| `recon-run:gpt-5.6/2026-08-29-v0.2` | `sha256:4404900b111ce459faa9cc355ea559dc754f8d29c793adf26c8d605c9142118a` |
| `recon-run:gpt-5.6/2026-08-30-temporal-drift` | `sha256:e6362e42cf2ea49f59f87705559374c4b77cda01ce1b23b259c64213c79ff43d` |
| `recon-run:claude-5/2026-08-30-persistence-under-authority` | `sha256:24647cafefa2c852b7129e165b1164b007d6ee6e9cc17d28d0a8c74b26bfa641` |
| `recon-run:cross-provider/2026-08-30-outcome-economics` | `sha256:1b02d239b8e34ec622f1669e0269dd6e2d5766aea6d56efaabc1ac8a44b6420f` |

Validated corpus contour: 4 runs, 83 source captures, 77 atomic observations
and 25 clusters. These counts are a receipt for this capture, not schema or test
oracles.

## Durable versus temporary validation

The retained checks protect reusable invariants: schema/ID/reference integrity,
segment provenance, dependency lineage, independent-origin semantics,
configuration gaps, outcome-axis separation, temporal/supersession refs,
local artifact digests, generic new-provider/family acceptance, and the
pre-canon promotion boundary.

No permanent assertion names a real model/provider, URL, current price, score,
source count or packet filename as an epistemic rule.

Temporary surface created and removed:

- one-time `migrate_seed_v02.py` converter;
- one-time `author_post_seed_runs.py` data writer;
- one-time `augment_live_research.py` countersearch writer;
- `baseline.md` and `requirements-and-design.md` coordination notes;
- the complete task-local `work/aoa-models-web-recon-goal/` directory;
- bytecode for the new scripts/tests and the goal-created Ruff cache.

The bounded cleanup audit found the task-local directory and named helpers
absent. The pre-existing `.pytest_cache/`, `build/`, `scripts/__pycache__/` and
`tests/__pycache__/` paths were preserved rather than erased for appearance.

## Local validation

Executed after temporary cleanup:

- `validate_models.py` — green: 10 claims, 2 projections, 2 identities, 15
  realizations, 16 studies, 4 recon runs, 83 sources, 77 observations and 25
  clusters;
- `validate_research_intake.py` — green with the four canonical digests above;
- model-fit projection check — green, 2 projections current;
- decision-index check — green, 6 decisions current;
- full unit suite — green, 37 tests;
- Ruff on changed Python/tests with `--no-cache` — green;
- `git diff --check` — green.

## Separate currentness result

The live Codex catalog probe is red independently of research intake. Ambient
Codex is `0.150.1`; two declared active `0.149.1` realizations mismatch, and no
exact live runtime subject was supplied. This condition predates the goal and
was neither repaired nor used to weaken the research contract. The probe proves
only catalog/currentness compatibility, not runtime health, fit or acceptance.

## Automation disposition

Stable enough for later narrow automation:

- capture a selected mutable segment and compute retained bytes/digest;
- detect that a known segment changed without interpreting the change;
- suggest predecessor/supersession links for manual review;
- run the existing deterministic schema/semantic check.

Still premature:

- broad crawler or continuous monitor;
- universal source ranking or scalar confidence;
- automated atomization, contradiction resolution or independent-origin
  judgment;
- consensus-to-claim, route selection or any automatic promotion.

The manual runs still changed the method around route realization,
orientation/loop recovery, integrity coverage and quota termination. That is
evidence that discovery semantics remain too live to freeze into a crawler.

## Review, CI and landing

- Local source review: complete; generic-code hardcode scan, secret-pattern
  scan, packet summaries, lineage digests and full diff were reviewed.
- GitHub Repo Validation: pending push/PR.
- Source landing on `main`: pending ordinary repository route.
- Runtime deployment, activation and external effects: not performed and not
  authorized by this goal.
- Proof/eval verdict: not produced; `aoa-evals` remains the owner.
- Owner/human acceptance: not inferred from validation or landing.
