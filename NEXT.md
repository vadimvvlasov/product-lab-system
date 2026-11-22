# Next — на чём остановились

Обновлено: 2026-10-19. Фреймворк перестроен и закоммичен (`main`, `e063f9d`). Дальше — первый реальный цикл: sweep → outreach → review.

## Сделать по порядку

- [ ] Открыть в Obsidian `registry.base` и `leads.base` — проверить, что виды открываются без ошибок (синтаксис Bases не проверялся).
- [ ] Вписать 1–3 сегмента в § Сегменты в ротации в [inbox](inbox.md).
- [ ] Задать `timebox_hours`, порог продолжения и порог остановки в [EXP-ASC-004](projects/anti-scope-creep/experiments/exp-asc-004-outreach.md) и [EXP-ASC-010](projects/anti-scope-creep/experiments/exp-asc-010-segment-agencies.md).
- [ ] Провести первый sweep ([10-discover](system/10-discover.md), § Sweep) — можно попросить Claude: «проведи sweep по сегментам из inbox.md». Результат: 20 лидов в `projects/anti-scope-creep/leads/`.
- [ ] Запустить outreach EXP-ASC-004: 20 контактов, не больше 10 сообщений в день.
- [ ] По желанию: поставить ежемесячный sweep через `/schedule`.

## Позже

- Реализовать сетевой read-only verifier URL/цитат: проверка `http_status`, наличия выдержки и `content_hash` с записью лога (`verified_at`). Offline snapshot-проверка по локальным клиппингам уже есть (`python -m pls_evidence verify`, [evidence-шаблон](templates/evidence.md), § Snapshot-проверка); она не заменяет `verified_by: human` для B/A. Сетевой verifier не реализован и сетево не тестировался.
- Выделить стартовый шаблон для новых MVP из репо anti-scope-creep (задача по коду в репо). Пока шаблон не выделен, это цель, а не блокер: G1/G3 от него не зависят, новый MVP можно начинать с текущего проекта.
- Через 1–2 месяца: виды «Калибровка» и «Доходность» → поправить веса и пороги скоринга.

Когда пункт выполнен — отметить здесь; когда все выполнены — удалить файл.
