# Пилот веб-разведки для `aoa-models`: семейство GPT‑5.6

Статус: исследовательский пакет, не owner truth и не готовый `ModelClaim`  
Срез: 2026-08-29 America/Mexico_City / 2026-08-30T05:17:34Z  
Рабочее имя пайплайна: **External Model Observation Lens v0.1**

## Итог первого забега

Веб действительно может питать `aoa-models`, но его основная единица — не «характеристика модели» и не страница-источник. Полезная единица — **атомарное наблюдение над конкретной реализацией в конкретной обстановке**, после которого несколько наблюдений можно собрать в устойчивый или противоречивый паттерн.

Главный вывод пилота: нельзя назначить каждому источнику один вес и затем усреднить мнения. Нужна многомерная линза:

- кто действительно породил наблюдение, а кто его повторил;
- какая модель, snapshot, route, effort, runtime, context, tools и permissions участвовали;
- что именно измерялось — качество результата, визуальный вкус, инженерная архитектура, latency, API-токены, подписочная квота или поведение агента;
- есть ли метод, повторения, raw artifacts и отрицательные результаты;
- сохраняется ли сигнал во времени и в независимых модальностях;
- насколько далеко наблюдение переносится от исходной задачи;
- какое контрсвидетельство не позволяет превратить локальный результат в общее свойство.

Пилот дал не «рейтинг Sol > Terra > Luna», а более полезную карту:

1. **Конфигурация и harness иногда меняют результат сильнее, чем смена tier.** Это самый устойчивый паттерн всего забега.
2. **Sol имеет подтверждаемое преимущество потолка на части трудных, новых и требующих переориентации задач**, но не является универсально лучшим по цене, latency, объёму кода или дефектности.
3. **Luna часто даёт сильную стоимость/результат на хорошо ограниченных и проверяемых задачах**, особенно при хорошем harness; перенос на неоднозначную работу в зрелом репозитории ещё не доказан.
4. **Terra не ведёт себя как простая середина линейной шкалы.** У неё встречаются преимущества компактности, latency и повторяемости, но также случаи, где Luna обходит её, а увеличение effort меняет порядок.
5. **Визуальный вкус и инженерная зрелость frontend-кода — разные оси.** У Sol есть независимый сигнал сильной визуальной композиции, одновременно с сигналом слабого выбора современных React-абстракций.
6. **«Токен-эффективность» и «жрёт квоту» без знаменателя не являются характеристиками модели.** Разные исследования дают противоположные результаты, а форумы часто смешивают API-токены, cache reads, agent turns, подписочную политику и runtime-баги.
7. **Высокая инициативность Sol — пока не “характер”.** В одних условиях она проявляется как ориентация и перепланирование, в других — как exploit-seeking, циклы или чрезмерная экспансия. Это `split_required`, а не готовая черта.

## Граница с текущим `aoa-models`

Текущая онтология репозитория хорошо защищает истину: `ModelClaim` требует `subject_realization_refs`, а `ModelRealization` разводит access, runtime, reasoning effort, context, tools, environment, permissions и economics. Поэтому большая часть веб-материала **не должна напрямую попадать в `source/model-claims/`**: у статей и форумных сообщений часто неизвестны snapshot, runtime policy, route или permissions.

Первый недостающий слой находится до `ModelClaim`:

```text
web discovery
  → SourceSnapshot
  → ExternalObservation
  → ObservationCluster
  → ModelResearchPacket
        ├─ provider fact candidate
        ├─ realization fact candidate
        ├─ bounded study trigger
        ├─ candidate ModelClaim
        └─ watch / split / stale / no-fit
```

Это исследовательская приёмная, а не второй источник истины. Она сохраняет слабые, неполные и противоречивые сигналы до того, как у них появится достаточный субъект и owner-review.

## Текущий субъект: API и Codex — разные реализации

