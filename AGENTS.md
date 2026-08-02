# AGENTS.md

## Orientation

`aoa-models` owns empirical, configuration-scoped model knowledge. Before
editing, identify the exact realization, evidence modality, observation
interval, lifecycle transition, and consumer that motivated the change.

Do not turn a convenient model nickname into source truth. Model, effort,
runtime, access regime, context, tools, environment, and permissions remain
separate fields.

## Authority

- Owner-authored records under `source/` are the local source of model meaning.
- Schemas constrain record shape; they do not prove a claim.
- Generated projections under `generated/` are rebuildable consumer views and
  never authorize activation, routing, acceptance, or external effects.
- `aoa-evals` owns proof bundles and verdict meaning.
- `aoa-sdk` owns routing and runtime-neutral incarnation binding.
- `abyss-stack` owns process execution, session persistence, and runtime
  receipts.
- The human operator remains the only human authority.

## Mutation route

1. Read `README.md`, `DIRECTION.md`, and the nearest schema or decision law.
2. Preserve the distinction between provider fact, runtime observation,
   behavioral evidence, task outcome, internal-space measurement, causal
   intervention, training-lineage evidence, and bounded inference.
3. Add or change owner source first.
4. Rebuild generated projections with their builder; never hand-edit them.
5. Run the affected semantic validator and unit tests.
6. Hand activation, runtime, proof, acceptance, publication, and external
   effects to their stronger owners.

## Claim lifecycle

The supported lifecycle is:

`hypothesis -> observed -> reviewed -> weakened|stale|superseded|retracted`

Not every claim must reach `reviewed`. Promotion requires evidence appropriate
to the modality and an independent review reference. `weakened`, `stale`,
`superseded`, and `retracted` preserve history and must name their transition
reason; semantic history is not rewritten silently.

## Validation

```bash
python scripts/validate_models.py
python scripts/build_model_fit_projections.py --check
python scripts/generate_decision_index.py --check
python -m unittest discover -s tests -v
```

## Stop lines

Stop before claiming or writing when:

- the exact realization or observation interval is unknown;
- a claim would infer closed-model training data or internal geometry from
  behavior alone;
- a proof verdict would be copied or reinterpreted instead of referenced;
- a model-fit projection would become a routing or activation decision;
- the change needs runtime, host, secret, global configuration, publication,
  or external-effect authority;
- safe work would overwrite unrelated dirty changes.
