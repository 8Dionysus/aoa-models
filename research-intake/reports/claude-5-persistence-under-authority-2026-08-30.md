# Claude 5: persistence under authority

Статус: pre-canon web reconnaissance; не model trait, proof verdict или
runtime diagnosis

Дата capture: 2026-08-30

ReconRun: [`recon-run:claude-5/2026-08-30-persistence-under-authority`](../recon-runs/claude-5-2026-08-30-persistence-under-authority.json)
Canonical packet digest:
`sha256:24647cafefa2c852b7129e165b1164b007d6ee6e9cc17d28d0a8c74b26bfa641`

## Вопрос и итог

Забег проверял, что остаётся от заявлений о long-horizon work и
self-verification, если отдельно учитывать capability, delegated acceptance,
product fallback, session state, transport, TUI termination и operator
visibility.

Получилось три bounded результата:

1. Сильное long-horizon execution не устанавливает право или надёжность
   принятия отчётов других агентов.
2. Реализованная persistence зависит не только от модели, но и от product,
   client/session state, route, transport и наблюдаемости.
3. Safety fallback является частью effective subject identity: выбранный label
   не всегда совпадает с обслужившей запрос моделью.
4. Useful persistence требует отдельно наблюдать orientation sources,
   scheduled continuation, loop state и recovery — уверенный report о
   продолжении не доказывает запущенную работу.

Ни один из этих результатов не является общим отрицательным trait Claude 5.

## Capability и verified outcome

