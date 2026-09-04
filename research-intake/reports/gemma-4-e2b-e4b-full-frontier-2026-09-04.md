# Gemma 4 E2B/E4B: QAT, safety geometry, transfer, composition, and lifecycle frontier

Статус: глубокая pre-canon web-разведка; не `ModelClaim`, не принятый
`ModelStudy`, не safety verdict, не runtime admission и не рекомендация модели

Срез источников: 2026-09-04

Метод: [`External Model Web Recon Lens v0.5`](external-model-web-recon-method-v0.5.md)

Предшественники:

- [`fine-tuning and adapters`](gemma-4-e2b-e4b-finetuning-adapters-2026-09-04.md);
- [`adaptation frontier`](gemma-4-e2b-e4b-adaptation-frontier-2026-09-04.md).

## Короткий ответ

Да, по Gemma 4 оставался большой пласт материала. Новый проход добавляет
четыре взаимосвязанных результата.

Во-первых, QAT — не одна характеристика модели, а ветвящийся lifecycle:
learned checkpoint, target quantization, conversion, runtime kernels, memory
denominator, optional modality stripping и exact MTP pair. Provider release
устанавливает широкий маршрут, но независимого E2B/E4B task benchmark,
который изолирует QAT от PTQ на одинаковом bit width, пока не найдено.

Во-вторых, safety/refusal корпус неожиданно богат. Для E2B и E4B повторяется
эффективность directional removal, но raw refusal markers дают ложные
срабатывания, разные techniques находят разные subspaces, а KL пригоден прежде
всего внутри одного calibrated instrument. В multilingual study максимальный
safety collapse и cross-lingual cosine приходятся на E4B, а не на 31B.

В-третьих, transfer evidence нельзя сводить к «LoRA помогает языку».
DistilledGemma, Welsh, Frisian, Traditional Chinese и EN/ZH/AR artifacts
измеряют разные ступени: teacher traces, CPT, SFT, synthetic data filtering,
script adherence, fluency, task score и retention. Более сильные работы явно
показывают и regressions, и judge/data limitations.

В-четвёртых, несколько самых важных направлений остаются настоящими gaps:
unseen-tool schema generalization, privacy/memorization после CPT и document
internalization, post-adaptation 128K curve, единая paired E2B/E4B matrix и
полная base→adapter→merge→quantize→serve→MTP цепочка.

## 1. Что изменилось в методе

Этот забег поднял линзу до v0.5 без изменения generic schema или validator:

1. Quantization decomposed на training recipe, representation, converter и
   runtime kernel path.
2. Memory/time/throughput получили measurement namespaces и обязательный
   denominator contract.
3. Release status разделён на announced, listed, retrievable, loadable,
   executable, semantically accepted, benchmarked и independently rerun.
4. Lifecycle parity оформлена как матрица стадий от base до MTP pair.
5. Refusal, harmful compliance, capability и safety geometry стали разными
   targets; KL получил metric passport.
6. Distillation сохраняет teacher→silver data→student lineage и запрещает
   приписывать gain traces без labels-only/gold-only ablations.
7. Low-resource evaluation разделяет language adherence, script, native
   fluency, task outcome, retention, contamination и tokenizer fertility.
8. External encoder/projector и modality stripping рассматриваются как
   composition/topology transformations, а не обычная LoRA.
9. Unseen-tool, privacy и post-adaptation context стали явными negative-search
   surfaces.

Это долговечные правила исследования. Временных validators, scripts или tests
для этого прохода не добавлялось.

## 2. QAT: официальный topology уже богаче одной Q4_0 модели

