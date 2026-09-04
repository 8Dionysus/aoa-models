# Gemma 4 E2B/E4B: corroboration and inversion dossier

Date: 2026-09-04

Status: reviewed pre-canon research intake

Owner: `aoa-models`

Method: [External Model Web Recon Lens v0.3](external-model-web-recon-method-v0.3.md)

Predecessor: [Gemma 4 E2B/E4B deep web-recon dossier](gemma-4-e2b-e4b-web-recon-deep-dossier-2026-08-30.md)

This pass asks a narrower and harder question than the first dossier: which
E2B/E4B directions repeat across genuinely independent origins, and where does
the evidence itself show that a global family ranking would be false? It adds
controlled agentic, clinical, and audio studies; independent edge and Apple
runtime measurements; two code-bearing MTP investigations; and a currentness
review of the PLE placement issue.

The result remains research intake. It is not a `ModelClaim`, accepted
`ModelStudy`, route, runtime admission, fit verdict, proof, or Operator
acceptance.

## Strongest synthesis

1. **The resource direction is strongly repeated.** Across the predecessor's
   H100, energy, and OpenVINO evidence and three additional Raspberry Pi / MLX
   origins, E2B repeatedly occupies the lower-memory and higher-decode
   operating point. The absolute ratios are not portable; the direction is.
2. **E4B usually occupies the capability or reliability side, but not every
   endpoint.** New agentic, clinical, and audio studies place E4B ahead on most
   captured aggregate or modality-aligned outcomes. The same studies also
   expose bounded E2B wins: agentic pass-at-least-once, four-shot readmission,
   and one chain-aggregation score. These are not noise to erase; they prevent
   a false universal ordering.
3. **MTP is a realized route behavior, not a stable model multiplier.** A
   code-bearing same-machine investigation changes the sign of MTP between
   PyTorch/MPS and MLX. A second investigation changes it by task shape. Long,
   predictable or structured generation often benefits; short or creative
   generation may be neutral or slower.
4. **Execution capacity is not usable context.** One runtime benchmark reaches
   256K with both sizes, but generates only 32 tokens over repetitive filler
   and performs no semantic long-context grading. It proves allocation and
   syntactic completion on that route, not usable 256K context and not a change
   to the provider's nominal 128K contract.
5. **Source audit remains part of evidence, not a pre-filter by prestige.** One
   useful benchmark mislabels dense PLE E2B/E4B as MoE. One MTP repository's
   top-level summary emphasizes positive averages while its detailed MLX
   reports preserve systematic slowdowns. The measurements can remain useful
   after the unsupported semantic layer is isolated.
6. **The PLE issue changed state, not meaning.** Transformers issue `#47705`
   is now closed after stale automation. The original measurement survives;
   the earlier sentence saying the support question "remains open" is no
   longer current. Closure supplied neither a PLE-specific supported
   `device_map` nor a fixed-version reproduction.

## Recurrence map

| Direction | Independent support added here | Counter-pressure retained | Supported reading |
| --- | --- | --- | --- |
| E2B resource / decode advantage | Raspberry Pi llama.cpp, M5 Max MLX, M5 Max long-context MLX | Quantization, output length, runtime, and hardware differ | Treat E2B as the recurring resource-side candidate, then measure the exact realization. |
| E4B capability / reliability advantage | T1-Bench, INSPECT clinical study, AudioProcessBench | Each instrument contains at least one bounded E2B endpoint win | Treat E4B as the usual capability-side candidate, never as a universal winner. |
| MTP benefit is conditional | DGX Spark predecessor, M1 Max LiteRT-LM, M4 PyTorch/MLX | Neutral and negative rows recur | Admit MTP only with backend, assistant, task shape, output length, and acceptance evidence. |
| Nominal context differs from usable context | Provider 128K predecessor, Android failures, PLE placement, M5 Max 256K execution | No common semantic long-context grader | Keep nominal, allocated, completed, and semantically usable context as separate claims. |
| Source semantic defects can coexist with useful data | UDAE MoE label, Incept5 MoE label, MTP summary/detail conflict | Exposed code and raw tables preserve bounded measurements | Audit subject, method, comparison, and conclusion independently. |

