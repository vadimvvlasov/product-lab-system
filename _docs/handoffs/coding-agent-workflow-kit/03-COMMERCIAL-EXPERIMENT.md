# Commercial experiment brief — Coding Agent Workflow Kit

> Использовать как вход для создания канонических idea/experiment notes по актуальным шаблонам репозитория. Это не замена `templates/idea.md` или `templates/experiment-s.md`.

## Draft: idea

**Working title:** Coding Agent Workflow Kit: проверяемый workflow для coding agents с независимым QA.

**Proposed project slug:** `coding-agent-workflow-kit`.

**Proposed short code:** `CAWK`, только если ID не конфликтуют с уже существующими.

**Track:** `business`.

**Stage/status:** начать с `inbox`/`researching` и провести экспресс-оценку по текущей модели; не маркировать как подтверждённую идею без evidence.

**Target segment hypothesis:** solo builders / individual developers, которые регулярно делегируют coding agents изменения в существующем репозитории.

**Situation:** агент реализует задачу, но критерии приёмки расплывчаты, сам себе ставит PASS, пропускает регрессию, расширяет scope или не оставляет чёткий handoff.

**Current workaround hypothesis:** длинный `AGENTS.md`, промпты в одном чате, собственная коллекция шаблонов, ручной code review или другие agent frameworks.

**Offer hypothesis:** компактный, готовый к копированию Markdown workflow kit с ролями, шаблоном issue, acceptance criteria, независимым QA, bounded repair loop и одним проверенным примером.

**Critical assumption:** люди, уже использующие coding agents, считают эту проблему достаточно дорогой и готовы купить готовый, проверенный процесс вместо того, чтобы собрать его самостоятельно.

**What remains unknown:** частота проблемы, best-fit segment, готовность платить $19, канал, который может приводить квалифицированных людей, и то, какие agent hosts реально используют потенциальные покупатели.

**Do not pre-fill without evidence:** score, source counts, weeks to revenue, current demand, competitor conclusions or budget. Use a short evidence sweep and record real URLs, dates and quotes per repository rules.

## Draft: first experiment

**Method:** `post`.

**post_goal:** `pricing`.

**Experiment question:** смогут ли квалифицированные пользователи, увидевшие конкретную демонстрацию workflow kit и честное предложение, совершить реальную покупку по тестируемой цене?

**Hypothesis:** «Разработчики, которые уже используют coding agents и сталкивались с поверхностным QA/неясными критериями, будут готовы купить готовый kit, если увидят конкретный воспроизводимый пример workflow, состав продукта и ограничения».

**Offer:** один самостоятельный комплект Markdown-файлов с документацией установки и примером, прошедший проверку в чистом демонстрационном репозитории. Продукт должен существовать и быть доступен к доставке до взимания денег.

**Proposed test price:** `$19`, только hypothesis; требует явного approval владельца до внешней публикации цены/checkout.

**Primary metric:** confirmed paid orders from qualified target customers during the test window. Keep numerator/denominator and buyer qualification explicit. Revenue is recorded in USD gross in `revenue`; refunds, direct cash cost and spent hours are recorded separately.

**Exposure:** use the current system's starting floor for `method: post`: 100 qualified visits OR 20 substantive replies. Define qualifying audience and what counts as a meaningful reply before launch. Floor is an initial heuristic, not statistical proof; do not lower it after seeing results.

**Timebox:** use the current canonical starting heuristic for `post` (4 hours) unless the current branch says otherwise. Timebox includes the bounded experiment work agreed in the experiment note. Do not silently extend it. Any subsequent test gets its own ID/timebox.

**Attribution:** one distinct `utm_campaign` / campaign identifier and stable offer link for this post. The agent drafts tracking instructions; the owner chooses/approves the actual channel and performs publication.

**Guardrails:**
- no publishing, sending DMs, running ads, changing price, taking payment or deploying without explicit owner approval;
- no claims of measured time savings or error reduction without real measurements;
- no payment for an unavailable product or undefined refund terms;
- no sensitive information, private conversation, credentials or client data in published content;
- avoid presenting one purchase as PMF or scale permission.

**Review condition:** when timebox expires or exposure floor is reached, whichever comes first according to the experiment design; then enter `review` and decide based on actual evidence. If exposure is insufficient, separate channel/delivery failure from demand failure and consider only one permitted `more-evidence` retry on that channel.

**Decision logic:**
- confirmed order(s) plus verified delivery = positive L5 evidence; consider only the next limited experiment, not automatic scale;
- target engagement but no checkout/payment = inspect offer, price, trust and checkout friction before choosing iterate/pivot;
- insufficient qualified exposure = `more-evidence`, not `kill`;
- adequate qualified exposure with no meaningful action/payments = assess whether to change offer/segment or park/kill, based on the evidence and current rules.

## Owner choices required before launch

- Approval of the final price and actual commercial terms.
- Approval of the content channel and the final post draft.
- Approval of the checkout/payment provider and refund terms, if payments are enabled.

The agent can prepare drafts and local artifacts without these choices; it must not execute the external actions.
