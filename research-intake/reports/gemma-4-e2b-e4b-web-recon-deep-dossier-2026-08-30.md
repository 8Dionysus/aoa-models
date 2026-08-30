# Gemma 4 E2B/E4B deep web-recon dossier

Date: 2026-08-30

Status: reviewed pre-canon research intake

Owner: `aoa-models`

Method: [External Model Web Recon Lens v0.3](external-model-web-recon-method-v0.3.md)

This dossier preserves a bounded, temporally aware investigation of the Gemma
4 family with emphasis on E2B and E4B. It is research intake, not accepted
model source. It does not establish a `ModelIdentity`, `ModelRealization`,
`ModelClaim`, `ModelStudy`, route, fit verdict, runtime admission, deployment,
proof, or Operator acceptance.

The useful unit is not the brand label alone. Findings below keep checkpoint,
format, runtime, hardware, context, protocol, instrument, and observation time
separate whenever the source exposes them.

## Bounded question

What remained stable across official specification, versioned artifacts,
controlled evaluations, implementation evidence, primary runtime reports, and
field measurements for Gemma 4 E2B and E4B; where do their capability and
resource frontiers split; and which statements still require owner-controlled
replication before they can enter canonical model source?

## Executive synthesis

1. **The family is temporally segmented.** The 2026-03-31 launch comprised
   E2B, E4B, 26B A4B, and 31B. MTP assistants followed on 2026-04-16, and 12B
   Unified joined on 2026-06-03. A current five-size catalog must not be read
   back into the launch event.
2. **E2B and E4B are dense PLE models, not sparse MoE models.** Their short
   names describe an effective language-model scale, while the retained
   checkpoints contain about 5.12B and 8.00B parameters respectively. PLE
   tables, a roughly 150M vision encoder, and a roughly 300M audio encoder are
   part of the storage and placement problem even when they are not all active
   in the same way as the recurrent transformer computation.
3. **E4B is usually the capability-side point; E2B is usually the
   resource-side point.** The provider benchmark table and one controlled
   external evaluation both place E4B ahead on most captured task outcomes.
   Paired deployment evidence gives E2B lower resident memory, higher decode
   throughput, and lower energy per generated token in the measured
   configurations. These are Pareto observations, not a universal ranking.
4. **PLE placement is an operating-point lever.** Official static-load
   estimates are much larger than the effective labels imply. A primary E4B
   report moved one PLE table from GPU to CPU and observed resident VRAM fall
   from 10.11 GB to 4.48 GB with greedy output parity in that one setup. This
   is an open feature request, not a supported cross-runtime guarantee.
5. **Nominal capability and usable runtime support diverge.** The weights and
   cards advertise text, image, audio, 128K context, thinking, and function
   calling. Runtime reports expose format-specific missing graphs, GPU numeric
   corruption, parser and token-budget confounds, context stalls, and
   conversion failures. Weight capability therefore cannot stand in for route
   admission.
6. **MTP is workload-shaped.** On one DGX Spark/vLLM setup, official four-layer
   assistants produced about 1.9-2.1x long-form decode speedups, but no useful
   improvement on eight-token answers. Acceptance rate, answer length,
   hardware, and runtime version belong in the configuration.
7. **The strongest remaining gaps are practical.** No retained independent
   run establishes usable 128K context on a named E2B/E4B mobile route; no
   paired study combines output acceptance, TTFT, prefill, decode, energy,
   thermal behavior, and reliability; and no captured result is an AoA-owned
   workload study.

## Temporal family map

| Effective date | Event | Supported reading |
| --- | --- | --- |
| 2026-03-31 | Gemma 4 launch: E2B, E4B, 26B A4B, 31B | Original four-model launch boundary. |
| 2026-04-02 | Launch article published | Edge/offline positioning, multimodality, 128K for E-series, Apache 2.0, and ecosystem intent. |
| 2026-04-16 | E2B/E4B MTP assistants released | Separate speculative-decoding artifacts; not new base checkpoints and not a default speed guarantee. |
| 2026-06-03 | 12B Unified released | Current family expansion; does not alter the earlier launch event. |
| 2026-07-15 to 2026-07-20 | Current base and IT repositories updated | Exact repository revisions retained below. |
| 2026-07-24 | Technical report v2 | Later architecture/evaluation instrument; results must carry the v2 identity. |
| 2026-08-30 | This bounded capture | Current mutable docs and registry state sampled; future refresh can change currentness without rewriting history. |

