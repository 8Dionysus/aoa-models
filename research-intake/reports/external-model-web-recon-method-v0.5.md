# External Model Web Recon Lens v0.5

Статус: pre-canon исследовательский метод; не owner truth, не канон, не
`ModelClaim`, не `ModelStudy`, не proof verdict и не автоматическое основание
для выбора модели

Срез метода: 2026-09-04

Предшественник: `external-model-web-recon-method-v0.4.md`

Эмпирическая основа этой revision:

- [`Gemma 4 E2B/E4B adaptation frontier`](gemma-4-e2b-e4b-adaptation-frontier-2026-09-04.md);
- [`Gemma 4 E2B/E4B full frontier`](gemma-4-e2b-e4b-full-frontier-2026-09-04.md).

v0.5 выросла из трёх разных давлений: QAT и deployment нельзя измерять одной
цифрой памяти, safety/refusal нельзя сводить к substring counter, а
distillation/CPT нельзя атрибутировать student без teacher, data и scorer
lineage. Эти уточнения общие и не кодируют Gemma, конкретный runtime или
название метрики в schema либо validator.

## 1. Наследуемые границы

Без изменения действуют:

- pre-canon и owner boundaries;
- сегментная, временная и origin-aware работа с источниками;
- атомарные observations;
- exact subject/configuration binding;
- outcome, denominator, confound и counterevidence ledgers;
- optional `search_probes` для положительного, слабого и отрицательного поиска;
- пять ступеней adaptation maturity;
- scorer/mechanism/seed/intervention separation;
- silent-path, runtime semantic-delta и paired-artifact acceptance;
- отсутствие автоматического consensus, ranking и promotion.

Новая revision не меняет machine contract. Она уточняет, какие данные следует
помещать в уже существующие generic поля и когда сравнение недопустимо.

## 2. Причинная декомпозиция deployed artifact

Слово «модель» часто скрывает несколько независимых преобразований:

```text
training recipe
  -> learned checkpoint
  -> representation / quantization format
  -> conversion or export
  -> runtime kernels and scheduling
  -> loaded process and cache policy
  -> workload-specific observed outcome
```

Если QAT build быстрее PTQ build, это не доказывает speed effect QAT: могли
измениться bit width, tensor mix, file layout, dequant kernel, warmup, cache,
batching или speculative path. Если fine-tuned checkpoint затем quantized,
первоначальная calibration не считается сохранённой без нового evidence.

Каждая observation по возможности называет:

- исходный checkpoint и его exact revision;
- training recipe, если сравнивается обучение;
- фактический tensor format и precision каждого крупного subtree;
- converter и runtime revision;
- hardware, concurrency, prompt/output lengths и cache state;
- какой участок причинной цепочки действительно варьировался.

## 3. Measurement namespace и denominator contract

Одинаковая единица не создаёт одинаковую метрику. `GB` может означать file
size, весовые tensors, resident VRAM, process RSS, peak high-water mark или
полный stack вместе с KV cache и supporting software.

Для каждой количественной меры сохраняются semantic namespace и denominator:

```text
memory:
  file_bytes | weight_tensors | loaded_static | resident_process
  | peak_process | full_stack_peak

time:
  cold_start | conversion | repack | warmup | prefill | decode
  | time_to_first_token | time_to_first_semantic_unit | end_to_end

throughput:
  single_request | fixed_concurrency | saturation
  + input_tokens + output_tokens + batch/cache policy

energy:
  idle-adjusted or raw + integration interval + tokens counted
```

Числа из разных namespaces не объявляются tension. Сначала проверяется, не
измеряют ли они разные части системы. Сводная Pareto допускается только после
явной нормализации или рядом с сохранёнными различиями.

## 4. Release-state ladder

Mutable ecosystem особенно часто смешивает намерение и доступность. Для
checkpoint, converter, runtime feature или compatibility path различаются:

```text
announced
  -> listed
  -> bytes retrievable
  -> loader accepts
  -> execution completes
  -> semantic acceptance passes
  -> benchmark protocol retained
  -> independently rerun
```

Model card, документация и collection могут опережать release package.
Успешный локальный patch может опережать upstream. Каждый переход получает
своё evidence; более ранняя ступень не доказывает более позднюю.

## 5. Lifecycle parity matrix

Для адаптированной или quantized модели минимальная полная матрица строится по
стадиям, а не только по именам файлов:

