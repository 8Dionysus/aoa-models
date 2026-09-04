# Gemma 4 E2B/E4B: adaptation frontier beyond the first recipes

Статус: глубокая pre-canon разведка; не `ModelClaim`, не принятый
`ModelStudy`, не runtime admission и не рекомендация модели

Срез источников: 2026-09-04

Метод: [`External Model Web Recon Lens v0.4`](external-model-web-recon-method-v0.4.md)

Предшественник: [`fine-tuning and adapters`](gemma-4-e2b-e4b-finetuning-adapters-2026-09-04.md)

## Короткий ответ

Нет, первым проходом тема не исчерпывалась. После выхода за пределы official
recipes обнаружились по меньшей мере семь дополнительных исследовательских
фронтов: scorer/mechanism separation, data-quality/capacity coupling,
preference/RL reward sensitivity, silent multimodal failures, adapter
composition, serving-time no-op и post-adaptation MTP.

Главный новый результат — не список удачных LoRA. Повторяется более строгий
рисунок:

> Адаптация является цепочкой из данных, target topology, optimizer/reward,
> scorer, export, runtime mapping и paired artifacts. Положительный сигнал на
> одной ступени не переносится автоматически на следующую.

Для E2B появились сильные controls по scorer и использованию контекста, а
также GRPO-эксперименты с явными неудачами. Для E4B корпус богаче в области
LoRA specialization, merge/composition, multimodal DoRA и адаптированного MTP.
Это асимметрия доступного evidence, не рейтинг размеров.

## 1. Как расширился сам метод

Этот забег одновременно изменил исследовательскую линзу:

1. В `ReconRun` добавлен необязательный coverage ledger `search_probes`.
   Теперь сохраняются не только найденные источники, но и вопросы, поисковые
   стратегии, отрицательные результаты и следующий контрпоиск.
2. Зрелость adaptation split на пять ступеней: surface, implementation,
   execution, semantic effect, exported/served portability.
3. Scorer, mechanism, seed и intervention стали отдельными осями.
4. Для multimodal маршрутов введена silent-path проверка: batch keys, modality
   expansion, tower forward/gradient и post-training counterfactual.
5. Runtime acceptance требует наблюдаемого semantic delta, а MTP — парного
   target/drafter результата.
6. Metric lineage теперь сохраняет ошибочный instrument, исправление и rerun,
   а не переписывает историю.

Эти изменения общие: schema и validator не знают названий Gemma, E2B, E4B,
LoRA или конкретных библиотек.

## 2. Карта покрытия

| Направление | E2B | E4B | Что найдено | Главный пробел |
|---|---:|---:|---|---|
| SFT/LoRA mechanism controls | сильный | средний | три seeds, scorer rotation, context removal; held-out specialization | общей suite между размерами нет |
| Data quality/capacity | нет | сильный | около 100 runs, corpus/rank/LR arc | 4-bit и single-seed ограничения |
| Preference/DPO | нет | средний | domain-level gains и regressions | круговой NLI scorer, seed не указан |
| RL/GRPO | средний | weak | reward-collapse и dense-reward recovery | нет независимой replication |
| Multimodal adapters | средний | средний | vision LoRA, audio DoRA, silent audio fix | разные tasks и author-only evals |
| Adapter composition | weak | средний | TIES и masked components | мало prompts, нет общего baseline corpus |
| Export/serving | средний | средний | vLLM no-op и namespace/tower issues | часть fixes остаётся unreleased/open |
| Long context after tuning | gap | gap | только nominal serve claims | нет квалифицированного 128K behavior eval |
| MTP after adaptation | нет | средний | joint tuning и один derivative pair | нет общей LoRA/drafter matrix |

`gap` означает состояние поиска этого забега, а не доказанное отсутствие.

## 3. E2B: scorer может перевернуть вывод

