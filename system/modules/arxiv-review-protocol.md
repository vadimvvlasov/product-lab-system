# Product Lab — arXiv Research Review Protocol

**Document type:** Repeatable research procedure  
**Applies to:** Product Lab System (PLS)  
**Used by:** Research Loop / independent research-review agent  
**Companion prompt:** [`arxiv-review-prompt.md`](./arxiv-review-prompt.md)  
**Default cadence:** monthly scan; quarterly deep review  
**Decision authority:** Product Lab owner

---

## 1. Purpose

This protocol defines how Product Lab reviews scientific and technical research for improvements to its own operating method.

Product Lab is a project-agnostic system for continuously:

1. discovering customer problems and product opportunities;
2. evaluating evidence and commercial potential;
3. prioritizing what to investigate;
4. running inexpensive, informative experiments;
5. learning from real customer and production behavior;
6. updating future decisions based on observed outcomes.

The research review exists to improve the quality and efficiency of this loop. It is **not** a parallel product-idea discovery pipeline, a general AI-news digest, or a mechanism for automatically changing PLS.

### Core rule

**A paper can justify investigating a change; it cannot, by itself, authorize changing Product Lab.** A proposed change must be translated into a testable hypothesis, evaluated in the PLS context, and approved by the owner after evidence is collected.

---

## 2. Research questions

Organize searches around the following capability areas. These are lenses for finding relevant methods, not a requirement to find a fixed number of papers in every category.

| Capability | Research question | PLS relevance |
|---|---|---|
| Opportunity discovery | How can we detect recurring, costly, urgent, underserved problems and distinguish them from weak signals? | Sweep |
| Evidence quality | How can we assess source quality, corroborate claims, find disconfirming evidence, and represent uncertainty? | Sweep, Screen, research artifacts |
| Prioritization | How should we allocate scarce time and money when outcomes and probabilities are uncertain? | Screen, portfolio decisions |
| Experimentation | Which low-cost experiments produce the most useful information about demand, willingness to pay, retention, or feasibility? | Experiment |
| Learning loop | How can observed user behavior and commercial outcomes update beliefs, scoring, and future choices? | Live, Review / Decision |
| Agentic automation | Where can agents reduce research or execution costs without lowering evidence quality or introducing unacceptable failure modes? | Cross-cutting |

Agentic automation is subordinate to the first five areas. Do not recommend agents merely because a paper demonstrates an agent benchmark.

---

## 3. Cadence and review modes

### 3.1 Monthly scan

Purpose: detect relevant new work and update the evidence picture without repeating a full review.

Default procedure:

1. Read the previous report and its open questions.
2. Search for papers published or substantially updated since the previous scan, normally covering the previous 30–45 days plus any missed period.
3. Search for important corrections, replications, benchmark updates, negative results, or published versions of previously reviewed preprints.
4. Screen new papers for relevance and evidence quality.
5. Deep-read only papers that could materially change a previous conclusion or support a promising new improvement.
6. Update the cumulative index and record whether any recommendation changed status.

A monthly scan may legitimately conclude: **no material new evidence; no change recommended**.

### 3.2 Quarterly deep review

Purpose: reassess whether PLS's methods are aligned with the strongest available evidence.

Default procedure:

1. Revisit all six capability areas.
2. Reassess important papers from previous quarters, including published versions and replications.
3. Search for systematic reviews, meta-analyses, benchmark papers, and competing methods.
4. Compare methods and baselines rather than evaluating papers in isolation.
5. Identify persistent PLS weaknesses and areas where the evidence has materially changed.
6. Produce no more than three high-priority improvement proposals.
7. Recommend experiments, not automatic adoption.

The quarterly review should synthesize cumulative knowledge; it should not simply append another monthly bibliography.

---

## 4. Search strategy

### 4.1 Time window