The release-history segments and mutable registry metadata were captured as
immutable pre-canon snapshots under `research-intake/capture-snapshots/`.
Those snapshots preserve request, locator, transport result, and digests; they
do not archive a general crawl and do not promote their content.

## Current E2B/E4B subject matrix

| Dimension | E2B | E4B | Boundary |
| --- | --- | --- | --- |
| Effective / retained parameters | 2.3B effective; 5,123,178,051 retained in current safetensors metadata | 4.5B effective; 7,996,156,490 retained | “Effective” is PLE-specific vocabulary, not MoE active-parameter vocabulary. |
| Transformer layers | 35 | 42 | Current configs and official report. |
| Hidden size | 1,536 | 2,560 | Current IT configs. |
| Attention / KV heads | 8 / 1 | 8 / 2 | Current IT configs; head dimension 256. |
| Hybrid attention | four sliding layers then one full-attention layer | five sliding layers then one full-attention layer | Sliding window 512; final layer is global. |
| Nominal text context | 131,072 tokens | 131,072 tokens | Nominal model limit, not a retained claim of usable context on every runtime. |
| Vocabulary | 262,144 | 262,144 | Large embedding and output surfaces materially affect total footprint. |
| Modalities | text, image, audio; video represented as sampled frames plus audio | same | Runtime/export support remains route-specific. |
| Vision / audio encoder scale | about 150M / 300M | about 150M / 300M | Shared approximate component scale; not the whole memory denominator. |
| Thinking | IT checkpoints support thinking; can be disabled through the documented protocol | same | Output-token and latency cost depend on prompt and termination. |
| Function calling | documented for thinking IT use | same | Parser, template, token budget, and runtime support remain configuration. |
| Base checkpoint revision | `d29ff6b45f081a49ee2733a859c9c9c2d95d1a6f` | `411aa17b749aa952df1359d2dcea73917a544d9a` | Hugging Face API snapshot at 2026-08-30. |
| IT checkpoint revision | `3e22461f65e89153144f8adb70e3b8c2cc9845a7` | `ee0ef6023621cff504d758262d4e04895a5af4a2` | Hugging Face API snapshot at 2026-08-30. |
| License | Apache 2.0 in provider/model-card metadata | same | License metadata does not establish fitness for a deployment. |

### Protocol and multimodal limits

The current cards specify input ordering rather than a modality-free bag:
images precede text and audio follows text. Image token budgets range from 70
to 1,120 per image; audio input is documented up to 30 seconds; video is
documented up to 60 seconds at one frame per second. These are card-level input
contracts. A runtime that loads the language weights but lacks an encoder,
exported auxiliary graph, template, or parser does not thereby support the
advertised modality or tool protocol.

The provider recommends sampling around temperature 1.0, top-p 0.95, and
top-k 64. Controlled external evaluations in this dossier often use greedy or
temperature-zero decoding instead. Their outcomes therefore do not reproduce
the provider-recommended conversational operating point.

## Parameter and memory vocabulary

Three different denominators recur and must not be merged:

1. **Effective language-model scale**: 2.3B for E2B and 4.5B for E4B under the
   PLE accounting used by the provider.
2. **Retained checkpoint parameters**: about 5.12B and 8.00B in the current
   base/IT repository metadata, including large embedding surfaces and
   multimodal components.
3. **Runtime residency**: checkpoint format plus placement, allocator,
   runtime, context/KV state, and transient buffers on a named device.

The current provider memory table estimates static load memory with roughly
20% overhead and explicitly excludes context-state memory:

| Format / placement estimate | E2B | E4B |
| --- | ---: | ---: |
| BF16 | 11.4 GB | 17.9 GB |
| SFP8 | 5.7 GB | 8.9 GB |
| Q4 | 2.9 GB | 4.5 GB |
| Mobile package | 1.1 GB | 2.5 GB |
| Mobile text-only | 0.84 GB | 2.2 GB |

The technical report separately lists a smaller **text-only footprint** table
(E2B 4.6 GB BF16 / 0.8 GB quantized; E4B 9.0 GB / 2.3 GB) and an int8 KV-cache
estimate at 32K. This is not treated as a contradiction: the labels and
included components differ. A future canonical memory fact must carry format,
included components, context length, KV dtype, placement, runtime, and whether
the value is static, resident, peak, or on-disk.

