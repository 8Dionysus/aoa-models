# AGENTS.md

## Orientation

`aoa-models` owns empirical, configuration-scoped model knowledge. Before
editing, identify the exact realization, evidence modality, observation
interval, lifecycle transition, and consumer that motivated the change.

Do not turn a convenient model nickname into source truth. Model, effort,
runtime, access regime, context, tools, environment, and permissions remain
separate fields.

External web evidence belongs in `research-intake/` until a separate owner
review establishes a canonical fact, study, or claim. A valid recon packet is
pre-canon structure, not proof or fit evidence.

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

1. Start with `DIRECTION.md` and the nearest schema or decision law.
   `README.md` remains the human/public map when scope or owner routing is
   unclear; it is not an unconditional edit prerequisite.
2. Preserve the distinction between provider fact, runtime observation,
   behavioral evidence, task outcome, internal-space measurement, causal
   intervention, training-lineage evidence, and bounded inference.
3. Add or change owner source first.
4. Rebuild generated projections with their builder; never hand-edit them.
5. Run the affected semantic validator and unit tests.
6. Hand activation, runtime, proof, acceptance, publication, and external
   effects to their stronger owners.

For web research, preserve source segments, origin dependencies, instrument
revision, configuration gaps, counterevidence, and transfer limits. Do not feed
research-intake paths into `query_model_fit.py` or canonical source evidence.

Bounded research automation may retrieve one declared segment, create a new
snapshot, classify change, or package a review proposal. It must refuse output
overwrite, preserve unavailable and partial states, bind local retained refs by
digest, and leave `ReconRun` and canonical source unchanged. Provider, model,
publisher, URL, and source class remain data; broad crawling, ranking,
consensus, scheduling, and automatic supersession are outside this contour.

## Claim lifecycle

The supported lifecycle is:

`hypothesis -> observed -> reviewed -> weakened|stale|superseded|retracted`

Not every claim must reach `reviewed`. Promotion requires evidence appropriate
to the modality and an independent review reference. `weakened`, `stale`,
`superseded`, and `retracted` preserve history and must name their transition
reason; semantic history is not rewritten silently.

## Validation

Run the model validation route in `VALIDATION.md` on demand.

## Stop lines

Stop before claiming or writing when:

- the exact realization or observation interval is unknown;
- a claim would infer closed-model training data or internal geometry from
  behavior alone;
- a proof verdict would be copied or reinterpreted instead of referenced;
- a model-fit projection would become a routing or activation decision;
- a pre-canon web observation would be promoted without a separate owner
  review and the evidence required by the target source object;
- the change needs runtime, host, secret, global configuration, publication,
  or external-effect authority;
- safe work would overwrite unrelated dirty changes.
