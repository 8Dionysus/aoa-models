# External Model Web Recon Lens v0.3

Статус: pre-canon исследовательский метод; не owner truth, не канон, не
`ModelClaim`, не `ModelStudy` и не автоматическое основание для выбора модели

Срез метода: 2026-08-30
Предшественник: `external-model-web-recon-method-v0.2.md`

Эмпирическая основа этой revision:

- [`GPT-5.6 temporal drift`](gpt-5.6-temporal-drift-2026-08-30.md);
- [`Claude 5 persistence under authority`](claude-5-persistence-under-authority-2026-08-30.md);
- [`cross-provider outcome economics`](cross-provider-outcome-economics-2026-08-30.md).

Они являются тремя bounded post-seed забегами, а не доказательством полноты
метода.

## 1. Что изменилось после первого корпуса

v0.2 задал форму приёма: источник по сегментам, атомарное наблюдение,
конфигурационно связанный субъект, кластеры, tensions и явная временная
линия. Три последующих забега добавили более строгую границу вывода.

Наблюдаемое качество агентной модели распадается как минимум на пять осей:

```text
capability
  -> realization and product binding
  -> executed trajectory
  -> completed and verified outcome
  -> outcome economics and operator visibility
```

Сильный результат на первой оси не доказывает последующие. Долгая модельная
траектория может завершиться корректным артефактом, зависнуть в TUI, потерять
доступный контекст из-за session state, пережить transport retries или стать
непригодной для supervision из-за отсутствия наблюдаемого текста. И наоборот,
единичный runtime-сбой не опровергает capability.

Для long-horizon работы до execution появляется ещё одна проверяемая граница:
какие owner/memory/session sources были доступны и какие из них действительно
были прочитаны до выбора траектории. Наличие orientation evidence в context не
равно его использованию. После обещания продолжить также различаются reported,
scheduled и фактически executed continuation.

Поэтому центральный вопрос v0.3:

> Какое минимальное утверждение остаётся истинным после разделения model,
> snapshot, product, provider route, harness, instrument, runtime, operator
> visibility и verified outcome?

Если такого ядра пока нет, зрелый результат забега — `split_required`, а не
усреднённая «характеристика модели».

## 2. Пять линз одного забега

Полезный забег старается посмотреть на вопрос через разные механизмы. Это не
обязательная квота источников, а карта контрпоиска.

| Линза | Что она может установить | Чего она не устанавливает |
|---|---|---|
| Provider surface | текущие интерфейсы, цены, заявленный scope, product policy | независимую эффективность и incidence |
| Exposed instrument | task pool, attempts, grader, pass/fail, tokens, time, cost | перенос на иной harness или рабочий класс |
| Artifact or trace | конкретный execution/outcome при известной конфигурации | частоту в популяции и model-only causality |
| Operational reports | повторяющееся давление и воспроизводимые симптомы | общий trait без изоляции реализации |
| Counterevidence | границу, отрицательный контроль, альтернативный механизм | автоматическое опровержение соседней оси |

Source class остаётся ролью, а не универсальным рейтингом. Официальная цена
сильнее форумного воспоминания о цене; первичный packet capture сильнее
provider marketing для локализации transport reset; ни один из них не
заменяет owner eval.

## 3. Правило устойчивого ядра

Кластер получает сильную формулировку только на пересечении поддерживаемых
областей его observations.

```text
supported(cluster)
  = intersection(subject bounds)
  ∩ intersection(configuration bounds)
  ∩ intersection(outcome axes actually observed)
  ∩ intersection(valid temporal intervals)
```

Число URL не входит в формулу. Несколько пересказов одного benchmark дают
один origin. Несколько issue от разных пользователей могут создать
`recurring_pressure`, но не model claim, если общий механизм находится на
уровне product/runtime.

Практические ступени:

1. Один первичный эпизод — `anecdotal_signal`; сохранить, ограничить, искать
   контроль или повтор.
2. Несколько независимых эпизодов одного operational surface —
   `recurring_pressure`; маршрутизировать к владельцу реализации или
   предложить replication.
3. Разные modalities с общим bounded ядром — `cross_modal_pattern`; формула
   ядра не должна быть шире общей области.
4. Provider claim плюс независимый benchmark — всё ещё два разных объекта,
   пока subject/configuration/outcome не совпали.
5. Никакая ступень не продвигается в canonical source без отдельного owner
   review, подходящего контракта и собственных доказательств.