Repeated direction is counted by independent origin, not by number of pages or
tables. A repository README and its detailed reports are one origin. A paper
and its own code are one origin. A downstream retelling adds no vote.

## Agentic reliability: T1-Bench

T1-Bench v1 evaluates multi-turn tool use across 25 domains and 76 tools, with
three stochastic trials per task. It reports both `Pass@K` (at least one trial
succeeds) and `Pass^K` (all trials succeed), which exposes a useful reliability
split:

| Metric | E2B | E4B |
| --- | ---: | ---: |
| Tool output exact match | 76.39 | 79.88 |
| Pass@3 | 56.00 | 54.67 |
| Pass^3 | 28.38 | 35.62 |
| Helpfulness | 4.63 | 4.85 |
| Coherence | 4.78 | 4.93 |

E4B is more consistent across all three runs and stronger on exact output and
judge scores. E2B has a slightly higher probability of producing at least one
successful run. A single "tool-use score" would destroy this distinction.
The paper exposes sampling parameters and trial count, but its v1 page promises
future code/data release rather than resolving a public versioned artifact;
reproduction remains incomplete.

## Clinical multimodal outcomes: INSPECT

The clinical study uses 23,248 CTPA studies from 19,402 patients, an official
patient split, eight tasks, BF16 E2B/E4B checkpoints, and fixed zero-/four-shot
protocols. Across 23,079 completed task instances, E4B is the strongest
aggregate Gemma 4 point and leads the strongly modality-aligned pulmonary
embolism diagnosis task:

| CTPA + EHR pulmonary embolism diagnosis | E2B | E4B |
| --- | ---: | ---: |
| Zero-shot AUROC | 0.8497 | 0.9683 |
| Zero-shot AUPRC | 0.5598 | 0.9084 |
| Four-shot AUROC | 0.9467 | 0.9706 |
| Four-shot AUPRC | 0.8660 | 0.9150 |

But four-shot CTPA+EHR 30-day readmission reverses locally: E2B reports AUROC
0.6141 and F1 0.2221 versus E4B at 0.5541 and 0.1791. Those absolute results
are weak and should not become a capability claim. Their value is structural:
even a study strongly favorable to E4B contains a task/prompt-conditioned
inversion.

## Audio reasoning-chain criticism: AudioProcessBench

AudioProcessBench contains 3,872 reasoning traces and 23,497 human-reviewed
steps across six error types. Its critic-model table reports:

| Metric | E2B | E4B |
| --- | ---: | ---: |
| Overall | 43.6 | 50.5 |
| Final-error identification | 24.7 | 35.5 |
| Audio-error identification | 44.2 | 54.0 |
| Error-type average | 43.4 | 55.0 |
| Chain aggregation average | 52.8 | 51.9 |

E4B's advantage is broad and large on step/error detection. E2B's 0.9-point
chain-aggregation edge is small, but it again blocks the claim that larger
effective scale monotonically improves every endpoint.

## Independent runtime recurrence

### Raspberry Pi llama.cpp

The `potato-os/core` benchmark pins its document commit and llama.cpp revision,
uses five turns at a 16K context, and exposes the differing quantizations. On a
Raspberry Pi 5 16 GB it reports E2B Q4_K_M at 6.5 chat tok/s versus E4B Q4_0 at
3.7; `llama-bench` generation is 6.71 versus 3.48 tok/s. On a Pi 4 8 GB, E4B
chat times out while E2B reaches 1.7 tok/s. The one-repetition microbenchmark
and non-matched quant types make ratios fragile, not the route-level fit
pressure.

### M5 Max MLX

