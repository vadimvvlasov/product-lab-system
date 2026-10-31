# Product Lab — arXiv Research Review 2026-10-31

> **Review mode:** quarterly deep review (baseline; no previous research review)
> **Search cut-off:** 2026-10-31
> **Repository:** `main` @ `e040929e11f5881ddbb0d572278117878d3cfa71`
> **Status:** research-only. No PLS rules, templates, code, or configuration were changed. No issues, PRs, branches, commits, or pushes were created.

## 0. How to read this report

The protocol requires facts, interpretation, and hypotheses to be separated. This report uses three labels:

- **Observed** — directly supported by a paper, repository artifact, or metadata record. The source is linked.
- **Interpretation** — the reviewer's assessment of what the observation means for PLS. It is not a fact about the paper or the repository.
- **Hypothesis** — a proposed change whose benefit is not yet established. It must be tested before adoption.

Two grading systems are used independently:

- **Inspection level:** `A` = abstract/metadata only; `F` = full paper text; `C` = relevant code, data, or benchmark inspected; `E` = a relevant experiment or reproduction performed by the reviewer. This review used `A` and `F` only. No `C` or `E` was awarded.
- **Study strength:** `S0` conceptual; `S1` synthetic/narrow benchmark; `S2` empirical but limited; `S3` strong comparative evidence; `S4` independently supported. These are qualitative labels, not universal rankings.

Publication status is recorded separately from study strength. A preprint can be useful; peer review does not guarantee correctness or transferability.

---

## 1. Metadata

| Field | Value |
|---|---|
| Review title | Product Lab — arXiv Research Review 2026-10-31 |
| Review mode | Quarterly deep review; baseline (no previous review report found) |
| Review date | 2026-10-31 |
| Search cut-off | 2026-10-31 |
| Time window | 2024-11-01 to 2026-10-31 (24 months); older foundational work only where it remained relevant |
| Repository | `/home/vadim/work/Obsidian/product-lab-system` |
| Git branch / revision | `main` @ `e040929e11f5881ddbb0d572278117878d3cfa71` |
| Pre-existing worktree state | Untracked: `_docs/graph-engine-implementation-spec.md`, `_docs/graph-engine-stage-0-plan.md`, `_docs/handoffs/`, `system/modules/arxiv-review-prompt.md`, `system/modules/arxiv-review-protocol.md`. These were preserved and not modified. |
| Reviewer | AI research agent (DeepSeek V4.1 Flash Free via OpenCode) |
| Tools used | arXiv API; Crossref API; OpenAlex API; Python standard-library HTTP/XML; locally converted PDF text (`pdftotext`) |
| Tools not used | No browser automation; no Semantic Scholar; no paid databases; no institutional full-text access; no code execution; no paper reproduction |
| Previous report reviewed | None found. This is the first arXiv research review in the repository. |
| Report location | `_docs/arxiv-review-2026-10-31.md`. `_docs/` is the existing documentation directory. No dedicated research-report directory existed, and no new documentation structure was created. |
| Language | English body; Russian owner summary in §13 |
| Reproduction | None. No paper experiment was rerun; no paper code was executed. |
| Changes to PLS | None. The only repository write is this report. |

### 1.1 Why this is a baseline review

No prior arXiv or research-review report exists in the repository. The review therefore cannot compare against a previous evidence picture, previous recommendations, or a cumulative index. It establishes the first baseline. This is a limitation, not a claim of completeness.

### 1.2 Search and access limitations up front

- Eight papers were read in full. Six additional papers were assessed at abstract/metadata level only. `C` and `E` were not awarded.
- The primary discovery source was arXiv. Crossref and OpenAlex were used for publication status and DOI checks, not for systematic discovery.
- Several relevant papers are preprints. Their findings are reported with that status visible.
- The repository contains no executable PLS implementation, so "implemented behavior" means manually maintained Markdown records, not code. Documented process is not evidence of executed process.
- The repository has one project, ten experiments, and no closed experiment. The execution evidence is therefore thin and cannot support causal claims about PLS design.
- Search hit counts are discovery context, not a precise measure of coverage. Some queries combined `OR` and `AND` without parentheses; the date filter may have bound only to the last term, and out-of-window results appeared. Those results were excluded at screening.

---

## 2. Executive summary

### 2.1 What materially changed in the evidence landscape

This is a baseline review, so there is no previous evidence picture to change. The review establishes one:

- **The strongest and most consistent signal is about evidence verification, not about adding new stages.** Across several independent 2026 papers, surface citation quality was a weak proxy for whether evidence supports a claim or a conclusion. One evaluation of 14 LLMs found link validity above 94% and relevance above 80%, but factual accuracy of only 39–77%; in the paper's two-frontier-model ablation, fact-check accuracy fell by about 42% as tool calls increased from 2 to 150. A separate audit of deep-research agents concluded that citation correctness does not establish conclusion validity, because adaptive search can expose a one-sided evidence set. A 38-mechanism taxonomy argued that repeatability and accuracy do not rule out hidden judgment failure.
- **Calibration and forecasting metrics are not a shortcut to better decisions.** A peer-reviewed study found that forecast skill does not reliably translate into decision skill; model rankings can change at the decision level. A peer-reviewed reanalysis of 240 participants and 7,200 trials found that 67.3% of reported belief changes were exactly zero, and that pooled updating slopes mix movement and magnitude. Industrial group-sequential A/B designs show large runtime gains, but at a scale and infrastructure that PLS does not have.
- **Opportunity-discovery automation is not yet a good trade for a solo builder.** A full-text study found that a supervised fine-tuned LLM matched professional analysts at customer-need abstraction, but only with 1,549 labeled CN–verbatim pairs; zero-shot and few-shot foundation models were substantially worse, and the fine-tuned model could not prioritize needs. Structured customer-context graphs improve voice-of-customer answers in one abstract-level industry study, but require a data graph and a rubric that PLS does not have.

### 2.2 What this means for PLS

**Observed (repository):** PLS already contains the right conceptual safeguards: human source verification, source independence and clustering, a `counter_evidence` field, confidence A/B/C, L0–L5, exposure floors, a decision table, stop rules, and LLM research guardrails. The problem is not a missing philosophy.

**Observed (repository):** The safeguards are not yet exercised. Ten experiments exist: nine are `draft`, one is `review`, and none is `closed`. The only review experiment, `EXP-ASC-005`, is `more-evidence` because exposure and waitlist counts were not recovered; it also lacks `timebox_hours`, `exposure_floor`, `owner`, `score_at_launch`, and `confidence_at_launch`. The only idea, `IDEA-ASC-001`, is `testing` with empty `score`, `confidence`, and `owner`, and has no evidence table. The system cannot currently distinguish "no demand" from "no exposure" for its only launched test.

**Observed (repository):** The written rules already provide a short S form (`templates/experiment-s.md`), an 8-field evidence minimum (`templates/evidence.md`), and an explicit exemption from G1/G3 for S methods (`system/00-model.md`, `system/30-experiment.md`). The gap is not a missing minimal path; it is that the minimal path is not the visible, enforced default, and the only review record does not contain the G2 fields.

**Interpretation:** This is not proof that PLS is too complex. The project is young, and `EXP-ASC-005` was registered retrospectively, which explains some missing launch fields. But the gap between documented controls and recorded decisions is large enough to justify a low-cost test of a smaller default path.

**Hypothesis:** If the default S-test path is reduced to the evidence and decision fields that actually gate G2/G4, more tests will reach a recorded decision without reducing evidence quality. This is tested in Recommendation 2, not assumed.

### 2.3 Recommendations

| ID | Recommendation | PLS fit | Evidence strength | Expected impact | Feasibility | Owner decision |
|---|---|---|---|---|---|---|
| R1 | Record claim-level support in the existing human verification step; require one disconfirmation/negation check for B/A evidence | 3 | 2 | 2 | 3 | **Adopt for experiment** |
| R2 | Make the existing 8 evidence fields + 9 experiment fields (plus existing B/A fields) the visible, enforced S-test minimum; move calibration, portfolio accounting, production analytics, full template, and LLM-eval data out of the default path until their triggers | 3 | 1 | 2 | 3 | **Adopt for experiment (exploratory)** |
| R3 | Defer calibration/forecast-metric expansion until at least three experiments are closed with complete G4; keep the two launch fields and the outcome fields, and defer the review ritual | 2 | 2 | 2 | 3 | **Defer** |

R1 meets the protocol's normal bar (`PLS fit >= 2`, `Evidence strength >= 2`). R2 is explicitly exploratory: it addresses a direct observed execution gap, but no paper directly tests "fewer fields produce more closed experiments." R3 is a deferral recommendation, not an adoption proposal.

### 2.4 Main limitations of this review

- Eight full-text papers and six abstract-level papers are a small sample of a large literature. The review does not claim exhaustive coverage.
- Most evidence-quality papers study LLM agents on benchmark tasks, not a human solo builder verifying sources. Transfer is plausible but not directly tested.
- Several key papers are preprints. Only three of the fourteen table papers have verified peer-reviewed venues; two more report acceptance in arXiv comments, which was not independently verified.
- No code was inspected, no dataset was reanalyzed, and no experiment was reproduced. `C` and `E` are absent.
- The execution evidence comes from one project with ten experiments and zero closed experiments. It cannot establish that PLS design causes the observed state.
- Search was English-language and arXiv-centric. Relevant work in information systems, HCI, or management journals may be missed.

---

## 3. Repository baseline

### 3.1 What was inspected

| Artifact | Role in PLS | What was checked |
|---|---|---|
| `README.md` | System overview, loop diagram, stage names | Read; confirmed the Discover → Screen → Experiment → Deliver → Review loop and the project-agnostic framing |
| `AGENTS.md` | Agent working rules and governance | Read; confirmed research-only boundaries, QA independence, commit/closure rules |
| `_docs/process.md` | Review workflow | Read; confirmed issue-based flow and role separation |
| `_docs/team/roles.md` | Role contracts | Read; confirmed PM / Methodology Engineer / QA boundaries |
| `system/00-model.md` | Canonical stages, statuses, transitions, gates, L0–L5, decision vocabulary, stop rules | Read in full; this is the source of truth for terminology |
| `system/10-discover.md` | Sweep, evidence capture, problem statement, counter-evidence | Read; confirmed 2–4 hour sweep, evidence table, source rules |
| `system/20-screen.md` | Business score, confidence, thresholds, G1, portfolio, calibration | Read; confirmed scoring/confidence logic and calibration ritual |
| `system/30-experiment.md` | Experiment design, exposure floors, decision table, measurement, review | Read; confirmed hard rule that below-floor results can only be `more-evidence` |
| `system/40-deliver.md` | Delivery and release | Read; confirmed G3/release path |
| `system/modules/llm-research.md` | LLM-assisted research guardrails | Read; confirmed LLM cannot be a primary source or promote A/B; human verification required |
| `system/modules/llm-eval-data.md` | Quality evaluation for AI features | Read; confirmed scope is `method: quality` and AI feature evaluation |
| `templates/evidence.md` | Evidence schema and minimum fields | Read in full; 22 columns, 8-field scoring minimum, `verified_by` definition |
| `templates/experiment-s.md` | Short S-test form | Read in full; ★ fields and G4 result section |
| `templates/experiment.md` | Full experiment form | Read; 178 lines, calibration and forecast fields |
| `templates/idea.md` | Idea card | Read; problem/segment/evidence/alternatives/scoring |
| `templates/lead.md`, `project.md`, `system-change.md`, `release-checklist.md` | Supporting artifacts | Read; not central to this review |
| `registry.base`, `leads.base`, `inbox.md` | Obsidian views and inbox | Read; `registry.base` has calibration/portfolio views; syntax not validated |
| `NEXT.md` | Current priorities | Read; confirms first real cycle is still ahead, verifier unimplemented, calibration review planned in 1–2 months |
| `projects/anti-scope-creep/` | The only project instance | Read project card, one idea, ten experiments; recorded statuses and missing fields |
| `_docs/graph-engine-implementation-spec.md`, `_docs/graph-engine-stage-0-plan.md`, `_docs/handoffs/` | Untracked planning documents | Excluded from the implemented PLS baseline; not code, not executed, not referenced by the core loop |
| `.obsidian/` | Vault configuration and plugins | Excluded except as context; not PLS methodology |

### 3.2 Documented versus implemented behavior

**Observed:** The repository is an Obsidian methodology vault. It contains Markdown rules, templates, Bases views, and project records. It does not contain a Python/JS/TS application, CLI, test suite, or CI pipeline for PLS. The only JavaScript files are Obsidian plugin assets under `.obsidian/`, not PLS logic.