## Architecture and lineage

The technical report describes E2B and E4B as dense decoders using per-layer
embeddings (PLE). A token lookup supplies layer-specific embeddings while the
transformer remains dense. The 26B A4B sibling is the family member that uses
sparse experts. One independent benchmark calls E2B/E4B MoE models despite
publishing otherwise useful measured outcomes; its architecture interpretation
is therefore not reused.

The lineage to Gemma 3n is bounded:

- PLE is explicitly carried forward “as in Gemma 3n”.
- the audio encoder is described as similar to Gemma 3n but reduced from about
  680M to about 305M parameters;
- Gemma 3n documents MatFormer nesting and an E2B submodel inside E4B;
- no captured Gemma 4 provider source establishes that MatFormer/nested-model
  relation for Gemma 4 E2B/E4B;
- current Gemma 4 implementations expose separate 35- and 42-layer classes.

The last two points are counter-pressure, not proof of absence. This dossier
therefore carries PLE and the audio lineage, while leaving Gemma 3n MatFormer
and E2B-inside-E4B nesting unresolved rather than inherited by name.

## Official capability evidence

The provider technical-report table places E4B above E2B on the captured
reasoning, multilingual, multimodal, agentic, and long-context metrics. Examples
include MRCR v2 eight-needle 128K at 25.4 versus 19.1, TerminalBench 8 versus 3,
and higher values across most table rows. This is a useful paired provider
instrument. It is not a population estimate, a route benchmark, or an AoA fit
verdict, and it does not price the extra storage, runtime memory, or output
tokens.

## Independent and field operating points

### Controlled task benchmark: UDAE v2

The May 18 v2 study evaluates seven models over ARC-Challenge, GSM8K, Math
Level 1-3, and TruthfulQA MC1 with zero-shot, chain-of-thought, and few-shot
chain-of-thought. It reports 19,992 evaluated examples, batch size one, greedy
decoding, seed 42, Python 3.13.11, PyTorch 2.10/CUDA 12.8,
Transformers 5.6.2, and an eight-H100-80GB server. BF16 is attempted before a
4-bit fallback policy.

| Variant / strategy | Weighted accuracy | Mean latency | Peak memory | Throughput |
| --- | ---: | ---: | ---: | ---: |
| E2B few-shot CoT | 0.688 | 5.997 s | 9.543 GB | 31.747 tok/s |
| E2B zero-shot | 0.671 | 5.098 s | 9.543 GB | 31.648 tok/s |
| E4B few-shot CoT | 0.761 | 3.677 s | 14.895 GB | 25.850 tok/s |
| E4B zero-shot | 0.758 | 4.373 s | 14.895 GB | 25.684 tok/s |

This supports a bounded E4B accuracy / E2B memory-and-decode frontier. It does
not show E2B universally faster in wall time: generated lengths, task mix, and
fallback realization remain confounds. The paper's incorrect MoE label also
shows that exposed measurement method and accurate subject metadata must be
audited separately. Its v1 and v2 result populations differ, so only v2 is used
for current observations.

### Official MTP assistants on DGX Spark

A primary field benchmark used DGX Spark GB10, 128 GB LPDDR5X, vLLM
`0.20.2rc1.dev99+g9c0812ffd`, PyTorch 2.11/CUDA 13.0, Transformers 5.8, BF16
targets and official four-layer assistants. In twelve repeated long-form
prompts, averaging runs 2-12, MTP changed E2B from 36.5 to 69.1 tok/s (1.89x,
38.8% acceptance) and E4B from 18.5 to 38.7 tok/s (2.10x, 44.6%
acceptance). On 200 eight-token Japanese certification answers it changed E2B
by 0.96x and E4B by 1.01x. Accuracy moved by at most one item in that small
test.

Supported reading: MTP can materially improve sufficiently long single-stream
generation on that runtime, while short outputs cannot amortize drafter cost.
The accuracy check is a smoke guard, not proof of general output equivalence.

### Paired energy measurement

A 2026 University of Vaasa master's thesis used Ollama/llama.cpp on a server
with two NVIDIA L40S 48 GB GPUs and CodeCarbon measurements spanning GPU, CPU,
RAM, and VRAM. It aggregated FinQA, SWE-bench-derived prompts, and WikiHow.
The paired averages reported:

