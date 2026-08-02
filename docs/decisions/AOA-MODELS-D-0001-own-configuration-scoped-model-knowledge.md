# Own configuration-scoped model knowledge in a separate organ

## Status

Accepted for the owner-local experimental repository. Ecosystem registration
and runtime admission remain pending proof in their stronger owners.

## Index metadata

- Decision ID: AOA-MODELS-D-0001
- Original date: 2026-08-01
- Owner facets: owner-boundary, model-realization, claim-lifecycle, consumer-projection
- Posture: accepted-owner-local

## Context

AoA needs to choose and study model configurations for bounded work without
equating an agent role with a model brand or treating informal experience as
durable truth. Existing owners cover roles, dispatch, proof, runtime, host fit,
memory, and derived statistics, but none owns a cross-runtime record of the
exact configuration under which a model property was observed and how that
claim later weakens, becomes stale, is superseded, or is retracted.

The immediate pressure is to study GPT-5.6 Luna `max` and `xhigh` for the long
landing tail while preserving a future research line into model character,
temperament, internal spaces, and persistent agent life. Those research images
must remain open rather than being frozen into the first data model.

If this rationale existed only in a commit or runtime adapter, a future reader
would lose why model knowledge is a separate owner class, why realization
scope is mandatory, and why activation and verdict authority are deliberately
excluded.

## Contract-gap map

| Existing owner | Existing authority | Gap kept outside it | Handoff from `aoa-models` |
| --- | --- | --- | --- |
| `aoa-agents` | role, mandate, tier requirements, stop-line | empirical truth about a model configuration | fit projection reference only; no role-to-brand equation |
| `aoa-sdk` | dispatch ABI, runtime-neutral plan, lifecycle client | model-claim authorship and process execution | realization reference for an incarnation binding |
| `aoa-evals` | fixtures, scoring, comparison, verdict meaning | model catalog and claim lifecycle | study/result references; verdict is never copied |
| `abyss-stack` | launch, process/session state, runtime receipt | role meaning, model-fit truth, proof | exact realization input; runtime receipt returned |
| `abyss-machine` | host facts and machine policy | cross-runtime model meaning | host-fit reference when relevant |
| `aoa-memo` | reviewed durable memory | live model source and automatic trial writeback | explicit reviewed intake candidate only |
| `aoa-stats` | derived usage, cost, latency, movement | source facts and acceptance | measurement event/reference only |
| `Agents-of-Abyss` | organ law, federation, center registry | owner-local model records | registration request only after useful proof |

The missing link is therefore paired rather than monolithic:

1. this repository owns exact model knowledge and consumer projections;
2. `aoa-sdk` binds a role/task reference to one model realization;
3. `abyss-stack` gives that binding an external process and durable session;
4. `aoa-evals` independently judges the resulting claim.

## Options considered

- Keep model-fit notes inside `aoa-agents`. This would blur normative role
  requirements with empirical and time-bounded model observations.
- Expand `abyss-stack` runtime model cards into the general owner. This would
  turn host/backend-fit projections into cross-runtime model truth and mix
  process evidence with claim authority.
- Delay ownership until a full internal-space laboratory is designed. This
  would postpone the immediately useful Luna contour and encourage more
  unversioned model folklore.
- Create a minimal separate `aoa-models` owner now, while keeping runtime,
  proof, routing, role, and center acceptance external.

## Decision

Create `aoa-models` as the source owner for exact model identity and
realization records, configuration-scoped claims and their lifecycle,
reproducible model-study definitions and result references, and generated
model-fit projections.

A realization is scoped by model/version, provider and access mode,
billing/quota regime, Codex/runtime version, reasoning effort, context regime,
tool and MCP surface, prompt/environment, permissions, and observation
interval. A projection may inform a consumer but cannot choose a route,
activate a process, issue a proof verdict, accept a landing, or authorize an
effect.

The first source records cover Luna `max` and `xhigh` in the observed local
Codex/ChatGPT regime. Landing suitability remains a hypothesis until fixed
trials, independent review, and `aoa-evals` evidence justify a narrower claim.
Model studies own an observe-only usage policy: they count actual usage and
initiative but do not impose predeclared token, time, turn, output, or cost
ceilings. Provider limits and operator interruption remain evidence rather
than model-organ budgets.

## Rationale

This boundary gives a volatile empirical object its own currentness and
counterevidence lifecycle without forcing adjacent owners to absorb a second
authority. It also lets future internal-space studies strengthen or overturn
behavioral claims while retaining modality and attribution limits.

The separate repository is justified by a distinct object of truth, not by a
preference for more repositories. Keeping the first contour small prevents it
from becoming a launcher, scheduler, universal A2A ontology, database, MCP
service, or proof system before evidence requires those forms.

## Consequences

- Model claims become addressable, realization-scoped, and reversible rather
  than informal brand-level beliefs.
- Consumers gain compact projections without receiving source or acceptance
  authority.
- Every useful runtime route crosses explicit owner handoffs and therefore
  carries more references than a single monolithic config.
- Provider facts, runtime observations, behavioral outcomes, internal-space
  measurements, causal interventions, and training-lineage evidence stay
  distinguishable.
- The initial schema may be superseded as real studies reveal missing
  dimensions; it is not a final ontology of artificial individuality.
- Remote repository creation, center registration, runtime admission, and all
  external effects remain separate decisions or approvals.

## Source surfaces

- `README.md`
- `AGENTS.md`
- `DIRECTION.md`
- `HANDOFFS.md`
- `schemas/`
- `source/`
- `generated/`

## Follow-up route

Implement and validate the first Luna realization and study contour here;
then hand typed incarnation binding to `aoa-sdk`, external process/session
execution to `abyss-stack`, and comparison/verdict work to `aoa-evals`.
Request center registration only after owner-local practical proof.

## Verification

- `python scripts/generate_decision_index.py --check`
- `python scripts/validate_models.py`
- `python scripts/build_model_fit_projections.py --check`
- `python -m unittest discover -s tests -v`

Remote GitHub currentness was inspected through the connected GitHub surface
because shell DNS was unavailable. No remote repository, branch, PR, merge,
release, runtime, or public surface was created by this decision.
