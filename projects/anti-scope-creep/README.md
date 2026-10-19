---
kind: project
id: ASC
status: active
production: https://anti-scope-creep.vadimvlasov.workers.dev/
repository: https://github.com/vadimvvlasov/anti-scope-creep/
verified_at: 2026-10-19
---

# Project: Anti-Scope Creep

> Карточка связывает проект с его идеями, экспериментами и репозиторием. Технические факты живут в репозитории; `verified_at` — дата последней сверки.

**Роль в Product Lab:** первый продукт, на котором проверяется весь повторяемый процесс — от web evidence и идеи до release, аналитики и решения о следующих инвестициях.

**Основная идея:** [[idea-asc-001-contract-risk-review]] — проблема, сегмент, свидетельства, неизвестные и score живут в карточке идеи.

## Источники истины в репозитории

| Что | Где |
|---|---|
| Состояние и возможности | [README](https://github.com/vadimvvlasov/anti-scope-creep#readme) — «Current status»; предупреждение о false alarms Groq на коммерческих договорах |
| Спецификация | [`docs/spec.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/docs/spec.md) |
| Правила для coding agent | [`AGENTS.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/AGENTS.md), [`docs/ai-workflow.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/docs/ai-workflow.md) |
| События аналитики и воронка | [`docs/analytics.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/docs/analytics.md), `scripts/funnel.sql` |
| Качество / eval | [`eval/README.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/eval/README.md) (метод), [`docs/eval.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/docs/eval.md) (результаты) |
| Мониторинг и ops | [`docs/architecture.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/docs/architecture.md) § 6 (план, phase 4), [`ops/README.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/ops/README.md) (runbook, инциденты) |
| Данные и приватность | [`docs/ai-data-policy.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/docs/ai-data-policy.md), [`security/README.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/security/README.md) |

### Сверка 2026-10-19

- Аналитика уже работает (PR #38, 2026-10-13): собственный `POST /events`, UTM first-touch, воронка `pageview → signup_completed → analysis_started → report_exported → pro_cta_clicked → pro_waitlist_joined`. Тексты договоров и PII в события не попадают.
- В production идёт проверка спроса Pro ($19/мес, waitlist) — зарегистрирована как [[exp-asc-005-pro-waitlist]].
- Мониторинг: runbook и разборы инцидентов есть; метрики, dashboards и alerts — план phase 4.
- History Search: UI на mock data, backend `POST /query` возвращает `501`. LoRA-классификатор не начат.

### События, которых не хватает экспериментам

Сверх текущей воронки: `sanitized_preview_opened`, `sanitized_preview_edited`, `analysis_confirmed` ([[exp-asc-001-anonymized-preview]]); `history_search_started`, `history_search_completed`, `history_search_helpful` ([[exp-asc-002-history-search]]); `analysis_completed`, `finding_feedback_submitted`, `second_analysis_completed` (качество и retention); `payment_completed` (когда появится оплата). Только минимальные метаданные — правила в `docs/analytics.md`.

## Каналы и посты

Гипотеза серии: целевые англоязычные freelancers сталкиваются с проблемными договорными условиями и готовы попробовать узкий инструмент анализа договоров, если показать конкретный сценарий и прозрачно объяснить обработку данных.

Каналы-кандидаты:

- LinkedIn: посты от личного профиля, кейсы, опросы и демонстрация работающего инструмента.
- Reddit: поиск и полезные комментарии в сообществах о freelance; сначала проверить правила каждого сабреддита, не спамить ссылками.
- Indie Hackers / r/SideProject: отзывы на продукт и инженерный подход; аудитория смещена к builders — не путать её реакцию со спросом целевых покупателей.
- Hacker News Show HN: технический запуск, если продукт соответствует правилам площадки; не делать его единственным каналом.
- Отзывы/сравнения существующих contract review tools: искать систематические жалобы и неудовлетворённые потребности.

Последовательность (каждый пост — отдельный эксперимент `method: post`):

1. [[exp-asc-004-pain-post]] — последний неприятный случай с договором.
2. [[exp-asc-006-case-post]] — разбор обезличенного условия.
3. [[exp-asc-007-demo-post]] — работающий продукт.
4. [[exp-asc-008-feature-post]] — конкретное улучшение (preview или History Search).
5. [[exp-asc-009-follow-up-post]] — результаты улучшений.

Правила для всех постов проекта:

- Не публиковать и не просить присылать конфиденциальные документы в открытые комментарии.
- Не утверждать, что продукт заменяет юриста или гарантирует отсутствие риска.
- Учитывать правила рекламы/самопродвижения площадки.
- Прямо указывать, что продукт внешний и использует AI; объяснять обработку данных до загрузки договора.
- UTM по формату из `docs/analytics.md`: `utm_source=<site>&utm_medium=<post|video|listing|comment>&utm_campaign=<what>`.

После серии: какой канал привёл целевых людей и какие гипотезы подтвердились. Реакция без продуктовых действий — повод проверить предложение и аудиторию, а не объявлять спрос доказанным.

## План применения Product Lab

1. ~~Instrumentation и source attribution~~ — сделано в репо (`docs/analytics.md`).
2. Предпросмотр псевдонимизированного текста как гипотеза доверия — [[exp-asc-001-anonymized-preview]].
3. Посты, которые проверяют проблему и приводят целевую аудиторию; измерять core actions, а не только реакции — серия выше.
4. Text-to-SQL как retention/utility experiment для пользователей с несколькими договорами — [[exp-asc-002-history-search]].
5. Синтетика и LoRA как quality/portfolio workstream — [[exp-asc-003-synthetic-data-lora]]; не считать это свидетельством спроса.
6. Discover/Screen для основной идеи ретроспективно: evidence-таблица и scoring в [[idea-asc-001-contract-risk-review]].
7. На регулярном review объединять выводы из public evidence, production events, feedback и оплат.

## Треки

- **Business:** люди реально проверяют договоры, используют результаты, возвращаются и платят.
- **Portfolio:** хороший eval pipeline, безопасный text-to-SQL agent, воспроизводимый LoRA benchmark, documented architecture.

Обе цели допустимы, но отчётность и решения по ним ведутся отдельно. Сводка экспериментов — [[registry.base]].