| Variant | Energy per output token | Throughput |
| --- | ---: | ---: |
| E2B | `7.3e-7` kWh/token | 118 tok/s |
| E4B | `1.1e-6` kWh/token | 91 tok/s |

The study does not preserve enough checkpoint/quantization/runtime revision
identity for a canonical realization comparison and explicitly does not grade
output quality. It supports a configuration-bounded energy/throughput signal,
not the conclusion that E2B is more useful per accepted outcome. Thinking
increased output count and total energy in the broader corpus while average
energy per token stayed roughly stable; termination length remains an economic
variable.

### Lunar Lake NPU/GPU/CPU field matrix

A field report on Core Ultra 7 258V compared custom OpenVINO 2026 nightly IRs
under 60-second sustained greedy generation:

| Format | NPU | Arc 140V GPU | CPU | Important boundary |
| --- | ---: | ---: | ---: | --- |
| E2B INT4, 1.3 GB LM | 24.9 tok/s | 36.0 | 12.0 | Stable measured run. |
| E2B INT8, 2.2 GB LM | 17.8 | 26.0 | 11.3 | Stable measured run. |
| E4B INT4, 2.6 GB LM | 12.0 | 18.5 | 7.2 | Stable measured run. |
| E4B INT8, 4.4 GB LM | excluded | 13.4 | 6.6 | NPU smoke reached 12.7 tok/s but repeated runs hit device loss. |

NPU absolute system power was lower (about 27-30 W versus 37-39 W GPU), but
GPU throughput won joules per token in this setup. The official OpenVINO E4B
exports also had compile/performance failures while the author's custom IRs
worked for several points. This is conversion/runtime/hardware evidence, not a
model-only defect.

### PLE placement on one E4B GPU route

An open Transformers issue reports `google/gemma-4-E4B-it` with
Transformers 5.8.1, Accelerate 1.13.0, PyTorch 2.6.0+cu124, bnb NF4 and an RTX
A5000 Laptop 16 GB. Moving `embed_tokens_per_layer` to CPU after load changed
resident VRAM from 10.11 to 4.48 GB and changed an 8.5K-token prefill from OOM
at 15.5 GB to a measured 11.84 GB peak. Greedy output matched token-for-token
for 2,287 tokens; estimated transfer was roughly 20 MB per 1K tokens.

This is a detailed primary observation with no maintainer-confirmed supported
`device_map` path and no E2B replication. It demonstrates placement leverage,
not a general “free” offload guarantee.

### LiteRT runtime reliability reports

One Android E2B issue names Pixel 10a / Tensor G4 / Mali-G715 / Android 14,
LiteRT-LM 0.10.x, an approximately 2.5 GB mixed-quant package, and 357
single-turn plus 29 multi-turn cases. Post-condition verification reduced
previously reported pass rates by 6-40 percentage points. The most recent
reported run completed 325/357 cases, with 71.4% honest pass, p50 9.3 s, p95
26.4 s, and p99 42.5 s. The reporter separated GPU numeric/JSON corruption,
tool-count degradation, near-cap hangs, rehydration fragility, and Android
memory-accounting error. CPU removed the observed corruption but decoded about
2-3x more slowly.

A paired Ubuntu 24.04 LiteRT CPU report held the C ABI route constant and
observed an E2B silent post-decode hang and an E4B segmentation fault at named
package revisions. The root cause remained unresolved. These are valuable
route-level failure modes, not incidence estimates or model-only causality.

### Nominal 128K versus usable context

Provider artifacts establish a 131,072-token nominal limit. The retained
field evidence does not establish usable 128K on mobile. The detailed Android
route instead reports stalls near an 8,192-token generation cap and fragile
state rehydration. This is not evidence that the model cannot use 128K in a
different runtime; it is evidence that model context capacity and route-level
usable context are separate questions. The countersearch did not find a
paired, artifact-backed E2B/E4B mobile run spanning long-context accuracy,
prefill time, peak memory, thermal behavior, and completion reliability.

## Runtime support is not weight capability

The captured issues divide into distinct owner surfaces:

| Symptom | Most honest current owner surface | Why not model-only |
| --- | --- | --- |
| Missing or unsupported PLE forward graph | runtime implementation / conversion | Loader-visible tensors do not prove the execution graph consumes them correctly. |
| Audio weights present but export path missing | converter / runtime modality support | Stored modality components are not an executable route contract. |
| JSON corruption on Mali GPU but not CPU | numeric backend / runtime | Device path changes the symptom while checkpoint is held. |
| Tool accuracy falls with tool count | model + prompt + generation budget + parser/harness | The issue itself exposes truncation and parsing confounds. |
| E4B INT8 NPU device loss | format size + NPU memory + compiler/runtime | E4B INT4 and GPU/CPU routes remain usable in the same report. |
| Near-cap hang / rehydration failure | runtime state and context policy | Nominal model context does not establish state-management reliability. |
| E4B PLE offload changes fit | placement and allocator | Same weights, different residency. |

## Recurring clusters and bounded conclusions

### 1. E2B/E4B form a Pareto pair, not a strict ladder

E4B carries a recurring outcome advantage in provider and independent task
tables. E2B carries a recurring storage, residency, decode-throughput, and
energy-per-token advantage in paired deployment evidence. The correct next
question is workload utility per accepted outcome under a named route, not
which short name “wins”.

### 2. PLE makes parameter labels operationally dangerous

Effective, retained, static-load, resident, peak, and context-state sizes can
all be correct for different denominators. Any canonical fact that says only
“2B”, “4B”, or “fits in N GB” would erase the mechanism most likely to decide
deployment feasibility.

### 3. MTP is an amortization mechanism

Long generations can benefit strongly; very short generations do not. Draft
acceptance, target/assistant revision, runtime implementation, answer length,
batching, and hardware bandwidth belong in a study configuration.

### 4. Multimodality is route-composed

Provider weights and protocol support are necessary but insufficient. Vision,
audio, video, and tool use require the right encoders, preprocessing, template,
export, auxiliary graph, parser, and runtime version. “Multimodal checkpoint”
must not become “multimodal route admitted”.

### 5. Reliability evidence is granular but not yet recurrent enough for an incidence claim

Primary issues reveal repeatable failure classes inside their own fixtures,
but they do not share checkpoints, runtimes, hardware, or harnesses. The stable
finding is the attribution split and need for route-specific reproduction, not
a family-wide failure rate.

## Tension ledger

| Tension | Resolution posture | Remaining question |
| --- | --- | --- |
| E2B/E4B names vs 5.12B/8.00B retained parameters | Resolved by denominator | Which component and placement dominate each target route? |
| Technical-report text-only memory vs current static-load table | Resolved by scope; exact component accounting still partial | Can one owner harness measure disk, static, resident, peak, and KV/context state together? |
| E4B outcome advantage vs E2B resource advantage | Resolved by axis split | What is utility per accepted AoA outcome? |
| Official edge/offline positioning vs runtime failures | Resolved by product/runtime route | Which exact packages pass admission on each supported device? |
| MTP long-form speedup vs short-form no gain | Resolved by instrument and output length | Where is the break-even length under AoA traffic? |
| 128K nominal context vs 8K-route stalls | Partially resolved by route | What usable-context frontier survives long-context correctness, memory, thermal, and reliability checks? |
| Multimodal weights vs missing exporter/auxiliary graph | Resolved by owner surface | Which runtime versions support each modality end to end? |
| Controlled benchmark measurements vs incorrect “MoE” label | Resolved by evidence split | Does the study's realization fallback differ between E2B and E4B? |
| Gemma 3n MatFormer/nesting vs Gemma 4 E-label reuse | Unresolved; inheritance denied without evidence | Does any provider implementation or report establish nesting for Gemma 4? |

## Confound and currentness ledger

- Current docs and registry APIs are mutable; the 2026-08-30 snapshots are
  observations, not perpetual truth.
- Provider benchmark rows share one origin and one provider instrument.
- UDAE v2 exposes method and versions but mislabels E2B/E4B architecture and
  uses a BF16-then-4-bit fallback policy; exact per-row realization remains
  incomplete.
- The energy thesis aggregates task outputs and hardware energy but omits the
  exact model digest, quantization, and Ollama/llama.cpp versions and does not
  measure accepted output quality.
- Field MTP results use one single-client runtime/hardware point; they do not
  establish batching or multi-tenant behavior.
- The OpenVINO article uses custom-converted IRs for successful points and is
  one field origin, not an official compatibility matrix.
- GitHub issues are primary reports with exact environments to varying degree;
  open/unconfirmed issues are not maintainer verdicts or incidence estimates.