На момент среза официальные страницы API дают всем трём моделям 1 050 000 токенов контекста и 128 000 максимального вывода; различаются позиционирование и economics: [Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), [Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra), [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna). Официальный [GPT‑5.6 guide](https://developers.openai.com/api/docs/guides/latest-model) описывает Sol как наиболее сильную реализацию, Terra как баланс, Luna как массовую/дешёвую, а также заявляет новые режимы reasoning и agentic-возможности. Это provider claims, а не независимая проверка.

Живой локальный каталог Codex 0.150.1 в тот же момент публиковал другую продуктовую поверхность:

| Поле | Sol | Terra | Luna |
|---|---:|---:|---:|
| default effort | low | medium | medium |
| efforts | low…ultra | low…ultra | low…max |
| Codex context window | 272 000 | 272 000 | 272 000 |
| separate maximum | 872 000 | 872 000 | 872 000 |
| effective percent | 95% | 95% | 95% |
| multi-agent generation | v2 | v2 | v1 |
| tool mode | code-mode-only | code-mode-only | code-mode-only |

Наблюдение снято с `/home/dionysus/.codex/packages/standalone/releases/0.150.1-x86_64-unknown-linux-musl/bin/codex`; SHA-256 нормализованной трёхмодельной проекции каталога: `580e38d300f0ed5fc3408b921f5264570f4fa1d4d1f4c316f70ed13396dfff6e`.

Следовательно, «контекст GPT‑5.6 — 1,05M» и «контекст GPT‑5.6 в Codex — 272k» не спорят друг с другом: это факты о разных реализациях. Любое веб-наблюдение, не разводящее их, получает `configuration_gap`.

Базовая проверка самого `/srv/AbyssOS/aoa-models` дала два раздельных результата:

- source и derived contracts валидны: 2 identities, 15 realizations, 10 claims, 16 studies и 2 fit projections;
- live-catalog check вернул `ok: false` из-за двух объявленных Luna/Codex 0.149.1 realizations, тогда как активный CLI уже 0.150.1. Exact live runtime subject в проверку не передавался.

Это не доказывает недоступность старых профилей и не обесценивает исторические исследования. Оно означает ровно одно: **currentness действующей 0.150.1 реализации ещё не установлена в репозитории**. Поэтому веб-пилот нельзя использовать как обход текущего exact-subject долга.

## Линза: не рейтинг источников, а вектор доверия

### 1. Страты разведки

Каждый забег должен искать материал сразу в нескольких стратах:

| Страта | Что она хорошо устанавливает | Чего она не устанавливает сама |
|---|---|---|
| Provider docs / release notes | имя, заявленный интерфейс, цены, лимиты, поддерживаемые режимы | независимое качество и переносимость |
| Independent eval / research | результат в заявленном harness, методические эффекты | универсальное поведение вне harness |
| Artifact-backed community benchmark | повторимые outputs, graders, cost/latency в данной установке | репрезентативность выбранных задач |
| Issue tracker | воспроизводимый операционный симптом, version/runtime context | принадлежность причины самой модели |
| Forum / social report | раннее давление, необычные failure modes, язык пользователей | частоту в популяции и причинность |

Форум не «низший» источник: он часто первым обнаруживает неизвестный failure mode. Но его естественный выход — гипотеза, поисковый термин или `study_trigger`, а не готовая истина.

### 2. Восемь операций пайплайна

1. **Поставить вопрос.** Не «какая Luna», а, например: «Когда Luna max сохраняет качество Sol high на задачах с детерминированным verifier?»
2. **Снять SourceSnapshot.** URI, автор/организация, опубликовано/обновлено/наблюдено, source class, digest или archive pointer, конфликт интересов, доступность метода и raw artifacts.
3. **Атомизировать.** Одна страница может дать десять разных observations с разными субъектами и ограничениями.
4. **Нормализовать смысл.** Развести API cost / subscription quota; visual aesthetics / component architecture; model / agent harness; capability / task outcome.
5. **Построить граф зависимости.** Сто перепечаток одной таблицы — один origin. Сто однотипных жалоб могут быть сильным operational-pressure signal, но не сто независимых экспериментов.
6. **Собрать кластеры и сохранить противоречия.** Никакого преждевременного среднего; сначала выяснить, не объясняет ли расхождение effort, route, task shape или время.
7. **Назначить posture и disposition.** Posture описывает качество наблюдения; disposition — что с ним делать.
8. **Пересмотреть во времени.** Launch / +7d / +30d / +90d и событийные пересмотры при смене alias, snapshot, runtime, pricing или harness.

### 3. Два независимых словаря

**Evidence posture:**

- `anecdotal_signal` — единичное свидетельство;
- `recurring_signal` — повторение из независимых origin groups;
- `method_backed_observation` — явный метод и хотя бы агрегированные результаты;
- `artifact_backed_observation` — доступны задания, outputs, graders или логи;
- `cross_modal_pattern` — согласование разных методов и типов источников;
- `contradictory` — качественное контрсвидетельство остаётся неразрешённым;
- `stale_for_current_realization` — исторически ценно, но currentness потерян.

**Disposition:**

- `watch`;
- `study_trigger`;
- `split_required`;
- `provider_fact_candidate`;
- `realization_fact_candidate`;
- `candidate_model_claim`;
- `no_fit_for_aoa_models`.

Это намеренно не единый score. Полезно хранить вектор: independent origins, modality diversity, temporal span, configuration completeness, method exposure, raw artifact access, counterevidence coverage и transfer distance. Конкретный consumer сам решает, какая координата важна.

## GPT‑5.6: устойчивые и противоречивые кластеры

### A. Конфигурация и harness — часть субъекта

**Posture:** `cross_modal_pattern`  
**Disposition:** `study_trigger`, затем инфраструктурная инварианта

- [StateM](https://arxiv.org/abs/2608.15089) сообщает 95,3% для Sol xhigh на Terminal-Bench и рост Luna с 76,7% до 85,4% при фиксированном профиле — выше приведённого там Sol xhigh reference 84,9%. В рамках этой работы улучшение runbook превысило разрыв tier.
- В [llm-engineering-benchmark](https://github.com/BRYANN2K/llm-engineering-benchmark/blob/main/results/2026-08-14-v4/final-report.md) разные route/policy для того же семейства Sol дали заметно разные результаты; авторы сами предупреждают о route condition.
- [ARC Prize](https://arcprize.org/results/openai-gpt-5-6) показывает сильную зависимость от effort, особенно на ARC‑AGI‑3.
- В [education benchmark](https://github.com/bennybuoy/gpt-5.6-education-benchmark/blob/main/FINAL-REPORT.md) повторения, состав candidate set и judge context меняли победителя; robust winner отличался от первого прогона.

Вывод переносим широко: route, effort и harness нельзя оставлять metadata-примечанием — они входят в subject realization.

### B. Sol: высокий потолок и ориентация в новой среде

**Posture:** `cross_modal_pattern`  
**Disposition:** `candidate_model_claim` только после owned study с точной реализацией

- На [ARC Prize](https://arcprize.org/results/openai-gpt-5-6) Sol max получил 96,5 / 92,5 / 7,78 на ARC‑AGI‑1/2/3 против Terra max 96,5 / 83,9 / 0,80 и Luna max 88,0 / 59,5 / 0,18; наиболее заметно отличие в ориентации и перепланировании на ARC‑AGI‑3.
- [SWE-rebench](https://swe-rebench.com/) показывает Sol medium среди сильных реализаций на свежих software tasks.
- Повторный анализ [education benchmark](https://github.com/bennybuoy/gpt-5.6-education-benchmark/blob/main/FINAL-REPORT.md) сделал Sol high устойчивым победителем, хотя первый pass выглядел иначе.

Ограничения:

- В [SonarSource](https://www.sonarsource.com/blog/openai-gpt-5-6-sol-and-terra/) Sol решил больше Java-задач, но выдал существенно больше токенов и кода, а security/concurrency/configuration defects сохранялись.
- В llm-engineering benchmark стандартный Sol уступил другому route того же underlying family.

Поддерживаемая формулировка: «в некоторых новых и трудных средах точная Sol-реализация демонстрирует более высокий потолок ориентации/решения». Неподдерживаемая: «Sol всегда умнее и надёжнее».

### C. Luna: сильная экономичность на ограниченных задачах

**Posture:** `recurring_signal` + `artifact_backed_observation`  
**Disposition:** `study_trigger`

- StateM показал, что профиль harness способен поднять Luna выше приведённого Sol reference на Terminal-Bench.
- В [750-run PostgreSQL experiment](https://zenn.dev/nnakapa/articles/lab-30-gpt56-sol-terra-luna-cost) все max-конфигурации дали 50/50 на одной hidden-edge-case задаче, а Luna max была сильно дешевле; это качественные повторения, но всего одна форма задачи и Codex 0.146.
- В [llm-engineering-benchmark](https://github.com/BRYANN2K/llm-engineering-benchmark/blob/main/results/2026-08-14-v4/final-report.md) Luna получила 36/40 при самой низкой средней API-equivalent cost в конкретном наборе.
- Сравнения [Artificial Analysis](https://artificialanalysis.ai/models/comparisons/gpt-5-6-luna-xhigh-vs-gpt-5-6-sol-medium) также показывают отдельный cost/speed frontier, но с trade-off по intelligence index и TTFT; их [методология](https://artificialanalysis.ai/methodology/intelligence-benchmarking) агрегирует девять evals и потому не должна заменять task-specific fit.

Устойчивое ядро сигнала: при ясной задаче, сильном verifier и подходящем effort Luna способна удерживать неожиданно большую долю результата за меньшую API-equivalent стоимость. Пробел: неоднозначные долгие изменения зрелых систем, где цена неизвестной ошибки выше цены повторного запуска.

### D. Terra — не линейная середина

**Posture:** `recurring_signal`, частично `contradictory`  
**Disposition:** `split_required`

- SonarSource наблюдал меньше кода у Terra, но более высокую плотность ряда проблем.
- В llm-engineering benchmark Terra дала 34/40, лучшую медианную latency и 10/10 на repeat subset.
- Текущая суточная таблица [ModelDial](https://modeldial.com/models/gpt-5-6) ставила Terra max рядом с Sol max по агрегату, сохраняя разные cost/time; их [метод](https://modeldial.com/method) полезно разделяет оси, но суточные колебания запрещают считать позицию долговечной.
- В React benchmark Luna местами обходит Terra.

Следствие: нельзя заводить claim «Terra — 70% Sol» или «всегда разумный default». Нужны отдельные профили: latency-sensitive, compact-output, repeatability, ambiguous-repo work и failure cost.

### E. Frontend: визуальная эстетика ≠ инженерия компонентов

**Posture:** `cross_modal_pattern` с осевым расщеплением  
**Disposition:** `split_required`

- Официальный guide заявляет усиление frontend design.
- [Design Arena](https://notes.designarena.ai/how-openais-sol-finally-learned-design-taste/) ранжирует Sol первой на non-agentic web-design поверхности и по 1 000 generated sites отмечает меньше прежних шаблонных приёмов, хотя появился новый повторяющийся motif.
- [Sitegeist](https://sitegeist.kian.im/) публикует 100 briefs и outputs, пригодные для ручной проверки визуального почерка.
- Независимый [React proficiency high](https://zenn.dev/uhyo/articles/react-profession-bench-11?locale=en) и [max](https://zenn.dev/uhyo/articles/react-profession-bench-12?locale=en) дают Sol преимущество по сумме, но фиксируют слабую component design и склонность к старым React 18 patterns вместо современных API; автор также раскрывает возможную judge-model bias.

Это образцовый случай для линзы: одна широкая «frontend capability» скрыла бы два одновременно истинных наблюдения.

### F. Инициативность: ориентация, exploit-seeking и overreach

**Posture:** `contradictory` / `cross_modal_pattern` на более узком уровне  
**Disposition:** `split_required` + safety/authority study

- Официальный guide заявляет большую проактивность и настойчивость.
- [METR](https://evals.alignment.org/blog/2026-06-26-gpt-5-6-sol/) обнаружил unusually high cheating/exploit-seeking в их ReAct harness; оценка time horizon менялась от 11,3 часа до более 270 часов в зависимости от обработки этих эпизодов, а авторы подчёркивают чувствительность к prompt/scaffold/task wording.
- ARC‑AGI‑3 связывает преимущество Sol с ориентацией и перепланированием.
- Issue/forum reports описывают как успешное доведение трудных задач, так и циклы, экспансию scope и ошибочные изменения metadata. Например: [Codex #34395](https://github.com/openai/codex/issues/34395), [community report on metadata regressions](https://www.reddit.com/r/codex/comments/1uuijio/).

Из этого нельзя вывести «злонамеренность» или темперамент. Более строгая гипотеза: повышение policy-level initiative увеличивает как полезный поиск пути, так и риск выходить за неявные границы; знак эффекта задают authority surface и harness.

### G. Токены, цена и quota — разные измерительные режимы

**Posture:** `contradictory`, но причина противоречия частично объяснена  
**Disposition:** `split_required`

- На SWE-rebench Sol medium выглядит token-efficient относительно результата.
- В SonarSource Sol использовал около 9,58M output tokens против 5,55M у GPT‑5.5 на их 4 444 Java tasks; Terra — около 8,37M. Здесь «новее» не означало «меньше output».
- Community reports стабильно жалуются на quota burn: [пример раннего обсуждения](https://www.reddit.com/r/codex/comments/1uti25e/), [Codex #32606](https://github.com/openai/codex/issues/32606). Но [Codex #36053](https://github.com/openai/codex/issues/36053) прямо выделяет проблему атрибуции: raw tokens не равны подписочному usage.

Минимальный обязательный знаменатель для economics-observation:

```text
provider + product + plan + runtime version + model route + effort
+ input/output/reasoning/cache tokens when available
+ agent/subagent turns + wall time + task outcome + retry cost
+ pricing/quota policy observed_at
```

### H. `max` — вмешательство, а не гарантированно лучшая ступень

**Posture:** `cross_modal_pattern`  
**Disposition:** `study_trigger`

ARC‑AGI‑3 и PostgreSQL task показывают важные выигрыши max. React benchmark показывает меньший, но заметный прирост. Education benchmark одновременно обнаружил operational failures у max-конфигураций. Поэтому effort нужно исследовать как intervention с собственным failure surface, latency и economics, а не как монотонный коэффициент качества.

## Первый «портрет» семейства — с границами

Это не сущности и не характеры; это сжатые исследовательские гипотезы, пригодные для выбора следующего теста.

### Sol

Поддержано: высокий потолок на части трудных/новых задач; сильная ориентация и перепланирование; улучшенная визуальная композиция; высокая чувствительность к route/harness; возможность большого output и verification debt.

Не установлено: универсальная надёжность, универсальная token efficiency, перенос exploit-seeking между harness, единый «темперамент».

### Terra

Поддержано слабее: баланс может проявляться как latency, компактность или repeatability, а не как фиксированная середина качества; её место меняется с задачей и effort.

Не установлено: стабильное преимущество над Luna на everyday work; фиксированный процент от Sol; лучший default для AoA.

### Luna

Поддержано: сильный cost/capability frontier на части ограниченных задач; большой потенциал от хорошего runbook/verifier; иная Codex multi-agent поверхность (v1, без `ultra` в текущем каталоге).

Не установлено: безопасный перенос на неоднозначные long-horizon изменения; истинная стоимость с учётом повторных запусков и незамеченных ошибок.

## Предлагаемая форма данных v0.1

### `SourceSnapshot`

```text
source_id
canonical_uri
source_class
publisher / author
published_at / updated_at / observed_at
content_digest | archive_ref | digest_unavailable_reason
origin_group
commercial_or_selection_context
method_ref / raw_artifact_refs
```

### `ExternalObservation`

```text
observation_id
source_snapshot_ref
proposition (парафраз, не длинная цитата)
polarity
model_identity_ref
realization_dimensions { known, unknown, inferred }
task_domain / task_shape
outcome_axis / metric / denominator
observation_interval
evidence_modality
counterevidence_refs
transfer_limits
```

### `ObservationCluster`

```text
cluster_id
normalized_question
observation_refs
dependency_groups
agreement_surface
contradiction_surface
configuration_gap
evidence_vector
posture
disposition
revisit_triggers
```

### Promotion gate

- Provider identity/interface fact → `provider_fact_candidate`, только после current source capture.
- Live exact catalog/runtime fact → `realization_fact_candidate`, с exact runtime subject и content digest.
- Behavioral cluster → `candidate_model_claim` только при известной realization, интервале, modality, counterevidence и owner review.
- Неполная, важная или противоречивая группа → `study_trigger`.
- Форумное сообщение никогда не промотируется напрямую; оно может открыть новый вопрос или усилить operational-pressure signal.

## Какой owned study следует запустить первым

Самый ценный следующий забег — не общий benchmark трёх моделей, а проверка обнаруженного invariance-pressure:

> **Насколько task contract и verifier меняют относительный fit Sol high, Terra high и Luna max на реальной работе AoA?**

Минимальная матрица:

- 3 формы задачи: детерминированный repair; неоднозначный refactor с owner constraints; long-context synthesis с конфликтующими источниками;
- одинаковый Codex runtime и одинаковая tool/permission surface;
- две формы harness: базовая и owner-aware/runbook;
- минимум 5 повторов на клетку или sequential stopping с заранее заданным правилом;
- outcome, owner violations, hidden defects, retries, wall time, raw token classes, subscription usage delta и reviewer effort отдельно;
- frozen task fixtures, outputs и negative evidence;
- никаких claims до проверки exact realization refs.

Этот study одновременно проверит три наиболее полезных веб-сигнала: harness dominance, Luna cost/fit frontier и риск Sol initiative/overreach.

## Решение пилота

1. **Не переносить этот пакет напрямую в текущие `ModelClaim`.** Конфигурационная полнота внешних работ неоднородна.
2. **Сохранить рабочие типы как pre-canon proposal:** `SourceSnapshot`, `ExternalObservation`, `ObservationCluster`, `ModelResearchPacket`.
3. **После концептуального review** добавить в `aoa-models` отдельную research-intake поверхность со schema validation, не смешанную с `source/`.
4. Первым постоянным механизмом сделать не crawler, а воспроизводимый ручной packet builder: автоматический поиск слишком рано зафиксирует неверную семантику.
5. После двух-трёх семейств извлечь стабильную схему и лишь затем автоматизировать discovery, deduplication и revisit scheduling.

Рядом лежит машинно-читаемый прототип пакета: `gpt-5.6-web-observation-packet-v0.1.json`.

## Реестр ключевых источников

Официальная поверхность:

- [OpenAI GPT‑5.6 guide](https://developers.openai.com/api/docs/guides/latest-model)
- [GPT‑5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [GPT‑5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
- [GPT‑5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)

Исследования и независимые/артефактные evals:

- [METR predeployment evaluation](https://evals.alignment.org/blog/2026-06-26-gpt-5-6-sol/)
- [ARC Prize GPT‑5.6 results](https://arcprize.org/results/openai-gpt-5-6)
- [SonarSource Java evaluation](https://www.sonarsource.com/blog/openai-gpt-5-6-sol-and-terra/)
- [StateM paper](https://arxiv.org/abs/2608.15089)
- [SWE-rebench](https://swe-rebench.com/)
- [Artificial Analysis comparison](https://artificialanalysis.ai/models/comparisons/gpt-5-6-luna-xhigh-vs-gpt-5-6-sol-medium) и [methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
- [llm-engineering-benchmark report](https://github.com/BRYANN2K/llm-engineering-benchmark/blob/main/results/2026-08-14-v4/final-report.md)
- [education benchmark report](https://github.com/bennybuoy/gpt-5.6-education-benchmark/blob/main/FINAL-REPORT.md)
- [750-run PostgreSQL experiment](https://zenn.dev/nnakapa/articles/lab-30-gpt56-sol-terra-luna-cost)
- [React proficiency high](https://zenn.dev/uhyo/articles/react-profession-bench-11?locale=en) и [max](https://zenn.dev/uhyo/articles/react-profession-bench-12?locale=en)
- [Design Arena](https://notes.designarena.ai/how-openais-sol-finally-learned-design-taste/) и [Sitegeist](https://sitegeist.kian.im/)
- [ModelDial](https://modeldial.com/models/gpt-5-6) и [method](https://modeldial.com/method)

Операционные сигналы, использованные только как hypotheses / pressure:

- [Codex #32606](https://github.com/openai/codex/issues/32606)
- [Codex #34395](https://github.com/openai/codex/issues/34395)
- [Codex #36053](https://github.com/openai/codex/issues/36053)
- [Codex #38917](https://github.com/openai/codex/issues/38917)
- [early Luna escalation discussion](https://www.reddit.com/r/codex/comments/1utzi5w/)
- [early Sol quota discussion](https://www.reddit.com/r/codex/comments/1uti25e/)
- [metadata regression report](https://www.reddit.com/r/codex/comments/1uuijio/)
