# External Model Web Recon Lens v0.4

Статус: pre-canon исследовательский метод; не owner truth, не канон, не
`ModelClaim`, не `ModelStudy` и не автоматическое основание для выбора модели

Срез метода: 2026-09-04

Предшественник: `external-model-web-recon-method-v0.3.md`

Эмпирическая основа этой revision:

- [`Gemma 4 E2B/E4B fine-tuning and adapters`](gemma-4-e2b-e4b-finetuning-adapters-2026-09-04.md);
- [`Gemma 4 E2B/E4B adaptation frontier`](gemma-4-e2b-e4b-adaptation-frontier-2026-09-04.md).

Это развитие общей линзы v0.3 под давлением адаптации. Оно не превращает
Gemma 4 в шаблон для всех семейств и не доказывает полноту метода.

## 1. Что сохраняется из v0.3

Без изменения действуют:

- pre-canon и owner boundaries;
- сегментная, временная и origin-aware работа с источниками;
- атомарные observations вместо пересказа страницы целиком;
- точная привязка subject, configuration, outcome и instrument;
- outcome ledger `requested -> executed -> artifact -> verified -> reported`;
- denominator, confound и counterevidence ledgers;
- отсутствие автоматического consensus, ranking и promotion;
- supersession только через явную связь с сохранённой историей.

v0.4 добавляет две недостающие вещи: наблюдаемое покрытие самого поиска и
более строгую проверку причинности адаптационных результатов.

## 2. Coverage ledger: искать также пробелы

Список найденных источников не показывает, что исследователь пытался
опровергнуть свою картину. Поэтому забег может сохранять `search_probes`.
Каждый probe отвечает на один вопрос и фиксирует:

- варианты запроса или стратегии поиска;
- роли источников, которые искались;
- время поиска;
- найденные source и observation refs;
- состояние результата;
- ограничения и следующий ход.

Допустимые состояния различают:

```text
qualified_evidence_found
mixed_evidence_found
weak_signal_only
no_qualified_source_found
access_limited
deferred
```

`no_qualified_source_found` означает только: в указанное время, указанными
способами и по указанным критериям квалифицированный источник не найден. Это
не утверждение, что доказательства не существуют. `weak_signal_only` сохраняет
направление без повышения его до observation, если найденная поверхность не
достигает заявленного порога.

Coverage ledger нужен не для квоты. Он позволяет следующему агенту быстро
увидеть уже пройденные направления, ограничения и наиболее ценный следующий
контрпоиск. Старые packets остаются валидны без `search_probes`.

## 3. Пять ступеней зрелости адаптации

Фраза «поддерживает LoRA» слишком широка. Для каждого пути различаются:

```text
surface exists
  -> implementation accepts configuration
  -> execution completes
  -> intended parameters or towers actually change behavior
  -> exported/served artifact preserves the semantic delta
```

Отсюда:

- notebook или код доказывает доступность маршрута, но не завершённый run;
- завершённый trainer и ненулевые LoRA tensors не доказывают полезный
  behavioral delta;
- успешная загрузка адаптера не доказывает, что runtime его применил;
- валидный файл и совпавший размер не заменяют digest identity;
- работающий HF checkpoint не доказывает эквивалентность merged, quantized,
  GGUF, MLX или vLLM варианта.

Для каждого этапа фиксируется собственное свидетельство и собственный
failure mode. Более зрелая ступень не выводится из предыдущей.

## 4. Механизм отдельно от метрики

Адаптация может улучшить score, не улучшив предполагаемый механизм. Поэтому
сильное observation по возможности разделяет:

- behavioral outcome;
- mechanism probe;
- scorer/parser;
- seed и run variance;
- intervention control.

Полезные intervention controls:

- убрать управляющий контекст, закон, schema или modality input;
- подставить нерелевантный контекст;
- повернуть порядок вариантов ответа;
- пересчитать альтернативным scorer;
- сравнить несколько seeds;
- проверить base, tuned и ablation на одном instrument revision.

Если parser и constrained scorer меняют знак сравнения, сохраняются оба
результата и tension разрешается по instrument, а не усреднением. Если tuned
модель лучше отвечает с данным законом, но difference-in-differences не
показывает большего использования закона, корректное ядро — behavioral gain
без подтверждённого mechanism gain.

## 5. Training proxy, selection и held-out acceptance

Training loss, validation loss и целевой outcome — разные инструменты. Для
низкоэнтропийных или шаблонных targets loss может улучшаться одновременно с
ухудшением OOD-задачи.

Минимальная сильная цепочка:

```text
train signal
  -> disjoint development selection
  -> frozen held-out evaluation
  -> orthogonal retention/safety probes
```

В packet сохраняются:

- правило выбора checkpoint;
- использовался ли test set при выборе;
- data split и contamination guard;
- повторные epochs/checkpoints, если они меняют вывод;
- LoRA rank, alpha и merge strength как отдельные оси;
- negative controls и orthogonal suites.

Ослабление adapter delta при merge — не косметика и не универсальный рецепт.
Это конфигурация, которую нужно выбирать на disjoint development surface и
проверять заново после export.

## 6. Data quality, capacity и optimizer coupling

