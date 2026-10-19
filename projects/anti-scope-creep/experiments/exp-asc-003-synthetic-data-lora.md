---
kind: experiment
id: EXP-ASC-003
project: "[[projects/anti-scope-creep/README|Anti-Scope Creep]]"
idea: "[[idea-asc-001-contract-risk-review]]"
method: quality
post_goal:
track: portfolio
status: draft
decision:
signal:
owner:
created: 2026-10-18
launch_date:
review_date:
timebox:
---

# EXP-ASC-003: LLM-синтетика и LoRA-классификатор

Тема: AI quality / engineering portfolio. Цель — улучшить классификацию рискованных положений и получить воспроизводимый технический кейс. Коммерческий спрос не считается доказанным самим фактом fine-tuning. Метод — модуль [[llm-eval-data]]. **Timebox не задан** — обязателен для `track: portfolio` до старта.

## Исходное состояние

Есть gold/evaluation data с ручной разметкой и offline evaluation pipeline (репо: `eval/README.md`, `docs/eval.md`). Перед работой зафиксировать версии набора, baseline модели и результатов на production-подобной конфигурации.

## Гипотеза

Синтетические контрастные примеры и LoRA могут улучшить извлечение/классификацию рискованных положений без неприемлемого роста false positives, стоимости или latency.

## Дизайн (G2)

- **Минимальное изменение (pipeline):**
  1. Разделить train/validation/test на уровне документов, исключить утечки.
  2. Оставить gold test set неизменным и недоступным генератору.
  3. На примерах train попросить LLM создавать разнообразные положительные/отрицательные варианты и контрастные пары.
  4. Требовать метки, точный evidence span, rationale и происхождение примера.
  5. Проверить схему, привязку evidence span к тексту, дубликаты, class distribution и противоречия.
  6. Использовать verifier/critic как фильтр, не как окончательную истину.
  7. Сохранить версии модели-генератора, prompt, seed/config и confidence.
  8. Сравнить baseline, prompt-only, synthetic augmentation и LoRA на одном зафиксированном test set.
  9. Разобрать false positives/false negatives по каждой из шести категорий.
- **Primary metric / метрики:** precision, recall, F1 и число false positives/false negatives по категории; качество severity; доля цитат, точно встречающихся в документе; latency/cost; устойчивость на разных типах договоров.
- **Baseline / control:** текущая production-конфигурация на зафиксированном test set.
- **Порог продолжения / остановки:** задать до обучения — какие метрики должны улучшиться, какой спад допустим в других классах, какие ошибки неприемлемы.
- **Если inconclusive:** если качество на test set не улучшается — это валидный вывод; не выбирать новую модель по train loss или синтетическому benchmark.
- **Timebox / момент review:**

## Риски

- Качество результата: утечка test в train через синтетику.
- Стоимость / latency: обучения и inference.

## Реализация — портфельные артефакты

- описание dataset provenance и split;
- синтетический data generator;
- validators и deduplication;
- воспроизводимый training/evaluation script;
- benchmark report и error analysis;
- ограничения и выводы о качестве.

## Результат и решение (G4)

Заполнить по [[experiment|шаблону]] после review.