- Primary window: research from the previous 24 months.
- Include older foundational work when it remains relevant or is repeatedly used as a baseline.
- For rapidly evolving areas (for example, agent evaluation), explicitly record the search cut-off date.
- A recent preprint is not automatically stronger than an older replicated result.

### 4.2 Sources

Use arXiv as the primary discovery source. Cross-check using authoritative sources where available:

- publisher or conference proceedings pages;
- DOI / Crossref metadata;
- OpenAlex or Semantic Scholar metadata for discovery and citation context;
- official benchmark, dataset, and code repositories;
- paper appendices and supplementary material.

Use citation counts only as discovery context. They are not a measure of correctness or direct applicability to PLS.

### 4.3 Query design

For each capability area, formulate at least two distinct search queries using different terminology or research communities. Combine terms rather than relying on one broad query.

Example query themes (adapt and refine; do not treat these as exhaustive):

| Area | Search themes |
|---|---|
| Opportunity discovery | customer problem discovery; need finding; unmet needs; demand signals; market opportunity identification; jobs to be done; problem interviews |
| Evidence quality | evidence synthesis; source reliability; claim verification; corroboration; counterfactual evidence; uncertainty calibration; research agent evaluation |
| Prioritization | value of information; Bayesian decision theory; active learning; portfolio selection; opportunity cost; sequential decision-making |
| Experimentation | lean experimentation; startup experiments; willingness to pay; demand testing; field experiments; sequential testing; minimum viable test |
| Learning loop | product analytics; retention prediction; behavioral feedback; experimentation platforms; causal inference; online learning; decision calibration |
| Agentic automation | research agents; tool-use evaluation; agent reliability; human-in-the-loop; workflow automation; multi-agent collaboration |

Search broadly, then narrow. Record the actual query strings and the sources searched. Do not claim exhaustive coverage based on a handful of queries.

### 4.4 Search coverage and stopping

A practical default for a deep review is:

- search all relevant capability areas;
- use at least two query formulations per area;
- inspect titles and abstracts of potentially relevant results;
- shortlist approximately 10–30 candidates where the literature volume permits;
- deep-read the most relevant 3–8 papers, prioritizing those that can change a PLS decision.

These are workload guidelines, not quality scores or mandatory quotas. In a narrow topic, fewer papers may be sufficient. In a broad or contested topic, more may be needed.

Stop searching a topic when additional queries produce mostly duplicates or clearly irrelevant results and the key competing approaches, foundational references, and credible counter-evidence have been identified. Explain the stopping rationale and remaining gaps.

### 4.5 Search log

For each search session record:

- review date and search cut-off date;
- database / website;
- exact query;
- date range and filters;
- number of results inspected, when available;
- shortlisted papers;
- known access limitations.

This makes the review repeatable and allows later reviewers to identify search gaps.

---

## 5. Screening and paper selection

Screen in two passes.

### Pass 1 — Title and abstract

Keep a paper when it plausibly:

- addresses one of the research questions in Section 2;
- presents a method, dataset, benchmark, evaluation, or synthesis relevant to a PLS capability;
- offers evidence that could affect a design or operating decision.

Exclude or deprioritize:

- generic AI commentary without a method or evidence;
- papers whose use case is too remote to transfer and has no clearly transferable mechanism;
- duplicate versions, unless the newer version materially changes results;
- papers that merely restate a known method without meaningful evaluation.

Record important exclusions briefly when they reveal a recurring search boundary.

### Pass 2 — Full-text assessment

For shortlisted papers, inspect the full paper where accessible, including methods, results, limitations, appendices, and supplementary materials when important.

Extract:

1. problem and research question;
2. method and assumptions;
3. dataset, sample, environment, and selection process;
4. baselines and comparison conditions;
5. metrics and measured results;
6. uncertainty, statistical analysis, and failure cases;
7. limitations and threats to validity;
8. code, data, and reproduction availability;
9. publication and replication status;
10. possible transfer to Product Lab.

If only an abstract or partial text is available, do not describe the paper as fully reviewed.

---

## 6. Evidence classification

