# Inbox

Сырые сигналы до экспресс-оценки ([10-discover](system/10-discover.md), § Sweep). Одна строка — один сигнал: дата, URL, одна фраза о боли. Разбирается на ежемесячном sweep.

## Сегменты в ротации

Порядок обхода в sweep: 1–3 сегмента за раз.

1. Digital-фрилансеры (разработчики, дизайнеры) — beachhead для [EXP-ASC-004](projects/anti-scope-creep/experiments/exp-asc-004-outreach.md).
2. Небольшие digital-агентства и малый бизнес — для [EXP-ASC-010](projects/anti-scope-creep/experiments/exp-asc-010-segment-agencies.md).

## Сигналы

<!-- - YYYY-MM-DD — <URL> — <боль одной фразой> -->

Sweep 2026-11 (сегмент 1). Страницы открыты, выдержки получены из текста страницы, но не проверены человеком (`verified_by` не заполнено). Все — L2, сегмент «независимые подрядчики», не фрилансеры-дизайнеры. Даты постов старые.

- 2026-11-22 — https://news.ycombinator.com/item?id=28538879 (пост 2021-09-15, Guid_NewGuid) — безлимитная indemnity в контракте подрядчика: «realised after a bug related to payment processing I had the clause in my contract»; убрал клаузу.
- 2026-11-22 — https://news.ycombinator.com/item?id=28538879 (2021-09-15, TYPE_FASTER) — «I have been given SOWs/contracts to sign as an individual that included indemnification clauses»; страховка «a nonstarter for me» по цене; клаузы удавалось убрать.
- 2026-11-22 — https://news.ycombinator.com/item?id=13640224 (2017-02-14, chrisbennet) — контракт на разработку с ответственностью за «estimated loss of profits»; отказал, нашёл остальные ловушки через своего юриста.
- 2026-11-22 — https://news.ycombinator.com/item?id=13640224 (2017-02-14, mikekchar) — отказался подписать indemnity работодателю; слабее: это найм, а не клиентский договор.

Sweep 2026-11, Chrome (сегмент 1, смежная боль: условия оплаты). Текст прочитан на странице; человек не проверял. Ветка про просрочку оплат, не про риски договора, поэтому для идеи это косвенный сигнал. В ветке много авторов-продавцов своих инструментов; в записи только авторы без заявленного продукта.

- 2026-11-22 — https://www.indiehackers.com/post/freelancers-of-ih-how-do-you-actually-deal-with-a-client-paying-late-or-never-55972ef40e (Kevin Kan, 2026-07-23/24) — dev-фрилансер: «Usually one or two invoices at a time, a few thousand each, dragging 60 to 90 days past due.»; workaround: депозит 30–50%, работа на staging до оплаты, net-15 против подписанного PO.
- 2026-11-22 — тот же URL (SongTrailer, 2026-07-24) — «once work continued after the due date, the client learned that the deadline had no real consequence»; workaround: пауза работы после второго просроченного срока.

Sweep 2026-11, Reddit (сегмент 1). Тексты взяты из файлов-клиппингов владельца в `~/Downloads`, ссылки и даты из их заголовков; страницы я не открывал (Reddit закрыт для моих инструментов), человек не проверял. Восьмой пост из списка (`1sz8sk7`, дубль заголовка «Clauses I wish…») файлом не передан.

