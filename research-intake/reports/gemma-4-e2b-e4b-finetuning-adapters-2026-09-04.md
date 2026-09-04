# Gemma 4 E2B/E4B: fine-tuning, adapters, and adaptation closure

Date: 2026-09-04
Status: pre-canon web reconnaissance
Paired packet: `research-intake/recon-runs/gemma-4-2026-09-04-e2b-e4b-finetuning-adapters.json`

## Question

Which fine-tuning and adaptation paths are actually evidenced for Gemma 4 E2B
and E4B; which configuration dimensions determine whether an adapter is valid;
what quality, retention, resource, multimodal, and deployment effects repeat;
and which attractive claims remain framework-, revision-, task-, or
artifact-bound?

This report does not select a model, prescribe a training run, accept a study,
or promote web observations into `ModelClaim`. It extends the earlier Gemma 4
lineage, operating-point, and corroboration runs with a separate adaptation
axis.

## Short answer

There is no single "Gemma 4 fine-tuning" path. The retained sources support at
least five materially different operations:

1. full or language-subtree supervised fine-tuning;
2. text-conditioned LoRA/QLoRA adapters;
3. multimodal training whose data contains image or audio, with an independently
   chosen question of whether the corresponding tower is trainable;
4. full-weight continued pretraining for language or domain adaptation;
5. joint target-plus-MTP-drafter tuning when speculative-decode throughput is a
   required property.

Across official recipes, independent studies, real adapter artifacts, and
runtime issues, the durable unit is not an adapter file alone. It is an
**adaptation bundle**:

```text
exact base + base revision
+ method and quantization
+ trainable module/tower selectors
+ processor, chat template, thinking mode, and loss mask
+ data and evaluation contract
+ library revisions and known-fix state
+ adapter/load/merge/export/serve acceptance
+ paired drafter and acceptance test, when MTP matters
```

This is the strongest repeated result of the pass. It is supported by provider
guidance, two current Google Gemma 4 QLoRA recipes, PEFT and Transformers defect
history, independent specialization studies, a real E2B adapter, MLX checkpoint
round-trip failure, and NVIDIA's joint E4B/drafter route.

## Method split

| Path | Evidence retained | What it proves | What it does not prove |
| --- | --- | --- | --- |
| Language-subtree SFT | Hugging Face/Google Cloud E2B tool-calling recipe | A concrete BF16 `SFTTrainer` path that freezes vision, audio, and embeddings and trains the language subtree | No completed-job artifact or held-out quality result is published on the page |
| Text QLoRA | Google Gemma 4 text-to-SQL recipe; E2B artifact; E4B tool-use study | Current PEFT defaults can scope Gemma 4 LoRA to LM layers; adapters can be retained separately or merged | A tutorial sample or training loss is not general capability proof |
| Vision-conditioned QLoRA | Google Gemma 4 vision recipe | Images can participate in Gemma 4 SFT while the default LoRA surface remains the LM | It does not show that the vision tower itself was adapted |
| Audio/vision-tower PEFT | PEFT topology guidance; commit-pinned Unsloth E4B audio notebook | Tower adaptation is possible through framework-specific, scope-aware selectors | No independent held-out audio comparison or cross-runtime portability was found |
| Full continued pretraining | Armenian E4B study plus E2B tokenizer ablation | Data mixture, learning rate, tokenizer choice, and replay materially affect adaptation and forgetting | One new language study does not define a universal CPT recipe |
| Joint target/drafter tuning | Google MTP coupling description; NeMo E4B recipes and 20-prompt benchmark | MTP speed after adaptation can be treated as a paired-artifact property and co-trained | It is full joint tuning, not evidence that an arbitrary LoRA adapter preserves MTP acceptance |

## Official runnable surfaces

### Language-subtree SFT is not LoRA

