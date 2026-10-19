---
kind: experiment
id: EXP-ASC-007
project: "[[projects/anti-scope-creep/README|Anti-Scope Creep]]"
idea: "[[idea-asc-001-contract-risk-review]]"
method: post
post_goal: demo
track: business
status: draft
decision:
signal:
owner:
created: 2026-10-19
launch_date:
review_date:
timebox_hours:
spent_hours:
score_at_launch:
confidence_at_launch:
---

# EXP-ASC-007: Working demo: показать работающий продукт

Часть серии постов — гипотеза серии, каналы-кандидаты и общие правила в карточке проекта, § Каналы и посты.

## Гипотеза

Целевые пользователи переходят по ссылке, регистрируются и выполняют анализ своего договора (L3–L4).

## Дизайн (G2)

- **Сегмент:** англоязычные digital-фрилансеры.
- **Канал / триггер:**
- **Минимальное изменение:** Показать фактический продукт и пригласить проверить сценарий.
- **Основное действие:**
- **Primary metric:** Завершённые анализы (`analysis_started` → результат) с UTM поста.
- **Baseline / control:**
- **Guardrail metrics:** нарушения правил площадки, жалобы.
- **События аналитики:** воронка из `docs/analytics.md` по `utm_campaign` поста.
- **Достаточность данных:**
- **Timebox / момент review:**
- **Порог продолжения:**
- **Порог остановки:**
- **Если inconclusive:**

### Пост

- **Площадка / сообщество:**
- **Правила площадки проверены:** no
- **UTM / campaign ID:**
- **Главный вопрос / CTA:**
- **URL после публикации:**
- **Текст / тезис:**

## Риски

- Приватность / security: не просить присылать договоры в открытые комментарии.
- Нарушение правил площадки или ожиданий пользователей: самопродвижение.

## Результат и решение (G4)

Заполнить по [[experiment|шаблону]] после review.
