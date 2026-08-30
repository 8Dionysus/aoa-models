# External Model Web Recon Lens v0.2

Статус: проект исследовательского метода; не owner truth, не канон и не автоматическое основание для `ModelClaim`  
Срез метода: 2026-08-29  
Местность назначения: pre-canon research intake для `aoa-models`

## 1. Назначение

Веб-разведка нужна `aoa-models` не как поток «отзывов о моделях», а как способ постепенно обнаруживать устойчивые свойства, границы переносимости, эксплуатационные давления и вопросы для собственных исследований.

Основная единица метода — не страница, не рейтинг и не характеристика модели. Это:

> атомарное наблюдение о точно очерченном субъекте, полученное определённым инструментом в определённый момент и сопровождаемое известными ограничениями.

Линза не должна отбрасывать ранние, субъективные или неудобные сигналы. Она должна сохранять их в правильной роли:

- единичный форумный эпизод может быть ценным `watch` или `study_trigger`;
- официальный benchmark остаётся provider evidence, а не независимой истиной;
- независимый benchmark устанавливает результат только в своём task pool, harness и grader;
- повторяющийся operational symptom не становится свойством модели, пока не отделены продукт, runtime, quota policy и orchestration;
- противоречие не устраняется усреднением, если стороны измеряли разные поверхности.

Цель v0.2 — сформировать достаточно мягкую, но различающую приёмную поверхность, чтобы последующие забеги могли улучшать сам метод под давлением реального корпуса.

## 2. Что именно мы пытаемся узнать

Веб может давать по меньшей мере шесть разных типов материала. Их нельзя складывать в один рейтинг доверия.

| Target kind | Пример вопроса | Возможный будущий потребитель |
|---|---|---|
| `provider_fact` | Какая цена или заявленная длина контекста действовала в дату X? | realization/economics candidate |
| `benchmark_result` | Какой результат показала конфигурация в benchmark revision Y? | `ModelStudy` candidate |
| `model_behavior` | Возвращается ли определённый паттерн при смене продукта и harness? | bounded `ModelClaim` candidate |
| `runtime_behavior` | Возникает ли сбой только в Codex build X? | runtime owner / realization currentness |
| `product_policy` | Как subscription quota считается относительно API tokens? | product surface; обычно не `ModelClaim` |
| `operational_pressure` | На что регулярно жалуются пользователи и что стоит воспроизвести? | watchlist / study trigger |

Первый обязательный вопрос атомизации: **о чём именно это свидетельство?** Если ответ неизвестен, наблюдение сохраняется с `target_kind: unresolved`, а не приписывается модели по умолчанию.

## 3. Четыре минимальные сущности

Для первого приземления достаточно четырёх верхнеуровневых примитивов. Остальные различия лучше пока хранить полями, а не плодить отдельные объекты.

### 3.1 `SourceCapture`

Фиксирует доступный источник и конкретные использованные фрагменты.

Минимум:

```json
{
  "source_id": "src-...",
  "uri": "https://...",
  "source_class": "provider_doc | paper | benchmark | issue | forum",
  "publisher": "...",
  "published_at": null,
  "updated_at": null,
  "captured_at": "...",
  "origin_group": "...",
  "dependency_refs": [],
  "segments": [
    {
      "segment_id": "seg-...",
      "locator": "heading/table/issue-comment/artifact",
      "effective_from": null,
      "effective_to": null,
      "digest": null
    }
  ]
}
```

Почему нужен segment level: страница релиза может получить новую шапку, сохранив историческую таблицу; live leaderboard меняется без нового URL; issue может содержать исходный репорт, позднюю диагностику и closure с разным смыслом.

`origin_group` отвечает на вопрос «сколько независимых происхождений у сигнала?». Десять статей, повторяющих одну provider table, дают десять URL, но один origin.

### 3.2 `ExternalObservation`

Одна проверяемая формулировка или измерение.