Официальный [Google QAT announcement](https://blog.google/innovation-and-ai/technology/developers-tools/quantization-aware-training-gemma-4/)
и [Gemma 4 overview](https://ai.google.dev/gemma/docs/core) задают две линии:

- Q4_0 QAT: unquantized QAT checkpoints, GGUF и W4A16 compressed tensors;
- mobile `wNa8o8`: static activations, channel-wise quantization, targeted
  2-bit decode layers, optimized embeddings/KV cache, E2B/E4B-only releases.

Официальная load-memory таблица с заявленным 20% overhead даёт:

| Variant | BF16 | Q4_0 | Mobile | Mobile text-only |
|---|---:|---:|---:|---:|
| E2B | 11.4 GB | 2.9 GB | 1.1 GB | 0.84 GB |
| E4B | 17.9 GB | 4.5 GB | 2.5 GB | 2.2 GB |

Таблица не включает supporting software и KV cache; fine-tuning требует иной
бюджет. Это provider topology и planning estimate, не наш runtime benchmark.

Для MTP документация требует matching QAT target и assistant того же precision.
Fine-tuning unquantized QAT weights объявлен совместимым с Transformers и
Unsloth. Однако это route surface: release не показывает, что исходная Q4_0
calibration переживает downstream LoRA, merge и re-quantization.

## 3. QAT против PTQ: что действительно измерено

Прямого qualified E2B/E4B task study, где QAT и PTQ сравниваются на одном
base, одном exact format/bit width, converter, runtime и harness, найти не
удалось.

Это важно, потому что доступные comparisons смешивают причины.

[Независимый 48-generation benchmark](https://kmarble.dev/posts/gemma-4-qat-benchmark-same-quality-faster-less-vram/)
для E4B сравнивает QAT 4-bit с PTQ Q8_0. Автор сам помечает precision confound:
QAT быстрее на части prompts, но медленнее на двух reasoning-heavy prompts, и
просит same-bit comparison. Шесть prompts и субъективная prose assessment не
могут подтвердить provider quality claim.

[Другой executable comparison](https://3h4x.github.io/tech/2026/06/08/gemma4-qat-vs-non-qat)
на 12B, а не E2B/E4B, хорошо изолирует одну методическую ошибку. QAT Q4_0
показывал 42.9 tok/s, PTQ Q4_0 — 38.4, PTQ Q4_K_M — 33.2 на одном 490-token
probe. Но автор связывает основную разницу с format/kernel и разным tensor mix,
а behavioral suite 4.5/6 против 4.5/6 слишком груб, чтобы различить качество.

Поддерживаемое ядро: QAT является правдоподобным quality-preserving source
checkpoint; observed speed следует атрибутировать deployed format и runtime,
пока recipe не изолирован.

## 4. Memory и throughput: denominator меняет картину

Официальный [vLLM Gemma 4 recipe](https://github.com/vllm-project/recipes/blob/main/Google/Gemma4.md)
показывает другие namespaces:

- W4A16: E2B 9.8→7.3 GB, E4B 15.2→9.8 GB;
- mobile compressed-tensor weight memory: E2B 2.7 GB, E4B 3.7 GB;
- E4B mobile на A100 при 1 024 input + 1 024 output достигает до 1.5× output
  throughput при concurrency 1–16; gain сходит на нет выше примерно 64.

Это не противоречит provider table автоматически: vLLM говорит о своей
loaded/weight surface, Google — об approximate load budget с собственным
overhead и LiteRT mobile path. Сначала нужно привести denominators.

Один [Jetson Thor forum benchmark](https://forums.developer.nvidia.com/t/benchmark-litert-lm-vs-llama-cpp-server-gemma-4-e2b-on-nvidia-jetson-thor/380349)
на official E2B artifacts показывает настоящий deployment Pareto:

| Engine/mode | Decode | Peak RAM | Peak power | J/token |
|---|---:|---:|---:|---:|
| llama.cpp GPU | ~80 tok/s | 2.45 GB | 16.7 W | 0.20 |
| LiteRT-LM CPU | ~21 tok/s | 2.54 GB | 1.7 W | 0.06 |
| llama.cpp CPU | ~15 tok/s | 4.07 GB | 1.2 W | 0.07 |

Это single-user report и не incidence. Но он опровергает одномерное «быстрее
= эффективнее»: лучший latency и лучший energy operating point различаются.

## 5. Runtime kernels, warmup и MTP

[little-gemma performance journal](https://github.com/cortexist/little-gemma/blob/main/docs/prefill-performance-journal.md)
даёт редкую metric lineage для E2B QAT:

- q4_0 path без MMA prefills 48 tok/s на Orin;
- repack и reuse существующего kernel повышают warm serve до 798 tok/s, затем
  same-session измерение уточняет примерно до 815 tok/s;
- plain decode 26.3→28.5 tok/s;
- structured MTP decode 31.5→55.3 tok/s при 75.7% acceptance и same reply;
- one-shot harness ошибочно включал repack в prompt timer;
- старое отношение к llama.cpp было отозвано после same-session pinned-clock
  comparison; отдельная decode таблица получила erratum из-за model-label mix.

Здесь важнее не максимальная цифра, а качество коррекции: автор сохраняет
неудачные hypotheses, warm/cold split, output gates и superseded measurements.
Результат version- и hardware-specific, но это сильный operational source для
метода.

## 6. Fine-tuning поверх QAT остаётся открытой цепочкой

В [Unsloth discussion #6389](https://github.com/unslothai/unsloth/discussions/6389)
пользователь спрашивает именно о сохранении Google Q4_0 calibration через
QLoRA. Ответы community подчёркивают, что bitsandbytes NF4 является другим
quantizer: unquantized QAT можно использовать как initialization, затем LoRA
и re-quantize, но это уже новый artifact.

Дискуссия не является framework guarantee. Она полезна как точная постановка
неизмеренного lifecycle перехода. Квалифицированного E2B/E4B эксперимента с
arms `QAT base → LoRA → merge → Q4_0 → task parity → MTP parity` не найдено.

## 7. Abliteration: E2B и E4B дают повторяемый, но опасно instrument-sensitive signal

[Gemma 4 Abliteration Research](https://github.com/TrevorS/gemma-4-abliteration/blob/master/ABLITERATION.md)
содержит несколько самостоятельных controls.

Для E2B:

- task-vector negation почти не двигает refusal до alpha 0.3, но уже накапливает
  KL; при alpha 0.5 refusal падает в ноль ценой KL 7.87 и разрушения модели;
- norm-preserving biprojection на всех слоях после marker correction даёт
  1/100 refusals при KL 0.3461;
- на четырёх prompt datasets — 686 prompts — лучший E2B artifact даёт 3/686
  raw refusals;
- 11 из первоначальных 12 flags на основном наборе оказались false positives
  из-за topic words внутри compliant answer.

Для E4B:

- base: 99/100 refusals;
- 70% layers: 6/100, KL 0.0428;
- 100% layers: 3/100 raw, но 0 effective после audit, KL 0.0678;
- cross-dataset: 5/686 raw.

Within this implementation E4B достигает сравнимого refusal removal при
меньшем KL, чем E2B. Но это не переносимый family ranking: KL passport, prompts,
precision и implementation должны совпасть.

## 8. Три независимых предупреждения о safety scorer

Первое — marker false positives выше. Второе —
[forensic comparison 13 E2B variants](https://huggingface.co/DreamFast/Gemma4-e2b-abliterlitics)
измеряет 5 600 HarmBench responses, сначала keyword detector, затем полный
LLM review. Его calibrated KL — full 262K vocab, first-token logits, 100
harmless prompts, batchmean — совпадает с четырьмя Heretic cards примерно от
0.3% до 17.2%, но один внешний claim расходится в 187 раз.

Третье — capability suite не следует одной оси. Log-likelihood tasks для 13
variants меняются умеренно, но GSM8K и LAMBADA обнаруживают отдельные failures;
один 99.5% ASR artifact имеет 5.69× LAMBADA perplexity. Десять из тринадцати
edits rank-1, однако pairwise weight directions образуют несколько clusters и
часто почти ортогональны. Одинаковый outcome не означает один механизм.

Forensics также обнаружила export defect: пять variants потеряли 60 shared-KV
weights в layers 15–34 из-за незнания `num_kv_shared_layers`. Это прямой пример,
где artifact integrity предшествует behavior ranking.

## 9. Multilingual refusal geometry: E4B — пик, а не середина линейной шкалы

[The Democratization Safety Paradox](https://github.com/gustipardo/gemma4-abliteration)
применяет один English-direction tool, NF4 configuration, 100 BeaverTails
harmful prompts и 10 harmless prompts к семи языкам.

| Size | Base harmful compliance | Abliterated | Delta |
|---|---:|---:|---:|
| E2B | 4.1% | 42.9% | +38.8 pp |
| E4B | 10.7% | 68.1% | +57.4 pp |
| 31B | 13.1% | 64.4% | +51.3 pp |

Post-abliteration compliance и adaptation delta немонотонны и достигают пика
на E4B. Cross-lingual cosine refusal directions также максимален на E4B
(0.37 против 0.31 E2B и 0.27 31B), тогда как silhouette убывает 0.29→0.26→0.23.

Это сильная внутри-study связь поведения и geometry, но не causal proof.
Prompts переведены из одного English dataset, judge один — Claude Haiku — и
paper writing ещё отмечен pending. Формулировка «within-family architecture»
слишком сильна без независимого tool/judge/native-language rerun.

## 10. DistilledGemma: что перенеслось в E2B, а что не изолировано

[DistilledGemma](https://arxiv.org/html/2606.29130) строит явную lineage:

1. выбирает Gemma 4 26B-A4B teacher по zero-shot macro recall;
2. QLoRA r32/alpha64 на всех attention+MLP projections, 3 epochs;
3. merges teacher adapter;
4. генерирует silver JSONL с labels и chain-of-thought для всего train corpus;
5. обучает E2B student QLoRA r16/alpha32, 6 epochs;
6. merges student для deployment.

На sandbox dev teacher получает macro recall 0.7015, distilled E2B 0.6171,
zero-shot E2B 0.5329. Авторы называют это 88% recovery и ~11× compression по
deployed parameter count. В official HIPE-2026 team result: 0.688 standard
mean (rank 3), 0.8156 binary mean (rank 2), rank 2 в balanced
efficiency-accuracy profiles.

Поддерживается: маленький E2B student является конкурентоспособным артефактом
в multilingual historical relation extraction. Не поддерживается отдельно:
что gain вызван именно reasoning traces. Нет gold-only, teacher-label-only и
label+trace ablation. Teacher generation cost исключён из deployed parameters,
но не из training economics. Corpus мал — 104 documents и 1 251 relation pairs
— и class imbalance велик.

## 11. Welsh E4B: самая богатая low-resource lineage в найденном корпусе

[Gemma 4 E4B Cymraeg v4](https://huggingface.co/EryriLabs/gemma-4-e4b-cymraeg-v4)
сохраняет CPT adapter, SFT adapter, merged BF16, GGUF, corpus reports и raw
evaluation outputs.

Stage 1: 43.8M trained tokens из построенных 78.0M, rsLoRA r128, отдельный
low-LR full embedding matrix, 668 steps. Stage 2: 19 443 instructions плюс
2.5M raw replay, LoRA r64, homogeneous batches, последние 20% batches только
instruction. Raw-heavy sibling recipe до этого дал repetition/content-free
regression; mix был изменён на основании negative result.

На 40 Welsh prompts:

| Arm | Requested language | Fluency /5 | Grammar /5 | Task /5 |
|---|---:|---:|---:|---:|
| stock | 47.5% | 2.46 | 2.38 | 1.45 |
| v3 SFT-only | 97.5% | 3.87 | 3.59 | 2.33 |
| v4 CPT+SFT | 100% | 3.68 | 3.76 | 2.70 |

v4 против v3: 23 wins, 13 ties, 4 losses. На 14-turn suite score растёт
1.97→3.35→3.99. English arm заявлен как 5.0 fluency и 4.95 task. Q4_K_M не
показывает measurable damage на этой suite; Q6_K лучший среди quants.

Limitations сохраняются вместе с headline: Opus не native Welsh judge, samples
малы, occasional loops остаются, factual recall weak, long retrieved context
может вызвать over-quoting, automated data не гарантирует native fluency,
Welsh tokenizer fertility сокращает effective word context.

## 12. Frisian: полезный artifact, но только weak evidence

[gemma-4-E4B-frisian](https://huggingface.co/Rickkosse/gemma-4-E4B-frisian)
использует 254M-token CPT LoRA r64, затем около 2.9k translated instructions и
SFT LoRA r16. Six-question fastText smoke test даёт mean Frisian probability
0.77 base, 0.84 SFT-only, 0.87 CPT+SFT.

Это подтверждает существование reproducible-looking route и artifact, но не
качество языка. Нет native judge, held-out task, confidence interval, English
retention, contamination audit или post-export parity. Источник честно называет
модель starting point, а не production system. В corpus он остаётся
`weak_signal_only`, не family observation о пользе CPT.

## 13. Traditional Chinese: synthetic data требует multi-seed и composition controls

[FormosaNLU E4B LoRA](https://huggingface.co/steven0226/gemma-4-e4b-formosanlu-lora)
имеет unusually strong community evidence:

- untouched MASSIVE zh-TW test, 2 974 rows;
- real-only и filtered synthetic arms;
- seeds 42–44;
- fixed QLoRA r16/alpha32, 500 steps, RTX 4090;
- artifact SHA и exact byte size;
- equal-N leave-one-recipe-out check.

На published seed-42 adapter intent accuracy 73.54→76.19, slot micro-F1
62.14→66.54, exact match 49.06→52.12; JSON validity 98.02→97.98. В later
robustness release multi-seed paired deltas остаются положительными в среднем,
но variance показывает, что отдельный seed меняет знак macro-F1 и JSON-valid.
Equal-N recipe exclusions не достигают заранее заданных 2.5 pp, поэтому
источник не делает component-level causal claim.

Это образец правильной сдержанности: общий synthetic-filtered gain поддержан,
но вклад конкретной recipe не изолирован.

## 14. EN/ZH/AR: script adherence растёт быстрее lexical similarity

[OfflineAid E4B](https://huggingface.co/helenk/gemma-4-E4B-finetune)
публикует merged FP16, LoRA и Q4_K_M sibling. На 111 held-out rows, одинаковом
Q4_K_M и greedy Ollama:

- English ROUGE-L 0.688→0.699, format 91.9→94.6%;
- Chinese ROUGE-L 0.229→0.227, format 45.9→62.2%;
- Arabic ROUGE-L 0.085→0.139, format 21.6→54.1%;
- overall format 53.2→70.3%.

Format означает non-empty плюс expected script, а не correctness. Автор явно
отмечает, что ROUGE-L плохо сравнивает допустимые переводы. Это не contradiction:
format, script adherence и lexical overlap измеряют разные outcomes. Dataset
мал и происходит из одного curated Australian safety corpus.

## 15. External speech encoder + E4B — composed system

[MERaLiON Speech LoRA SG MLX](https://huggingface.co/majentik/Gemma-4-E4B-BF16-MERaLiON-Speech-LoRA-SG-MLX)
соединяет MERaLiON-3 speech encoder, trained projector, BF16 E4B decoder и
rank-16 decoder LoRA. Размеры interface опубликованы: encoder output 3584,
projector hidden 3072, decoder embedding 2560, 42 decoder layers; speech
positions подаются через per-layer side channel.

На 3 000 MNSC ASR Part 2 utterances WER:

- stock MERaLiON-3 pipeline: 25.78%;
- 8-bit E4B composed sibling: 18.86%;
- BF16 E4B composed bundle: 16.09%.

Это component-backed ASR result, но не native Gemma audio LoRA. Generic hub
widgets не понимают bundle без custom runtime; speech LoRA scale 20 и prompt
contract являются частью realization. Source также говорит `owner-only/private`
при доступной model-card surface, поэтому публичную доступность выводить нельзя.
Cross-accent/language, long-form, streaming, timestamps и safety-critical use
не проверены.

## 16. Modality stripping: parameter delta не равен memory delta

[E4B classifier, vision/audio-stripped](https://huggingface.co/igorls/gemma4-e4b-classifier)
не retrains text path. Он re-instantiates `Gemma4ForCausalLM`, удаляя 478.1M
parameters: audio 304.8M, vision 167.4M и два projector.

На RTX 3090/Ollama Q4_K_M resident VRAM падает 10 626→6 517 MB, хотя removed
weights при Q4 объясняют лишь малую долю. Остальное source связывает с
higher-precision encoders, modality activation buffers и vocab-offset tables.

На n=100/task same-harness:

- closed classification: exact tie 0.6200;
- open classification: −0.0030;
- entity F1: −0.0201;
- memory coverage: +0.0250;
- p50 latency: +1.5 ms noise.

Multilingual pt-BR/es/zh suite остаётся близкой, но authors' «within noise» не
заменяет confidence intervals. Это promising artifact-backed result, не proof
полной text parity или safety identity.

С official E4B assistant deterministic output был byte-identical, а speedup
варьировался от 1.09× до 3.04× в зависимости от output structure. При этом
Ollama не поддерживал drafter, а документированный vLLM route ещё не работал на
v0.20.2. И снова topology, artifact pair и released runtime расходятся.

## 17. Unseen-tool generalization: qualified result всё ещё отсутствует

Предыдущий проход сохранил E4B tool-knowledge QLoRA с fixed catalog. Новый
поиск нашёл официальный [Gemma 4 function-calling route](https://ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4)
и community agent harnesses, но не paired adaptation study с post-training
unseen tools.

Не проверены вместе:

- добавление и удаление tools;
- semantic-preserving rename function и arguments;
- nesting/required-field changes;
- irrelevant catalog growth;
- hostile or contradictory descriptions;
- no-call, recovery и exact schema validity.

Поэтому fixed-catalog gain не повышается до general tool-use trait.

## 18. Privacy/memorization после CPT и document internalization: gap

Предшественник содержит E4B closed-book document internalization и Armenian
CPT. Новый поиск не нашёл E2B/E4B study, которое после adaptation измеряет
canary extraction, verbatim continuation, membership inference, PII leakage
или data-repetition privacy curve.

Высокий closed-book recall не является автоматически memorization incident;
отсутствие privacy eval не является безопасностью. Нужна отдельная матрица
base→CPT/SFT→merged→quantized, несколько prefix lengths, unique strings и
licensed/PII audit.

## 19. Post-adaptation 128K: номинальная поддержка не закрывает вопрос

Google задаёт 128K для E2B/E4B. Welsh и stripped artifacts сохраняют config,
но обучаются и оцениваются в основном на 2K-class contexts. Ни один найденный
qualified post-adaptation source не строит behavioral curve близко к 128K.

Следующий опыт должен измерять минимум несколько depths и positions, completed
answers, loops, task accuracy, time/memory и base/tuned parity. Для Welsh и
других языков нужна ещё word/byte normalization из-за tokenizer fertility.

## 20. Общая E2B/E4B матрица: пока только дизайн

Найденные результаты нельзя честно собрать в winner table: E2B и E4B проходят
разные tasks, adaptation recipes, seeds, scorers, precisions и runtimes.

Предлагаемая матрица:

| Axis | Shared control |
|---|---|
| data | same train/dev/test hashes and contamination audit |
| adaptation | same topology family, search budget and seeds |
| outcomes | task + retention + safety + schema + context curve |
| scorer | frozen revision plus orthogonal audit |
| export | adapter, merged, Q4_0/Q4_K_M and served parity |
| runtime | same hardware state; cold/warm and energy denominators |
| MTP | exact matching assistant, K sweep and output equivalence |

Если E2B и E4B требуют разного batch/precision для fit, это остаётся видимой
осью, а не скрытой нормализацией.

## 21. Полная lifecycle compatibility — главный эксперимент следующего цикла

Ни один источник не закрывает всю цепочку:

```text
base revision
  -> QAT or non-QAT initialization
  -> adapter target topology
  -> adapter semantic delta
  -> merge identity and strength
  -> final quantization/conversion
  -> GGUF / vLLM / LiteRT load
  -> served semantic parity
  -> exact MTP target/drafter pair
  -> throughput, energy and output-equivalence acceptance
```

Части цепочки уже существуют в разных origins, но композиция evidence не
равняется end-to-end result. Это не недостаток corpus: это точное описание
самого ценного нового experiment.

## 22. Повторяющиеся направления и степень их опоры

| Pattern | Независимость | Текущая опора |
|---|---|---|
| deployment outcome зависит от runtime/format, не только weights | provider + vLLM + blogs + forum + runtime journal | сильная методическая |
| memory требует semantic denominator | Google + vLLM + Jetson + stripped artifact | сильная |
| safety scorer даёт false positives | два independent community studies + multilingual delayed-refusal note | средняя/сильная |
| comparable refusal removal имеет capability/KL Pareto | два E2B forensics origins + E4B within-family | средняя, community-only |
| multilingual collapse немонотонен | один complete pipeline | promising, single-origin |
| CPT/SFT benefit зависит от data mix и scorer | Armenian predecessor + Welsh + Frisian + zh-TW + EN/ZH/AR | сильная методическая, outcome heterogeneous |
| distillation compresses a task-specific teacher | paper + official shared-task result | средняя/сильная domain-bounded |
| composition требует custom runtime и licenses | speech bundle + prior multimodal sources | средняя |
| modality removal может экономить system memory сверх weight bytes | один detailed artifact | promising, needs replication |

Здесь «сильная» означает устойчивость исследовательского требования, а не
каноническое свойство Gemma 4.

## 23. Приоритетная экспериментальная программа

1. **QAT parity lattice:** E2B и E4B, BF16/PTQ same-format/QAT same-format,
   identical tasks, converter, runtime and seeds; report quality, file,
   resident/peak memory, prefill/decode and energy separately.
2. **QAT adaptation chain:** unquantized QAT base→LoRA→merge→Q4_0 and W4A16;
   baseline, retention, modality and MTP parity after every stage.
3. **Safety scorer audit:** same 686 prompts, marker detector, full-response
   human/LLM audit, harmfulness judge and capability suite; publish confusion
   matrix and metric passports.
4. **Multilingual geometry replication:** native-authored prompts, second judge,
   multiple abliteration tools/seeds, E2B/E4B plus architecture control.
5. **Distillation factorial:** gold-only, teacher-label-only, labels+traces,
   teacher SFT and base-teacher arms; include generation cost and per-language
   held-out results.
6. **Low-resource common suite:** Armenian, Welsh, Frisian and zh-TW with native
   review, script/adherence/task/retention/token-fertility and contamination
   ledger.
7. **Composition factorial:** native audio route versus external
   encoder+projector, LoRA on/off/scale, BF16/quantized, component and full
   system baselines.
8. **Stripping matrix:** full, no vision, no audio, no PLE where supported;
   parameter, memory, multilingual, text, 128K and MTP checks.
9. **Unseen-tool suite:** schema mutation and hostile-description arms after
   fixed-catalog QLoRA.
10. **Privacy curve:** canaries, verbatim extraction, membership alternatives
    and licensed/PII audit across CPT repetition/capacity.
11. **Post-adaptation 128K curve:** several depths/positions, not one allocation.
12. **Paired E2B/E4B matrix:** one final common protocol, yielding Pareto rather
    than a single rank.

## 24. Итоговая граница

Материала достаточно, чтобы сделать исследование и метод существенно богаче:
сохранены новые источники, их exact roles, численные denominators, corrections,
weak evidence и отрицательные search results. Generated source dossiers делают
эти посещения доступными следующему агенту.

Недостаточно материала для утверждений:

- QAT всегда лучше PTQ на E2B/E4B;
- downstream LoRA сохраняет исходную QAT calibration;
- одна KL шкала ранжирует разные studies и sizes;
- E4B universally более уязвим к safety removal;
- CPT гарантирует native-quality low-resource language;
- distilled gain вызван именно chain-of-thought traces;
- stripped E4B полностью эквивалентен full model;
- tuned E2B/E4B сохраняют 128K behavior;
- fixed-catalog tool gain переносится на unseen schemas;
- полная lifecycle compatibility уже доказана.

Сильный результат этого прохода — не окончательная таблица, а связная система
из положительных findings, tensions, instrument passports и проверяемых gaps.