- 2026-11-22 — https://www.reddit.com/r/webdev/comments/1qps223/how_do_you_handle_clients_asking_for_just_one/ (gersa9080, 2026-01-29) — L2: «Then I'm working nights and weekends for the same money.»; сначала соглашается на доп. работу, чтобы не потерять клиента.
- 2026-11-22 — https://www.reddit.com/r/freelancing/comments/1w6zmr1/how_do_you_handle_prospective_clients_who_want_to/ (ImObluentasteit, 2026-09-04) — L2: юристы корпоративного клиента вычеркнули «2-round revision limit» и штраф за просрочку; автор боится «infinite unpaid scope creep».
- 2026-11-22 — https://www.reddit.com/r/freelancing/comments/1rr4bqu/whats_the_worst_contract_youve_ever_signed/ (vncprograms, 2026-03-12) — L1: случай «a friend of mine»: «unlimited revisions as reasonably required» на стр. 4, шесть месяцев правок; из вторых рук, один сигнал.
- Слабые, не засчитаны: Mammoth-Ad-2074 (https://www.reddit.com/r/freelancing/comments/1tlkcv3/i_stopped_gutfeeling_my_freelance_quotes_here_is/, 2026-05-23) — «lose thousands of dollars», но пост продвигает собственный «pricing engine»; stealthagents (2026-04-10, в ветке «Clauses…») — «working on one project for weeks», но тот же аккаунт оставил в той же ветке комментарий не по теме про «subscription charge» и «free reads» — похоже на шаблонные ответы.
- Не L2 (советы или процесс без личной боли): Confident_Ad9717 «Clauses I wish…» (шесть клауз: payment on approval, unlimited revisions, IP на всё, non-compete, auto-renewal, uncapped indemnification — полезно как список категорий); `__blue________`, Leather-Concept8657, советчики в ветках.

Sweep 2026-11, Reddit, второй пакет клиппингов (сегмент 1, плюс креативные подрядчики). Читал только текст поста автора и первые комментарии; ветки целиком не читал. Те же оговорки: страницы не открывал, человек не проверял.

- 2026-11-22 — https://www.reddit.com/r/freelance/comments/1x7vsd6/startup_founder_wants_me_to_sign_an_8page/ (pixelpoetess_, 2026-10-17) — L2: клиент прислал «NDA» на 8 страниц с исключительной передачей IP, отказом от моральных прав, запретом портфолио; «Only I'm bound, 10-year confidentiality, retroactive to earlier conversations.»
- 2026-11-22 — https://www.reddit.com/r/freelancing/comments/1x0fke9/legit_contract_feels_like_somethings_are_missing/ (EmptyCalOuR, 2026-10-08) — L2 слабый: в присланном договоре нет сроков и порядка оплаты.
- 2026-11-22 — https://www.reddit.com/r/freelancing/comments/1xpy6ma/client_not_releasing_payment_project_submitted_in/ (Dry_Slice_8020, 2026-11-07) — L2: разработчик сдал firmware, клиент держит оплату, пока не будет готов CMS другого исполнителя.
- 2026-11-22 — https://www.reddit.com/r/freelance/comments/1x0xgky/client_owes_me_250_after_i_completed_their/ (rxmxn9, 2026-10-08) — L2: $250 по условию «upon approval» не оплачены; small claims «around $150 just to pursue $250».
- 2026-11-22 — https://www.reddit.com/r/freelance/comments/1qqtkoh/looking_for_advice_after_a_payment_dispute_with_a/ (Cultural-Knowledge17, 2026-01-30) — L2: после договора и 50% предоплаты клиент использует принятую работу и заявляет, что она «wasn't completed properly»; другие подрядчики того же заказчика сообщили о похожем.
- 2026-11-22 — https://www.reddit.com/r/freelance/comments/1uteu9k/how_should_i_handle_a_client_who_keeps_responding/ (helloitsapotato, 2026-07-11) — L2: клиент присылает правки к договору в день вступления в силу; автор дважды пересматривал договор с юристом.
- 2026-11-22 — https://www.reddit.com/r/freelance/comments/1to9m9h/nightmare_client_from_hell_please_help/ (Fantastic-Toe9905, 2026-05-26) — L2: веб-разработчик; шесть месяцев scope creep; клиент требует исходники до оплаты и присылает договор, сгенерированный ChatGPT, «basically forces me into slavery».
- 2026-11-22 — https://www.reddit.com/r/freelance/comments/1uqpl05/laid_off_and_then_hired_back_as_a_1099_contractor/ (Least-Fig7206, 2026-07-08) — L2: подписал под давлением, «The scope is broad/poorly written. It's based on hours per week, not project-based.»; сегмент маркетинг, вне текущих.
- 2026-11-22 — https://www.reddit.com/r/freelance/comments/1xsssk6/microsoft_word_contract/ (Important-Try-909, 2026-11-10) — L2: ретушёр ведёт договор с брендом через две итерации; юристы клиента просят подписать Word вместо PDF, автор опасается правок после подписи.
- 2026-11-22 — https://www.reddit.com/r/freelance/comments/1xg8vps/new_chat_gpt_freelance_design_scam/ (BenderWorks, 2026-10-27) — L1: дизайн-студия, в нескольких письмах за месяц одинаковое требование NDA и «must own all IP», затем молчание; автор подозревает скам, а не договор.
- 2026-11-22 — https://www.reddit.com/r/freelance/comments/1x1eaf6/exclient_and_her_husband_are_harassing_my_family/ (Broad-Motor2277, 2026-10-09) — L2 для «нет письменного договора»: дизайнер работал без договора, спор о файлах и сайте перерос в угрозы; к проверке договора отношения не имеет.
Sweep 2026-11, Reddit, третий пакет клиппингов (первые сигналы по агентствам). Читал первые ~30–40 строк каждого файла; ветки комментариев не читал. Оговорки те же.

- 2026-11-22 — https://www.reddit.com/r/freelancing/comments/1xsi9he/how_do_you_handle_outofscope_work_in_a_proposal/ (obeckett21, 2026-11-10) — L2, **агентство**: «We tighten the language, we walk through it on a call, and it still happens.» — клиенты после подписания SOW добавляют работу вне объёма.
- 2026-11-22 — https://www.reddit.com/r/agency/comments/1xqg46g/client_wants_to_change_pricing/ (Large_Somebody1231, 2026-11-08) — L2, **агентство**: клиент требует оплату только после заказа вместо retainer; «payout potentially a year out or never.»
- 2026-11-22 — https://www.reddit.com/r/freelancing/comments/1xpedah/how_much_feedback_is_too_much/ (Capable-Employee-410, 2026-11-06) — L2: видеоредактор, правки без конца, лимит раундов не назван, «I don’t even charge for it.»
- 2026-11-22 — https://www.reddit.com/r/freelancing/comments/1xzmvo3/getting_client_to_sign_msa_and_sow/ (Raosted, 2026-11-18) — L2: клиент не подписывает MSA и SOW до начала работ; автор хочет быть защищён по «risk and liability».
- 2026-11-22 — https://www.reddit.com/r/freelancing/comments/1xmzm74/should_i_setup_a_llc_and_get_eo_insurance_before/ (EyeTechnical7643, 2026-11-03) — L1: спрашивает про LLC, E&O и «maximum liability» в договоре; личного случая нет.
- 2026-11-22 — https://www.reddit.com/r/freelancing/comments/1xngsi5/is_this_normal_for_freelancing_or_am_i_being/ (Mindless_Sherbert_36, 2026-11-04) — L2: фрилансер-аналитик; в договоре scope без admin и ops, но клиент добавляет эту работу («that's just how startups are»), часы в договоре не указаны; клиент предлагает перейти на 40 часов, новый договор на подписание.
- Четвёртый пакет клиппингов (~65 файлов): почти все — Showoff Saturday, пересказы личных проектов, найм продавцов и «как найти клиентов». Открыто 2 файла, один дал сигнал выше; второй (CharlieandtheRed, r/webdev, 2026-11-10) — усталость от ИИ, договор клиента с GEO-компанией не его.
Sweep 2026-11, не для ASC: кластер «подрядчик получает доступ к данным клиента без защиты». Тексты из клиппингов `~/Downloads/reddit/`, человек не проверял.

- 2026-11-22 — https://www.reddit.com/r/webdev/comments/1xtom77/update_its_genuinely_not_depressing/ (Lee-chaolan, 2026-11-11) — L2: дали админ-доступ и тысячи CSV с данными клиентов и пациентов, пароли в открытом виде; «All without having signed an NDA or contract by the way.»
- 2026-11-22 — https://www.reddit.com/r/webdev/comments/1xm6kbz/developer_looking_for_advice_on_encryption_and/ (PuzzleheadedPin4797, 2026-11-03) — L1: «I’m a solo developer building a web and Android app that handles private documents and account records.»; просит проверить подход к безопасности.
- Не засчитано: BarFantastic7174 (бесплатные видео-образцы, не про договор), metro_wars (опрос о сборе документов, автор сам ищет инструмент), SnooRevelations5974 (процесс онбординга), посты про поиск клиентов и инструменты. Один и тот же аккаунт burimbp оставляет в ветках комментарии со ссылкой на «contract thread» и вопросом к автору; похоже на привлечение разговоров, не засчитан.
- Не читал, по заголовкам не про договор: цены и оплата (три поста, один на испанском и один на тагальском), поездки, поиск клиентов (около десяти), инструменты и ИИ-видео.
- Слабое совпадение, не засчитано: lil_tink_tink (2026-08-30, проиграл тендер, договор не обсуждается), Local_Kangaroo6370 (2026-11-02, нет письменного договора), Last-Investment383 (2026-02-19, проект остановлен без сообщения), aboy76 (2025-12-03, задержка оплаты; старше года), Expert-Advisor9990 (поиск работы).
- Не читал, по заголовкам не про риски договора: расписание клиентов, Gmail, предоплата $150 как подозрение на скам, перенос встреч семь раз, ожидание клиентов, инвойсы, Google Ads, найм холодных звонков, первый клиент, управление проектами, две оферты, ценовые возражения, поиск клиентов, холодные звонки в Индию. Два файла дублируют уже прочитанные.

Конкуренты, замеченные в комментариях (в idea § 3 «не исследованы»): clausely.eu (Adventurous_Papaya43, 2026-04-09), REDLYNE / redlyneai.com (Lazy_Motor_9030, 2026-05-04); раньше в поиске: ContractGhost, ClauseShield, ContractReview, ReadThePrint. Пространство занято; это влияет на вопрос 6 идеи.

Не записано как свидетельство (L0): блоги Upwork, Fiverr, Freelancers Union, Contra, Sprintlaw; страницы продуктов (ContractGhost, ClauseShield, ContractReview и др.); посты продавцов.

## Отклонены экспресс-оценкой

- «Не начинай работу до подписи и аванса» (не ASC) — ✗ 2026-11: сигналы есть (Lee-chaolan, helloitsapotato, Raosted, SnooRevelations5974), но цепочка «договор → аванс → старт» уже автоматизирована в HoneyBook, Dubsado, Plutio ($19), Indy ($9), Agiled ($12–40); бесплатный совет «stop until paid and signed» популярнее любого инструмента; в отзывах нет жалоб на сам гейт депозита; пустое место только до подписи (предложения и превью без договора), но боль поведенческая. Проверить одним вопросом в EXP-ASC-004: «пользуетесь ли CRM и что мешает начать только после подписи».

- Доступ подрядчика к данным клиента без NDA и защиты (не ASC) — ✗ 2026-11: два автора на L1–L2 и один конкретный (Lee-chaolan), покупатель не определён (проблема на стороне клиента, не подрядчика), по каждому куску уже есть предложения (NDA-генераторы бесплатно, DPA через Fiverr, E&O и cyber от брокеров, pentest за $1500–3500 и автоматические сканы за $199–500); готовности платить нет.

- Безлимитная indemnity и IP у независимых подрядчиков (кластер из HN выше) — 4 «да» по экспресс-оценке (L2, 3 автора, затраты/workaround, сегмент), но ✗ канал: HN без личных сообщений. Статус кластера: оставить в inbox, искать площадки с каналом.
- Digital-агентства и малый бизнес (сегмент 2) — ✗ 2026-11: не найдено ни одного личного случая; только статьи юристов и страницы продуктов (L0).
- Фрилансеры: scope creep и безлимитные правки — ✗ 2026-11: только гайды и вендорские блоги; ветки Upwork вернули редирект на support.upwork.com, содержимое не прочитано.