| Stage | Identity | Required acceptance |
|---|---|---|
| base | exact weights + tokenizer/template | frozen baseline suite |
| adapter | base + adapter + target map | intended semantic delta |
| merged | exact merge algorithm/strength/order | delta and retention parity |
| quantized | converter + format + calibration | task and corruption parity |
| served | runtime + flags + context/cache policy | ordinary request-path parity |
| accelerated | exact target + drafter + K | output equivalence, acceptance and speed |

`loaded`, `HTTP 200`, matching file size и coherent sample не заменяют
semantic acceptance. Для deterministic задач предпочтительны byte-identity и
paired per-item deltas; для stochastic — fixed seeds и distributional checks.

## 6. QAT после адаптации

QAT checkpoint является обученным состоянием, а не вечной лицензией на
последующее quantization качество. После LoRA, QLoRA, merge, modality stripping
или vocabulary change задаются отдельные вопросы:

1. На каком представлении фактически обучался adapter?
2. Совпадает ли training quantizer с target deployment format?
3. Остались ли отдельными base и adapter или веса merged?
4. Был ли final artifact заново quantized/calibrated?
5. Повторены ли task, retention, multimodal и MTP checks после export?

Формулировка «fine-tune QAT weights directly» устанавливает route surface.
Она не доказывает, что исходный Q4 calibration сохранён после изменения весов.

## 7. Warm, cold и setup accounting

Kernel benchmark обязан отделять persistent service от one-shot process.
Conversion, repack и page-fault cost могут честно входить в cold path и честно
исключаться из warm path, но не должны случайно смешиваться с prefill/decode.

Минимальная запись:

- clock/power state и thermal posture;
- cold/warm arm и число discarded runs;
- setup, model load, repack и cache preparation;
- client-side versus server-side timestamps;
- same-session comparator или причина его отсутствия;
- raw per-run values, а не только лучший result.

Старое число, опровергнутое same-session rerun, остаётся в metric lineage как
retired measurement, а не исчезает.

## 8. Safety, refusal и harmfulness — разные targets

Refusal removal, harmful compliance, capability preservation и alignment
связаны, но не тождественны. Нужны разные instruments:

- marker/parser refusal detector;
- full-response judge, учитывающий refusal-then-comply и delayed refusal;
- harmfulness or policy compliance judge;
- harmless capability/utility suite;
- distributional shift measure;
- mechanistic probes of directions, layers или experts.

Substring marker audit обязателен, когда ключевые слова встречаются внутри
дисклеймера, цитаты или полезного ответа. Указывается доля вручную или вторым
judge пересмотренных positives и negatives. `ASR` без точного определения не
сравнивается между работами.

## 9. Metric passport и сопоставимость KL

Название `KL divergence` недостаточно. Metric passport включает:

- reference и candidate distribution;
- prompt corpus и число prompts;
- token position(s) и context length;
- полный vocab или subset;
- direction `KL(P||Q)`;
- reduction (`sum`, `mean`, `batchmean`);
- temperature, masking reserved/non-finite logits;
- precision и quantization;
- instrument revision.

Без совпадающего passport KL остаётся within-study dial. Его нельзя превращать
в cross-study или cross-size ranking. То же относится к refusal rate, WER,
ROUGE, language ID, LLM-judge score и MTP acceptance.

## 10. Safety geometry across languages

Multilingual safety comparison фиксирует:

- были ли prompts native-authored или translated;
- одинаковы ли semantics и harmfulness across languages;
- language/resource/script labels;
- base compliance отдельно от adaptation delta;
- judge language competence и calibration;
- decoding и quantization;
- geometry extraction method и layer alignment.

Немонотонный size result сохраняется как форма измеренной curve, не как
универсальный закон. Совпадение behavioral peak и geometric peak — полезная
гипотеза механизма, но не causal proof без intervention.

## 11. Distillation lineage

Student outcome декомпозируется по цепочке:

```text
teacher base
  -> teacher adaptation
  -> teacher merge/runtime
  -> silver input set
  -> generated labels/traces
  -> filtering and leakage controls
  -> student objective/adaptation
  -> student merge/export/runtime
  -> held-out and external evaluation
```

Нужно различать gold labels, teacher labels и teacher explanations. Без
ablation `gold-only vs labels-only vs labels+traces` нельзя приписывать gain
chain-of-thought. Offline teacher cost не входит в deployed parameter count,
но входит в training economics и воспроизводимость.

## 12. Low-resource language adaptation

Language adherence не равна fluency, grammar, task success, factuality или
English retention. Минимальная suite разделяет:

