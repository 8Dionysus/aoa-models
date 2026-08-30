# Cross-provider agent outcome economics

Статус: pre-canon comparative web reconnaissance; не ranking, route или
procurement decision

Дата capture: 2026-08-30

ReconRun: [`recon-run:cross-provider/2026-08-30-outcome-economics`](../recon-runs/cross-provider-2026-08-30-outcome-economics.json)
Canonical packet digest:
`sha256:1b02d239b8e34ec622f1669e0269dd6e2d5766aea6d56efaabc1ac8a44b6420f`

## Вопрос и итог

Забег проверял, что остаётся от слов «качество» и «эффективность», если
связать их с task class, effort, harness, instrument revision, tokens, cache,
turns, wall time, pay-per-token cost, termination и исключёнными operational
costs.

Устойчивый вывод: outcome economics — вектор, а не одно место модели в
рейтинге. В одном текущем instrument Opus 5 xhigh имеет более высокий
aggregate outcome, а GPT-5.6 Sol max — меньшие cost, time, turns и token
volume. Per-eval лидеры различаются. Выбор требует owner utility function и
данных на owner tasks.

## Общий instrument и разные фронты

[Coding Agent Index v1.4](https://artificialanalysis.ai/methodology/coding-agents-benchmarking/)
содержит 326 задач: 113 DeepSWE, 89 Terminal-Bench v2.1 и 124
SWE-Atlas-Q&A, с тремя attempts на задачу. На
[текущей comparison surface](https://artificialanalysis.ai/agents/coding-agents/comparisons/claude-code-vs-codex)
зафиксированы следующие bounded rows:

| Конфигурация | Index | DeepSWE | Terminal | Q&A | Cost/task | Agent wall time | Turns | Tokens | Cache hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Code, Opus 5 xhigh | 68 | 60 | 89 | 55 | $8.17 | 23.7 min | 152.1 | 21.6M | 97% |
| Codex, GPT-5.6 Sol max | 65 | 69 | 83 | 43 | $5.00 | 10.2 min | 112.3 | 13.2M | 90% |

Aggregate 68 против 65 не превращается в общий ranking: Sol ведёт на DeepSWE,
Opus — на Terminal и repository Q&A. Cost также не является ценой принятого
production artifact: benchmark учитывает pay-per-token API charges, но не весь
engineering, supervision, verifier и operational overhead.

## Effort — часть конфигурации

На тех же v1.4 rows:

- Sol high → max: index 64 → 65, cost $3.00 → $5.00, time 6.2 → 10.2 min,
  tokens 8.0M → 13.2M на задачу.
- Opus high → xhigh: index 66 → 68, cost $3.92 → $8.17, time 14.0 →
  23.7 min, tokens 9.9M → 21.6M на задачу.

Это два локальных effort frontier, а не совет всегда избегать максимального
effort. Marginal return зависит от task distribution и per-eval целей, поэтому
owner study должен сохранять Pareto points, а не выбирать одну глобальную
настройку.

## Token volume, token price и accepted outcome различны

В Codex max rows Luna получила index 57 при $0.29 и 16M tokens/task, Terra —
60 при $1.93 и 9.7M, Sol — 65 при $5.00 и 13.2M. Большее число токенов может
стоить меньше из-за различий base rates; меньшее API cost всё ещё не означает
меньшую стоимость accepted outcome.

На 2026-08-30 базовые rates были $4/$20 за миллион input/output tokens для
[Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol) и $5/$25 для
[Opus 5](https://platform.claude.com/docs/en/docs/about-claude/models/choosing-a-model).
Фактический per-task cost дополнительно зависит от input/output composition,
cache, effort и завершённых attempts.

## Нельзя строить временной график через смену instrument

Июльская [launch analysis](https://artificialanalysis.ai/articles/gpt-5-6-has-landed)
публиковала Sol max с index 80, тогда как августовская v1.4 surface показывает
65. Между ними менялись task pool, Terminal-Bench revision, Q&A scoring, token
accounting и reward-hacking rules. Поэтому 80 → 65 является instrument
discontinuity, а не наблюдаемой model regression. Для temporal claim нужен
same-revision rerun.

## Operational overhead не равен нулю

В [первичном cache report](https://github.com/anthropics/claude-code/issues/82563)
анализ 732 sessions и 13,688 requests нашёл 85 full-prefix rewrites. Они дали
31.3% cache-write tokens; 25 episodes произошли быстрее чем за 300 секунд, а
наблюдение затронуло четыре Claude families. Это указывает на client/cache
mechanism, а не на efficiency trait одной модели.

Эти числа нельзя арифметически прибавить к benchmark cost: corpus, route и
denominator другие. Они показывают, какие operational категории owner study
должен измерять отдельно — cache writes, retries, supervision, verifier time,
termination и accepted artifacts.

## Что не установлено и куда идти

- Нет универсального победителя между модельными семьями.
- Нет сравнения total cost per accepted AoA outcome.
- Один benchmark origin не создаёт независимой cross-instrument репликации.
- Historical и current index нельзя сравнивать как одну time series.
- Product-runtime issue не доказывает model-only cost pressure.

Следующий осмысленный шаг — exact candidate configurations на AoA task classes
с общей revision и ledger `requested → executed → artifact → verified →
reported → termination`, включая wall time, token composition, cache, retries,
operator time и acceptance. До такого study packet остаётся `review_for_study`,
а не routing input.
