# GPT-5.6: temporal drift recheck

Статус: pre-canon web reconnaissance; не `ModelClaim`, не `ModelStudy`, не
runtime-currentness и не основание для routing/activation

Дата capture: 2026-08-30

ReconRun: [`recon-run:gpt-5.6/2026-08-30-temporal-drift`](../recon-runs/gpt-5.6-2026-08-30-temporal-drift.json)
Canonical packet digest:
`sha256:e6362e42cf2ea49f59f87705559374c4b77cda01ce1b23b259c64213c79ff43d`

## Вопрос и итог

Забег проверял не «изменилась ли GPT-5.6 вообще», а какие факты изменились
или остались разделены по времени, сегментам страницы и product surface после
первого seed-пакета.

Устойчивый результат состоит из двух границ:

1. Currentness принадлежит использованному сегменту, а не URL целиком.
2. Family/tier label без product и release-time недостаточен для идентичности
   наблюдаемого субъекта.
3. API capacity, product catalog ceiling и local-tool route принадлежат разным
   realization layers.
4. Quota interruption является termination/recovery pressure продукта, а не
   мерой model efficiency.

Это ограничения на вывод, а не новая характеристика GPT-5.6.

## Что выдержало повторный capture

### Цена требует даты и сегмента

На текущих API model pages 2026-08-30 были указаны базовые цены за миллион
токенов: Sol — $4 input / $20 output, Terra — $2 / $12, Luna — $0.20 / $1.20
([Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol),
[Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra),
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)). При этом
[release page](https://openai.com/index/gpt-5-6/) сохранила исходную июльскую
таблицу $5/$30, $2.50/$15 и $1/$6 рядом с более поздними уведомлениями о
снижении цен.

Эти значения не образуют спор о «правильной цене»: одно является историческим
launch-сегментом, другое — текущим датированным API-сегментом. Page-level
freshness уничтожила бы это различие.

### Tier label не равен одному product-time subject

Августовское обновление Sol и Luna относилось к Chat; Work и Codex продолжали
использовать июльские версии. Это прямо разделено в
[Chat update](https://openai.com/index/improving-gpt-5-6-sol-in-chatgpt/) и
[August safety update](https://deploymentsafety.openai.com/gpt-5-6-august-update).
Одинаковый tier label и одинаковая Preparedness designation поэтому не
доказывают одинаковый snapshot или замену прежней версии.

### Result identity тоже исторична

В safety update значение comparator для hard-negative protein binding было
исправлено с 0.4% на 1.48%: прежнее число оказалось pass@1, тогда как подпись
говорила pass@4. Это не независимая репликация результата, но сильный пример
того, что identity одного benchmark value включает metric semantics и revision,
даже если URL не меняется.

### Повтор документации не создаёт новый origin

[Cumulative release notes](https://help.openai.com/en/articles/6825453)
повторяют границу Chat против Work/Codex, но остаются зависимым пересказом того
же provider origin. Они усиливают discoverability, а не независимую поддержку.

### API capacity не равна Codex route realization

Текущая Sol API page описывает 1.05M model context и 128k maximum output. В
[controlled primary report](https://github.com/openai/codex/issues/40258) тот
же ChatGPT Pro account и request получал для Sol `max_context_window=272000`
под четырьмя coding originators и 872000 при omitted/other originator; Terra и
Luna оставались на 872000. Coding route давал 258,400 effective tokens под
описанной 95% policy.

Это сильнее общего quota impression, потому что report меняет одну route
переменную и сохраняет ETags/timeline. Но это всё ещё открытый issue без
provider confirmation и owner-bound runtime subject. Он уточняет product-route
realization; он не уменьшает API model specification.

### Tool route может сломаться до model execution

В [Windows Codex Desktop report](https://github.com/openai/codex/issues/40944)
простая локальная команда не доходила до исполнения: code-mode host handshake
падал для Sol и Luna на двух bundled runtime versions, тогда как GPT-5.5
control в том же окружении выполнял listing. Sandbox, MFA, manual host startup
и локальный cache были проверены, но effective route/comp hash между control
arms различались.

Disposition поэтому — runtime owner и exact replication, не отрицательный
claim о tool-use capability GPT-5.6.

### Quota является outcome termination

[Один Plus-plan report](https://github.com/openai/codex/issues/40905) описывает
два прерывания одного multi-hour Sol goal пятчасовой usage boundary. Здесь есть
минимальный denominator — 2 interruptions / 1 goal — но нет token classes,
состояния artifact, exact accounting или подтверждённого accepted outcome.

Забег сохраняет это как product-policy study trigger: измерять checkpoint,
manual resume, восстановленную траекторию и completion. Переводить его в
«Sol дорог/неэффективен» нельзя.

## Что не установлено

- Нет exact snapshot IDs для всех product surfaces.
- Нет controlled comparison поведения Chat и Work/Codex версий.
- Provider-only material не создаёт независимого consensus о capability.
- Route A/B не подтверждён provider и не связан с exact AoA runtime subject.
- Windows tool-host report не изолирует model от product protocol/comp hash.
- Один quota-interrupted goal не устанавливает incidence или total outcome
  economics.
- Retained launch prose не доказывает, что launch prices всё ещё действуют.
- Benchmark correction не воспроизводит исходный эксперимент.

## Воздействие на метод

Забег принял четыре изменения метода v0.3:

- currentness, digest и supersession связываются с сегментом;
- subject включает product и temporal binding;
- исправленный результат сохраняет старую форму как историю, а не переписывает
  её;
- dependent restatement не увеличивает число независимых origins.
- capacity и tool behavior связываются с product/originator/client/runtime
  route;
- quota записывается в termination/recovery ledger с denominator.

Следующий забег нужен при изменении цен, alias/snapshot/product rollout,
новой correction или достижении заявленного трёхмесячного горизонта временного
снижения цены Sol; а также после provider-confirmed cause/fix для catalog или
code-mode traces и публикации точного quota checkpoint/resume contract.

## Disposition

Сохранить packet как исторически адресуемый pre-canon слой. Не продвигать его
напрямую в `source/`. Любой realization candidate должен заново подтвердить
точный product, snapshot, runtime subject, дату и owner evidence chain.