**Observed:** `NEXT.md` states that the read-only URL/quote verifier is not implemented and has not been network-tested; until it exists, `verified_by: human` is the only allowed verification. `NEXT.md` also states that the `registry.base` views have not been checked for syntax errors.

**Interpretation:** Documented behavior is not implemented behavior. The review can assess the written method and the manual records, but it cannot claim that gates, scores, or transitions are enforced automatically. Any statement about "PLS behavior" below refers to the written rules plus the actual project records, not to running software.

### 3.3 Observed execution state

| Record | Observed state | Consequence |
|---|---|---|
| `projects/anti-scope-creep/ideas/idea-asc-001-contract-risk-review.md` | `status: testing`; `score`, `confidence`, `portfolio_value`, `timebox_hours`, `test_cost`, `owner`, `review_date` empty; no evidence table | Screen and confidence cannot be reconstructed; there is no traceable evidence base for the idea |
| `projects/anti-scope-creep/experiments/exp-asc-001..010` | 9 × `status: draft`; 1 × `status: review`; 0 × `closed` | No completed learning cycle; no outcome data for calibration |
| `exp-asc-005-pro-waitlist.md` | `status: review`; `decision: more-evidence`; missing `timebox_hours`, `exposure_floor`, `owner`, `score_at_launch`, `confidence_at_launch`; primary result "unknown — waitlist count not recovered" | Cannot distinguish no demand from no exposure; exactly the failure mode the exposure floor is meant to prevent |
| `NEXT.md` | Next steps: fill inbox segments, set timeboxes for EXP-ASC-004/010, run first sweep, launch outreach; verifier later; calibration review in 1–2 months | Confirms the system is at the beginning of its first real cycle, not at a mature operating state |
| `registry.base` | Calibration and revenue views exist; syntax not validated | No evidence the views are usable; no evidence of use |
| `projects/anti-scope-creep/README.md` | `paying_customers: 0`, `revenue_total: 0` | Commercial context, not a PLS design failure |

**Observed:** `EXP-ASC-005` was registered retrospectively on 2026-10-19 for a launch on 2026-10-13. Its note says the production facts were not recovered and that numbers were not replaced with zeros. This is honest recording. It also means the missing launch fields are partly a consequence of retrospective registration, not necessarily a failure of the template at launch time.

**Interpretation:** The repository does not prove that PLS is too heavy. It does show that the current operating state has no closed decision, no evidence table, and no usable calibration data. A minimal-path experiment is a proportionate response to that state, not a verdict on the methodology.

### 3.4 Baseline conclusion

- **Observed:** PLS is a well-specified, document-heavy method with a small, early project instance and no completed experiment.
- **Interpretation:** The binding constraint may be execution capacity, channel access, or demand—not the number of fields. The review cannot distinguish these.
- **Hypothesis:** Reducing the default path will improve closure without reducing evidence quality. This is worth a small, reversible test because the current state provides no outcome data and the change is cheap.

---

## 4. Search coverage

### 4.1 Sources, dates, and filters

| Item | Value |
|---|---|
| Primary discovery | arXiv API (`https://export.arxiv.org/api/query`) |
| Publication-status checks | Crossref API (`https://api.crossref.org/works/{DOI}`), OpenAlex (`https://api.openalex.org/works/https://doi.org/{DOI}`) |
| Search date | 2026-10-31 |
| Search cut-off | 2026-10-31 |
| Date filter | `submittedDate:[202411010000 TO 202610312359]` |
| Sort | Relevance (`sortBy=relevance`) |
| Screening depth | Top 8 results per query printed and screened at title/abstract level |
| Full-text access | Eight papers downloaded as PDF and converted to text locally; six additional papers assessed at abstract/metadata level |
| Code/data inspection | None. Code and data links were recorded where found, but no repository or dataset was opened or executed. |
| Reproduction | None |

### 4.2 Query design and coverage

The review used 56 distinct queries across the six protocol capability areas plus a dedicated simplification/process-overhead probe. Every capability area had at least two distinct formulations, and most had five or more. The queries combined terms from different research communities (marketing/management, HCI, NLP/agents, statistics/experimentation, and organizational learning) rather than relying on one broad string.

| Area | Queries | Sum of reported hits | Result entries screened | Main query themes |
|---|---:|---:|---:|---|
| Opportunity discovery | 13 | 122 | 70 | customer problem discovery, need finding, pain points, demand signals, unmet needs, jobs to be done, review mining, voice of customer, problem mining |
| Evidence quality | 7 | 546 | 50 | claim verification, evidence synthesis, calibration/uncertainty, citation verification, source reliability, epistemic uncertainty, multi-source disagreement |
| Prioritization | 8 | 801 | 64 | value of information, Bayesian/optimal experimental design, decision calibration, portfolio experiments, sequential decisions, Brier scores, verbalized confidence, decision quality |
| Experimentation | 8 | 290 | 38 | sequential A/B, willingness to pay, small-sample A/B, minimum detectable effect, fake door/pretotyping, interim analysis, peeking, experiment stopping |
| Learning loop | 7 | 765 | 48 | product analytics, retention prediction, causal inference, belief updating, organizational learning, learning from experiments, experiment databases |
| Agentic automation | 7 | 3,135 | 56 | research agent evaluation, LLM-as-judge reliability, deep-research citations, agent verification, human-in-the-loop, judge-human agreement, citation evaluation |
| Simplification / process overhead | 6 | 17 | 15 | stage-gate, lean startup experiments, organizational learning, process overhead, minimum viable experiment, bureaucracy/innovation |
| **Total** | **56** | **5,676** | **341** | |

**Observed:** The sum of reported hits is 5,676, but this is not a count of unique papers. Broad queries returned hundreds of off-topic results; the same paper appeared under multiple queries; and some queries had `OR`/`AND` precedence that let out-of-window results through. The 341 screened entries reduced to 327 unique arXiv IDs. These numbers describe search effort, not coverage completeness.

**Observed:** The dedicated simplification probe returned almost nothing relevant: 17 total hits across six queries, mostly off-topic. The literature does not directly study "how many fields a solo-builder stage-gate system should require." The simplification case in this report is therefore based on repository observations and a testable hypothesis, not on a research consensus.

### 4.3 Screening and selection

**Pass 1 — title/abstract.** The top eight results per query were screened. A paper was kept when it plausibly addressed a PLS capability, offered a method or empirical result that could change a PLS decision, and had a setting with some transfer potential. Generic AI commentary, pure benchmark papers with no workflow implication, domain-specific papers with no transferable mechanism, duplicate versions, and papers outside the 24-month window were excluded.

**Pass 2 — full text.** Eight papers were selected for full-text review because they could materially change a PLS decision:

1. `2503.01870` — opportunity discovery and the limits of LLM need abstraction.
2. `2605.06635` — citation validity versus factual support.
3. `2609.39026` — citation correctness versus conclusion validity and evidence selection.
4. `2610.39070` — failure taxonomy for LLM-assisted evidence synthesis.
5. `2609.22246` — corroboration and source-provenance failure.
6. `2610.27899` — sequential A/B design and stopping.
7. `2512.14779` — forecast skill versus decision skill.
8. `2608.20828` — belief updating and calibration interpretation.

Six additional papers were assessed at abstract/metadata level because they were relevant but not central enough to justify full-text review: `2505.08128`, `2602.00521`, `2610.13008`, `2608.17501`, `2610.09375`, `2602.18693`.

**Shortlist size:** 14 papers in the evidence table, plus additional candidates recorded in §6.4 and §10. The table alone is within the protocol's suggested 10–30 range.

**Stopping rationale:** Additional queries in each area returned mostly duplicates or clearly irrelevant results; the key competing approaches (citation checking, evidence selection correction, sequential A/B, calibration/decision evaluation, LLM-as-judge reliability) had been identified; and the remaining gaps were access-related rather than query-related. The review does not claim exhaustive coverage.

**Exclusion examples:** Pure portfolio-optimization papers (many were financial portfolio math, not experiment portfolios); ad/recommendation A/B papers with no small-sample transfer; medical/geophysics papers returned by broad terms; generic "AI for research" commentaries; papers that only restated LLM-as-judge without a reliability evaluation. These exclusions are recorded as a search boundary, not as judgments about quality.

### 4.4 Search log

The exact query strings and reported arXiv hit counts are below. Each query used the date filter shown in §4.1; where a query is shown without the filter, the filter was appended in the actual API call. Counts are arXiv `totalResults` at the time of search and are not deduplicated.

#### Opportunity discovery (13 queries, 122 reported hits)

1. `all:"customer problem discovery" OR all:"need finding" AND submittedDate:[202411010000 TO 202610312359]` — 14
2. `all:"pain point" AND all:"LLM" AND submittedDate:[202411010000 TO 202610312359]` — 12
3. `all:"demand signal" OR all:"market opportunity" AND submittedDate:[202411010000 TO 202610312359]` — 30
4. `all:"customer discovery" AND submittedDate:[202411010000 TO 202610312359]` — 3
5. `all:"unmet needs" AND all:"large language models" AND submittedDate:[202411010000 TO 202610312359]` — 3
6. `all:"review mining" OR all:"opinion mining" AND all:"product" AND submittedDate:[202411010000 TO 202610312359]` — 25
7. `all:"jobs to be done" AND submittedDate:[202411010000 TO 202610312359]` — 3
8. `all:"problem discovery" AND all:"LLM" AND submittedDate:[202411010000 TO 202610312359]` — 1
9. `all:"voice of customer" AND submittedDate:[202411010000 TO 202610312359]` — 7
10. `all:"customer needs" AND all:"large language models" AND submittedDate:[202411010000 TO 202610312359]` — 5
11. `all:"pain points" AND all:"reviews" AND submittedDate:[202411010000 TO 202610312359]` — 11
12. `all:"opportunity identification" AND all:"LLM" AND submittedDate:[202411010000 TO 202610312359]` — 2
13. `all:"problem mining" OR all:"need elicitation" AND submittedDate:[202411010000 TO 202610312359]` — 6

#### Evidence quality (7 queries, 546 reported hits)

1. `all:"claim verification" AND all:"source" AND submittedDate:[202411010000 TO 202610312359]` — 34
2. `all:"evidence synthesis" AND all:"LLM" AND submittedDate:[202411010000 TO 202610312359]` — 50
3. `all:"calibration" AND all:"LLM" AND all:"uncertainty" AND submittedDate:[202411010000 TO 202610312359]` — 410
4. `all:"citation verification" AND all:"LLM" AND submittedDate:[202411010000 TO 202610312359]` — 19
5. `all:"source reliability" AND all:"LLM" AND submittedDate:[202411010000 TO 202610312359]` — 13
6. `all:"epistemic uncertainty" AND all:"LLM" AND all:"calibration" AND submittedDate:[202411010000 TO 202610312359]` — 18
7. `all:"disagreement" AND all:"multi-source" AND all:"claim" AND submittedDate:[202411010000 TO 202610312359]` — 2

#### Prioritization (8 queries, 801 reported hits)

1. `all:"value of information" AND all:"experiment" AND submittedDate:[202411010000 TO 202610312359]` — 35
2. `all:"Bayesian experimental design" OR all:"optimal experimental design" AND submittedDate:[202411010000 TO 202610312359]` — 277
3. `all:"decision calibration" AND submittedDate:[202411010000 TO 202610312359]` — 22
4. `all:"portfolio" AND all:"experiments" AND all:"uncertainty" AND submittedDate:[202411010000 TO 202610312359]` — 40
5. `all:"sequential decision" AND all:"information" AND submittedDate:[202411010000 TO 202610312359]` — 275
6. `all:"Brier score" AND all:"LLM" AND submittedDate:[202411010000 TO 202610312359]` — 62
7. `all:"verbalized confidence" AND all:"calibration" AND submittedDate:[202411010000 TO 202610312359]` — 74
8. `all:"decision quality" AND all:"forecast" AND submittedDate:[202411010000 TO 202610312359]` — 16

#### Experimentation (8 queries, 290 reported hits)

1. `all:"A/B testing" AND all:"sequential" AND submittedDate:[202411010000 TO 202610312359]` — 72
2. `all:"willingness to pay" AND all:"experiment" AND submittedDate:[202411010000 TO 202610312359]` — 18
3. `all:"small sample" AND all:"A/B testing" AND submittedDate:[202411010000 TO 202610312359]` — 1
4. `all:"minimum detectable effect" AND submittedDate:[202411010000 TO 202610312359]` — 18
5. `all:"fake door" OR all:"pretotyping" AND submittedDate:[202411010000 TO 202610312359]` — 0
6. `all:"interim analysis" AND all:"experiment" AND submittedDate:[202411010000 TO 202610312359]` — 0
7. `all:"peeking" AND all:"A/B" AND submittedDate:[202411010000 TO 202610312359]` — 5
8. `all:"experiment stopping" OR all:"early stopping" AND all:"experiment" AND submittedDate:[202411010000 TO 202610312359]` — 176