```json
{
  "observation_id": "obs-...",
  "statement": "...",
  "target_kind": "benchmark_result",
  "subject": {
    "family": "gpt-5.6",
    "model": "gpt-5.6-sol",
    "snapshot": null,
    "provider": "openai",
    "product": "api",
    "runtime_version": null
  },
  "configuration": {
    "reasoning_effort": "high",
    "route": null,
    "context_policy": null,
    "tools": [],
    "permissions": null,
    "harness": "...",
    "instrument_revision": "...",
    "grader": "..."
  },
  "outcome": {},
  "source_segment_refs": ["src-...#seg-..."],
  "confounds": [],
  "evidence_posture": "method_backed_observation",
  "disposition": "cluster",
  "observed_at": "..."
}
```

Наблюдение должно быть атомарным. Фраза «Sol лучше, дешевле и надёжнее» раскладывается минимум на три observations, вероятно с разными denominators и разным контрсвидетельством.

### 3.3 `ObservationCluster`

Не «черта модели», а объяснимая связь нескольких observations.

```json
{
  "cluster_id": "clu-...",
  "label": "Harness и state могут доминировать над tier",
  "observation_refs": ["obs-..."],
  "independent_origin_count": 3,
  "modality_count": 3,
  "temporal_span_days": 40,
  "supported_scope": "...",
  "counterevidence_refs": [],
  "unresolved_configuration_gaps": [],
  "posture": "cross_modal_pattern",
  "next_action": "owned replication"
}
```

Кластер хранит и поддерживаемое ядро, и границу. Он не обязан сводиться к одной положительной формуле; `split_required` часто является более зрелым результатом, чем искусственный consensus.

### 3.4 `ReconRun`

Контейнер воспроизводимости забега:

- вопрос и временной срез;
- discovery queries и strata;
- inclusion/exclusion decisions;
- версии метода и корпуса;
- неизвлечённые или недоступные источники;
- review state;
- ссылки на source captures, observations, clusters и tensions.

`ReconRun` позволяет позднее понять, почему источник отсутствует и что изменилось между v0.2 и v0.3.

## 4. Не score, а вектор доказательности

Единый confidence score создаёт ложную взаимозаменяемость: хороший метод не компенсирует неизвестный субъект, а много ссылок не компенсируют общий origin. Для каждого observation/cluster полезен вектор:

| Ось | Что спрашивает |
|---|---|
| `subject_binding` | Известны ли model/snapshot/provider/product/runtime? |
| `configuration_completeness` | Известны ли effort, route, tools, permissions, context и harness? |
| `directness` | Это raw outcome, первичный отчёт или пересказ? |
| `origin_independence` | Сколько независимых производителей наблюдения? |
| `method_exposure` | Видны ли задания, repeats, scoring и exclusions? |
| `artifact_access` | Доступны ли outputs, logs, files, tests или grader traces? |
| `repeatability` | Есть ли повторы и variance, а не один удачный прогон? |
| `temporal_stability` | Возвращается ли сигнал после обновлений? |
| `counterevidence_coverage` | Искалось ли качественное опровержение? |
| `transfer_distance` | Насколько далеко claim уходит от измеренной задачи? |
| `confound_load` | Сколько правдоподобных альтернативных причин не изолировано? |

Вектор не обязан быть числовым. Для v0.2 достаточно `known / partial / absent` плюс пояснение. Числа стоит вводить только там, где consumer действительно использует их как контракт.

## 5. Evidence posture и disposition — разные словари

### Evidence posture

- `anecdotal_signal` — единичное первичное свидетельство;
- `recurring_pressure` — несколько независимых reports об operational surface;
- `method_backed_observation` — описаны task, run и scoring;
- `artifact_backed_observation` — доступны raw artifacts или проверяемый outcome;
- `cross_modal_pattern` — согласование разных методов/источников;
- `contradictory` — качественное контрсвидетельство не снято;
- `stale_for_current_subject` — исторически полезно, currentness текущей реализации отсутствует;
- `propagation_only` — новый URL не создаёт нового origin.

### Disposition

- `preserve` — сохранить без сильного вывода;
- `cluster` — связать с родственными observations;
- `watch` — пересмотреть после времени/события;
- `replicate` — сформировать собственный опыт;
- `review_for_study` — достаточно определённый subject/method для кандидата `ModelStudy`;
- `review_for_claim` — возможен bounded claim после owner review;
- `route_to_runtime_owner` — материал не о модели;
- `reject_as_propagation` — не считать независимым подтверждением.

Posture говорит, **что у нас есть**. Disposition — **что делать дальше**. Например, единичный, но подробно документированный разрушительный эпизод может иметь posture `anecdotal_signal` и disposition `replicate`, а не «низкую ценность».