Use **two separate labels**. Do not conflate how much of a paper the reviewer inspected with how strong the study itself is.

### 6.1 Inspection level — what the reviewer checked

| Label | Meaning |
|---|---|
| A | Abstract or metadata only |
| F | Full paper text reviewed |
| C | Relevant code, configuration, benchmark, or dataset inspected |
| E | A relevant experiment or reproduction was performed by the reviewer / PLS |

Multiple labels may apply, for example `F+C`. `E` means that an experiment was actually conducted; it must never be awarded merely because the paper reports an experiment.

### 6.2 Study strength — what kind of evidence the paper provides

This is an internal qualitative rubric, not a universal scientific ranking.

| Level | Description | Typical caution |
|---|---|---|
| S0 — Conceptual | Theory, framework, position paper, or proposal without empirical evaluation | Useful for generating hypotheses, not proof of effectiveness |
| S1 — Synthetic / narrow benchmark | Simulation, synthetic data, toy task, or a narrow benchmark | Performance may not transfer to real workflows |
| S2 — Empirical, limited | Real-world data or user / field evidence, but limited sample, setting, or controls | Confounding and external validity may be substantial |
| S3 — Strong comparative | Meaningful baselines, suitable metrics, controlled or carefully comparative evaluation, and substantial analysis | Still check dataset, benchmark, and publication limitations |
| S4 — Independently supported | Independent replication, multiple external settings, or credible longitudinal evidence in real use | Stronger support, but not automatic proof of PLS benefit |

Assign a level with a short justification. If the paper does not provide enough information, use `unclear` rather than guessing.

### 6.3 Publication status

Record one of:

- peer-reviewed publication (name the venue and year);
- preprint only;
- accepted / in press (verify from venue or author source);
- publication status unknown.

A preprint can contain valuable evidence, but its status must be visible. Peer review also does not guarantee that a finding is correct or transferable.

### 6.4 SOTA claims

Use the phrase **state of the art (SOTA)** only when the comparison is properly bounded. Record:

- task and benchmark version;
- evaluation metric;
- comparison date;
- baseline methods and whether comparisons are fair;
- whether results are independently reproduced;
- known benchmark contamination, data leakage, or evaluation limitations.

Otherwise write **“best result reported by the authors under this evaluation”**, not “proven SOTA”.

---

## 7. Critical appraisal and transfer to Product Lab

For each important finding, assess:

### 7.1 Internal validity

- Is the comparison fair?
- Is the sample or dataset appropriate?
- Are metrics aligned with the claimed benefit?
- Are uncertainty and failure cases reported?
- Could data leakage, benchmark overfitting, selection bias, or researcher degrees of freedom explain the result?
- Are negative or null results available?

### 7.2 External validity

- Does the study concern real users, real purchasing behavior, or merely benchmark tasks?
- Does its setting resemble a solo builder / small team?
- Does it transfer across industries, geographies, and product types?
- Does it assume large datasets, paid panels, substantial budgets, or enterprise infrastructure?
- Does it rely on tools, permissions, or data that PLS does not have?

### 7.3 Practicality

- What is the smallest implementation that preserves the method's essential mechanism?
- What recurring time, money, compute, and maintenance costs are introduced?
- What new failure modes or incentives are created?
- Can the method be measured with existing PLS artifacts and production data?
- Does it reduce end-to-end learning time, improve decision quality, or merely increase activity and reporting?

### 7.4 Existing-practice comparison

Classify each finding as one of:

- **Supports:** reinforces an existing PLS practice.
- **Refines:** suggests a specific improvement to an existing practice.
- **Challenges:** provides credible evidence against an existing practice.
- **Adds:** offers a useful capability not currently present.
- **Not transferable:** interesting research, but insufficient fit for PLS.

Do not propose a new module if a small update to an existing rule or template would achieve the same goal.

---

## 8. Recommendation prioritization

Return no more than three high-priority recommendations per review. A recommendation is not mandatory.

