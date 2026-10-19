# Project: Anti-Scope Creep

**Роль в Product Lab:** первый продукт, на котором проверяется весь повторяемый процесс — от web evidence и идеи до release, аналитики и решения о следующих инвестициях.

- **Production:** https://anti-scope-creep.vadimvlasov.workers.dev/
- **Repository:** https://github.com/vadimvvlasov/anti-scope-creep/
- **Проверено по публичному README:** 2026-10-18. Состояние следует периодически сверять с репозиторием и production.

## Продуктовая гипотеза

Фрилансеры и малые бизнесы получают договоры, в которых могут быть невыгодные условия. Anti-Scope Creep анализирует договор, показывает возможные риски по категориям, цитирует соответствующие пункты, объясняет риск, предлагает изменение и готовит черновик письма клиенту.

Основные заявленные категории: расплывчатый объём работ/scope creep, unlimited revisions, одностороннее расторжение, передача IP до оплаты, неограниченная ответственность и неблагоприятные условия оплаты.

**Предварительный beachhead-сегмент:** англоязычные digital-фрилансеры (например, software developers и designers), которые регулярно получают клиентские договоры. Это гипотеза, а не доказанный ICP.

## Что есть сейчас по публичному README

- Production frontend на Cloudflare Workers и backend в AWS Lightsail; Postgres хранится в Neon.
- Регистрация и вход, загрузка PDF/TXT/текста, история договоров, анализ через Groq `openai/gpt-oss-120b`, результаты с цитируемыми положениями и предложенными изменениями, черновик email, PDF/DOCX report export.
- Имена и контактные данные, включая некоторые другие идентификаторы, заменяются placeholder-значениями перед LLM-вызовом и восстанавливаются в ответе.
- Цитируемый фрагмент проверяется на наличие в исходном тексте; находки с отсутствующей цитатой отбрасываются.
- Есть offline evaluation с hand-labeled gold sets по CUAD и синтетическим freelance-контрактам; пользователем также заявлен собственный размеченный gold dataset.
- Text-to-SQL History Search описан как следующий этап: UI пока использует mock data, реальный backend возвращает `501`.
- Fine-tuned classifier/LoRA и мониторинг перечислены в README как незавершённые направления на дату проверки.
- README предупреждает, что production-анализатор имеет больше false alarms на коммерческих договорах, чем желательно.

Источники: публичные [README и статус проекта](https://github.com/vadimvvlasov/anti-scope-creep) и [production app](https://anti-scope-creep.vadimvlasov.workers.dev/).

## Главные риски/неизвестные

1. Кто наиболее заинтересован и чаще всего испытывает проблему: freelancer, agency или иной сегмент?
2. Достаточно ли точно production-модель работает на реальных договорах по каждой категории?
3. Что сильнее мешает первому использованию: доверие к AI, конфиденциальность, onboarding, качество или отсутствие срочной потребности?
4. Возвращаются ли пользователи со следующим договором и готовы ли платить за разовый анализ/подписку?
5. Является ли поиск по истории реальным частым workflow или просто технически интересной функцией?
6. Что пользователь получает лучше, чем с универсальным LLM и ручной проверкой?

## План применения Product Lab

1. Проверить instrumentation и добавить source/experiment attribution; не логировать тексты договоров в обычную аналитику.
2. Тестировать предпросмотр псевдонимизированного текста как гипотезу доверия/прозрачности.
3. Публиковать контент и исследовательские посты, которые проверяют проблему и привлекают целевую аудиторию; измерять не только реакции, но и core actions.
4. Отдельно проверить Text-to-SQL как retention/utility experiment для пользователей с несколькими договорами.
5. Вести LLM-generated training data и LoRA как quality/portfolio workstream; не считать это само по себе свидетельством рыночного спроса.
6. На регулярном review объединять выводы из public evidence, production events, feedback и оплат.

## Связанные эксперименты

- [EXP-ASC-001: псевдонимизированный предпросмотр](experiments/exp-asc-001-anonymized-preview.md)
- [EXP-ASC-002: History Search / Text-to-SQL](experiments/exp-asc-002-history-search.md)
- [EXP-ASC-003: синтетические данные и LoRA](experiments/exp-asc-003-synthetic-data-lora.md)
- [EXP-ASC-004: серия постов и acquisition](experiments/exp-asc-004-post-series.md)

## События, которые полезно иметь

`landing_view`, `signup_completed`, `contract_upload_started`, `sanitized_preview_opened`, `sanitized_preview_edited`, `analysis_confirmed`, `analysis_completed`, `finding_feedback_submitted`, `report_exported`, `history_search_started`, `history_search_completed`, `history_search_helpful`, `second_analysis_completed`, `pricing_clicked`, `payment_completed`.

События должны содержать только минимальные метаданные: источник, experiment ID, вариант, длительность, статус, категорию ошибки и версию модели/промпта. Не отправлять в аналитику исходный договор или персональные данные.

## Не смешивать бизнес- и портфельные цели

- **Коммерческий успех:** люди реально проверяют договоры, используют результаты, возвращаются и платят.
- **Инженерная/портфельная ценность:** хороший eval pipeline, безопасный text-to-SQL agent, воспроизводимый LoRA benchmark, documented architecture.

Обе цели допустимы, но отчётность и решения по ним ведутся отдельно.