## 6. Временная модель

Для быстро меняющихся моделей одного `published_at` мало. Нужны:

- `published_at` — когда материал появился;
- `source_updated_at` — когда издатель изменил страницу;
- `captured_at` — когда мы видели конкретный фрагмент;
- `observed_at` — когда произошло измерение/эпизод;
- `effective_from` / `effective_to` — когда цена, alias, snapshot или policy действовали;
- `instrument_revision` — версия benchmark, task pool и grader;
- `supersedes` / `superseded_by` — явная связь наблюдений.

Рекомендуемый cadence — не механическое расписание, а сочетание временных и событийных пересмотров:

```text
launch → +7d → +30d → +90d
       ↘ alias/snapshot/product update
       ↘ price/quota change
       ↘ benchmark/grader revision
       ↘ runtime/client release
       ↘ strong contradiction or reproduced failure
```

Нельзя молча заменить launch score текущим leaderboard score. Это два observations с разными instrument revisions. Нельзя назвать историческое issue «текущим поведением», если closure или новая версия не проверены.

## 7. Граф происхождения и независимость

Для каждой связи `supports` или `repeats` нужно знать происхождение:

```text
provider table
 ├─ news article A
 ├─ forum post B quoting A
 └─ benchmark commentary C quoting the same table
```

Это один measurement origin и три propagation nodes.

Иная структура:

```text
user issue A ─ raw log A
user issue B ─ raw log B
independent benchmark C ─ artifact set C
provider note D ─ aggregate telemetry D
```

Здесь может возникнуть cross-modal cluster, даже если отдельные measurements несопоставимы. Но поддерживаемое ядро нужно формулировать на их общей высоте, например: «существует повторяющееся давление на outcome-level efficiency», а не «модель использует на 18% больше токенов».

## 8. Конфигурация входит в субъект

Минимальный subject binding для сильного model observation:

```text
model family + exact model/snapshot when available
+ provider/route + product surface + runtime/client version
+ effort + context policy + tools + permissions
+ prompt/scaffold/runbook + task pool + grader
+ observed_at
```

Отсутствие части полей не делает материал бесполезным. Оно ограничивает перенос. Поле `configuration_gap` должно перечислять неизвестное, а не просто ставить общий warning.

Особенно важно разводить:

- API model context window;
- product-advertised context limit;
- конкретный client catalog limit;
- эффективную recall/usage способность;
- compaction и retained reasoning policy.

То же относится к economics:

- API list price;
- cache pricing;
- actual input/output/reasoning tokens;
- subscription credits/quota;
- turns, retries и wall time;
- стоимость принятого результата, а не одного вызова.

## 9. Outcome bundle для агентных задач

Обычный `pass/fail` скрывает важные режимы. Для агентного наблюдения v0.2 предлагает сохранять раздельно:

```json
{
  "requested": "что было поручено",
  "executed": "какие действия фактически произошли",
  "artifact": "что осталось в среде",
  "verified": "какая проверка действительно прошла",
  "reported": "что модель заявила пользователю",
  "termination": "clean | timeout | disconnect | quota | protocol_missing | unknown"
}
```

Это позволяет различить:

- верный файл при отсутствующем protocol completion;
- красивый финальный ответ без tool execution;
- частично выполненную работу, выданную за завершённую;
- корректный отказ из-за отсутствующего инструмента;
- clean stop после проверенного результата.

## 10. Рабочий pipeline

### 10.1 Постановка вопроса

Вопрос должен содержать ось и перенос. Хорошо:

> При каких verifier/runbook условиях Luna сохраняет outcome Sol на ограниченных software tasks?

Плохо:

> Какая Luna?

### 10.2 Discovery matrix

Искать одновременно по стратам:

1. provider docs, release notes, pricing, system card;
2. первичные papers и benchmark methodology;
3. artifact-backed independent experiments;
4. issue trackers с version/log/control evidence;
5. forums для ранних pressure/failure vocabulary;
6. контрпоиск по каждому формирующемуся выводу.

### 10.3 Capture

- сохранить canonical URL и publisher;
- выделить использованный segment;
- зафиксировать capture time и возможную mutable surface;
- записать origin/dependency;
- не переписывать source claim своим более сильным языком.