## 4. Время принадлежит сегменту

URL не является единицей currentness. Одна release page может одновременно
содержать:

- историческую таблицу launch pricing;
- поздние update notices;
- текущую доступность;
- сравнения, рассчитанные старой revision инструмента.

Для каждого использованного сегмента нужно уметь ответить:

- когда он был опубликован или изменён;
- когда именно он был захвачен;
- к какому product/snapshot он относится;
- остаётся ли он current, historical или unresolved;
- какое более новое observation его уточняет или supersedes.

Повторный capture без изменения тоже полезен: он подтверждает только то, что
сегмент был виден в новую дату. Он не превращает mutable page в immutable
источник и не продлевает currentness соседних сегментов.

Новая цена, alias, snapshot, safety classifier, product rollout или benchmark
revision создаёт новое observation. Старое не переписывается.

## 5. Instrument identity обязательна для результата

Название benchmark недостаточно. Минимальная идентичность результата:

```text
task pool + revision + attempts/repeats + agent variant
+ model/effort + harness + tools/network
+ scoring/verifier/grader + exclusions
+ integrity-control scope + adjudicator
+ capture date
```

Если один leaderboard заменил Terminal-Bench v2 на v2.1, изменил Q&A scoring,
token accounting или reward-hacking detection, его старый и новый top-level
score нельзя трактовать как временной график качества модели. Это разные
инструменты. Связь между ними — `resolved_by_instrument`, не «регрессия» без
rerun на общей revision.

Per-eval breakdown важнее близких aggregate scores: два агента могут иметь
почти одинаковый index и противоположный порядок на implementation,
terminal-use и repository-Q&A задачах.

## 6. Outcome ledger вместо слова «успех»

Каждое агентное observation раскладывается:

```text
requested -> executed -> artifact -> verified -> reported -> termination
```

Эти состояния не выводятся друг из друга:

- tool calls без финального текста могут выполнить задачу, но лишить оператора
  наблюдаемости;
- готовый artifact без verifier не является verified outcome;
- `stop_reason: tool_use` не означает, что интерактивный runtime сможет
  продолжить;
- retry recovery сохраняет completion, но добавляет latency и transport
  pressure;
- completion statement без исполнения — reported outcome без executed
  outcome.

Для долгих прогонов дополнительно фиксируются, когда доступны:

- orientation inputs available и orientation inputs actually consulted;
- полезный wall time и agent wall time;
- число turns/tool calls/retries;
- input, cache-read, cache-write, reasoning и answer tokens;
- operator-visible progress;
- reported continuation, scheduled continuation и выполненный следующий шаг;
- checkpoint state, termination, recovery action и восстановленный outcome;
- verifier, artifact и acceptance boundary.

Фраза «продолжаю» без запущенной работы или явного wake/checkpoint является
reported state, а не persistence. `--resume` после kill доказывает только тот
recovery outcome, который после него реально наблюдался.

## 7. Экономика только с denominator

Цена токена, quota, Cost per Task и стоимость завершённого принятого артефакта
— разные величины.

Quota boundary дополнительно относится к termination semantics. Число часов в
окне не говорит, сколько работы потеряно: нужны состояние goal при остановке,
checkpoint, число manual resumes, восстановленная траектория и принятый
результат.

Допустимые формулировки называют denominator явно:

- USD / benchmark task-attempt;
- wall minutes / task;
- turns / task;
- tokens / task;
- retries / request или / session;
- verified outcomes / attempted tasks;
- operator minutes / accepted artifact.

Если telemetry отсутствует, это не ноль. Если benchmark исключает missing
telemetry, это часть метода. Consumer plan usage нельзя переводить в API USD
без опубликованного accounting contract.

Полезный минимум сравнения:

```text
outcome quality
+ completion/reliability
+ token composition
+ wall time and turns
+ pay-per-token cost
+ cache behavior
+ supervision/recovery cost
```

Pareto-вывод делается внутри общего task pool и revision. Нельзя объявлять
модель экономичнее вообще, если измерены только один effort и один harness.

## 8. Confound ledger для agentic evidence

Для каждого сильного симптома проверяются альтернативные владельцы:

| Возможный владелец | Примеры различающих данных |
|---|---|
| Model/snapshot | A/B на том же product и harness; точный model ID |
| Provider route | endpoint, region, headers, entitlement, retry telemetry |
| Product policy | plan, quota window, fallback, safety routing |
| Harness | client build, agent prompt, tool schema, compaction policy |
| Runtime/UI | OS, terminal, event loop, transcript/render divergence |
| Instrument | task revision, attempts, verifier, grader, exclusions |
| Operator protocol | permissions, checkpoints, acceptance and supervision |