Свежая независимая работа
[`Do Small Models Use the Law You Give Them?`](https://arxiv.org/html/2608.30327v1)
дала наиболее сильную на сегодня E2B-цепочку controls:

- 2 165 reviewed bilingual fine-tuning examples;
- group split по act/section: 1 728 train, 220 validation, 217 internal test;
- три LoRA seeds: 17, 42 и 73;
- E2B NF4 QLoRA, rank/alpha 16, все LM projections, sequence 1 536,
  effective batch 16, 216 steps на одном T4 16 GB;
- constrained option-letter logit scoring и циклическая rotation вариантов;
- отдельный 150-item контроль с governing section, без него и с нерелевантным
  материалом.

На 398 Bar Council outputs знак сравнения E2B зависит от инструмента:

- exact-line parser: tuned лучше reference на 10,1 percentage points;
- constrained scoring: tuned хуже на 2,5 points;
- parser delta повторяется на всех трёх seeds: +11,3, +10,1, +10,8;
- constrained delta также стабильно отрицательна: −1,5, −2,5, −1,8.

На supplied-law control reference показывает 70,0% без закона, 84,7% с ним и
69,3% после удаления governing section. Средний tuned E2B: 58,9%, 78,7% и
64,4%. Закон помогает обоим, но difference-in-differences не показывает, что
fine-tuning увеличил зависимость от governing provision.

Поддерживаемое ядро поэтому узкое: LoRA изменила surface behavior, но не
продемонстрировала усиление заявленного механизма использования закона; parser
способен приписать адаптеру противоположный результат.

Есть и implementation lesson. Первый E2B setup случайно matched 249
multimodal modules из 494 вместо 245 LM modules; исправленный маршрут имел 490
LoRA tensors, плюс были исправлены prompt loss masking и shuffle. В статье
зафиксировано семь training attempts. Exact model name не защищает от неверной
target topology.

## 4. E4B: data quality сильнее rank, но только после capacity gate

Работа
[`Data Quality over Capacity`](https://arxiv.org/html/2607.21861v1)
исследует закрытую интернализацию документов в 4-bit Gemma 4 E4B примерно на
100 runs:

- 15-document curation — короткие canonical answers и удаление trivia —
  поднимает общий результат с 57,7% до 85,7%; curated recall — 84,2%;
- BM25-RAG с base reader даёт 58,9%, realistic gold-chunk oracle — 65,6%;
- LoRA применяется к MLP всех 42 layers в MLX на Apple Silicon;
- pipeline разделён на CPT-like document exposure и supervised QA stage.

Но «data quality важнее capacity» действует после capacity gate. При росте
corpus rank должен расти, а rank и learning rate оказались спутаны:

- 25 documents, rank 64: 71,1% recall;
- 50 documents: rank 64 — 50,0%, rank 128 — 64,0%;
- 100 documents: rank 128 — 55,2%; rank 256 при 4e-5 — 46,7%, при 2e-5 —
  61,6%.

Авторы сначала неверно диагностировали несколько причин; прямые counts
исключили предполагаемую truncation. Это важнее самой победной цифры: capacity,
optimizer и data intervention надо разделять экспериментально.

Ограничения существенны: один seed 42, максимум 99 документов, 4-bit
quantization как confound, max sequence 3 072 (2 048 для rank 256), а метрика
стилистически благоприятна для adapter outputs. Это не доказательство
long-context retention и не универсальная формула rank.

## 5. E4B: specialization — не одна ось

Предыдущий забег уже сохранил
[`Internalizing Tool Knowledge`](https://arxiv.org/html/2605.17774v2):
description-free E4B QLoRA улучшает AT-F1 в fixed catalog, но MCQ retention
падает с 84% base до 69% при rank 8 и 67% при rank 32.

Новый artifact-backed контроль
[`gemma-4-E4B-wallet-ft-v5`](https://huggingface.co/ef-dai-team/gemma-4-E4B-wallet-ft-v5)
делает selection failure ещё видимее:

- 2 288 examples, один epoch, LoRA r=16/alpha=16, attention+MLP projections;
- отдельный 145-case development set и замороженный 1 000-case exact-match
  benchmark;
- финальный adapter merged с strength 0,75;
- tuned score 94,9% без safety clause и 95,1% с ним против base 90,3%/91,0%;
- за три epochs validation loss снижался, но OOD accuracy упала на 14,5
  points; выбор по `eval_loss` выбирал худший checkpoint;
- ослабление полной adapter delta восстановило прежние capabilities; strength
  выбрана на dev, а test оценён один раз.

Это единичный community/provider artifact и узкая wallet-задача. Однако он
даёт воспроизводимый counterexample двум популярным shortcuts: lowest val loss
не обязан быть лучшим checkpoint, а merge strength 1.0 не является нейтральной
константой.

Дополнительный E4B
[`Hybrid-DPO`](https://arxiv.org/abs/2605.04539v4) использует SFT из 13 211
examples, затем всего 164 preference pairs для E4B. NLI по доменам меняется
неравномерно: Cardiff 0,2117→0,3505, Auckland 0,3911→0,4377, оба medical
domain растут, Sydney падает 0,2469→0,2309; answer-correctness также местами
ухудшается.

Здесь scorer входит в причинную петлю: один DeBERTa-NLI участвует и в выборе
preference pairs, и в основной оценке. Отдельный LLM-judge предпочитает более
многословный SFT logically stronger DPO в 69% сравнений; self-preference того
же judge достигает 95%. Результат полезен как domain-level Pareto и сильное
требование независимого held-out scorer, но не как общий DPO gain.

## 6. E2B GRPO: reward определяет, что вообще является обучением

Artifact
[`nla-gemma-4-e2b`](https://github.com/SolshineCode/nla-gemma-4-e2b)
сохраняет не только удачный run, но и неудачные режимы:

- первая GRPO sweep: пять rewards, четыре entropy regimes, 120 rollouts;
- только r40 остаётся coherent; остальные варианты уходят в gibberish,
  whitespace или evasion;
- все варианты остаются на chance по L2; улучшения над SFT нет;
- later dense cosine reward на M40 даёт routing 0,524→0,617→0,674 для
  base→500→1 000 steps;
- within-domain percentile улучшается 0,448→0,421→0,402, где меньше лучше;
- paired 500→1 000 p=1,5e-7;
- два независимых seeds есть на 500 steps, но 1 000 — продолжение seed 0.

Даже внутри удачного режима метрики спорят: top-1 count идёт 3→9→7, тогда как
rank metric улучшается. Qwen-judge предпочитает dense1000 в 88,1% пар, Claude
Haiku даёт null и проваливает контроль предыдущего эксперимента. А абсолютный
36-row usability bar против Anthropic NLA остаётся 0,0/3 для base, 500 и 1 000.

Поддерживаемое ядро: dense reward способен улучшить несколько относительных
NLA metrics E2B, но результат зависит от reward, metric и judge и пока не
прошёл абсолютный acceptance bar.

Текущий official-style
[`Unsloth E2B GRPO notebook`](https://github.com/unslothai/notebooks/blob/main/nb/Gemma4_(E2B)_Reinforcement_Learning_2048_Game.ipynb)
показывает runnable contour — E2B, LoRA r=32, max sequence 4 096, 60 steps —
но сохраняет только assertion ненулевых LoRA tensors. Это implementation
surface, не held-out behavioral evidence.

Связанные loader и text-logits defects имеют merged fixes
([#6089](https://github.com/unslothai/unsloth/issues/6089),
[#5121](https://github.com/unslothai/unsloth/issues/5121)), однако свежий
полный rerun notebook после обоих fixes не найден. Мerged fix и observed
end-to-end currentness остаются разными утверждениями.

## 7. Multimodal: успешный trainer может молча не видеть modality

В [Unsloth issue #6004](https://github.com/unslothai/unsloth/issues/6004)
audio collator удалял `input_features`, `<|audio|>` оставался одним token, а
audio tower не выполнялась — без ошибки trainer. Исправление
[`unsloth-zoo#723`](https://github.com/unslothai/unsloth-zoo/pull/723)
проверено независимым AMD trace на наличии tensors, token expansion и audio
encoder forward; полный backward там не завершён из-за отдельного ROCm/bnb
ограничения.

Именно этот случай породил долговечную silent-path acceptance boundary. Для
multimodal adapters нужно наблюдать путь данных, а не только отсутствие
exception.

Два model-card эксперимента показывают разные Pareto:

- [`E4B audio-v3`](https://huggingface.co/bnovikov/gemma-4-e4b-audio-v3):
  single-stage DoRA r=32/alpha=64, 91k audio QA, 200 steps, RTX 4090 24 GB;
  MMAU test-mini 55,0→58,8 на 1 000 items. Предварительная адаптация audio
  encoder на ~100k mixed captions оказалась хуже сохранения pretrained
  encoder. Есть subcategory regressions, включая Emotion Flip −15 points;
  checkpoint выбран после OOM при следующем save, не по заранее заданному
  stopping rule.
- [`E2B OceanGuard`](https://huggingface.co/asferrer/gemma-4-E2B-it-oceanguard-marine-debris):
  vision+LM LoRA r=16/alpha=32, held-out n=200; mAP@0.5 0,1067→0,3256. Но
  language-only baseline около 0,3253, поэтому глобальная прибавка от vision
  adaptation почти отсутствует, хотя отдельные texture-rich classes растут.
  JSON validity падает с 94,5% language-only до 88,5%; Metal Debris остаётся
  нулевым. Доступен GGUF, но это не равняется подтверждённой semantic parity.

Оба результата авторские и task-bound. Вместе с silent audio failure они
поддерживают не семейный quality claim, а требование: отделять multimodal data,
tower adaptation, per-class effect и format retention.

## 8. Composition: компоненты не складываются по названию

[`Gemma4-E4B-TIES-3mask-r64`](https://huggingface.co/ToastyPigeon/Gemma4-E4B-TIES-3mask-r64)
объединяет три независимо обученных r64/alpha16 adapter через PEFT TIES,
density 0,2 и равные weights. Все компоненты применяют instruct-subspace
gradient mask.

По авторской suite base IFEval — 83,36. Masked components теряют от 6,84 до
8,50 points, тогда как unmasked comparators — от 12,20 до 14,97. TIES merge
теряет только 0,92; style probability растёт с ~0,10 до 0,343, dialogue score
с 0,42 до 0,51.

Это полезное artifact-backed доказательство, что mask+merge contour существует
и может удержать instruction following лучше компонентов. Но style eval имеет
лишь 10 prompts при temperature 1, density проверена одной точкой, нет
held-out leakage control и общей независимой репликации. Правильный disposition
— replicate, не «TIES работает для E4B вообще».

## 9. Serving: loaded adapter может быть семантически выключен

Открытый [vLLM issue #41754](https://github.com/vllm-project/vllm/issues/41754)
фиксирует Gemma 4 adapters, которые загружаются без ошибки, но дают
byte-identical output с base. Связанный
[`vllm#39816`](https://github.com/vllm-project/vllm/pull/39816) остаётся
открытым на срезе; cherry-pick исправляет dense E2B/31B у нескольких участников,
а MoE требует дополнительного expert mapping.

Соседний [issue #41702](https://github.com/vllm-project/vllm/issues/41702)
показывает другой слой: старые broad Unsloth adapters содержат vision tower
names, которые vLLM отвергает. Vision-LoRA support был merged отдельно, тогда
как text mapping change не был принят.

Это повторяет общий урок из MLX round-trip предыдущего забега: adapter
portability — не свойство расширения файла. Минимальный test обязан сравнивать
base и adapter-enabled output на deterministic probe с заранее ожидаемым
semantic delta и точной artifact identity.

## 10. MTP после адаптации: пробел сузился, но не закрылся

Предыдущий забег нашёл provider joint-tuning E4B target+drafter, но не
arbitrary LoRA compatibility. Новый derivative
[`Gemma-4-E4B ... MTP NVFP4`](https://huggingface.co/Adolphsson/Gemma-4-E4B-Uncensored-HauhauCS-Aggressive-MTP-NVFP4)
добавляет измеренный post-adaptation pair:

- vLLM 0.28, RTX 5090, greedy, fresh server для каждого K;
- два runs по шести prompts, cap 300 output tokens;
- K=0 около 242,5 tok/s; K=5 около 528–534 tok/s, примерно 2,1x;
- acceptance при K=5 — 0,305; при K=1 — 0,669 и снижается с глубиной.

Ранние 624–700 tok/s не воспроизвелись. Причина — streaming harness считал
events как tokens, хотя MTP event мог содержать несколько token deltas. После
исправления числа были пересчитаны. Без дополнительного `sitecustomize` patch
server отвечал HTTP 200, но выдавал деградированный текст; неверный patch
drafter давал acceptance 0/15.

Это сильный пример metric lineage и того, почему health check не является
semantic acceptance. Он также сужает прежний gap: по крайней мере один E4B
fine-tuned derivative измеренно работает с official assistant. Но это
community assembly с runtime patch, а не гарантия для произвольного E4B LoRA.

## 11. Что не удалось подтвердить

После прямых поисков не найден квалифицированный post-adaptation E2B/E4B
benchmark, который проверяет long-context behavior близко к заявленным 128K.
Найдены artifacts, обученные на 2–3K, способные конфигурационно запускаться с
большим `max_model_len`; например,
[`Gemma-4-E4B-GLM5.1-distill`](https://huggingface.co/Dhiaul/Gemma-4-E4B-GLM5.1-distill)
прямо говорит, что long reasoning формально не оценивался.

Это `no_qualified_source_found` для данного capture interval, а не утверждение
об отсутствии таких работ. Nominal positional capacity и demonstrated
post-tuning long-context behavior остаются разными observations.

Также не найден общий experiment, который одновременно сравнивает E2B и E4B
на одном dataset, LoRA topology, seed set, scorer, retention suite, export и
runtime. Семейный Pareto поэтому нельзя свести к одной таблице победителя.

## 12. Повторяющиеся, уже достаточно устойчивые направления

Через независимые методы повторяются следующие требования:

1. **Целевая специализация и retention образуют Pareto.** Это видно в E4B tool
   QLoRA, CPT, DPO, wallet merge strength, E2B/E4B multimodal tasks.
2. **Data/reward quality может доминировать над размером adapter**, но после
   capacity gate и в связке с learning rate.
3. **Scorer является частью результата.** Parser, constrained logits, NLI
   grader, rank metric и LLM judge меняют не только величину, но иногда знак.
4. **Silent success реален.** Multimodal tower или served adapter может не
   работать при успешном startup/training loop.
5. **Export/runtime — новая экспериментальная ступень.** Необходимо заново
   подтвердить semantic delta.
6. **Связанные артефакты нужно принимать парами.** MTP после adaptation зависит
   от target, drafter, runtime, K и workload.
7. **Отрицательный поиск — полезный результат**, если сохраняет scope,
   ограничения и следующий шаг.

Это не свойства «Gemma 4 вообще». Это повторяющиеся правила исследования,
подкреплённые несколькими независимыми origin groups.

## 13. Следующие наиболее ценные эксперименты

1. Одна paired E2B/E4B матрица: одинаковые data split, target modules, rank,
   seeds, scorer, retention и hardware accounting.
2. Для E2B legal LoRA — отдельный mechanism suite с alternative scorer и
   unseen acts; для E4B document LoRA — multi-seed rank×LR factorial.
3. End-to-end current Unsloth E2B GRPO rerun после merged loader/logits fixes с
   frozen held-out task и absolute bar.
4. Audio/vision silent-path probes, пригодные для любого collator/runtime.
5. Base→adapter→merged→quantized→served semantic parity suite на одних prompts.
6. E4B composition factorial: weighted sum, TIES, masks, density и adapter
   strength на общей retention/task suite.
7. Post-adaptation context-length curve, а не одиночный `max_model_len`.
8. Target/drafter matrix: base, LoRA-only target, joint-tuned pair, разные K и
   output distributions с исправленным token counter.

## 14. Итоговая граница

Материала уже достаточно, чтобы сделать aoa-models заметно богаче: не только
сохранить новые результаты, но и научить каждый следующий проход видеть
непройденные направления и различать ступени доказательства.

Недостаточно материала для:

- универсального рейтинга E2B против E4B;
- общего «лучшего rank/alpha/merge strength»;
- утверждения о сохранении 128K после tuning;
- гарантии vLLM adapter correctness;
- произвольной совместимости adapted target с MTP drafter;
- автоматического promotion в owner source.

Зрелый результат этого прохода — расширенная карта, проверяемые contradictions,
сохранённые пробелы и более сильный контур следующего эксперимента.