### 10.4 Atomization

Каждое предложение проходит тест:

1. один ли здесь субъект;
2. одна ли измеряемая ось;
3. один ли instrument revision;
4. один ли temporal interval;
5. можно ли независимо опровергнуть эту формулировку.

Если нет — делить.

### 10.5 Confound pass

Обязательный список для agentic reports:

- model snapshot/alias drift;
- product surface;
- runtime/client version;
- tool availability/failure;
- prompt/system instructions;
- context/compaction;
- effort;
- quota/accounting;
- task selection;
- grader identity/self-preference;
- termination treatment;
- reporter selection bias.

### 10.6 Clustering

Сначала кластеризовать по механизму, не по тону. «Очень хорош» и «ужасно жрёт квоту» могут относиться к одному outcome-efficiency cluster. «Зацикливается» и «упорно доводит» могут быть разными знаками persistence под разной authority surface.

### 10.7 Contradiction pass

Для каждого сильного кластера искать:

- другой task shape;
- другой effort;
- другой product/runtime;
- более поздний срез;
- измерение другой модальности;
- отрицательный результат того же автора;
- методологическое объяснение расхождения.

Результат противоречия:

- `resolved_by_scope` — обе стороны истинны в разных пределах;
- `resolved_by_instrument` — изменился grader/harness;
- `resolved_by_time` — snapshot/product изменился;
- `unresolved` — сохранять напряжение;
- `invalid_origin_count` — одна сторона была зависимым пересказом.

### 10.8 Review and promotion

Никакого автоматического перехода из веб-кластера в `ModelClaim`.

```text
ExternalObservation
  ├─ product/runtime pressure → соответствующему owner
  ├─ exact method + exact subject → candidate ModelStudy
  ├─ repeated bounded behavior → owned replication
  ├─ provider fact → realization/economics review
  └─ unresolved / weak / stale → preserve + watch
```

## 11. Что может приземлиться в `aoa-models`

### Первая минимальная поверхность

Рекомендуется начать с append-friendly research packet, который валидирует только структурную честность:

- уникальность IDs;
- существование ссылок;
- допустимые target/posture/disposition vocabularies;
- наличие source segment для каждого observation;
- явный `configuration_gap`, если subject неполон;
- отсутствие автоматического owner-truth promotion.

Не следует сразу вводить:

- общий confidence score;
- универсальную иерархию источников;
- автоматический consensus;
- автоматическое aging/deletion;
- требование полного subject binding для сохранения раннего сигнала;
- top-level сущность для каждого confound;
- правило «N упоминаний = claim».

### Связь с существующими объектами

- `ModelRealization` остаётся владельцем exact access/runtime/economics subject.
- `ModelStudy` остаётся владельцем принятого исследования и его метода.
- `ModelClaim` остаётся owner-reviewed утверждением о связанных realizations.
- web-recon packet — pre-canon intake, который не подменяет ни один из них.

Полезная граница: research packet может ссылаться на существующий realization, но отсутствие такой ссылки не разрешает ему создать реализацию скрыто.

## 12. Как метод должен улучшать себя

После каждого забега сохранять `method_pressure`:

- какое различие корпус заставил добавить;
- какое поле оказалось шумом;
- где отсутствующая информация реально помешала выводу;
- какой source class дал новый failure vocabulary;
- какое правило ошибочно поглотило контрсвидетельство;
- что нужно воспроизвести локально;
- какой consumer пока не существует.

Изменение схемы оправдано не тем, что поле «может пригодиться», а повторяющимся случаем, где без него две существенно разные вещи стали неразличимы.

## 13. Критерий зрелого результата

Забег завершён не тогда, когда найдено много ссылок. Достаточный результат содержит:

1. карту точных субъектов и configuration gaps;
2. атомарные observations с origin graph;
3. несколько разных evidence modalities;
4. временную ось и mutable surfaces;
5. качественное контрсвидетельство;
6. поддерживаемое ядро каждого кластера и предел переноса;
7. следующий owned experiment или review route;
8. pressure notes, способные улучшить v0.3.

Так веб остаётся ценным, живым и чувствительным источником, но перестаёт незаметно превращать популярность, свежесть или красивую таблицу в модельную истину.