The `mlxcel` report exposes MacBook, OS, package and MLX revisions, cooldowns,
prompt, maximum output, and observed output lengths. At 4-bit it reports E2B
prefill/decode at 1382.74/225.08 tok/s versus E4B at 813.21/142.08. At 8-bit
the rows are 1226.90/148.16 versus 706.47/85.28. Thermal controls strengthen
the instrument; differing generated lengths and unpinned local checkpoint
directories still limit exact comparison.

The separate `Incept5` suite covers 4K through 256K on an M5 Max and retains
raw JSON and harness code. Its 4-bit rows again put E2B ahead in decode and
memory across the sweep. However, one run per target, a 32-token generation
cap, repetitive filler, mutable local model directories, and the erroneous MoE
label prevent semantic-context or architecture conclusions.

These are independent projects and hardware generations. Together with the
predecessor's OpenVINO, energy, and H100 measurements, they materially reinforce
the resource-side direction without making the absolute throughput portable.

## MTP: backend and task shape can change the sign

Official documentation describes the four-layer assistant and its shared
target activations/KV path, and states that speculative decoding preserves
target quality. Route evidence still has to demonstrate realized economics and
parity.

The Classmethod DGX Spark study in the predecessor found about 1.9-2.1x for
long outputs and about 1.0x for eight-token outputs. Two added origins sharpen
that result:

- The M1 Max LiteRT-LM task matrix uses one warmup and one measured round and
  estimates tokens from characters. E2B ranges from 0.82x on quick Q&A and
  summarization to 1.53x on JSON generation; E4B ranges from 0.91x on creative
  writing to 1.87x on coding. It is exploratory, but it directly exposes task
  shape and negative rows.
- The M4 repository runs the same prompt set on one machine through PyTorch/MPS
  and MLX. PyTorch averages improve: E2B BF16 1.87x, E4B BF16 2.27x, with still
  larger reported 4-bit ratios. MLX averages slow down systematically: E2B
  0.41x/0.52x and E4B 0.46x/0.57x for 16-/4-bit. The detailed reports therefore
  contradict any backend-free positive multiplier. Published baseline and MTP
  text also are not byte-identical, so the speed rows do not themselves prove
  exact output parity.

The stable conclusion is conditional: MTP benefit is a function of target and
assistant revisions, runtime/backend, quantization, task predictability,
output-length distribution, draft controls, batch/concurrency, and acceptance.

## Context admission has four layers

The sources now support four distinct predicates:

1. **Nominal model context:** the provider advertises 128K for E2B/E4B.
2. **Runtime allocation:** a runtime accepts the requested context and builds
   its state.
3. **Execution completion:** prefill and generation terminate without OOM,
   corruption, or device loss.
4. **Semantic usability:** an artifact-backed grader shows retained retrieval,
   reasoning, or task correctness at that position and route.

The Incept5 256K rows reach layers 2-3 for a short synthetic run. They do not
reach layer 4 and do not supersede the nominal provider contract. This is useful
pressure for a long-context owner study, not evidence of usable 256K.

## PLE currentness and qualified supersession

On 2026-08-30 the predecessor correctly captured issue `#47705` as open. The
current issue record is closed with reason `completed` after stale automation.
A maintainer comment only notes that a sufficiently fine-grained `device_map`
can offload a module; it does not publish an exact PLE map, a supported default,
or a verification run. Therefore:

- the reported 10.11 -> 4.48 GB resident-memory measurement is unchanged;
- the phrase "support question remains open" is stale for current issue state;
- "closed" must not be promoted to "PLE offload supported";
- the later observation is packaged as an `update` proposal for owner review,
  not silently applied to the earlier immutable observation.

There is no earlier locator-bounded capture snapshot for this issue. A
`ResearchChangeReceipt` would therefore invent a comparison baseline and is
not created. The exact two observations can still be content-addressed in a
`ResearchSupersessionProposal`; acceptance remains a later reviewed edit.

## What is reinforced enough to carry forward

- E2B is the recurring first candidate when local footprint, decode throughput,
  or small-device fit dominates.
- E4B is the recurring first candidate when aggregate task outcome, multimodal
  criticism, or all-run reliability dominates.