Use the following 0–3 ratings, always with a written rationale:

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| PLS fit | No clear fit | Indirect fit | Clear fit to a stage / decision | Directly addresses a demonstrated PLS weakness |
| Evidence strength | Unsupported | Preliminary / S0–S1 | Relevant empirical support / typically S2–S3 | Strong and independently supported / typically S4 |
| Expected impact | Negligible or unclear | Local convenience | Meaningful improvement plausible | Potentially material improvement in decision quality or learning efficiency |
| Feasibility | Not practical | High cost / major dependencies | Manageable with some work | Small, reversible, low-cost change |

Do not sum these numbers into a pseudo-scientific precision score. Use them to make trade-offs explicit.

### Recommendation eligibility

- A high-priority recommendation should normally have `PLS fit >= 2` and `Evidence strength >= 2`.
- A promising idea with weaker evidence may be listed as an exploratory hypothesis, not a proven improvement.
- A high-impact but expensive idea should normally be tested with a smaller prototype first.
- Contradictory evidence must reduce confidence and be visible in the report.
- If no proposal meets the bar, recommend no change.

### Required recommendation format

For each recommendation include:

1. **Problem:** specific observed weakness or opportunity in PLS.
2. **Change:** the smallest proposed change.
3. **Evidence:** papers, study-strength levels, inspection levels, and exact supporting findings.
4. **Counter-evidence:** credible contrary findings or limitations.
5. **PLS location:** exact file, rule, stage, template, or decision affected.
6. **Expected benefit:** what should improve and why.
7. **Cost and risk:** implementation, operating cost, complexity, and possible side effects.
8. **Experiment:** minimum test to validate the change.
9. **Measurement:** baseline, primary metric, guardrail metric, and observation window.
10. **Decision rule:** what result means adopt, iterate, or reject.
11. **Falsification:** what result would show that the idea does not work.
12. **Owner decision:** adopt for experiment / defer / reject. This is a recommendation, not an authorization.

---

## 9. Experiment-design requirements

Translate a research-backed proposal into a test that can be run without prematurely changing the whole system.

Where applicable, specify:

- **Hypothesis:** one falsifiable statement.
- **Intervention:** what changes in the workflow or decision process.
- **Baseline:** current PLS practice or a suitable comparison.
- **Unit of analysis:** idea, opportunity, experiment, product, or decision.
- **Sample / selection:** how cases are selected and likely sample limitations.
- **Primary metric:** the outcome the change is intended to improve.
- **Guardrails:** quality, cost, time, false-positive rate, user harm, or other relevant constraints.
- **Observation window:** long enough for the outcome to be meaningful.
- **Decision threshold:** pre-defined rule for adoption, iteration, or rejection.
- **Stop condition:** when to stop because of cost, risk, or futility.

Prefer metrics closer to actual value creation, such as validated problem frequency, qualified conversations, willingness to pay, paid conversion, activation, retention, or revenue, when the experiment can validly measure them.

Do not use the number of papers found, prompts executed, agents launched, ideas generated, or reports written as a proxy for product success.

For small samples, report uncertainty and avoid overstating statistical significance. A directional pilot can justify a larger test; it does not automatically establish a general effect.

---

## 10. Required report format

Each review report should contain these sections.

### 10.1 Metadata

- Review title and date.
- Review mode: monthly or quarterly.
- Search cut-off date and time window.
- Product Lab Git SHA / revision.
- Reviewer / agent and tools used.
- Previous report reviewed.

### 10.2 Executive summary

- What materially changed in the evidence landscape?
- Which existing PLS practices gained support or were challenged?
- The top recommendations, or an explicit “no change recommended”.
- Main limitations of the review.

### 10.3 Repository baseline

List the actual PLS documents and implementation areas inspected. Identify gaps between documented process and implemented behavior. Do not infer implementation from documentation alone.

### 10.4 Search coverage