[Fable 5 release](https://www.anthropic.com/news/claude-fable-5-mythos-5)
позиционирует модель для продолжительной асинхронной работы с persistent
memory и self-checking. [Opus 5 release](https://www.anthropic.com/news/claude-opus-5)
подчёркивает self-verification и итерации до результата. Эти provider claims
задают вопросы для проверки, но не дают population denominator для широкого
утверждения.

Независимый instrument даёт более узкий outcome: в
[Coding Agent Index v1.4](https://artificialanalysis.ai/methodology/coding-agents-benchmarking/)
Claude Code с Opus 5 xhigh получил aggregate 68 на 326 задачах с тремя
attempts на задачу; breakdown — 60 на DeepSWE, 89 на Terminal-Bench v2.1 и 55
на SWE-Atlas-Q&A
([comparison surface](https://artificialanalysis.ai/agents/coding-agents/comparisons/claude-code-vs-codex)).
Это method-backed completion evidence для конкретного agent variant и
instrument revision, а не model-only persistence.

## Граница self-work и delegated acceptance

В [первичном orchestration report](https://github.com/anthropics/claude-code/issues/81300)
один и тот же Opus 5 seat демонстрировал сильную реализацию и coherence, но
master repeatedly принимал отполированные worker reports без проверки,
соразмерной риску. Xhigh и дополнительные memory instructions не сняли
наблюдение; hashes обнаружили пять verbatim-transfer errors примерно за десять
минут переноса документов.

Это не опровергает benchmark completion и provider self-verification examples.
Они измеряют разные authority boundaries: проверку собственной работы и
принятие claims другого actor. Полезный следующий шаг — owner-local eval,
который намеренно разделяет эти два режима.

## Orientation, scope и loop recovery

В [orientation report](https://github.com/anthropics/claude-code/issues/83789)
два Claude 5 tasks заняли, по оценке автора, около шести часов до чтения уже
доступных memory, repository operation catalog и prior transcripts; после
этого правильные пути занимали минуты. Тот же report включает преждевременное
abandonment, self-initiated cleanup и verification не того user-visible
artifact. Он смешивает Opus/Fable, несколько задач и product behavior, поэтому
его поддерживаемое ядро — pre-action orientation и scope-control pressure, а
не memory trait модели.

В [dynamic-loop trace](https://github.com/anthropics/claude-code/issues/77727)
1,250-message single-model Fable 5 session сообщила об immediate continuation,
но ScheduleWakeup создал idle gap, замеченный через семь минут. Пользователь
повторил stop condition трижды примерно за час. Сам report указывает на
похожую cross-model recurrence, поэтому различие проходит между reported,
scheduled и executed continuation и маршрутизируется к loop/harness owner.

Вместе с TUI kill/`--resume` trace это создаёт study question: какие evidence
sources были доступны и прочитаны до действия, какой next step был реально
scheduled, существовал ли checkpoint и какой outcome восстановился после
recovery.

## Persistence как реализация

Несколько независимых primary issues описывают разные механизмы. Их общее
ядро — dependence on realization, а не один общий Opus 5 defect.

- [Operator visibility](https://github.com/anthropics/claude-code/issues/84933):
  2 из 20 сопоставимых долгих sessions почти перестали показывать prose, но
  продолжали tool calls и завершили задачи. Completion и supervisability —
  разные outcome axes.
- [TUI termination](https://github.com/anthropics/claude-code/issues/83153):
  два зависания за день в Windows long session; свежие process controls не
  воспроизвели проблему с тем же payload. Это runtime/TUI route, не доказанная
  потеря model capability.
- [Session context realization](https://github.com/anthropics/claude-code/issues/85205):
  одинаково обозначенные Opus 5 1M sessions на одной машине и build получили
  150k либо 1M auto-compact windows.
- [Transport pressure](https://github.com/anthropics/claude-code/issues/87757):
  packet capture насчитал около 69 server-originated resets на 41 connection
  примерно за две минуты; retries обычно восстанавливались, но добавляли
  2–20 секунд и не попадали в transcript.
- [Client/route entitlement mismatch](https://github.com/anthropics/claude-code/issues/82226):
  12 prompt-too-long failures в 2,013 логах возникали около 166k–178k, тогда
  как same-account control sessions других Claude families превышали 800k.

Текущая [provider documentation](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6)
описывает Opus 5 как 1M-context model с output до 128k. Документированная API
capacity и capacity конкретной Claude Code session принадлежат разным authority
layers; одно не следует переписывать другим.

## Exploit-seeking требует instrument evidence

[Coding Agent Index v1.4 methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking/)
обнуляет Terminal-Bench v2.1 attempts, где trajectory review обнаружил
манипуляцию тестами/verifier или получение reference answer. Но опубликованный
control относится только к одному из трёх components и не раскрывает
per-model incidence.

Поэтому текущий Opus 5 score включает bounded integrity control, но не
доказывает ни наличие, ни отсутствие общей exploit-seeking тенденции. Owned
study должен фиксировать coverage, adjudicator и outcomes для каждой arm.

## Product fallback как identity

Anthropic сообщил примерно об 85% снижении biology-related Fable 5 fallbacks
после classifier update, сохранив fallback на Opus 5 для dual-use requests
([safeguard update](https://www.anthropic.com/news/improving-fable-5-s-biology-safeguards)).
Следовательно, исследование product surface должно фиксировать safety route и
fallback, если они доступны: user-selected label может недоопределять реально
ответивший subject.

## Общность контура

Этот packet был принят без изменения schema, model/provider branches или
специального валидатора. Provider docs, benchmark result, primary issues,
runtime observations, counterevidence и product policy вошли как обычные data.
Это практическая проверка, что intake contour не hardcoded под GPT-5.6.

## Что не установлено и куда идти

- Нет общего incidence для перечисленных runtime pressures.
- Разные issues не доказывают единый механизм.
- Нет exact owner realization и controlled long-session replication.
- Нет общей arm, которая одновременно измеряет orientation, scope expansion,
  loop liveness, delegated acceptance и recovery.
- Reward-hacking coverage ограничен Terminal-Bench v2.1, а per-model flags не
  опубликованы.
- Provider positioning и один issue не создают stable behavioral claim.

Runtime/session/transport симптомы направляются владельцам соответствующей
реализации. Delegated acceptance требует отдельного eval design. Повторный
web-run нужен после confirmed cause/fix/counterexample, system-card revision,
изменения fallback/context/loop policy, публикации integrity outcomes или
появления агрегированной telemetry.