#### Learning loop (7 queries, 765 reported hits)

1. `all:"product analytics" OR all:"retention prediction" AND submittedDate:[202411010000 TO 202610312359]` — 30
2. `all:"causal inference" AND all:"product" AND submittedDate:[202411010000 TO 202610312359]` — 46
3. `all:"belief updating" AND all:"feedback" AND submittedDate:[202411010000 TO 202610312359]` — 14
4. `all:"experiment" AND all:"knowledge" AND all:"organization" AND submittedDate:[202411010000 TO 202610312359]` — 572
5. `all:"customer feedback" AND all:"product development" AND submittedDate:[202411010000 TO 202610312359]` — 0
6. `all:"learning from experiments" AND submittedDate:[202411010000 TO 202610312359]` — 89
7. `all:"experiment database" OR all:"experiment repository" AND submittedDate:[202411010000 TO 202610312359]` — 14

#### Agentic automation (7 queries, 3135 reported hits)

1. `all:"research agent" AND all:"evaluation" AND submittedDate:[202411010000 TO 202610312359]` — 250
2. `all:"LLM-as-a-judge" OR all:"LLM judge" AND all:"reliability" AND submittedDate:[202411010000 TO 202610312359]` — 1577
3. `all:"deep research" AND all:"citation" AND submittedDate:[202411010000 TO 202610312359]` — 57
4. `all:"agent" AND all:"verification" AND all:"evidence" AND submittedDate:[202411010000 TO 202610312359]` — 805
5. `all:"human-in-the-loop" AND all:"LLM" AND all:"evaluation" AND submittedDate:[202411010000 TO 202610312359]` — 337
6. `all:"LLM-as-a-judge" AND all:"human" AND all:"agreement" AND submittedDate:[202411010000 TO 202610312359]` — 79
7. `all:"research agent" AND all:"citation" AND all:"evaluation" AND submittedDate:[202411010000 TO 202610312359]` — 30

#### Simplification / process overhead (6 queries, 17 reported hits)

1. `all:"stage-gate" AND all:"innovation" AND submittedDate:[202411010000 TO 202610312359]` — 1
2. `all:"lean startup" AND all:"experiment" AND submittedDate:[202411010000 TO 202610312359]` — 1
3. `all:"experimentation" AND all:"organizational learning" AND submittedDate:[202411010000 TO 202610312359]` — 2
4. `all:"process overhead" AND all:"innovation" AND submittedDate:[202411010000 TO 202610312359]` — 3
5. `all:"minimum viable" AND all:"experiment" AND submittedDate:[202411010000 TO 202610312359]` — 10
6. `all:"bureaucracy" AND all:"innovation" AND all:"performance" AND submittedDate:[202411010000 TO 202610312359]` — 0


### 4.5 Search-quality notes and access limitations

- **Operator precedence.** Several queries used forms such as `all:"A" OR all:"B" AND submittedDate:[...]`. In arXiv's query language, `AND` can bind more tightly than `OR`, so the date filter may have applied only to the second term. Out-of-window results (for example, 2018 and 2019 papers) appeared in those queries and were excluded at screening. This means the reported hit counts overstate in-window coverage.
- **ID collision.** An initial metadata lookup for `2505.08128` returned a different paper (`2605.08128`, gene-regulatory-network inference). The correct paper was resolved by title and DOI cross-check. This is recorded because it shows why title/DOI verification matters even for arXiv IDs.
- **Version selection.** The latest version available at the cut-off was used (for example, `2503.01870v2`, `2512.14779v2`, `2505.08128v3`). Earlier versions were not separately reviewed.
- **No full text for six papers.** `2505.08128`, `2602.00521`, `2610.13008`, `2608.17501`, `2610.09375`, and `2602.18693` were assessed from abstracts/metadata only. Their findings are reported at that level and are not used as the sole basis for a recommendation.
- **No code/data inspection.** TRAILS (`https://github.com/carolelunny/TRAILS`) and SGHA (`https://github.com/SarveshVGharat/structural-gap-hypothesis-agent`) links were recorded but not opened. The `2608.20828` OSF link was present in the paper text but not opened. No dataset was reanalyzed.
- **No reproduction.** No paper experiment was rerun. The `E` inspection level is not used anywhere in this report.
- **Language and venue bias.** arXiv is English-language and CS/statistics-heavy. Relevant work in management, marketing, or HCI journals may be missed. Crossref/OpenAlex were used for verification, not discovery.
- **No independent second reviewer.** All screening and appraisal was done by one agent. Agent agreement would not be independent replication even if multiple agents were used.

---

## 5. Paper evidence table

The table includes the 14 papers used in the synthesis. Study strength and inspection level are separate. "Preprint" means no peer-reviewed venue was verified at the cut-off; "accepted" means the arXiv comment or venue metadata reports acceptance, not that the reviewer verified the final proceedings.