Если контроль изолирует harness или transport, observation имеет
`target_kind: runtime_behavior` или `operational_pressure`, даже когда в
заголовке issue указана модель. Заголовок источника не определяет владельца
истины.

## 9. Как работать с официальными заявлениями и отзывами

Provider statements сохраняются атомарно:

- факт интерфейса или цены;
- заявленный benchmark outcome;
- customer quote;
- product policy;
- safety/availability decision.

Customer quote на provider page остаётся curated provider surface, пока нет
ссылки на первичный метод или artifact. Он может подсказать вопрос и будущий
replication, но не считается независимым origin только из-за другого имени в
цитате.

Issue или forum report ценен сильнее, когда содержит:

- точную версию и route;
- timestamps/request IDs;
- denominators и отрицательный контроль;
- локальные логи или packet capture;
- перечисление того, что автор не смог установить;
- различение выполненного outcome и пользовательского впечатления.

Даже такой отчёт остаётся external observation, а не proof.

## 10. Остановка поиска и revisit

Забег можно остановить, когда одновременно:

- сформулировано поддерживаемое ядро и его границы;
- основные source roles представлены или их отсутствие записано;
- найдено и сохранено качественное counterevidence;
- конфаунды распределены по возможным владельцам;
- outcome и economics имеют denominators;
- следующий полезный шаг конкретен: watch, replication, owner route или
  bounded promotion review.

Повторный забег запускают события, а не только календарь:

- изменение price, alias, snapshot, product или fallback;
- новый client/runtime build;
- benchmark revision или grader change;
- controlled reproduction/closure;
- независимое опровержение;
- появление exact owner realization для сопоставления.

## 11. Почему crawler пока не нужен

Ручные пакеты всё ещё выявляют смысловые границы: segment currentness,
instrument identity, cache-write economics, operator visibility и
runtime/model attribution. Автоматический crawler сейчас умножил бы URL и
ложную независимость быстрее, чем качество наблюдений.

Автоматизацию стоит вводить по частям только после появления повторяющегося
ручного давления:

1. capture mutable segments и content digests;
2. detect changed segments без автоматического вывода;
3. suggest predecessor/supersession links;
4. оставлять atomization, tension resolution и promotion человеку/owner review.

## 12. Долговечная и временная проверка

Долговечная поверхность защищает общий контракт:

- schema и semantic validator;
- уникальность и ссылочная целостность;
- origin/dependency graph;
- temporal ordering и qualified supersession;
- local method/predecessor digest resolution;
- отсутствие прямой ссылки из canonical source на pre-canon packet;
- generic multi-provider tests без model/provider fixtures в коде.

Временная рабочая поверхность допустима для одного забега:

- конвертер отчёта в packet;
- одноразовый authoring script;
- query scratchpad;
- capture notes и промежуточные таблицы;
- exploratory assertions о конкретном URL, модели или числе источников.

Она обязана быть перечислена до использования и удалена после переноса
ценного результата. Конкретные модели, URL и benchmark values живут в data и
reports, но не в generic validator tests.

## 13. Проверка общности v0.3

Метод и контракт считаются общими не потому, что в них нет названий моделей,
а потому, что новый provider/family входит как data без изменения schema,
semantic validator или generic tests.

Первой такой проверкой служит семейство Claude 5: provider docs, release and
safety policy, независимый agent benchmark и несколько первичных runtime
traces укладываются в те же `SourceCapture`, `ExternalObservation`, cluster,
tension и method pressure. Это доказывает пригодность текущего контура для
следующей разведки, но не доказывает полноту будущей ontology.

## 14. Promotion boundary

Recon packet может породить только предложение:

- provider fact -> review точного realization field;
- benchmark observation -> review bounded `ModelStudy`;
- повторяемый behavior -> owned replication, затем review `ModelClaim`;
- runtime symptom -> runtime owner;
- product/quota pressure -> product owner;
- unresolved tension -> новый recon run.

Promotion требует отдельного owner action и нового evidence chain. Ссылка на
`research-intake/` не может быть прямым accepted source reference. Наличие
нескольких пакетов, зелёного validator или устойчивого web consensus этого не
меняет.