Фраза «больше rank лучше» недопустима без масштаба corpus, learning rate и
состава данных. Наблюдение должно по возможности разделять:

```text
data quality and target entropy
corpus size and diversity
adapter capacity and topology
learning rate and schedule
precision and quantization
number of steps and seeds
```

Если изменение rank одновременно меняет learning rate, вывод формулируется
как coupled configuration, пока отдельная абляция не изолирует параметры.
Прямая проверка counts, truncation, label masking и batch composition должна
предшествовать архитектурной диагностике.

## 7. Reward и judge sensitivity

Для preference tuning и RL reward является частью instrument identity.
Изменение reward может перевести один и тот же маршрут от collapse к
измеримому улучшению. Поэтому сохраняются:

- reward definition и scale;
- rollout count, steps, seeds и entropy regime;
- относительные и абсолютные acceptance bars;
- deterministic metrics рядом с LLM judges;
- judge identity, prompt и direction;
- противоречия между top-1, rank, percentile и preference.

Высокий win rate против base не означает пригодность, если обе модели не
проходят абсолютный критерий. Несогласие judges — не шум, который можно
скрыть средним; это evidence о зависимости вывода от adjudicator.

## 8. Silent-path validation для multimodal adapters

Мультимодальный batch может завершаться без ошибки, даже когда modality input
не дошёл до intended tower. Поэтому проверка «trainer запустился» недостаточна.

Для audio/vision и других side inputs проверяются, когда доступны:

1. batch keys после collator;
2. placeholder count и фактическое token expansion;
3. shapes и masks modality tensors;
4. forward hook или gradient evidence нужной tower/subtree;
5. label masking вокруг modality tokens;
6. число matched target modules и их namespace;
7. counterfactual без modality input;
8. post-training modality-specific held-out delta.

Это долговечная acceptance boundary. Она применима к любому multimodal
семейству и не кодирует названия Gemma modules в validator.

## 9. Composition, merge и retention как Pareto

Несколько adapters можно сложить технически, но это не доказывает сохранение
их функций. Для composition нужны:

- точная base identity всех компонентов;
- target namespaces, rank/alpha и training lineage;
- merge algorithm, weights, density, masks и ordering;
- component baselines и merged result на общей suite;
- retention, interference и style/task deltas;
- отдельная проверка merged/quantized/served artifact.

Один удачный TIES, SLERP или weighted merge является artifact-backed
существованием и гипотезой для replication. Он не создаёт общего рейтинга
алгоритмов композиции.

## 10. Runtime semantic delta

Runtime acceptance для adapter-bearing artifact требует парного теста:

```text
same base + same prompt + deterministic decode
adapter disabled vs adapter enabled
expected semantic delta observed
artifact identity and mapping verified
```

Отсутствие exception, HTTP 200, успешный health check или сообщение «adapter
loaded» не являются таким тестом. Для dynamic adapters дополнительно нужны
name mapping, tower policy, max rank, concurrency и per-request selection.

Если исправление существует только в открытом PR или cherry-pick, состояние
остаётся revision-sensitive. Issue closure, merged PR, released package и
независимый rerun сохраняются раздельно.

## 11. MTP и другие связанные артефакты

После адаптации target совместимость с drafter — свойство пары:

```text
target bytes + drafter bytes + runtime revision
+ draft depth + workload + acceptance instrument
```

Нужны target-only и paired arms, deterministic output equivalence,
acceptance rate, throughput, hardware и prompt/output distribution.
Совместимость joint-tuned пары не доказывает совместимость произвольного LoRA
с исходным drafter. И наоборот, один измеренный adapted derivative может
сузить прежний пробел, не превращаясь в семейную гарантию.

## 12. Metric lineage и исправление инструмента

Когда обнаружена ошибка счётчика или harness, старое число не стирается.
Сохраняются:

```text
metric -> instrument revision -> discovered defect
       -> corrected computation -> rerun -> revised observation
```

Особенно опасны streaming APIs, где один event может не равняться одному
token, и агрегаты, меняющие denominator между runs. Исправленный результат
получает новую instrument identity и явную связь с прежним наблюдением.

## 13. Остановка и продолжение разведки

Забег можно остановить, когда:

- сильные observations имеют exact source segments и transfer limits;
- основные counter-hypotheses либо проверены, либо отражены search probes;
- найденные противоречия разложены по axis/instrument/time;
- отрицательные результаты сформулированы как search state, не как мировая
  истина;
- следующий агент видит наиболее ценный незакрытый вопрос.

Причины продолжать:

- новый release меняет issue/PR/runtime state;
- появляется независимая replication;
- результат не имеет seed, scorer или intervention control;
- неизвестна переносимость на export/serve;
- nominal context заявлен, но long-context behavior после adaptation не
  измерен;
- component и merged adapters не проверены на общей suite.

## 14. Promotion boundary

Recon packet по-прежнему может породить только предложение. Наличие
`search_probes`, нескольких независимых origins, исправленного scorer или
полного adapter bundle не даёт автоматического пути в `source/`.

Продвижение требует отдельного owner review, подходящего контракта и своей
evidence chain. Method v0.4 делает неопределённость и покрытие наблюдаемыми;
он не подменяет ими истину владельца.
