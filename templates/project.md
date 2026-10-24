---
kind: project
id: XXX
status: active
production:
repository:
verified_at:
north_star: paying_customers
portfolio_north_star:
paying_customers: 0
revenue_total: 0
---

# Project: [название]

> Карточка связывает проект с его идеями, экспериментами и репозиторием. Технические факты (архитектура, события, eval, ops) живут в репозитории — здесь только ссылки на них. `verified_at` — дата последней сверки ссылок и статуса с репозиторием и production. `north_star` — `paying_customers | portfolio_artifact`. Для `portfolio_artifact` заполняется `portfolio_north_star`, а `paying_customers` не требуется.

**Роль в Product Lab:**

**Основная идея:** [[idea-xxx-001-slug]] — проблема, сегмент, свидетельства, неизвестные и score живут в карточке идеи.

## Источники истины в репозитории

| Что | Где |
|---|---|
| Состояние и возможности | |
| Спецификация | |
| Правила для coding agent | |
| События аналитики и воронка | |
| Качество / eval | |
| Мониторинг и ops | |
| Данные и приватность | |

## Треки

- **Business:** что будет считаться коммерческим успехом.
- **Portfolio:** какие инженерные артефакты ценны сами по себе.

## Идеи и эксперименты

Ведутся в `ideas/`, `experiments/` и `leads/` этой папки; сводка — в [[registry.base]] и [[leads.base]].

**Главная метрика:**
- `north_star: paying_customers` — `paying_customers` (до готового платного кода — пользователи с L4).
- `north_star: portfolio_artifact` — `portfolio_north_star`; `paying_customers` для такого проекта не обязателен.