- script and requested-language adherence;
- native-speaker or calibrated judge quality;
- task-specific held-out result;
- code-switch and register control;
- English/general retention;
- contamination and translated-data lineage;
- tokenizer fertility или bytes/tokens;
- repetition, corrupt-token и long-context behavior.

`fastText` на шести ответах — smoke test. Много-seed held-out task с raw rows и
confidence intervals — более сильное evidence, но всё ещё domain-bounded.
Automated translation может быть data source и scorer confound одновременно.

## 13. Composition versus native modality

External encoder + projector + decoder LoRA является composed system, а не
доказательством native modality tuning. Для него сохраняются:

- identity и license каждого компонента;
- encoder output, projector и decoder dimensions;
- side-channel/token interface;
- trainable/frozen subtrees;
- prompt contract и LoRA scale;
- standalone component baselines;
- end-to-end held-out result;
- generic-runtime portability.

Model hub widget или standard loader не обязан понимать такой bundle. Private,
owner-only и public-release-ready состояния не смешиваются.

## 14. Modality stripping

Удаление encoders, projectors или PLE проверяется по четырём независимым
направлениям:

1. exact parameter/tensor diff;
2. memory namespace before/after;
3. text and multilingual parity;
4. compatibility with tokenizer, context, MTP, quantization and serving.

Снижение resident memory может быть намного больше размера удалённых weights
из-за precision, activation buffers и vocab-offset structures. Поэтому
parameter count не предсказывает process memory без runtime evidence.

## 15. Unseen-tool and adversarial-schema suite

Fixed-catalog tool gain не доказывает general tool use. Следующий уровень:

- unseen tools drawn after training;
- add/remove/reorder tools;
- rename function while preserving semantics;
- rename arguments and alter nesting/required fields;
- paraphrase or contradict descriptions;
- include hostile descriptions and irrelevant tools;
- validate tool choice, exact schema, arguments, no-call decisions and recovery.

Tool execution remains permissioned by the application. A model-emitted call is
untrusted data, even if schema-valid.

## 16. Privacy and memorization after adaptation

Document internalization or narrow CPT creates a separate privacy surface.
Useful probes include:

- canary and unique-string extraction;
- verbatim continuation at multiple prefix lengths;
- membership inference or nearest-neighbor alternatives;
- PII and licensed-text audits;
- base versus CPT/SFT/merged/quantized arms;
- utility/privacy curve as data repetition and adapter capacity change.

Retrieval, closed-book answer accuracy and factual recall do not measure
memorization risk. Отсутствие Gemma-specific evidence сохраняется как search
gap, а не как безопасный verdict.

## 17. Context-length curve after adaptation

`max_model_len=128K` и успешный allocation — только configuration facts.
Behavioral curve должна включать несколько depths, position sweeps, multiple
needles или task-specific evidence, output completion, looping, latency, memory
и base/tuned parity. Для языков с разной tokenizer fertility дополнительно
нужны word/byte-normalized distances.

## 18. Общая семейная матрица

Семейное сравнение допускается только на общей матрице:

```text
same dataset and split
+ same prompt/template and decoding
+ same adapter topology and hyperparameter search budget
+ same seeds and scorer revision
+ same task, retention, safety and long-context suite
+ explicit hardware and memory denominators
+ same export/runtime acceptance stages
```

Если размеры требуют разных batch или precision, различия сохраняются как
configuration axes. Итог — Pareto surface, а не один winner.

## 19. Источники и повторение

Повторение считается сильнее, когда независимы origin, data, runtime и
instrument. Несколько mirrors одного model card не являются replication.
Provider docs сильны для intended topology и availability; независимые papers
и executable artifacts сильнее для measured outcomes; forums сильны для
failure discovery и operational pressure, но не для incidence.

Generated source dossiers остаются быстрым входом в историю exact URI. Новый
проход сначала читает dossier, затем добавляет новый source appearance или
search probe. Dossier не утверждает свежесть страницы.

## 20. Stop rule и promotion boundary

Забег можно остановить, когда:

- причинная цепочка и metric passports достаточно различимы;
- основные counter-hypotheses проверены или сохранены probes;
- lifecycle gaps видимы по стадиям;
- weak/private/mutable evidence не повышено до независимого proof;
- следующий эксперимент имеет конкретные arms и acceptance criteria.

Даже полная матрица не получает автоматического promotion. Recon может
породить proposal для owner review; source truth, study acceptance, runtime
admission, routing и activation остаются в своих owner surfaces.