- Neither direction is an owner fit decision without exact realization and
  workload utility.
- Endpoint inversions inside a common harness are evidence against global
  ranking, not failures to be averaged away.
- MTP, context, multimodality, and PLE placement belong to runtime-realization
  admission, not to a model-name feature checklist.
- Source correctness is layered: a metadata error narrows the source but does
  not automatically erase independently inspectable measurements.

## What remains plausible but unreinforced

- A portable numeric E2B/E4B speed, memory, energy, or quality ratio.
- Exact-output parity for MTP across the added backends and quantizations.
- Semantically usable 128K or 256K on a named constrained-device route.
- A supported generic Transformers `device_map` recipe for PLE.
- A universal prompt strategy that preserves the same sensitivity,
  specificity, reliability, and cost ordering across E2B and E4B.
- AoA workload fit, because no retained source is an AoA-owned study.

## Method pressure produced by this pass

This run proposes three refinements for a later method revision rather than
silently changing v0.3 mid-campaign:

1. Track recurrence **per metric direction and denominator**. A source may
   support E4B consistency while supporting E2B pass-at-least-once.
2. Audit **source-internal contradictions** before counting an origin. README,
   detailed report, raw data, and code are one origin with layers, not votes.
3. Split **nominal, allocated, completed, and semantically usable context** in
   every long-context claim.

The existing outcome-axis and configuration rules already support these
records. No family-specific schema field, validator branch, or permanent test
is needed. A v0.4 method change should wait until another family shows the same
pressure or an owner study needs the distinction operationally.

## Owner-study frontier

The next useful AoA study is a paired Pareto surface, not a leaderboard:

- exact E2B/E4B target and optional MTP assistant revisions;
- one held-constant runtime route plus a separately declared alternate backend;
- representative short, structured, long, multimodal, and tool-using tasks;
- requested/executed/artifact/verified/reported/termination separation;
- pass-at-least-once and all-run reliability over repeated trials;
- TTFT, prefill, decode, output length, peak/resident memory, energy, thermal
  state, and retries;
- semantic long-context probes at multiple positions;
- output acceptance and postconditions, not only parser success;
- owner utility weights applied only after the measurement surface exists.

Until then, this dossier supplies selection hypotheses and replication targets,
not canonical model truth.

## Primary sources

- T1-Bench v1: <https://arxiv.org/html/2606.11070>
- Clinical multimodal INSPECT study v1: <https://arxiv.org/html/2606.22442>
- AudioProcessBench v1: <https://arxiv.org/html/2606.09925>
- Raspberry Pi benchmark, commit `c55c0062`: <https://github.com/potato-os/core/blob/c55c0062f37cc0c59646ff53f3595d7fa99daafe/docs/benchmarks/gemma4-pi-benchmark-2026-04-04.md>
- MLXcel M5 Max benchmark, commit `64e8d9a8`: <https://github.com/lablup/mlxcel/blob/64e8d9a8b991e750fe58faff2b0e15cc377017fd/docs/benchmark_results/model_tests_m5max.md>
- Incept5 suite and raw data, commit `babe2bfc`: <https://github.com/Incept5/gemma4-benchmark/tree/babe2bfc1989269a50135444a829c2d56f2c0bda>
- LiteRT-LM task matrix, commit `cdc54884`: <https://github.com/Sunwood-ai-labs/gemma4-mtp-benchmark/blob/cdc548843bdddd7e6ac34d1491004d40abaffd44/benchmarks/2026-05-06-task-matrix-m1-max.md>
- M4 PyTorch/MLX MTP repository, commit `4a3ba8e6`: <https://github.com/pank-bhatt/gemma4-mtp-benchmark/tree/4a3ba8e6a1890b955939f189285ed3a33df56f9d>
- Official Gemma MTP guide: <https://ai.google.dev/gemma/docs/mtp/mtp>
- Transformers PLE placement issue `#47705`: <https://github.com/huggingface/transformers/issues/47705>
