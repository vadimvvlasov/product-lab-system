---
kind: experiment
id: EXP-ASC-005
project: "[[projects/anti-scope-creep/README|Anti-Scope Creep]]"
idea: "[[idea-asc-001-contract-risk-review]]"
method: feature
post_goal:
track: business
status: live
decision:
signal:
owner:
created: 2026-10-19
launch_date: 2026-10-13
review_date:
timebox_hours:
spent_hours:
revenue:
score_at_launch:
confidence_at_launch:
---

# EXP-ASC-005: Pro plan demand test (waitlist)

Зарегистрирован ретроспективно по репо: [`docs/analytics.md`](https://github.com/vadimvvlasov/anti-scope-creep/blob/main/docs/analytics.md), § «The Pro plan is a demand test»; PR #38 от 2026-10-13. `launch_date` — дата merge; фактическое появление в production проверить. Формулировка гипотезы и primary metric предложены при регистрации — в репо их нет, подтвердить или поправить.

## Гипотеза

Мы верим, что **зарегистрированные пользователи** будут **открывать диалог Pro и записываться в waitlist при показанной цене $19/мес**, потому что **анализ договоров для них достаточно ценен**. Если это произойдёт, мы ожидаем **ненулевую долю записей в waitlist среди активированных пользователей**.

## Дизайн (G2)

- **Сегмент:** зарегистрированные пользователи (кнопка Pro есть только на страницах после входа).
- **Канал / триггер:** кнопка Pro в header и рядом с ошибкой дневного лимита (`placement: header | daily_limit`).
- **Минимальное изменение:** диалог с ценой ($19/мес) и планируемыми функциями; прямо сказано, что Pro недоступен и ничего не списывается; кнопка waitlist. Платного плана нет.
- **Out of scope:** реальная оплата.
- **Основное действие:** запись в waitlist (`pro_waitlist_joined`). По лестнице сигналов — бесплатное намерение, не выше L3.
- **Primary metric:** доля `pro_waitlist_joined` среди пользователей с `analysis_started`, по `utm_source`.
- **Baseline / control:** нет.
- **Guardrail metrics:** нет данных.
- **События аналитики:** `pro_cta_clicked` (`placement`), `pro_waitlist_joined` (`placement`, `price_usd`); воронка — `scripts/funnel.sql` (14 дней, по `utm_source`).
- **Достаточность данных:**
- **Timebox / момент review:**
- **Порог продолжения:**
- **Порог остановки:**
- **Если inconclusive:**
- **Rollback / feature flag:** аналитика выключается сборкой без `VITE_ANALYTICS=true`; диалог — откатом frontend.

## Риски

- Нарушение ожиданий пользователей: fake door — пользователь может ожидать, что Pro доступен; смягчено явным текстом в диалоге.
- Приватность: связь `distinct_id` из `pro_waitlist_joined` с `users.id` нужна, чтобы написать людям из waitlist; email в событиях не хранится.

## Реализация

- Issue / PR: PR #38 (`feat/product-analytics`).
- Dashboard / logs: `psql "$DATABASE_URL" -f scripts/funnel.sql`.

## Результат и решение (G4)

Заполнить по [[experiment|шаблону]] после review.