The current [Hugging Face Google Cloud recipe](https://huggingface.co/docs/google-cloud/examples/vertex-ai-notebooks-fine-tune-gemma-4)
loads `google/gemma-4-E2B-it` in BF16 on one H100 Spot VM. It marks every
parameter outside `model.language_model` frozen, then uses three epochs,
batch size 4, gradient accumulation 2, gradient checkpointing, `use_cache=false`,
and learning rate `5e-6`. This is a useful partial-full-weight SFT route, not a
LoRA example. The page records a training script and launch route but no
held-out result or retained output checkpoint.

### Current Google QLoRA recipes narrow the early compatibility picture

Google's current [text QLoRA guide](https://ai.google.dev/gemma/docs/core/huggingface_text_finetune_qlora)
and [vision QLoRA guide](https://ai.google.dev/gemma/docs/core/huggingface_vision_finetune_qlora)
both list E2B and E4B as selectable bases, require Transformers `>=5.10.1` and
PEFT `>=0.19.0`, quantize the base to NF4, and use an `r=16`, `alpha=16`
adapter. They deliberately omit `target_modules`: the documented PEFT default
scopes Gemma 4 to the language-model layers. Both preserve `lm_head` and
`embed_tokens` and request weight tying because the training path handles
special tokens.

The vision recipe passes images through the processor but still leaves the LoRA
surface on the LM by default. Therefore these two statements must remain
separate:

- "the model was trained on multimodal examples";
- "the modality tower was adapted."

The guides also make an important deployment distinction. Training saves the
adapter, while a standalone serving checkpoint requires loading the exact base
and calling `merge_and_unload`; the examples warn that merging requires more
than 30 GB of CPU memory. Their evaluation is explicitly manual/vibe-check
oriented, so the recipes are operational evidence, not benchmark evidence.

## Module topology and framework revisions

Early Gemma 4 integrations exposed a topology constraint that remains useful
even after libraries mature. Vision and audio projections use
`Gemma4ClippableLinear`, a wrapper around an inner `.linear`. In
[PEFT issue #3130](https://github.com/huggingface/peft/issues/3130), broad target
suffixes such as `q_proj` matched both ordinary LM linears and wrapped tower
linears. Excluding the towers made text adaptation work but prevented tower
adaptation; a monkey patch enabled basic training but broke merge/unmerge. The
maintainer's bounded remedy was to target the inner `.linear` with a
tower-scoped regex.

This is not evidence that Gemma 4 LoRA is globally unsupported. It is evidence
that selectors must encode both **tower** and **wrapper depth**, and that a
training-only workaround cannot be assumed mergeable.

A second defect affected `modules_to_save` for kwargs-only modules. The fix was
merged in [PEFT PR #3199](https://github.com/huggingface/peft/pull/3199) and is
reported as shipped in PEFT 0.20.0. This matters when a recipe saves or adapts
components outside ordinary LM linears. The packet therefore preserves exact
library revision and fix state instead of treating `peft>=...` as decorative
metadata.

Transformers had a separate first-week defect: shared-KV behavior was coupled
to cache use, so training with `use_cache=false` could produce invalid logits
and very high loss. [Transformers PR #45312](https://github.com/huggingface/transformers/pull/45312)
was merged on 2026-04-09 and made KV states share during training and uncached
inference. This explains why old Gemma 4 loss anecdotes are unsafe to aggregate
without an exact revision. The current Google QLoRA guides' much later
`transformers>=5.10.1` floor is stronger evidence for a contemporary baseline
than launch-week notebooks.

## What real specialization results show

### E4B tool-use QLoRA: gain and forgetting coexist

The independent paper
[Internalizing Tool Knowledge in Small Language Models via QLoRA Fine-Tuning](https://arxiv.org/html/2605.17774v2)
uses 8-bit QLoRA on Gemma 4 E4B for a fixed MCP-style tool catalog. With 1,741
training examples and a 30-scenario held-out set, its main `r=32` run reports
AT-F1 `0.635` and judge score `3.60`, versus `0.47` and `2.88` for the informed
base that still receives the full catalog. A separate rank-sweep run reaches
`0.65` and `3.88`; that difference is retained as run-to-run variance, not
silently averaged. The fine-tuned prompt falls from roughly 2,400 to 128 tokens,
but the catalog is fixed and unseen-tool generalization is explicitly outside
scope.

Rank is a trade-off, not a monotonic quality dial. In the published sweep,
`r=8/16/32/64` produces AT-F1 `0.56/0.63/0.65/0.63`. On a separate 100-question
general-capability probe, base E4B scores 84%, while `r=8` scores 69% and `r=32`
scores 67%. The authors verify that 8-bit quantization alone does not explain
the drop. On one A100 80 GB, the E4B run reports 11.5 GB base memory, 24.1 GB
peak training memory, and 56 minutes of training. These are bounded instrument
measurements, not universal E4B requirements.

### Full E4B continued pretraining repeats the retention pressure

The fresh study
[From Zero to Hero: An Open LLM Ecosystem for Armenian](https://arxiv.org/html/2609.03350v1)
adapts Gemma 4 E4B through full continued pretraining over 10B tokens. It holds
trainer, seed, budget, replay, and code streams constant across controlled
mixture and learning-rate runs. News-only CPT at `1e-4` loses 21.2 points on
Belebele and 7.1 points on m-MMLU-hy. Reducing the learning rate to `3e-5`
recovers much but not all of the loss. Replacing 6% of the news share with
verified Armenian/English STEM data lifts the six-task mean from the base's
`0.477` to `0.500`. Twenty percent English replay was present in every run and
did not alone prevent forgetting.

An E2B ablation at 2B tokens also warns against treating tokenizer extension as
automatic progress: stock-tokenizer CPT reaches mean bits-per-byte `0.387`,
while mean-initialized `+8k` and `+16k` Armenian vocabularies reach `0.628` and
`0.651` (lower is better). The paper bounds this to its budget and initializer.

Together, the QLoRA and CPT studies form a cross-method recurring pressure:
specialization must be evaluated both on the target task and on retained
capabilities. They do not prove a universal forgetting rate or that LoRA and
full CPT are interchangeable.

## Artifact existence is weaker than capability evidence

The community
[E2B reasoning adapter](https://huggingface.co/xbruce22/gemma-4-e2b-reasoning-lora)
is useful because it is an inspectable adapter, not because its claimed behavior
has been independently accepted. It contains roughly 12.1M trainable parameters
and reports `r=8`, one epoch over 25,614 rows, assistant-only loss, max sequence
1,536, BF16 training on a 24 GB Intel XPU, and about 5.7 hours runtime. Its card
shows PEFT loading and merge instructions. It has no held-out capability or
retention suite, so training loss and examples remain artifact-backed
observations only.

The distinction matters downstream. [MLX issue #1210](https://github.com/ml-explore/mlx-lm/issues/1210)
documents a 140-key E2B shared-KV shape divergence between Python and Swift
implementations that breaks a fuse/load round trip. The issue was later closed
as part of queue reduction without a linked technical fix. Status `closed` is
therefore not evidence that portability was restored.

The acceptance ladder for a reusable adapter is consequently:

1. training completed and loss is numerically sane;
2. held-out task behavior improved;
3. orthogonal capabilities and safety boundaries were measured;
4. exact base plus adapter reloads;
5. merge/unmerge round-trips if merge is required;
6. export format loads in the target runtime;
7. the real serving path produces accepted outputs;
8. optional accelerators such as MTP retain their benefit.

These are separate claims. Passing one does not imply the next.

## Multimodal adaptation

The evidence supports three distinct cases:

- **text-only adaptation:** freeze vision/audio and adapt the LM;
- **multimodal-conditioned adaptation:** feed image/audio examples while
  adapting the LM, leaving the modality tower frozen;
- **tower adaptation:** explicitly target wrapped tower linears or other tower
  components with a framework-specific selector.

A commit-pinned Unsloth E4B audio notebook demonstrates the third route by
combining LM attention/MLP targets with named audio modules. It is a current
operational artifact, but its 60-step demonstration and training loss do not
form an independent audio-quality benchmark. The earlier Google DeepMind JAX
LoRA example remains Gemma 3 text-only and explicitly lacks multimodal LoRA;
it should not be generalized into a Gemma 4 incompatibility claim.

No independent same-instrument comparison was found for:

- frozen-tower versus adapted-tower E2B or E4B;
- E2B versus E4B on the same multimodal dataset and hardware;
- multimodal task gain plus text/audio/vision retention plus portable export.

## MTP makes adaptation a paired-artifact problem

Google's [MTP overview](https://ai.google.dev/gemma/docs/mtp/overview) states
that the E2B/E4B drafter shares the target's input embeddings and consumes its
last-layer activations. Exact output quality is preserved by target
verification, but acceptance rate and speed remain distribution- and
pair-dependent.

The [NeMo Automodel E4B discussion](https://github.com/NVIDIA-NeMo/Automodel/discussions/2481)
provides a concrete joint-fine-tuning path for target and drafter. After 500
steps on an 80/20 Tulu-3/Magicoder mix, its 20-prompt benchmark reports 25.05
tokens/s without MTP and 49.51 with MTP, mean accepted tokens per target step
2.473, or `1.98x`. The commit-pinned recipe uses K=4, drafter loss weight 0.01,
full language-model tuning, trainable embeddings, frozen vision/audio towers,
FSDP2, and activation checkpointing on eight H100 processes.

The defensible inference is narrow: when MTP throughput is part of an adapted
realization, target and drafter should be versioned and evaluated as a pair.
The source does not show that an independently trained LoRA adapter damages or
preserves MTP, so that remains an explicit experiment.

## E2B versus E4B

No apples-to-apples adaptation benchmark was found that holds dataset,
framework revision, module surface, rank, quantization, sequence length,
hardware, task grader, and retention suite constant across E2B and E4B.

Current evidence is asymmetric:

- E2B has official low-level recipes, a one-H100 language-subtree route, an
  inspectable 24 GB XPU adapter, and the cheaper tokenizer ablation role;
- E4B has the stronger controlled task-specialization and CPT studies, plus a
  concrete joint-MTP path;
- community VRAM claims use incompatible denominators and sometimes contradict
  themselves.

Therefore this pass does not declare an E2B or E4B tuning winner. It proposes a
paired owner study as the next discriminating evidence.

## Durable intake lens

Each future Gemma 4 adaptation observation should carry these fields before it
can be compared:

- exact base repository, revision, base/IT role, and processor revision;
- E2B/E4B and effective versus retained parameter denominator;
- method: full, language-subtree, LoRA, QLoRA, CPT, DPO/GRPO, or joint drafter;
- quantization format and compute dtype;
- target modules as fully qualified selectors, grouped by LM/vision/audio;
- `modules_to_save`, embedding changes, and weight-tying behavior;
- chat template, thinking policy, special tokens, response-only mask, and EOS;
- sequence length, packing, batch, accumulation, optimizer, LR/schedule, and
  checkpoint-selection rule;
- trainable parameters and retained base parameters with explicit denominator;
- dataset identity, construction, deduplication, contamination checks, and
  modality mix;
- target-task, retention, safety/boundary, and failure-case evaluations;
- save/load, merge/unmerge, export, runtime, and real serving receipts;
- target/drafter identities and MTP acceptance when applicable;
- exact Transformers, PEFT, TRL, framework, CUDA/runtime, and known-fix state.

This is a comparison lens, not a hard-coded recipe. A field may be genuinely
inapplicable, but it should not silently disappear.

## Proposed paired study

The most informative next owner experiment is a small, same-instrument E2B/E4B
matrix rather than another isolated tutorial run:

1. pin one fixed base revision per model and one fixed framework stack;
2. use the same text-only dataset, processor/template, sequence cap, optimizer,
   rank, target surface, token budget, and checkpoint rule;
3. record wall time, peak device/host memory, adapter size, and energy if the
   host surface supports it;
4. evaluate target behavior, an orthogonal capability suite, safety/boundary
   cases, and failure cases;
5. exercise separate-adapter reload, merge/unmerge, export, and the intended
   runtime;
6. if MTP matters, compare base/drafter acceptance before and after adaptation
   and consider joint tuning only from that evidence.

The result belongs in an accepted `ModelStudy` only after owner review. This
ReconRun merely preserves why the study is needed and which dimensions must not
be collapsed.

## Revisit triggers

- a same-instrument E2B/E4B adapter benchmark with retained artifacts appears;
- a fixed PEFT release and regression test establish wrapped-tower merge/export
  behavior across text, vision, and audio;
- an independent multimodal adapter study reports both task gain and retained
  capabilities;
- MLX Python/Swift Gemma 4 fused-checkpoint round-trip is resolved by a linked
  patch and reproducible test;
- standard sequence-classification support is accepted upstream or an official
  checkpoint defines the contract;
- a LoRA-specific target/drafter acceptance study is published;
- a long-context adaptation run approaches the 128K nominal context with
  training and serving evidence;
- the mutable official recipes or commit-pinned notebooks change materially.

## Source-quality notes

- Official documentation establishes supported paths and intended contracts,
  not comparative quality.
- Commit-pinned code establishes that an implementation path exists at a
  revision, not that a run completed successfully.
- Papers provide method-backed observations within their instruments; freshness,
  small held-out sets, single-run columns, and confounds remain visible.
- Hub artifacts establish existence and inspectable metadata; author-reported
  behavior remains unaccepted without evaluation artifacts.
- Issues are valuable failure evidence, but issue state and technical resolution
  are distinct.
- Multiple pages from one publisher or implementation lineage are not counted as
  independent corroboration merely because they have different URLs.
