# aoa-models

`aoa-models` is the AoA source owner for configuration-scoped, lifecycle-aware
knowledge about model realizations. It records what was actually observed,
under which model, runtime, access, effort, tool, context, environment, and
permission configuration, and how each bounded claim changes over time.

The repository is an experimental owner organ. It does not launch models,
choose routes, define agent roles, issue proof verdicts, or accept a landing.

## Owner boundary

| Relation | This repository |
| --- | --- |
| owns | exact model identities and realizations; configuration-scoped model claims; claim provenance, currentness, and lifecycle; model-study definitions and result references; derived model-fit projections |
| routes | role requirements to `aoa-agents`; routing and incarnation binding to `aoa-sdk`; proof to `aoa-evals`; process truth to `abyss-stack`; host fit to `abyss-machine`; reviewed memory to `aoa-memo`; derived measurements to `aoa-stats` |
| receives | provider facts; live runtime observations; bounded behavioral studies; eval verdict references; runtime receipts; reviewed internal-space studies when those later exist |
| hands off | activation; routing decisions; runtime execution; proof verdicts; owner acceptance; publication; and every external effect |

## First object contour

- `ModelIdentity`: stable provider, family, version, or snapshot identity.
- `ModelRealization`: one exact access and execution configuration.
- `ModelClaim`: one bounded, evidenced assertion with currentness and lifecycle.
- `ModelStudy`: a reproducible protocol with fixed arms and attribution limits.
- `ModelFitProjection`: a generated consumer view that cannot authorize use.

The first contour describes GPT-5.6 Luna `max` and `xhigh` under the locally
observed Codex/ChatGPT access regime. Each effort has a read-only readiness/
review realization and a dedicated-worktree workspace-write preparation
realization. The latter still has network and every external effect disabled;
it describes an exact callable configuration, not permission or evidence of
fit. Behavioral fit for landing remains a hypothesis until external-process
trials and `aoa-evals` review supply evidence.

Terms such as character, temperament, subjectivity, and internal world are
valid research images for future model study. This initial schema neither
reduces them to human categories nor freezes them into final object types.

## Source and derived surfaces

- `source/` contains owner-authored identities, realizations, claims, and study
  definitions.
- `schemas/` defines their machine-readable contracts.
- `generated/` contains rebuildable model-fit projections and indexes only.
- `docs/decisions/` preserves durable owner rationale.
- `scripts/` validates sources and rebuilds derived views.
- `tests/` proves the local lifecycle and source/derived guards.

## Validation

Run from the repository root:

```bash
python scripts/validate_models.py
python scripts/build_model_fit_projections.py --check
python scripts/generate_decision_index.py --check
python -m unittest discover -s tests -v
```

The external Luna runtime, incarnation binding, and proof packets live in
their stronger owners. See [HANDOFFS.md](HANDOFFS.md) for those routes and
[DIRECTION.md](DIRECTION.md) for the intentionally narrow first horizon.