- Forum and secondary retellings were used only for discovery/counter-pressure
  when they lacked artifacts, exact revisions, or paired controls.

## Countersearch and counterevidence

Countersearch was performed for each strong cluster:

- **E4B capability advantage:** provider and UDAE tables recur, but individual
  forum fixtures sometimes prefer E2B and the independent benchmark has a
  subject-metadata error. No universal rank is retained.
- **E2B deployment advantage:** paired memory/energy/throughput evidence recurs,
  but E4B can fit after quantization or PLE offload and can deliver higher task
  outcomes. “E2B always faster/cheaper” is not retained.
- **MTP acceleration:** the same field benchmark contains the decisive
  counterexample—short outputs erase the gain. RTX 5090 forum numbers were not
  merged because E2B and E4B used different runtimes/formats.
- **128K usability:** no retained mobile counterexample closes the gap; the
  absence is recorded as a search gap, not proof of failure.
- **PLE/runtime defects:** multiple runtime reports expose missing or fragile
  paths, while official Transformers/vLLM support and successful custom routes
  show the model can run. The cluster is runtime-version pressure, not model
  invalidity.
- **Gemma 3n inheritance:** explicit PLE/audio lineage exists; explicit Gemma 4
  MatFormer/nesting evidence was not found. The inheritance remains bounded.

## Source and origin map

Dependent retellings are not counted as independent recurrence.