Include databases, exact search queries, date filters, number of candidates inspected where available, selection approach, and access limitations.

### 10.5 Paper evidence table

| Paper | Year / status | arXiv / DOI | PLS area | Main finding | Study strength | Inspection level | Limitations |
|---|---|---|---|---|---|---|---|

Use direct links to the primary paper and the published version when available.

### 10.6 Synthesis by capability

Summarize the strongest findings under the research areas in Section 2. Compare competing methods and explain where evidence agrees, conflicts, or remains insufficient.

### 10.7 PLS gap analysis

For each finding, mark Supports / Refines / Challenges / Adds / Not transferable. Cite the exact PLS artifact or behavior.

### 10.8 Recommendations

Use the required recommendation format in Section 8. Include no more than three high-priority proposals.

### 10.9 Deferred and rejected ideas

Record potentially interesting methods that were not recommended and why: weak evidence, poor transferability, high cost, duplication, or no demonstrated PLS problem.

### 10.10 Open questions and next review

List unresolved evidence gaps, topics to monitor, and what would trigger an earlier re-review.

---

## 11. Source and citation rules

- Link to the original arXiv record and the paper PDF or HTML where available.
- Link to the publisher version / DOI when one exists.
- Link to official code and datasets, not third-party summaries, when possible.
- Verify title, authors, version, date, venue, and DOI before citing.
- Attribute numerical claims to the exact paper and preserve the evaluation context.
- Do not quote or paraphrase beyond applicable source limits.
- Never fabricate a DOI, result, sample size, benchmark, or publication status.
- If the source cannot be opened, say so and lower the inspection level.
- Use secondary sources for discovery or context, not as substitutes for a primary paper when the claim depends on the study itself.

---

## 12. Independence, uncertainty, and reviewer discipline

The reviewer must challenge its own preferred recommendations.

For every high-priority proposal, actively search for:

- a competing method;
- a failed or null result;
- a replication or critique;
- an evaluation limitation;
- a plausible reason the result would not transfer to PLS.

If two papers disagree, describe the difference in settings, definitions, datasets, and metrics. Do not resolve disagreement by simply choosing the newer paper.

Separate facts, interpretations, and hypotheses throughout the report. State confidence qualitatively and explain why.

Agent agreement is not independent scientific replication. If multiple agents are used, give them independent search or appraisal tasks and preserve disagreements for human review.

---

## 13. Governance and prohibited actions

A research review may create or update its research report and an explicitly designated research index. It must not:

- modify Product Lifecycle stages;
- change PLS scoring rules, policies, prompts, or templates;
- modify source code or runtime configuration;
- create GitHub issues, pull requests, branches, or commits;
- install dependencies or paid tools;
- deploy or trigger external side effects.

Any implementation proposal must be approved by the owner and then handled through the existing PLS experiment / implementation / review process.

The review is complete when the report is saved, sources and limitations are traceable, and each recommendation has a testable decision path—or the report explicitly concludes that no change is justified.

---

## 14. Quality checklist

Before submitting a report, verify:

- [ ] The current PLS repository and prior review reports were inspected.
- [ ] The report records the Git revision and search cut-off date.
- [ ] Searches covered the relevant capability areas with multiple query formulations.
- [ ] Screening decisions and access limitations are transparent.
- [ ] Important papers were assessed from full text where accessible.
- [ ] Inspection level and study strength are recorded separately.
- [ ] Publication status and SOTA claims were checked.
- [ ] Findings are compared with existing PLS behavior.
- [ ] Counter-evidence and limitations are included.
- [ ] No more than three high-priority recommendations are made.
- [ ] Each recommendation has a falsifiable experiment and decision rule.
- [ ] The report separates facts, interpretation, and hypotheses.
- [ ] No implementation or unapproved repository changes were made.

**The desired outcome is not a large bibliography. It is a small number of well-supported, low-cost experiments that can improve Product Lab's ability to find valuable problems, make better decisions, and learn faster.**
