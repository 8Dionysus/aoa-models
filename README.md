# aoa-models

> Current release: `v0.1.0`. See [CHANGELOG](CHANGELOG.md) for release notes.

`aoa-models` is the AoA source owner for configuration-scoped, lifecycle-aware
knowledge about model realizations. It records what was actually observed,
under which model, runtime, access, effort, tool, context, environment, and
permission configuration, and how each bounded claim changes over time.

The repository is an experimental owner organ. It does not launch models,
choose routes, define agent roles, issue proof verdicts, or accept a landing.

External web reconnaissance enters through a separate pre-canon
`research-intake/` surface. Its validated packets preserve source segments,
origin dependencies, incomplete configurations, contradictions, and revisit
triggers without becoming model source truth or fit-query input. See
[`docs/RESEARCH_INTAKE.md`](docs/RESEARCH_INTAKE.md).
The manual corpus includes a GPT-5.6 seed and temporal recheck, a
different-provider Claude 5 persistence run, a cross-provider outcome-
economics run, and a layered Gemma 4 E2B/E4B investigation covering lineage,
operating points, independent corroboration, fine-tuning/adapters, QAT and
deployment, safety geometry, distillation, multilingual adaptation, modality
composition and stripping, and qualified negative searches;
[`research-intake/README.md`](research-intake/README.md) indexes the packets,
reports, and bounded capture anchors.

The current v0.5 web-recon lens also retains optional search coverage and
bounded negative-search results. It separates scorer from mechanism, training
proxy from held-out selection, multimodal execution from silent tower bypass,
artifact load from served semantic effect, and an adapted target from its
exact MTP-drafter pair. It additionally binds deployment claims to a causal
artifact chain, explicit measurement namespaces, metric passports, release
states, distillation lineage, and base-to-accelerated lifecycle parity. These
remain pre-canon research objects and do not create a model ranking or
automatic promotion path.

The first bounded automation contour can capture one structured source segment,
refresh it into an append-only change receipt, and package a content-addressed
supersession proposal for review. It does not crawl, select, rank, promote, or
mutate research or model source.

A generated source-dossier catalog makes repeated web work cheap: it joins the
same exact normalized URI across runs with its cited segments, observations,
snapshots, change receipts, metadata variants, and supersession proposals.
Agents query it before reusing a source and rebuild it after changing retained
research. The catalog is a pre-canon read model and never claims that a page is
currently fresh or that its statements are true.

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
- `ReconRun`: a pre-canon external research packet; it cannot satisfy a model
  claim, study verdict, runtime-currentness, routing, or activation requirement.
- `ResearchCaptureSnapshot`, `ResearchChangeReceipt`, and
  `ResearchSupersessionProposal`: immutable mechanical intake candidates with
  no source-mutation or automatic-application authority.
- `ResearchSourceDossier`: a generated pre-canon history view over one exact
  normalized external source URI.

The first bounded access plane is `scripts/query_model_fit.py`. It accepts
role-derived task, exact runtime-subject identity, runtime compatibility,
permission, tool, and MCP requirements and returns informational candidates
from current projections. Each v2 result binds the exact query, clean owner
source, realization/projection catalog, candidate realization and projection
bytes, matched runtime subject, and their generating fit claims or studies. A
version match without the subject source and digest is rejected. It does not
select a model, route work, grant permission, activate a runtime, or issue a
proof verdict.

The first contour describes GPT-5.6 Luna `max` and `xhigh` under the locally
observed Codex/ChatGPT access regime. Each effort has a read-only readiness/
review realization and a dedicated-worktree workspace-write preparation
realization. The latter still has network and every external effect disabled;
it describes an exact callable configuration, not permission or evidence of
fit. Behavioral fit for landing remains a hypothesis until external-process
trials and `aoa-evals` review supply evidence.

The first operational expansion adds separate Luna hypotheses for bounded
`eval`, `stats`, and `memo` duties. They admit only evidence-complete real-work
canaries under owner review; provider capability, low price, schema-valid
completion, or adjacent landing evidence does not establish role fit.

Terms such as character, temperament, subjectivity, and internal world are
valid research images for future model study. This initial schema neither
reduces them to human categories nor freezes them into final object types.

## Source and derived surfaces

- `source/` contains owner-authored identities, realizations, claims, and study
  definitions.
- `research-intake/` contains pre-canon external recon runs and their bounded
  reports, capture snapshots, change receipts, and review proposals; it is
  neither `source/` nor accepted evidence.
- `schemas/` defines their machine-readable contracts.
- `generated/` contains rebuildable model-fit projections, indexes, and the
  research-source dossier catalog.
- `docs/decisions/` preserves durable owner rationale.
- `scripts/` validates sources and rebuilds derived views.
- `tests/` proves the local lifecycle and source/derived guards.

## Validation

Use the on-demand repository [validation route](VALIDATION.md) for model,
research-intake, projection, live-catalog, decision-index, and test checks.

The external Luna runtime, incarnation binding, and proof packets live in
their stronger owners. See [HANDOFFS.md](HANDOFFS.md) for those routes and
[DIRECTION.md](DIRECTION.md) for the intentionally narrow first horizon.