| Origin group | Primary sources used | Role |
| --- | --- | --- |
| Google / Google DeepMind | [release history](https://ai.google.dev/gemma/docs/releases), [launch article](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/), [model page](https://deepmind.google/models/gemma/gemma-4/), [core overview](https://ai.google.dev/gemma/docs/core), [technical report v2](https://arxiv.org/abs/2607.02770), [reference implementation](https://github.com/google-deepmind/gemma/blob/main/gemma/gm/nn/gemma4/_gemma4.py) | Family time, architecture, protocol, provider measurements. |
| Google model repositories on Hugging Face | [E2B base](https://huggingface.co/google/gemma-4-E2B), [E2B IT](https://huggingface.co/google/gemma-4-E2B-it), [E4B base](https://huggingface.co/google/gemma-4-E4B), [E4B IT](https://huggingface.co/google/gemma-4-E4B-it), [E2B MTP](https://huggingface.co/google/gemma-4-E2B-it-assistant), [E4B MTP](https://huggingface.co/google/gemma-4-E4B-it-assistant), [E2B mobile QAT](https://huggingface.co/google/gemma-4-E2B-it-qat-mobile-ct), [E4B mobile QAT](https://huggingface.co/google/gemma-4-E4B-it-qat-mobile-ct) | Current checkpoint, card, MTP, QAT, and mobile artifact surfaces. |
| Gemma 3n provider lineage | [overview](https://ai.google.dev/gemma/docs/gemma-3n), [E2B card](https://huggingface.co/google/gemma-3n-E2B-it) | Positive and negative inheritance boundary. |
| Boch et al. / UDAE | [paper v2](https://arxiv.org/abs/2604.07035v2), [code](https://github.com/mkboch/UDAE) | Controlled paired capability/resource measurement; architecture-label tension. |
| Classmethod field benchmark | [DGX Spark MTP benchmark](https://dev.classmethod.jp/en/articles/dgx-spark-gemma4-mtp-multi-token-prediction-bench/) | Paired long/short MTP operating points. |
| University of Vaasa | [energy thesis record](https://osuva.uwasa.fi/items/f1cf41f4-bd01-4a0c-868d-8a98e8ee0306) | Paired energy and throughput; incomplete realization identity. |
| Google AI Edge issue reporters | [Android reliability #2202](https://github.com/google-ai-edge/LiteRT-LM/issues/2202), [CPU crashes #2149](https://github.com/google-ai-edge/LiteRT-LM/issues/2149) | Primary runtime/harness failure observations. |
| Transformers issue reporters | [PLE placement #47705](https://github.com/huggingface/transformers/issues/47705), [PLE implementation #45206](https://github.com/huggingface/transformers/issues/45206) | Placement measurement and runtime implementation pressure. |
| llama.cpp issue reporter | [PLE forward support #22243](https://github.com/ggml-org/llama.cpp/issues/22243) | Unconfirmed runtime quality pressure. |
| jkudo field reports | [OpenVINO device/energy matrix](https://zenn.dev/jkudo/articles/ae85d7d099e672?locale=en), [LiteRT/OpenVINO graph analysis](https://zenn.dev/jkudo/articles/93b1f12f528a6b?locale=en) | Conversion-specific NPU/GPU/CPU support and representation gap. |
| vLLM project | [Gemma 4 recipe](https://docs.vllm.ai/projects/recipes/en/latest/Google/Gemma4.html), [MTP docs](https://docs.vllm.ai/en/latest/features/spec_decode/#multi-token-prediction) | Versioned runtime support, not performance proof. |

## Retained immutable capture set

The following nine snapshots are retained because mutable current segments or
exact registry revisions materially affect later comparison:

- `gemma4-release-launch-20260830.json`
- `gemma4-release-mtp-20260830.json`
- `gemma4-release-unified-20260830.json`
- `gemma4-core-memory-20260830.json`
- `gemma4-core-memory-considerations-20260830.json`
- `gemma4-hf-e2b-base-20260830.json`
- `gemma4-hf-e2b-it-20260830.json`
- `gemma4-hf-e4b-base-20260830.json`
- `gemma4-hf-e4b-it-20260830.json`

No schedule, crawler, automatic consensus, rank, promotion, or supersession was
created. Future refresh is justified only when a revisit trigger fires and
must produce a new snapshot plus a review-only receipt.

## Method delta from v0.3

The run validates rather than replaces the v0.3 lens:

- temporal segments prevented the later 12B addition from rewriting launch;
- origin grouping prevented model cards and provider tables from becoming
  false independent recurrence;
- subject/configuration/outcome decomposition kept model, checkpoint, format,
  runtime, hardware, harness, and protocol symptoms separate;
- tension and Pareto treatment preserved useful E2B/E4B trade-offs without a
  scalar confidence or ranking;
- explicit gaps prevented nominal 128K and multimodal weights from becoming
  route-level claims.

One general method pressure is proposed for a future revision: **audit subject
metadata and measured outcome method independently**. UDAE v2 exposes a useful
measurement protocol while misclassifying dense PLE E2B/E4B as MoE. The
measurements can remain bounded evidence while the mechanism interpretation is
rejected. One run is insufficient reason to change the schema, validator, or
method version now; the pressure is recorded in the operating-points ReconRun.

Parameter vocabulary, memory denominator, weight-versus-route modality, and
usable-versus-nominal context all fit existing v0.3 fields. No generic code or
permanent test change is warranted by this campaign.

## Bounded handoff candidates

These are review targets, not promotions:

1. **Realization-fact candidate:** exact current E2B/E4B base and IT repository
   revisions, retained parameter counts, layer/head/context configuration, and
   artifact license—after independent owner review against immutable provider
   refs.
2. **Study candidate:** an AoA-owned paired E2B/E4B operating-point matrix that
   freezes checkpoint, quantization, runtime, hardware, prompt set, output
   acceptance, TTFT, prefill, decode, peak memory, context, energy, thermal,
   retries, and termination.
3. **Runtime-owner handoff:** PLE placement/offload, multimodal export, long
   context, GPU numeric behavior, and MTP break-even belong to named runtime
   subjects, not family-wide claims.
4. **No current promotion:** provider benchmark tables, external field issues,
   energy thesis aggregates, and forum reports remain pre-canon until an owner
   selects and verifies a narrower target.

## Revisit triggers

- Google changes family membership, context, architecture, protocol, memory
  estimates, or published benchmark instrument.
- Any E2B/E4B base, IT, MTP, QAT, or mobile repository revision changes.
- A runtime release closes or materially narrows the cited PLE, device-map,
  GPU precision, exporter, NPU compile, context, or rehydration issues.
- A controlled paired run publishes exact E2B/E4B checkpoints plus output
  acceptance, TTFT, prefill, decode, memory, energy, thermal, and reliability.
- An artifact-backed mobile study tests usable context materially beyond 8K.
- Provider evidence explicitly confirms or denies Gemma 4 MatFormer/nested
  E2B-in-E4B lineage.
- An AoA owner selects an exact route and workload for a canonical study.

## Stop line

This run stops at reviewed research intake. It deliberately does not create a
crawler, recurrence threshold, universal score, automatic consensus,
automatic promotion, route recommendation, fit verdict, proof bundle, runtime
admission, deployment instruction, publication claim, or acceptance record.