| Paper | Year / status | arXiv / DOI | PLS area | Main finding | Study strength | Inspection | Limitations |
|---|---|---|---|---|---|---|---|
| Timoshenko, Mao & Hauser, *Transforming the Voice of the Customer: Large Language Models for Identifying Customer Needs* | 2025; arXiv v2 Apr 2026; SSRN working paper; not peer-reviewed | [arXiv:2503.01870](https://arxiv.org/abs/2503.01870) · [DOI 10.2139/ssrn.5167493](https://doi.org/10.2139/ssrn.5167493) | Opportunity discovery | Supervised fine-tuned LLM matched professional analysts on customer-need abstraction (z = 0.40, p = 0.69, h = 0.04); zero-shot/few-shot foundation models were significantly worse; 1,549 CN–verbatim pairs, 150 review sentences, three professional evaluators; the fine-tuned model could not prioritize needs | S3 | F | One VOC firm; wood-stain and service categories; requires 1,549 labeled pairs; preprint; no independent replication |
| Lunny et al., *When the Same Prompt Gives Different Answers (and the Same Answer Isn't Always Right): TRAILS taxonomy* | 2026; preprint | [arXiv:2610.39070](https://arxiv.org/abs/2610.39070) · code: [TRAILS](https://github.com/carolelunny/TRAILS) (not inspected) | Evidence quality | 38 failure mechanisms in 10 categories; repeatability and accuracy do not rule out hidden judgment failure; human evaluation should assess whether a judgment is grounded in the supplied evidence | S0 | F | Conceptual taxonomy; no outcome study; medical evidence-synthesis focus; 76 pages |
| Lu & Zhang, *The Corroboration Illusion: When More News Makes LLM Forecasts Less True* | 2026; preprint | [arXiv:2609.22246](https://arxiv.org/abs/2609.22246) | Evidence quality / agentic | 500 resolved ForecastBench questions; one LLM-written article flips 56% of forecasts across the 0.5 boundary; five articles flip 69–73%; Brier score degrades from 0.18 to 0.37; claimed publisher labels did not stop the effect; defenses were bypassed | S2 | F | Adversarial poisoning, three open 7–8B models; not ordinary research; preprint |
| Onweller et al., *Cited but Not Verified: Parsing and Evaluating Source Attribution in LLM Deep Research Agents* | 2026; preprint | [arXiv:2605.06635](https://arxiv.org/abs/2605.06635) | Evidence quality / agentic | 14 LLMs; link validity above 94%, relevance above 80%, factual accuracy only 39–77%; in a two-frontier-model ablation, fact-check accuracy drops about 42% as tool calls scale from 2 to 150; more retrieval did not produce more accurate citations | S2 | F | LLM-as-judge for fact check; preprint; web citations temporally unstable; no human gold standard at scale |
| Xiao et al., *Search Shapes Conclusions: Auditing Evidence Selection Bias in Deep Research Agents* | 2026; preprint | [arXiv:2609.39026](https://arxiv.org/abs/2609.39026) | Evidence quality / agentic | Citation correctness does not establish conclusion validity; adaptive search creates a selective evidence sample; CESS reduces MAE by 9.2% on MS2 and 60.1% on a public agent; 200 MS2 questions, 1,200 trajectories, 216 public-agent trajectories | S3 | F | Preprint; benchmark tasks; CESS requires logged selection probabilities; not a simple checklist |
| Perini et al., *Let Them Peek: Group Sequential Designs for A/B Testing* | 2026; preprint | [arXiv:2610.27899](https://arxiv.org/abs/2610.27899) | Experimentation | Group sequential A/B at Meta; 43.1% shorter average experiment runtime and 76% capacity increase; preserves the terminal decision rule; corrects for daily autocorrelation | S3 | F | Large-scale platform; requires infrastructure and statistical assumptions; not transferable to solo S-tests |
| Raeth & Ludwig, *Forecast Skill Is Not Decision Skill: Evidence from Weather-Dependent Decision Tasks* | 2025; v2 Sep 2026; peer-reviewed *Meteorological Applications* 33(5), 2026 | [arXiv:2512.14779](https://arxiv.org/abs/2512.14779) · [DOI 10.1002/met.70260](https://doi.org/10.1002/met.70260) | Prioritization / learning | Forecast-level performance does not reliably translate to downstream decision quality; model rankings can change even across seemingly similar decision tasks | S3 | F | Weather-dependent tasks; analogical transfer to product decisions; no PLS test |
| Biswas, Erlei & Gadiraju, *The Belief Update Gate: Separating Inertia from Learning in Human–AI Interaction* | 2026; peer-reviewed ACM CHAI 2026, pp. 73–87 | [arXiv:2608.20828](https://arxiv.org/abs/2608.20828) · [DOI 10.1145/3834580.3838740](https://doi.org/10.1145/3834580.3838740) | Learning loop | 240 participants, 7,200 trials; 67.3% of belief changes exactly zero; 76.4% smaller than five percentage points; pooled slope 0.494 vs 0.949 among movers; observed non-movement does not identify latent inertia | S3 | F | Reanalysis of a multi-task dataset; elicitation/reporting effects; not product forecasting |
| Wei et al., *Beyond Basic A/B Testing: Improving Statistical Efficiency for Business Growth* | 2026; peer-reviewed KDD 2026, pp. 1530–1541 | [arXiv:2505.08128](https://arxiv.org/abs/2505.08128) · [DOI 10.1145/3770854.3780326](https://doi.org/10.1145/3770854.3780326) | Experimentation | Estimating equations and U-statistics improve A/B efficiency for small samples, non-Gaussian outcomes, ROI, and confounding; applied to multiple LinkedIn A/B tests | S3 | A | Abstract only; requires randomized A/B and statistical setup; not an S-test method |
| Choi et al., *Diagnosing the Reliability of LLM-as-a-Judge via Item Response Theory* | 2026; accepted ICML 2026 per arXiv comment | [arXiv:2602.00521](https://arxiv.org/abs/2602.00521) | Agentic / evidence quality | IRT framework separates intrinsic consistency under prompt variation from human alignment of LLM judges | S2 | A | Abstract only; AI evaluation, not human evidence; acceptance not independently verified |
| Huang et al., *Provenance-Aware Belief Updating in Human-AI Feedback Loops* | 2026; accepted oral at NeurIPS 2026 workshop per arXiv comment | [arXiv:2610.13008](https://arxiv.org/abs/2610.13008) | Learning loop / evidence quality | Repeated reports can look like independent corroboration; provenance-aware training reduces new-evidence update RMSE by 41–44% and log-odds drift after eight relay steps by 89–91% | S1 | A | Abstract only; controlled binary benchmark; workshop; not product decisions |
| Gharat & Komiyama, *SGHA: Evidence-Grounded Research Problem Discovery with Local Language Models* | 2026; preprint | [arXiv:2608.17501](https://arxiv.org/abs/2608.17501) · code: [SGHA](https://github.com/SarveshVGharat/structural-gap-hypothesis-agent) (not inspected) | Opportunity discovery / agentic | Corpus-first, evidence-linked research-problem discovery with a local 9B model; compares with AI Scientist-v2 in five ML domains | S1 | A | Abstract only; scientific problem discovery, not customer problems; code not inspected |
| Raviraja G et al., *From Retrieval to Customer Context: Evaluating Frontier-Model Systems for Voice-of-Customer Analysis* | 2026; preprint | [arXiv:2610.09375](https://arxiv.org/abs/2610.09375) | Opportunity discovery | Customer-context-graph agent scored 0.961 vs 0.710 for a deep-research agent and 0.651 for agentic RAG on 9,432 public Cursor feedback records and 30 questions; led on 27/30 paired questions | S2 | A | Abstract only; one public dataset; rubric-based scoring; industry authors; no independent replication |
| Biswas & Uzuner, *Contradiction to Consensus: Dual Perspective, Multi Source Retrieval Based Claim Verification with Source Level Disagreement using LLM* | 2026; preprint | [arXiv:2602.18693](https://arxiv.org/abs/2602.18693) | Evidence quality | Multi-source claim verification retrieves evidence for both the original and negated claim, then aggregates source-level disagreement across Wikipedia, PubMed, and Google; evaluated on four benchmarks with five LLMs | S1 | A | Abstract only; preprint; not a human workflow study |

### 5.1 Publication-status notes

- **Peer-reviewed and DOI-verified:** `2512.14779` (*Meteorological Applications* 33(5), 2026); `2608.20828` (ACM CHAI 2026, pp. 73–87); `2505.08128` (KDD 2026 V1, pp. 1530–1541). Crossref metadata confirmed the titles, venues, pages, and dates.
- **Working paper with DOI but not peer-reviewed:** `2503.01870` (SSRN posted-content, DOI 10.2139/ssrn.5167493). The arXiv title differs from the SSRN title; the DOI record is for "Can Large Language Models Extract Customer Needs as well as Professional Analysts?"
- **Accepted, not independently verified:** `2602.00521` (arXiv comment says ICML 2026); `2610.13008` (arXiv comment says accepted oral at a NeurIPS 2026 workshop). No venue DOI was verified.
- **Preprint only:** `2610.39070`, `2609.22246`, `2605.06635`, `2609.39026`, `2610.27899`, `2608.17501`, `2610.09375`, `2602.18693`.

No paper is described as state of the art. Where a paper reports a best result, it is the authors' result under their own evaluation.

---

## 6. Synthesis by capability

### 6.1 Opportunity discovery

**Observed:** `2503.01870` is the only full-text paper that directly tests LLM customer-need abstraction. It reports that a supervised fine-tuned LLM performed at least as well as professional analysts (z = 0.40, p = 0.69, h = 0.04), while zero-shot and few-shot foundation models were significantly worse. The study used 1,549 customer-need/verbatim pairs, 150 review sentences, and three professional evaluators. The paper also states that the fine-tuned model can abstract needs but cannot yet prioritize them.

**Observed:** `2610.09375` (abstract only) reports that a customer-context-graph agent scored 0.961 vs 0.710 for a deep-research agent and 0.651 for agentic RAG on 9,432 public Cursor feedback records and 30 questions. The authors describe the advantage as analytical depth and evidence traceability. The evaluation is rubric-based, on one public dataset, by industry authors.

**Observed:** `2608.17501` (abstract only) describes a local 9B model that structures a scientific corpus into evidence-linked paper objects and detects research gaps. It is about scientific problem discovery, not customer problem discovery.

**Interpretation:** The evidence does not support automating PLS's problem definition. The fine-tuning result is real but expensive: 1,549 labeled pairs and a professional evaluation apparatus are far beyond a solo builder's default. The context-graph result is interesting but requires a customer-data graph and a rubric; it is not a drop-in replacement for a human-written problem statement. The paper's own conclusion that the model cannot prioritize needs reinforces keeping human scoring and selection.

**Counter-evidence:** `2610.09375` suggests that structured customer context can materially improve VoC analysis; a builder with a large feedback corpus might benefit. But the study is abstract-only, uses one dataset, and does not test a solo-builder workflow. `2503.01870` is a preprint/working paper from one VOC firm and two product categories; its external validity is limited.

**What it means for PLS:** No change recommended for Discover or Screen. Keep the human-written problem statement and the score/confidence judgment. Use LLMs for search, extraction, and drafting, as `llm-research.md` already allows. Do not add a need-abstraction model or a customer-context graph now. Mark this area **Not transferable now** for automation; **Supports** the existing human-first design.

### 6.2 Evidence quality

**Observed:** Four papers point in the same direction from different angles:

- `2605.06635`: 14 LLMs produced citations with link validity above 94% and relevance above 80%, but factual accuracy of only 39–77%. In the paper's two-frontier-model ablation, fact-check accuracy dropped by about 42% as tool calls increased from 2 to 150. More retrieval did not mean more accurate citations.
- `2609.39026`: a well-cited report can still reach a misleading conclusion. Citation correctness checks individual claims; it does not show whether adaptive search exposed a representative evidence set. The authors model this as adaptive evidence sampling and propose CESS, which reduced MAE by 9.2% on MS2 and 60.1% on a public agent.
- `2610.39070`: the TRAILS taxonomy identifies 38 mechanisms in 10 categories that can make LLM read-and-evaluate judgments unstable or invalid. Repeatability and accuracy do not rule out hidden judgment failure; human evaluation should check whether the judgment is grounded in the supplied evidence.
- `2602.18693` (abstract only): claim verification improves when the system retrieves evidence for both the original and the negated claim and analyzes source-level disagreement across Wikipedia, PubMed, and Google. This is a concrete disconfirmation mechanism.

**Observed:** `2610.13008` (abstract only) shows a related provenance problem: repeated reports of the same evidence can look like independent corroboration. Provenance-aware training reduced new-evidence update RMSE by 41–44% and log-odds drift after eight relay steps by 89–91%.

**Interpretation:** The evidence supports two distinct checks, not one:

1. **Claim-level support:** does the cited source actually support the specific claim, or is it merely on-topic and accessible?
2. **Disconfirmation/representativeness:** was there a search for evidence that could change the conclusion, or did the search only accumulate supporting material?

PLS already has the concepts for both. `llm-research.md` says an external tool does not replace human claim verification for A/B. `10-discover.md` says to look for reasons the idea may fail and to record `counter_evidence`. `templates/evidence.md` has `cluster`, `author_id`, and `counter_evidence`. The gap is operational: the evidence template defines `verified_by: human` as checking URL, excerpt, and date, and it does not record whether the excerpt supports the claim. The `counter_evidence` field exists but there is no required disconfirmation query for B/A rows.

**Counter-evidence and limitations:** All three main papers study LLM agents on benchmark or web-research tasks, not a human solo builder checking sources. `2605.06635` uses LLM-as-judge for fact check, which may retain judge biases. `2609.39026` shows that claim-level checks are insufficient by themselves; a claim check can create false assurance if the evidence set is one-sided. `2610.39070` is a conceptual taxonomy, not an outcome study. `2602.18693` is abstract-only. The cost of human claim verification may exceed its benefit for low-stakes C-level evidence, which is why the recommendation limits it to B/A rows.

**What it means for PLS:** **Refines** existing practice. The smallest change is not a new module or verifier; it is to make the existing human verification step record claim support and to require one disconfirmation/negation check for B/A. This is Recommendation 1.

### 6.3 Prioritization

**Observed:** `2512.14779` (peer-reviewed) finds that forecast-level performance does not reliably translate to decision-level performance. Some model differences only appear at the decision level, and rankings can change even among similar decision tasks. The authors conclude that typical forecast evaluations are insufficient for selecting a model for a specific decision.

**Observed:** `2609.27385` (abstract only) evaluates language-model decisions with budgeted forecast tools on 1,251 electricity and cycle-hire cases. It measures decision quality and forecast cost, not accuracy alone. `2608.28482` (abstract only) shows that different proper scoring rules (Brier, log, etc.) shape LLM forecaster behavior differently even when aggregate accuracy is similar. `2510.23471` (abstract only) studies robust decision making with partially calibrated forecasts.

**Interpretation:** PLS does not use probabilistic forecasts; its score and confidence are ordinal heuristics. The research warns against importing Brier scores, calibration curves, or decision-calibration metrics as a proxy for better product decisions. The useful principle is decision-level evaluation: did the score/confidence ranking lead to a better experiment or decision? PLS's calibration journal is already qualitative and outcome-based; it does not need a forecast-metric layer now.

**Counter-evidence:** Calibration research also shows that LLM confidence is often miscalibrated, so calibration is not irrelevant in general. But PLS's bottleneck is not a lack of metrics; it is a lack of closed outcomes. Adding metrics before outcomes would create measurement without a criterion. The two cheap fields `score_at_launch` and `confidence_at_launch` should be kept because they enable a future audit at near-zero cost.

**What it means for PLS:** **Challenges** the timing of calibration expansion, not the concept. Recommendation 3 defers expansion until at least three experiments are closed with complete G4.

### 6.4 Experimentation

**Observed:** `2610.27899` (preprint, Meta) reports that a group-sequential A/B policy reduced average experiment runtime by 43.1% and increased effective platform capacity by 76%, while preserving the terminal decision rule and correcting for daily autocorrelation. This is a strong industrial result.

**Observed:** `2505.08128` (peer-reviewed KDD 2026, abstract only) proposes estimating-equation and U-statistic methods for A/B tests with small samples, non-Gaussian outcomes, ROI considerations, and confounding; it reports applications to multiple LinkedIn A/B tests. `2607.08522` and `2609.27919` (abstracts only) address stopping and sample-size determination.

**Interpretation:** The transferable principle is not the statistical machinery; it is that experiments should have a predefined stopping rule, exposure/observation window, and decision criterion. PLS already has these: `30-experiment.md` requires an exposure floor, a decision table, a timebox, and a stop rule. The non-transferable part is the randomized, large-N, platform-scale apparatus. PLS S-tests are usually small, non-randomized demand tests with no control group; a group-sequential design would not have the sample or the independent increments it assumes.

**Counter-evidence:** `2610.27899` shows large gains, so it would be wrong to say sequential methods are useless. They are simply not the current constraint. If PLS later runs repeated randomized A/B tests with enough traffic, the methods become relevant. `2505.08128` likewise becomes relevant only with a randomized control and a statistical workflow.

**What it means for PLS:** **Not transferable now.** Keep the existing exposure floor and stop rule; do not add sequential testing, minimum-detectable-effect calculations, or A/B efficiency methods to the S-test path. Record them as deferred ideas with a scale trigger.

### 6.5 Learning loop

**Observed:** `2608.20828` (peer-reviewed) reanalyzes a 240-participant, 7,200-trial human–AI dataset. It finds that 67.3% of trial-level belief changes are exactly zero and 76.4% are smaller than five percentage points. The pooled within-trajectory slope is 0.494; among rows with nonzero movement it is 0.949. The authors explicitly caution that observed non-movement does not distinguish latent inertia from small unexpressed updates, rounding, or reporting effects.

**Observed:** `2512.14779` (peer-reviewed) shows forecast skill is not decision skill. `2610.13008` (abstract only) shows that repeated reports can masquerade as independent corroboration, and that provenance-aware updating reduces drift.

**Interpretation:** PLS's calibration journal is trying to learn from a small number of outcomes. The research suggests three disciplines:

- Do not interpret a single small-sample result as a belief update; show absolute counts and the denominator.
- Separate whether a metric moved from how much it moved; a zero change may be a reporting/threshold artifact.
- Evaluate decisions, not just forecasts or scores.

With zero closed experiments, the journal cannot yet do any of this. A monthly calibration review would be a ritual without data. Waiting for at least three closed experiments is not anti-calibration; it is the minimum condition for the journal to have something to calibrate.

**Counter-evidence:** The human–AI belief-updating setting is not the same as PLS idea scoring. The 67.3% zero-change result may not transfer to a builder's score updates. The paper is a reanalysis, not a new longitudinal study. These are reasons to be cautious, not reasons to add metrics.

**What it means for PLS:** **Refines** the calibration timing. Keep the two launch fields and the G4 outcome fields; defer the monthly review and any new calibration metric until there are at least three closed experiments. Recommendation 3.

### 6.6 Agentic automation

**Observed:** The agentic literature is dominated by failure modes, not by evidence that agents can be trusted to promote evidence:

- `2605.06635`: citations are often valid URLs but factually wrong; more tool calls reduce factual accuracy.
- `2609.39026`: adaptive search selects evidence; citation correctness does not establish conclusion validity.
- `2610.39070`: 38 mechanisms can produce unstable or invalid LLM judgments; repeatability and accuracy are not enough.
- `2609.22246`: a single adversarial article can flip 56% of forecasts; five flip 69–73%; provenance labels did not stop it.
- `2608.17501` and `2610.09375`: agents can help with structured, evidence-linked discovery when the corpus and provenance are controlled, but these are research prototypes with narrow evaluations.

**Interpretation:** Agents are useful for search, extraction, clustering, and drafting. They are not a substitute for the human verification gate, and they should not be allowed to promote evidence to confidence A/B. PLS's `llm-research.md` already says this; the research strengthens the case for keeping it. The cost and complexity of a corpus graph, a local 9B research agent, or a provenance-aware training pipeline are not justified for a solo builder's current evidence volume.

**Counter-evidence:** Agent benchmarks may improve quickly; a future agent with better citation verification could reduce the human burden. The current evidence does not support that assumption, and the reviewed papers are mostly 2026 preprints. Monitor, do not adopt.

**What it means for PLS:** **Supports** existing guardrails; **Refines** the evidence schema via Recommendation 1. No new agent module.

### 6.7 Cross-cutting: simplification and process overhead

**Observed:** The dedicated search for stage-gate, lean-startup, process-overhead, and bureaucracy literature returned almost nothing directly relevant: 17 hits across six queries, mostly off-topic. `2506.16334` (abstract only) is an observational study of 1,800 Chinese startups from 2011 to 2020; it finds that AI capabilities and the Lean Startup Method complement product innovation, with different effects for discovery-oriented vs optimization-oriented AI and for MVP prototyping vs controlled experimentation. It does not test the number of fields, gates, or artifacts in a solo-builder system. `2601.06087` (abstract only) is a conceptual "AI roles continuum" paper.

**Interpretation:** The literature cannot tell PLS which fields to drop. The case for simplification is internal: the repository has ten experiments and zero closed; the only review is inconclusive and missing mandatory fields; the idea card has no score, confidence, or evidence table. That is enough to justify a small test, not enough to declare the system too complex.

**Hypothesis:** A default path limited to the evidence and decision fields that actually gate G2/G4 will increase the proportion of S-tests that reach a recorded decision, without increasing false `kill`/`scale` decisions or reducing evidence completeness. This is Recommendation 2, explicitly exploratory.

**Counter-evidence:** The project is young; the nine drafts may be normal backlog, and `EXP-ASC-005` was registered retrospectively, which explains missing launch fields. The binding constraint may be channel access or demand, not documentation. A minimal path could skip a control that would have caught a bad decision. The experiment in R2 is designed to detect these failures, not to assume success.

### 6.8 Where the evidence agrees, conflicts, or is insufficient

- **Agreement:** Surface citation quality is not factual support (`2605.06635`, `2609.39026`, `2610.39070`). The three papers use different methods and settings but converge on the same failure mode.
- **Agreement:** Decision-level evaluation matters more than forecast-level accuracy (`2512.14779`, `2609.27385`). This is consistent with PLS's decision table, which is outcome-based rather than forecast-based.
- **Complement, not conflict:** `2605.06635` says individual claims are often unsupported; `2609.39026` says even supported claims can produce a misleading conclusion because the evidence set is selective. Together they imply claim check + disconfirmation, not one or the other.
- **Tension:** `2503.01870` shows LLM need abstraction can match analysts; `2610.09375` shows structured context improves VoC answers. Both suggest automation potential, but both require expensive inputs (labeled pairs; a customer-context graph). Neither shows a cheap path for a solo builder. The tension is about cost and transfer, not about whether the methods work in their settings.
- **Setting conflict:** `2610.27899` and `2505.08128` show real gains from sequential/small-sample A/B methods, but in randomized, platform-scale settings. PLS S-tests do not meet the assumptions. This is a transfer conflict, not a contradiction.
- **Insufficient:** There is no direct evidence on the optimal number of fields, gates, or artifacts for a solo-builder stage-gate system. The simplification recommendation is a hypothesis, not a research finding. The review says this plainly rather than dressing it as evidence-based.

---

## 7. PLS gap analysis

| Finding | Classification | Exact PLS artifact or behavior | Assessment |
|---|---|---|---|
| Link validity and relevance are weak proxies for factual support (`2605.06635`) | **Refines** | `templates/evidence.md` `verified_by`; `system/modules/llm-research.md` §Process 4 and 7 | PLS says claim verification matters for A/B, but the template defines human verification as URL/excerpt/date and has no claim-support value. Align the schema with the existing rule. |
| Citation correctness does not establish conclusion validity; adaptive search selects evidence (`2609.39026`) | **Refines / Challenges** | `system/10-discover.md` §Углублённый сбор step 6; `templates/evidence.md` `counter_evidence` | PLS has a counter-evidence field and says to look for disconfirming reasons, but there is no required disconfirmation query or record for B/A. Add one negation/disconfirmation check, not a CESS implementation. |
| Repeatability and accuracy do not rule out hidden judgment failure (`2610.39070`) | **Supports** | `system/modules/llm-research.md` guardrails; `system/30-experiment.md` quality metrics | Supports human review and the existing rule that LLM cannot promote A/B. No change. |
| Repeated reports can look like independent corroboration (`2610.13008`) | **Supports** | `templates/evidence.md` `cluster`, `author_id`; `llm-research.md` dedupe rules | Existing practice is correct. No change; keep cluster/author_id mandatory for B/A. |
| Forecast skill is not decision skill (`2512.14779`) | **Challenges** metric expansion | `system/20-screen.md` §Калибровка; `system/30-experiment.md` decision table | Keep qualitative calibration and decision outcomes; defer Brier/probability/decision-calibration metrics. |
| Belief reports are sticky and pooled slopes mislead (`2608.20828`) | **Refines** | `20-screen.md` §Калибровка; `registry.base` calibration view | Do not overinterpret small samples; show absolute counts; wait for ≥3 closed experiments before a calibration review. |
| Group-sequential A/B reduces runtime at platform scale (`2610.27899`) | **Not transferable now** | `30-experiment.md` sample/decision rules | Strong result, wrong scale. Defer until PLS runs randomized A/B tests with enough traffic. |
| Small-sample/non-Gaussian A/B methods improve efficiency (`2505.08128`) | **Not transferable now** | `30-experiment.md` sample-size guidance | Requires randomized control and statistical workflow. Defer. |
| SFT LLM matches analysts at need abstraction but needs 1,549 labels and cannot prioritize (`2503.01870`) | **Not transferable now / Supports human prioritization** | `10-discover.md` problem statement; `20-screen.md` score | Keep human problem definition and scoring. Do not add need-abstraction automation. |
| Customer-context graph improves VoC answers (`2610.09375`) | **Not transferable now** | `10-discover.md` evidence capture | Requires a customer-data graph and rubric; abstract-only. Defer. |
| Agentic research produces cited but wrong reports (`2605.06635`, `2609.39026`) | **Supports / Refines** | `llm-research.md`; `templates/evidence.md` | Keep the human gate; do not let agents promote evidence. R1 strengthens the gate. |
| AI + Lean Startup complement innovation (`2506.16334`) | **Supports general direction** | Whole loop | Observational, not a process trial. No specific change. |
| Process-overhead literature | **Insufficient** | System docs and templates | No direct evidence; R2 is an internal hypothesis. |
| LLM-as-judge reliability via IRT (`2602.00521`) | **Not transferable now** | `system/modules/llm-eval-data.md` | Relevant to AI quality evaluation, not demand tests. Defer. |

### 7.1 The three gaps that matter

**Gap 1 — Evidence verification is under-recorded.** This is the strongest and most directly actionable gap. PLS already says human verification is required and that an external tool does not replace claim verification for A/B. But `templates/evidence.md` operationalizes `verified_by: human` as URL, excerpt, and date. There is no field that records "the excerpt supports the claim." The research shows why that distinction matters. The gap is a consistency/enforcement gap, not a missing philosophy.

**Gap 2 — The default path carries dormant controls.** PLS has calibration, portfolio accounting, production analytics, a full experiment template, and an LLM-eval module. Each is appropriate at a trigger. None is needed for a first S-test. The observed state (0 closed, 1 inconclusive, no evidence table) is consistent with the owner spending attention on the wrong layer, but the evidence is too thin to prove it. This is a hypothesis to test.

**Gap 3 — Calibration is premature.** The calibration journal starts with the first experiment, but there are no closed experiments. The research says forecast/calibration metrics are not a proxy for decision quality and that small-sample belief reports are noisy. Keep the two cheap launch fields; defer the review and any metric expansion until at least three closed experiments.

### 7.2 What is not a gap

- **Opportunity discovery automation:** not needed; the human problem statement is cheaper and more accountable.
- **Sequential A/B / statistical efficiency:** not the current constraint; PLS lacks randomized scale.
- **Agentic research autonomy:** the evidence shows failure modes; the human gate is the right design.
- **Portfolio optimization:** PLS's portfolio value is qualitative; financial portfolio math does not transfer.
- **More templates or stages:** the repository already has more surface area than it executes. Adding process would worsen the likely bottleneck.

---

## 8. Recommendations

The protocol allows up to three high-priority recommendations. This review returns three: two adopt-for-experiment proposals and one deferral. None is an authorization to change PLS. Each has a falsifiable experiment and a decision rule.

### 8.1 R1 — Record claim-level support in the existing human verification step

**1. Problem.** PLS requires human verification of evidence and states that an external verifier does not replace human claim verification for A/B (`system/modules/llm-research.md` §Process 4 and 7). `templates/evidence.md` requires A's primary source to confirm the stated claim, but it does not record that judgment as a field, and B has no equivalent claim-support requirement. Its `verified_by: human` definition covers URL, excerpt, and date, not whether the excerpt actually supports the claim. A real URL with a real quote can still be irrelevant, partial, or contradictory. The research shows this is a common failure mode in LLM-generated research: link validity above 94%, relevance above 80%, factual accuracy 39–77% (`2605.06635`). PLS currently cannot distinguish, in the record, "source exists and quote is accurate" from "source supports the claim."

**2. Change.** A one-column, one-definition refinement to the existing evidence schema, limited to rows used for confidence A/B:

- Extend `verified_by: human` to mean: "URL, date, excerpt, and the excerpt supports the stated claim."
- Add `claim_supported: yes | partial | no | unknown` to the evidence row.
- Require one disconfirmation/negation check for B/A, recorded in the existing `counter_evidence` field. A practical form: search the negated claim (e.g., "X does not cause Y") and record the query, date, and result, or `none found`.
- Do not add a new stage, a new template, a verifier build, or a second review pass. The change replaces an under-specified check with a recorded one.

**3. Evidence.** `2605.06635` (F, S2) directly quantifies the gap between link/relevance and factual support: 14 LLMs, link validity >94%, relevance >80%, factual accuracy 39–77%, and a ~42% fact-check drop in a two-frontier-model ablation as tool calls go from 2 to 150. `2609.39026` (F, S3) shows citation correctness is not conclusion validity; it supports the additional disconfirmation check, not just the claim field. `2610.39070` (F, S0) explains why repeatability/accuracy do not rule out hidden judgment failure and why human evaluation should check grounding. `2602.18693` (A, S1) offers a concrete negation-retrieval mechanism: retrieve evidence for the original and negated claim and analyze source-level disagreement.

**4. Counter-evidence.** The main papers study LLM agents, not human verification by a solo builder; transfer is plausible but not directly tested. `2605.06635` uses LLM-as-judge for fact check, which may retain judge bias. `2609.39026` shows claim checks are insufficient without a representative evidence set, so R1 must include the disconfirmation check rather than present claim support as sufficient. `2610.39070` is a taxonomy, not an outcome study. Human claim verification costs time and may not scale; that is why the recommendation is limited to B/A rows and tested on 20 rows, not applied to all C-level evidence. PLS also has no evidence table yet, so the experiment must first create one; this is a real feasibility risk.

**5. PLS location.** `templates/evidence.md` (minimum fields, `verified_by`, new `claim_supported`); `system/modules/llm-research.md` §Process 4 and 7 (align wording); `system/10-discover.md` §Углублённый сбор step 3 (record the check); `system/20-screen.md` confidence A/B rules (reference only; no scoring change).

**6. Expected benefit.** B/A confidence would rest on a recorded judgment that the source supports the claim, not just that the URL works. This should reduce false confidence, make the existing rule auditable, and give the owner a concrete thing to check when an idea looks promising. It also creates a small dataset for judging whether the check changes decisions.

**7. Cost and risk.** About 5–10 minutes per B/A row, by estimate; the experiment will measure it. Risks: performative checking (ticking `yes` without rereading), slower evidence collection, false precision, and a false sense that claim support is sufficient when the evidence set is one-sided. Mitigations: limit to B/A, use a blind recheck on 20% of rows, and keep the disconfirmation check. No code, no new tool, no maintenance cost.

**8. Experiment.** Take the next 20 evidence rows intended for B/A across one or two ideas. For each row:

- Do the current check (URL, date, excerpt) and record the result.
- Then do the claim-support check and record `claim_supported` and the time spent.
- Do one negation/disconfirmation query and record it in `counter_evidence`.
- After 48 hours, re-check a random 20% of rows blind to the first judgment.

If fewer than 10 B/A-intended rows can be assembled in four weeks, the experiment is inconclusive; do not adopt on faith. The unit is the evidence row. The sample is 20 rows, selected consecutively from real work, not constructed examples.

**9. Measurement.** Baseline: no `claim_supported` data exists; current verification time is unmeasured. Primary metric: proportion of rows where `claim_supported` is `partial` or `no` despite passing the URL/date/excerpt check. Guardrails: median additional minutes per row; intra-rater consistency on the 20% blind recheck by the same owner (target: no more than one material disagreement in four rechecked rows); number of B/A decisions changed; share of rows with a recorded disconfirmation query. Observation window: four weeks or 20 rows, whichever comes first.

**10. Decision rule.** Adopt if at least one material `partial`/`no` appears in 20 rows, median additional time is ≤10 minutes per row, and every B/A row has a recorded `claim_supported` and disconfirmation note. Iterate if the unsupported rate is nonzero but median time is 10–20 minutes, or if only `partial` cases appear; reduce to a 5-row sample or use the negation query only. If 0/20 rows are `partial`/`no` and median time is ≤10 minutes, keep the check as a low-cost option but do not claim an accuracy benefit; re-test on a higher-stakes corpus before adopting. Reject for now if 0/20 rows are `partial`/`no` and median time is >10 minutes per row, or if the check delays a live test by more than one week without changing a decision. "Reject for now" means re-test on a different corpus later; 20 rows cannot prove the check is unnecessary in general.

**11. Falsification.** The recommendation is falsified for this context if claim-support checking never changes a B/A decision across 20 real rows and costs more than 10 minutes per row, or if it creates a false sense of security that leads to a B/A decision later contradicted by a disconfirmation check. If the blind recheck shows the owner cannot apply the judgment consistently, the field is not usable and should be rejected.

**12. Owner decision.** **Adopt for experiment.** This is a research recommendation, not an authorization. The owner must approve the 20-row pilot before any template change.

### 8.2 R2 — Make the minimal S-test path the default; move dormant controls to triggers

**1. Problem.** PLS documents a full system: stages, statuses, four gates, scoring, confidence, calibration, portfolio accounting, production analytics, quality evaluation, and LLM modules. It also documents a shorter S path, but the full apparatus is presented alongside it, and the only review record does not follow the G2 minimum. The observed state is ten experiments, nine drafts, one review, zero closed; the only review is inconclusive and missing `timebox_hours`, `exposure_floor`, `owner`, `score_at_launch`, and `confidence_at_launch`; the only idea has empty `score`/`confidence` and no evidence table. This is a young project and the review experiment was registered retrospectively, so the evidence is weak. The gap is still large enough to test whether making the existing minimal path visible and enforced improves closure.

**2. Change.** Make the rules that already exist explicit and hard to bypass; do not add a new gate or new fields:

- Define the blocking minimum for an S-test as the existing G2 fields plus the existing evidence scoring minimum:
  - **8 evidence fields:** `source_url`, `event_date`, `author_or_thread`, `verbatim_excerpt`, `signal`, `target_segment`, `source_quality`, `verified_by`.
  - **Existing B/A additions:** `source_type` (at least one `primary`), `author_id`, `verified_at`; plus `claim_supported` for B/A (R1).
  - **9 experiment fields:** hypothesis (segment, action, because, expected effect); channel/trigger; primary metric; exposure floor; exposure definition; continue/stop thresholds; timebox + review condition; stop rule; owner.
  - **Existing idea-level gate:** `score`, `confidence`, `test_cost`, `budget_until`, and `budget_signal` remain required before `testing`; this recommendation does not remove the budget guard.
- Make explicit that G2 (ready) and G4 (review/closed) are the only gates on the S path. G1/G3 already apply only to `feature | launch` and delivery, not to S.
- Move the following to triggered reference, not the default first pass:
  - **Calibration monthly review:** trigger = at least three closed experiments with complete G4. Keep `score_at_launch` and `confidence_at_launch` fields; defer the review ritual.
  - **Portfolio track hours / 30% cap:** trigger = a portfolio experiment is actually started, or a business experiment closes. Keep `portfolio_value` as an optional note.
  - **Production analytics (9-metric dashboard, event groups/properties):** trigger = `method: feature | launch` or a live product with users. For an S outreach/post/research test, one primary metric + exposure is enough.
  - **Full experiment template:** the short form is already the S form; keep the full template as the reference for M/L, `concierge`, `feature | launch`, or code.
  - **`llm-eval-data` module:** trigger = `method: quality` or an AI feature evaluation. Not for demand tests.
  - **Full 22-column evidence schema:** the 8-field scoring minimum is already the blocking requirement; keep the full schema as reference for complex/B/A evidence.
- Do not delete these sections. Mark them "dormant / reference" and keep the trigger visible. This preserves optionality and avoids a destructive rewrite.

**3. Evidence.** The primary evidence is the repository state in §3.3: 0 closed experiments, 1 inconclusive review, missing mandatory fields, no evidence table. This is the problem statement, not a paper finding. The research support is indirect and weak: `2506.16334` (A, S2) is an observational study of 1,800 Chinese startups; it finds that AI capabilities and the Lean Startup Method complement product innovation, with different effects for discovery vs optimization and MVP prototyping vs controlled experimentation. It supports disciplined, small experiments in general; it does not test the number of fields. `2610.27899` (F, S3) shows that sequential A/B can reduce runtime at Meta scale, but it is a reason not to add statistical machinery to a solo S-test, not a reason to add process. No paper directly tests "fewer mandatory fields → more closed experiments." R2 is therefore **exploratory, evidence strength 1**, and should not be described as evidence-based.

**4. Counter-evidence.** The strongest counter-evidence is the baseline itself: the project is young, the nine drafts may be a normal backlog, and `EXP-ASC-005` was registered retrospectively, which explains missing launch fields. The binding constraint may be channel access or demand, not documentation; if so, a minimal path will not help. Removing controls can increase false `kill`/`scale` decisions, missing exposure, and silent false confidence. Some "dormant" controls are cheap (two calibration fields) and should be kept. The experiment is small (three tests) and directional; it cannot prove a general effect.

**5. PLS location.** `system/00-model.md` (statuses, gates, transitions); `system/20-screen.md` (calibration, portfolio); `system/30-experiment.md` (design, measurement, review); `templates/experiment-s.md` (short form); `templates/experiment.md` (full form); `templates/evidence.md` (8-field minimum); `system/modules/llm-eval-data.md` (quality scope); `NEXT.md` (calibration timing). No edits now.

**6. Expected benefit.** More S-tests should reach a recorded G4 decision within their timebox, with less owner time spent on dormant controls. The owner should spend more time on exposure, customer contact, and the primary result, and less on filling sections that do not affect the current decision. If the hypothesis is wrong, the experiment will show that the bottleneck is channel/demand, which is also useful.

**7. Cost and risk.** The change is small and reversible: the pilot runs under the existing short form and treats the existing 8-field evidence minimum (plus `source_type`, `author_id`, `verified_at`, and `claim_supported` for B/A) and 9 G2 fields as blocking, without changing any rule. Risks: temporary inconsistency between what the docs say and what the experiment does; skipping a control that would have caught a bad decision; the owner may still not launch tests, in which case the experiment is inconclusive rather than a success. Operating cost is near zero; the main cost is the owner's discipline in recording exposure and decision fields.

**8. Experiment.** Run the next three S-tests (`research | outreach | post | demo`) in one project. Use the existing short form, but:

- Treat the 8 evidence fields, the existing B/A fields (`source_type`, `author_id`, `verified_at`, `claim_supported`), and the 9 G2 fields as the blocking minimum.
- Keep the idea-level `score`, `confidence`, `test_cost`, `budget_until`, and `budget_signal` gate; do not bypass it.
- Leave calibration, portfolio accounting, production analytics, the full template, the full 22-column schema, and `llm-eval-data` as reference/out of scope for the pilot.
- Record `spent_hours` in four categories: exposure/contact, evidence verification, artifact administration, analysis/decision.
- At review, complete G4: delivery status, exposure vs floor, primary result numerator/denominator, strongest signal, confirmed/refuted/unclear, decision, reason, next step.

The unit is the S-test. The sample is three tests, launched within 8–12 weeks. If fewer than three tests can be launched, report the reason and do not treat the experiment as a success. This is a directional pilot, not a controlled trial.

**9. Measurement.** Baseline: 0/10 experiments closed; 1/1 review experiment has `decision: more-evidence` but incomplete G4; `spent_hours` is empty, so time allocation is unknown. Primary metric: proportion of launched S-tests with a complete G4 decision within 2× the timebox. Target: at least 2/3. Guardrails: 100% of closed tests have exposure vs floor and a primary result with numerator/denominator; 0 `kill`/`scale` decisions below the exposure floor; every B/A evidence row has human verification, `source_type`, `author_id`, `verified_at`, and `claim_supported`; no test closes with `decision_reason` missing. Secondary metrics: median owner hours per closed test; share of hours in artifact administration (target ≤25%); share in exposure/contact (target ≥50%); number of tests that fail to launch due to channel/exposure.

**10. Decision rule.** Adopt if at least 2/3 S-tests close with complete G4 and all guardrails pass. Iterate if 1/3 closes, or if 2/3 close but one guardrail fails; adjust which sections are optional or add a launch checklist. Reject if 0/3 close, or if the same missing-field pattern recurs in two or more tests, or if time-to-decision increases, or if three consecutive tests fail to reach exposure because of channel/demand. A rejection means the minimal path is not the lever; diagnose channel/demand before changing PLS again.

**11. Falsification.** The hypothesis is falsified if the minimal path does not increase closure and the binding constraint is clearly channel or demand (tests launch but no qualified exposure), or if it produces a `kill`/`scale` decision below the exposure floor, or if evidence completeness falls (missing verification, missing counter-evidence). A negative result is useful: it redirects attention from process to channel.

**12. Owner decision.** **Adopt for experiment (exploratory).** This is below the protocol's normal evidence bar (`Evidence strength 1`), but it directly addresses an observed execution gap and is cheap and reversible. The owner should approve it only as a three-test pilot, not as a permanent rule change.

### 8.3 R3 — Defer calibration and forecast-metric expansion until there are outcomes

**1. Problem.** PLS has a calibration journal that is supposed to start with the first experiment and be reviewed on every monthly sweep (`system/20-screen.md` §Калибровка). `NEXT.md` separately says to review the calibration and revenue views in 1–2 months. There are zero closed experiments, so the journal has no forecast–outcome pairs. Adding Brier scores, probability calibration, decision-calibration metrics, or a more elaborate monthly review now would increase complexity without data. The research warns that forecast-level metrics are not a reliable proxy for decision quality and that small-sample belief reports are noisy.

**2. Change.** Keep the cheap inputs and outcomes, defer the review and the metric expansion:

- Keep `score_at_launch`, `confidence_at_launch`, `delivery_status`, `exposure`, `primary_result`, `decision`, and `decision_reason` in experiment records.
- Do not add Brier scores, probability calibration, decision-calibration metrics, or new calibration views now.
- Do not run the monthly calibration review as a standing ritual. Replace it with a trigger: at least three closed experiments with complete G4.
- At the trigger, run a one-page audit: idea, score/confidence at launch, exposure, primary result, decision, and whether a different threshold/weight would have changed the decision.
- Only if the audit shows a repeated misranking across at least three closed experiments, and a proposed change would have altered at least one decision for the better, consider changing weights/thresholds or adding a metric.

This is a deferral, not a deletion of the fields. Keeping the launch and outcome fields is cheap and preserves the option to calibrate later.

**3. Evidence.** `2512.14779` (F, S3, peer-reviewed) shows forecast skill is not decision skill; model rankings can change at the decision level. `2608.20828` (F, S3, peer-reviewed) shows 67.3% of belief changes are exactly zero and pooled slopes mix movement with magnitude; naive calibration/updating averages can mislead. `2610.27899` (F, S3) shows sequential A/B gains at Meta scale but is not transferable to solo S-tests. `2505.08128` (A, S3, KDD 2026) shows small-sample/non-Gaussian A/B methods, again in a randomized setting. `2609.27385` (A, S2) evaluates decision quality and forecast cost, not accuracy alone; `2608.28482` (A, S2) shows proper scoring rules shape forecaster behavior differently. Together they support decision-level evaluation and caution against metric expansion before outcomes.

**4. Counter-evidence.** Calibration research on LLM confidence is active and shows real miscalibration (for example, `2604.10585` on calibration collapse under sycophancy fine-tuning; `2605.27668` on aligning LLM uncertainty). Calibration is not irrelevant in general. A monthly review could catch a scoring problem early. But those papers concern model confidence, not PLS's score/confidence heuristics, and PLS has no outcomes to calibrate. The trigger preserves the benefit while avoiding a ritual. Dropping the two launch fields would be a mistake; R3 keeps them.

**5. PLS location.** `system/20-screen.md` §Калибровка; `system/30-experiment.md` review fields; `templates/experiment.md` calibration/forecast fields; `NEXT.md` calibration timing; `registry.base` calibration view.

**6. Expected benefit.** The owner spends time closing experiments instead of reviewing an empty calibration journal. The system keeps a cheap path to a future audit. The review avoids importing forecast metrics that do not map to PLS decisions.

**7. Cost and risk.** The main risk is delayed detection of a scoring bias. The trigger and the one-page audit mitigate it. There is no data loss because the launch fields and outcomes are retained. The audit itself is low-cost; the risk is that three closed experiments may take months, which is acceptable because calibration cannot be meaningful before then.

**8. Experiment.** This is a deferred audit, not a current experiment. At three closed experiments with complete G4, build the one-page table described above. Use a pre-defined outcome criterion recorded at each experiment's launch (for example, "meets primary threshold" vs "below threshold"), not a post-hoc ranking. Compare the observed decision with what the score/confidence ranking would have suggested. Include a naive baseline: "always `more-evidence`" or "rank by score only." The unit is the closed experiment. The sample is three, then six.

**9. Measurement.** Primary metric: number of closed experiments in which the score/confidence ranking is contradicted by the pre-defined outcome in a way that would have changed a decision. Guardrail: no weight/threshold changes before three closed experiments; no new metric without a demonstrated decision change; absolute counts and denominators are shown. Observation window: three to six closed experiments, however long that takes.

**10. Decision rule.** Adopt a calibration change only if at least three closed experiments show a repeated misranking in the same direction and the proposed change would have altered at least one decision for the better under the pre-defined outcome criterion. Iterate if the signal is mixed or only two experiments agree; collect to six. Reject the expansion if there is no repeated misranking, or if no proposed metric changes a decision; keep the two fields and the qualitative journal. If the audit is too ambiguous to rank outcomes, stop investing in calibration and keep only the fields.

**11. Falsification.** The recommendation is falsified if a simple three-experiment audit reveals a repeated, decision-relevant misranking that a richer metric would have caught, or if delaying the review causes a clearly wrong `scale`/`kill` decision that an earlier calibration check would have prevented. In that case, revisit the trigger and add the minimum metric that would have changed the decision.

**12. Owner decision.** **Defer.** Keep the fields; do not add metrics or a monthly review now. Re-open at three closed experiments.

### 8.4 Recommendation summary

| ID | Smallest change | Evidence grade | Experiment | Decision rule | Owner decision |
|---|---|---|---|---|---|
| R1 | `claim_supported` value + one disconfirmation check for B/A; no new stage | S2–S3 empirical, agent settings; F/A | 20 B/A evidence rows; unsupported rate + time | Adopt if ≥1 material unsupported in 20 and ≤10 min/row; reject if 0/20 and >10 min/row | **Adopt for experiment** |
| R2 | 8 evidence + 9 experiment fields (plus existing B/A fields) as the visible S-test minimum; move dormant controls to triggers | Repository observation + indirect S2; exploratory | 3 S-tests; closure + guardrails + time allocation | Adopt if ≥2/3 close with complete G4 and guardrails pass; reject if 0/3 or missing fields recur | **Adopt for experiment (exploratory)** |
| R3 | Keep launch and outcome fields; defer calibration review/metrics until ≥3 closed experiments | S3 peer-reviewed + S2/S3 adjacent | One-page audit at 3 closed experiments | Adopt only if repeated misranking and a decision would change; otherwise keep fields | **Defer** |

---

## 9. Simplification and removal analysis

### 9.1 Short answer

**Simplify the default path, not the method.** PLS does not need fewer safeguards; it needs fewer *simultaneous* safeguards on the first pass. The effectiveness of an S-test depends on three things:

1. **Exposure** — did the right people see the offer?
2. **Evidence support** — does the evidence actually support the claim?
3. **A recorded decision** — did the result produce a `scale`, `iterate`, `more-evidence`, `park`, or `kill` with a reason?

Anything that does not change those three on the current S-test is a candidate for deferral. Almost nothing should be removed from the system; a lot can be dropped from the default path.

The core docs and templates inspected total about 1,700 lines. That is context, not a measure of complexity or effectiveness. The stronger signal is behavioral: ten experiments, zero closed, one inconclusive review, no evidence table.

### 9.2 The default S-test path to keep

For an S-test (`research | outreach | post | demo`), the blocking minimum should be:

**Evidence (8 scoring fields, plus B/A additions):**

1. `source_url`
2. `event_date`
3. `author_or_thread` (with `author_id` for B/A independence)
4. `verbatim_excerpt`
5. `signal`
6. `target_segment`
7. `source_quality`
8. `verified_by`

For B/A, the existing additional fields remain required: `source_type` (at least one `primary`), `author_id`, `verified_at`, and `claim_supported` (R1). Plus one disconfirmation note in the existing `counter_evidence` field for B/A.

The evidence template already defines these 8 fields as the scoring minimum; the full 22-column schema is context, not a first-pass requirement. The recommendation is to make that minimum the visible default, not to invent a smaller schema.

**Experiment (9 fields, already the G2 ★ fields):**

1. Hypothesis: segment, action, because, expected effect
2. Channel / trigger
3. Primary metric
4. Exposure floor
5. Exposure definition
6. Continue / stop thresholds
7. Timebox + review condition
8. Stop rule
9. Owner

**Idea-level gate (already required):** `score`, `confidence`, `test_cost`, `budget_until`, and `budget_signal` remain required before `testing`. The 9 fields are the experiment record, not a replacement for the idea budget gate.

**Gates:** G2 (ready) and G4 (review/closed) only. G1/G3 stay for `feature | launch` and delivery.

**At review (G4):** delivery status, exposure vs floor, primary result numerator/denominator, strongest signal, confirmed/refuted/unclear, decision, reason, next step. These are not launch fields; they are closure fields.

This is enough to run a credible S-test and to distinguish "no demand" from "no exposure." It is also small enough to fill before launch.

### 9.3 What to move out of the default path (defer, do not delete)

| Item | Current location | Why it can leave the default S path | Trigger to restore |
|---|---|---|---|
| Monthly calibration review | `system/20-screen.md` §Калибровка; `registry.base` calibration view | Zero closed experiments; no forecast–outcome pairs | ≥3 closed experiments with complete G4 |
| Portfolio hours / 30% cap | `system/20-screen.md` §Портфельная оценка; `system/00-model.md` | No portfolio experiment and no business close; the track is dormant | A portfolio experiment starts, or a business experiment closes |
| Production analytics (9-metric dashboard, event groups/properties) | `system/30-experiment.md` §Измерение | S-tests need one primary metric + exposure, not a live-product dashboard | `method: feature | launch` or a live product with users |
| Full experiment template as the first S document | `templates/experiment.md` | The short form already exists and is sufficient for S; the full form is for M/L, `concierge`, `feature`, `launch`, or code | M/L, `concierge`, `feature | launch`, or code |
| `llm-eval-data` module | `system/modules/llm-eval-data.md` | Demand tests are not AI quality evaluations | `method: quality` or an AI feature evaluation |
| Full 22-column evidence schema as the first-pass form | `templates/evidence.md` | The template already sets the 8-field scoring minimum; the full schema is context for complex/B/A evidence | Complex evidence, B/A, or an audit |

**Interpretation:** None of these is useless. Each is a real control at the right trigger. The risk is that presenting them alongside the default path without a clear "start here" boundary makes the owner see a wall of requirements before the first customer contact.

### 9.4 What can be dropped outright from the default path

These are the only true drops from the default routine worth considering. They remove ritual or duplication, not safeguards:

- **The standing monthly calibration review** — replace it with the ≥3-closed-experiment trigger. Keep the fields.
- **The full experiment template as the first S document** — use the existing short form; keep the full form for M/L/feature/launch.
- **The full 22-column evidence schema as the first-pass form** — use the existing 8-field scoring minimum; keep the full schema for complex/B/A evidence.
- **The production analytics dashboard in the S-test path** — keep it for live products and `feature | launch`.
- **Portfolio hours/30% accounting in the default monthly routine** — keep it for a portfolio experiment; do not run it while no portfolio experiment exists.

Do **not** delete the underlying fields, gates, or templates. "Drop from the default path" is not "delete from the system."

### 9.5 What must not be dropped

These are the cheap safeguards that prevent false conclusions:

- **Exposure floor and exposure definition.** Without them, a zero result is uninterpretable. `EXP-ASC-005` is the live example.
- **Decision table and the hard rule "below floor → `more-evidence` only."** This prevents `kill`/`scale` on noise.
- **Stop rule and the two-`more-evidence` limit.** This prevents endless discovery.
- **Human verification and claim support.** This prevents a real URL from being mistaken for real evidence.
- **Counter-evidence/disconfirmation.** This prevents one-sided evidence sets.
- **Source independence (`cluster`, `author_id`, `source_quality`).** This prevents duplicate reports from looking like independent corroboration.
- **8 evidence fields, the B/A additions (`source_type`, `author_id`, `verified_at`, `claim_supported`), and 9 experiment fields.** These are the minimum for a traceable decision.
- **Idea-level budget gate (`budget_until`, `budget_signal`, `test_cost`).** This prevents an unbounded test.
- **G2/G4 for S; G1/G3 for feature/launch.** These are the authorization and decision points.
- **L0–L5 and confidence A/B/C.** These keep signal strength separate from opportunity size.
- **LLM research guardrails.** LLMs can sort and draft; they cannot be the primary source or promote A/B.

### 9.6 Expected effect and how to know

**Hypothesis:** The minimal path will increase the share of launched S-tests that reach a complete G4 decision, without increasing false `kill`/`scale` decisions or reducing evidence completeness.

**How to know:** R2's three-test pilot measures closure rate, G4 completeness, exposure vs floor, evidence verification, and time allocation. If at least 2/3 tests close with complete G4 and all guardrails pass, the minimal path is worth adopting. If 0/3 close, or the same missing-field pattern recurs, the hypothesis fails. If tests launch but do not reach exposure, the bottleneck is channel/demand, not process; that is a different problem.

**What would prove the simplification wrong:** More closed tests but worse decisions (for example, a `kill` below the exposure floor, a B/A decision without claim support, or a `scale` without repeat use). Speed without decision quality is not effectiveness.

### 9.7 What not to simplify

- Do not drop exposure or the decision table to "move faster." That is how you get a confident "no demand" conclusion from no exposure.
- Do not drop human verification or claim support to "reduce friction." That is how you get cited-but-wrong evidence.
- Do not drop counter-evidence to "focus on the positive case." That is how you get a one-sided evidence set.
- Do not drop the stop rule to "keep learning." That is how you get endless `more-evidence`.
- Do not replace human judgment with an LLM to "save time." The reviewed agent papers show exactly why that fails.
- Do not add calibration metrics before outcomes. That is measurement theater.
- Do not add a new module, stage, or template to solve an execution problem. The repository already has more surface area than it executes.

---

## 10. Deferred and rejected ideas

These are potentially interesting methods that are not recommended now. "Defer" means the method may become relevant at a trigger; "reject for now" means it does not fit PLS's current setting and should not be pursued without a new argument.

| Idea | Source | Why not now | Revisit trigger |
|---|---|---|---|
| Group-sequential A/B design / safe peeking | `2610.27899` (F, S3) | Strong industrial result, but requires large randomized experiments, independent increments, daily autocorrelation correction, and platform infrastructure. PLS S-tests are small and usually non-randomized. | 10+ randomized A/B tests with a stable traffic base |
| Small-sample / non-Gaussian A/B efficiency | `2505.08128` (A, S3) | Requires randomized control and a statistical workflow; abstract only. Not a demand-test method. | A randomized A/B program with enough volume to justify the modeling |
| Bayesian experimental design / value of information | e.g., `2302.14545`, `2603.24974` (A) | High modeling overhead for a solo builder; PLS's current bottleneck is execution, not optimal allocation. The value-of-information framing is useful conceptually but does not justify a new module now. | 10+ experiments with stable priors and a clear allocation decision |
| Brier scores / proper scoring rules / probability calibration | `2608.28482`, `2609.32885` (A) | Forecast metrics are not decision quality; PLS has no probabilistic forecasts or closed outcomes. R3 defers this. | ≥3 closed experiments and a decision-relevant misranking |
| LLM-as-judge reliability via IRT | `2602.00521` (A, accepted ICML 2026) | Relevant to AI quality evaluation, not demand tests. PLS's `llm-eval-data` module already covers the quality context. | A `quality` experiment or an AI feature evaluation |
| Voice-of-customer automation / customer-context graph | `2503.01870` (F, S3), `2610.09375` (A, S2) | The full-text study needs 1,549 labeled pairs; the context-graph study is abstract-only, one dataset, and needs a customer-data graph. PLS's human problem statement is cheaper and more accountable. | A large feedback corpus (>500 items) with labels and a clear extraction bottleneck |
| SGHA / local research-problem agent | `2608.17501` (A, S1) | Scientific problem discovery, not customer problem discovery; code not inspected; local 9B model + corpus graph is a research prototype. | A research-heavy project with a curated corpus and a need for traceable gap discovery |
| Agentic deep research as an autonomy layer | `2605.06635`, `2609.39026`, `2610.39070` (F) | The evidence shows cited-but-wrong reports, selective evidence, and hidden judgment failures. Agents can search/sort/draft, but should not promote evidence. | A verified agent workflow with claim-level evaluation and a human gate |
| Search-time contamination / DeepTRACE evaluation hygiene | `2606.05241` (A), `2509.04499` (A) | Evaluation hygiene for agent benchmarks, not a PLS workflow change. Useful as a caution when reading agent papers. | If PLS builds or evaluates an agent benchmark |
| Portfolio optimization / financial portfolio math | e.g., `2509.00447`, `2610.09246` (A) | PLS's portfolio value is a qualitative 0–5 note, not a financial portfolio. The math does not transfer. | A real portfolio allocation decision with multiple funded bets |
| AI + Lean Startup Method | `2506.16334` (A, S2) | Observational study of 1,800 Chinese startups; supports the general direction of disciplined experimentation, not a specific PLS change. | A process experiment with enough cases to test a specific mechanism |
| Graph-engine planning documents | `_docs/graph-engine-implementation-spec.md`, `_docs/graph-engine-stage-0-plan.md`, `_docs/handoffs/` | Untracked planning docs; not implemented, not referenced by the core loop, not a PLS capability. Counting them as system scope would inflate complexity. | If the graph engine is actually implemented and used by PLS |
| "Add more process" as a response to missing decisions | No supporting source | The observed problem is missing exposure/decisions, not missing templates. More process would likely worsen the bottleneck. | Evidence that a specific missing control caused a wrong decision |

### 10.1 Rejected for now, with reasons

- **Portfolio optimization** — rejected for now: the object of optimization is different; PLS has one project and no funded portfolio.
- **Generic agentic research automation** — rejected for now: the reviewed evidence is about failure modes, not reliable autonomy; the human gate is the correct design.
- **A new calibration metric layer** — rejected for now: no outcomes; R3's trigger is the path back.
- **A new evidence template or stage** — rejected for now: the existing template has the right minimum; the gap is the claim-support record, not the number of documents.
- **A new scoring model** — rejected for now: no closed experiments to calibrate against; changing weights would be guesswork.

---

## 11. Open questions and next review

### 11.1 Open questions

1. **R1:** Does claim-level verification change any B/A decision, or does it only add time? The 20-row pilot is designed to answer this.
2. **R2:** Does the minimal path increase the share of S-tests that reach a complete G4 decision? The three-test pilot is designed to answer this.
3. **R2:** Is the binding constraint documentation, channel, or demand? If tests launch but do not reach exposure, the answer is channel/demand, not process.
4. **R3:** After three closed experiments, do `score` and `confidence` predict outcomes well enough to justify a calibration change? The one-page audit will show whether a change would alter a decision.
5. **Generalization:** Does any of this transfer beyond one project and one owner? The review cannot answer this with the current repository.
6. **Evidence quality:** Do the 2026 agent findings replicate in human-only research workflows? The reviewed papers are mostly LLM-agent benchmarks.
7. **Publication status:** Will `2605.06635`, `2609.39026`, `2610.39070`, or `2609.22246` be peer-reviewed, revised, or replicated? A published version could change confidence.
8. **Search coverage:** What relevant work exists in management, marketing, or HCI journals that arXiv does not index? This review cannot claim to have found it.
9. **Process design:** What is the minimum documentation for a solo builder? There is no direct empirical literature; the answer must come from PLS's own experiments.
10. **Agentic automation:** Will citation-verification agents improve enough to reduce the human burden without lowering evidence quality? Monitor, do not assume.

### 11.2 Triggers for an earlier re-review

- A published version, major revision, or replication of `2605.06635`, `2609.39026`, `2610.39070`, `2609.22246`, or `2503.01870`.
- A retraction, correction, or credible critique of any paper used in a recommendation.
- Completion of the R1 20-row pilot or the R2 three-test pilot.
- A major change to PLS rules, templates, or gates.
- A new project or a second owner using PLS, which would test generalization.
- A material change in the evidence landscape for claim verification or calibration (for example, a validated human-in-the-loop verification method).

### 11.3 Next review

- **Monthly scan:** 2026-11-30 (30 days). Focus: published versions of the key preprints, new claim-verification work, and any replication of `2503.01870`.
- **Quarterly deep review:** 2027-01-31. Reassess all six capability areas, the R1/R2 results if available, and whether R3's trigger has been reached.
- **Earlier if:** a trigger in §11.2 occurs. A monthly scan may legitimately conclude "no material new evidence; no change recommended."

---

## 12. Quality checklist

- [x] The current PLS repository and prior review reports were inspected. No prior arXiv/research-review report exists; this is the baseline.
- [x] The report records the Git revision (`e040929e11f5881ddbb0d572278117878d3cfa71`) and search cut-off date (2026-10-31).
- [x] Searches covered all six capability areas with multiple query formulations (56 queries; at least six per area, 13 for opportunity discovery).
- [x] Screening decisions and access limitations are transparent (§4.3, §4.5).
- [x] Important papers were assessed from full text where accessible (8 full-text; 6 abstract-only, labeled `A`).
- [x] Inspection level and study strength are recorded separately for every table paper.
- [x] Publication status was checked via arXiv, Crossref, and OpenAlex; no SOTA claims are made.
- [x] Findings are compared with existing PLS behavior (§7).
- [x] Counter-evidence and limitations are included for every recommendation and for the synthesis.
- [x] No more than three high-priority recommendations are made (R1, R2, R3).
- [x] Each recommendation has a falsifiable experiment and a decision rule.
- [x] Facts, interpretation, and hypotheses are separated with explicit labels.
- [x] No PLS rules, templates, code, or configuration were modified; no issues, PRs, branches, commits, or pushes were created.

**Post-writing verification:** The only repository change from this review is the new file `_docs/arxiv-review-2026-10-31.md`. Pre-existing untracked files were preserved. This was verified with `git status --porcelain` after writing.

---

## 13. Ответ владельцу (по-русски)

### 13.1 Что сделано

Проведён квартальный обзор arXiv за последние 24 месяца по шести областям: поиск возможностей, качество свидетельств, приоритизация, эксперименты, цикл обучения и агентная автоматизация. Репозиторий: `main` @ `e040929e11f5881ddbb0d572278117878d3cfa71`. Прочитано полностью 8 статей, ещё 6 — на уровне абстракта. Ничего в PLS не менял: создан только этот отчёт. Коммитов, issue, PR, веток и пушей нет.

### 13.2 Главный вывод

Система не страдает от недостатка методики. Она страдает от того, что методика не доходит до решения.

Факты: 10 экспериментов, из них 9 в `draft`, 1 в `review`, 0 закрытых. Единственный review-эксперимент `EXP-ASC-005` не может отличить отсутствие спроса от отсутствия экспозиции: в нём нет `timebox_hours`, `exposure_floor`, `owner`, `score_at_launch`, `confidence_at_launch`, а число записей в waitlist не восстановлено. У единственной идеи `IDEA-ASC-001` пустые `score` и `confidence`, нет evidence-таблицы.

Это не доказательство, что система слишком сложная: проект молодой, а `EXP-ASC-005` зарегистрирован ретроспективно — этим объясняется часть пустых полей. Но этого достаточно, чтобы проверить минимальный путь, а не добавлять новые правила.

### 13.3 Как упростить систему

Короткий ответ: **упрощать не метод, а путь по умолчанию**. Оставить три вещи, которые определяют эффективность S-теста:

1. **Экспозиция** — нужные люди действительно увидели предложение.
2. **Подтверждение claim** — источник действительно поддерживает утверждение, а не просто существует.
3. **Записанное решение** — `scale`, `iterate`, `more-evidence`, `park` или `kill` с причиной.

Всё, что не меняет эти три вещи в текущем S-тесте, — кандидат на отсрочку.

**Что уже есть, но не стало видимым default:** в правилах уже есть короткая S-форма, 8-полевой минимум evidence и освобождение S от G1/G3. Проблема не в отсутствии минимального пути, а в том, что он не enforced и не виден как основной.

**Оставить как блокирующий минимум:**

- 8 полей evidence: `source_url`, `event_date`, `author_or_thread`, `verbatim_excerpt`, `signal`, `target_segment`, `source_quality`, `verified_by`;
- для B/A — существующие `source_type` (минимум один `primary`), `author_id`, `verified_at` и новый `claim_supported`;
- 9 полей эксперимента: гипотеза, канал/триггер, primary metric, exposure floor, exposure definition, пороги, timebox/review, stop rule, owner;
- idea-level `score`, `confidence`, `test_cost`, `budget_until`, `budget_signal`;
- G2 и G4;
- decision table и жёсткое правило «ниже floor — только `more-evidence`»;
- stop rule;
- L0–L5, score, confidence;
- human verification, counter-evidence, cluster/author_id.

**Убрать из пути по умолчанию (не удалять из системы):**

- ежемесячный calibration review — до 3 закрытых экспериментов;
- портфельный учёт часов и 30% — до портфельного эксперимента или первого business close;
- production-аналитику (9 метрик, event schema) — до `feature | launch` или live-продукта;
- полный шаблон эксперимента как первый документ S — для S использовать короткий;
- `llm-eval-data` — до `quality` или оценки AI-функции;
- полную 22-колоночную evidence-схему как обязательную — по шаблону уже достаточно 8 полей.

**Что из этого можно перестать делать совсем (не удаляя из системы):**

- стоячий ежемесячный calibration review;
- полный шаблон как первый документ S;
- полную 22-колоночную схему как обязательную;
- production dashboard в S-тесте;
- портфельные часы в ежемесячном routine.

Это не удаление полей и гейтов, а снятие их с пути по умолчанию.

**Не выбрасывать:** exposure floor, decision table, stop rule, human verification, claim support, counter-evidence, 8/9 минимумов, budget gate. Это дешёвые защиты от ложных выводов. Именно их отсутствие превращает «нет спроса» в догадку.

### 13.4 Что добавить

Одно поле `claim_supported: yes | partial | no | unknown` для B/A и один negation/disconfirmation check в существующем `counter_evidence`. Это не новый этап и не новый инструмент, а фиксация требования, которое уже есть в `llm-research.md`: внешний проверяльщик не заменяет человеческую проверку claim для A/B. Проверить на 20 B/A-строках; если это не меняет ни одного решения и стоит больше 10 минут на строку — отклонить для текущего корпуса.

### 13.5 Что отложить

Brier-оценки и калибровочные метрики, sequential A/B, Bayesian experimental design, portfolio optimization, автоматизацию voice-of-customer, автономных research-агентов. Причины разные: нет масштаба, нет данных, другая задача или research показывает failure modes. Это не «плохие методы», а «не сейчас».

### 13.6 Решения владельца

| Рекомендация | Что это | Решение |
|---|---|---|
| R1 | `claim_supported` + один disconfirmation check для B/A; без нового этапа | **Adopt for experiment** |
| R2 | 8 evidence + 9 experiment полей (плюс существующие B/A-поля) как видимый enforced-минимум для S; остальное — по триггерам | **Adopt for experiment (exploratory)** |
| R3 | Не добавлять калибровочные метрики и не запускать monthly calibration review до 3 закрытых экспериментов | **Defer** |

### 13.7 Следующий шаг

Выбрать R1 или R2 — лучше не запускать оба одновременно, чтобы не смешивать эффекты. Для R1: 20 B/A-строк, замер unsupported rate и времени. Для R2: 3 S-теста за 8–12 недель, замер closure rate, полноты G4 и распределения времени. После результатов — отдельное решение владельца; до этого правила PLS не меняются.

### 13.8 Ограничения

8 статей полностью, 6 — только абстракт; ни одна статья не воспроизведена; код не инспектирован; один проект и один владелец; несколько ключевых статей — препринты; поиск англоязычный и arXiv-центричный; второго независимого ревьюера не было. Это directional review, а не систематический обзор. Он достаточен, чтобы предложить три проверяемых эксперимента, но не чтобы утверждать, что PLS «слишком сложная» или что предложенное упрощение обязательно сработает.

