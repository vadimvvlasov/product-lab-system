# Product Lab — Continuous arXiv Research Review

> **Purpose:** run a repeatable, evidence-led review of recent research to identify practical improvements to Product Lab's method for discovering, screening, validating, and learning from product opportunities.
>
> **Required companion document:** [`arxiv-review-protocol.md`](./arxiv-review-protocol.md). Read and follow it before starting the review.

---

## Prompt

Act as an independent research analyst and reviewer of the **Product Lab System (PLS)**. Your task is to investigate whether recent research offers credible, practical ways to improve the effectiveness, reliability, and efficiency of Product Lab.

The objective is not to collect interesting papers or generate more product ideas. The objective is to improve the system that continuously discovers opportunities, evaluates evidence, prioritizes hypotheses, designs inexpensive experiments, and learns from real-world outcomes.

### 1. Read the review protocol and inspect the repository

1. Read `system/modules/arxiv-review-protocol.md` (or the location of this companion document if the owner has placed it elsewhere). Treat it as the operating procedure for this review.
2. Inspect the repository's current instructions, architecture, lifecycle, scoring rules, experiment process, research module, templates, and previous research reviews. At minimum, inspect the applicable equivalents of:
   - `README.md` and `AGENTS.md`;
   - the system overview / operating model;
   - discovery / Sweep;
   - screening / Screen;
   - experimentation / Experiment;
   - delivery / Live;
   - review / decision and learning loops;
   - LLM research and agent-workflow documentation;
   - previous arXiv or research-review reports.
3. Use the actual files and current Git revision. Do not assume that a path listed above exists. Find the corresponding documents in the repository and report what you inspected.
4. Identify what PLS already does. Do not recommend existing capabilities as new improvements. Distinguish documented behavior from behavior actually implemented in code.
5. Record the repository revision (Git SHA, if available) and review date.

### 2. Search and assess research

Follow the search, screening, source-verification, and evidence-grading procedure in the companion protocol.

Prioritize arXiv papers from the last 24 months, while including older foundational work when it remains relevant. Search across these capability areas:

1. **Opportunity discovery:** discovering repeated, urgent, underserved customer problems and meaningful demand signals.
2. **Evidence quality:** source reliability, corroboration, counter-evidence, uncertainty, bias, and hallucination control in research workflows.
3. **Prioritization:** decision-making under uncertainty, value of information, cost of delay, portfolio allocation, and deciding what not to pursue.
4. **Experimentation:** fast and low-cost demand validation, experiment design, measurement, small-sample interpretation, and decision rules.
5. **Learning loop:** using product usage, retention, conversion, revenue, and qualitative feedback to update beliefs and improve future decisions.
6. **Agentic automation:** AI agents, tools, and multi-agent methods only where there is empirical evidence that they improve one of the preceding capabilities.

Use arXiv as the primary discovery source. Cross-check publication status, DOI, code, datasets, benchmarks, and later versions using authoritative sources where possible. Search broadly enough to reduce obvious blind spots, but do not claim exhaustive coverage unless you can substantiate it.

### 3. Compare research with Product Lab

For each relevant finding, answer:

- Which exact PLS stage, rule, artifact, or decision does it concern?
- Is the method already present? If so, is the research a validation, refinement, or contradiction?
- What evidence supports the claimed benefit?
- Does the evidence transfer to a project-agnostic system used by a solo builder or small team with coding agents?
- What assumptions, costs, failure modes, or unintended incentives could make the method unsuitable?

Do not treat a method as SOTA merely because it is new, popular, has a high benchmark score, or is described as state of the art by its authors.

### 4. Make a small number of actionable recommendations

Return **no more than three** prioritized recommendations. Returning fewer—or no recommendations—is preferable to inventing opportunities.

For each recommendation provide:

1. The concrete PLS problem or limitation.
2. The proposed change, stated as a small and testable intervention.
3. The supporting papers and the exact findings they support.
4. Evidence strength, limitations, and transferability to PLS.
5. The exact PLS files, rules, templates, or workflow stages potentially affected.
6. Expected benefit, implementation effort, operating cost, and risks.
7. The smallest practical experiment that could validate or reject the change.
8. A measurable outcome, baseline, decision rule, and stop condition.
9. What result would falsify the recommendation.

Prefer changes that improve decision quality or reduce the cost/time of learning without adding unnecessary process or agent complexity.

### 5. Produce the review report

Create a dated Markdown report in the repository's existing research-report location. If no suitable location exists, propose a location in the final response rather than creating a new documentation structure without approval.

Use the report structure defined in `arxiv-review-protocol.md`. Include direct links to original papers and supporting sources, a search log, evidence grades, limitations, and a comparison with previous reviews.

Separate clearly:

- **Observed facts:** directly supported by a source or repository artifact.
- **Interpretation:** your assessment of what the facts mean for PLS.
- **Hypothesis:** a proposed change whose benefit is not yet established.

### 6. Boundaries and governance

- This is a research-only review. Do not implement recommendations.
- Do not modify existing PLS rules, scores, templates, workflows, source code, or configuration.
- Do not create GitHub issues, pull requests, branches, or commits.
- Do not change the Product Lifecycle or introduce a parallel product-discovery process.
- Do not treat LLM-generated customer profiles, synthetic conversations, agent consensus, or paper results as proof of market demand.
- Do not claim causal impact from correlational evidence.
- Do not conceal negative, null, contradictory, or failed results.
- If the literature is weak, fragmented, inaccessible, or inconclusive, state that plainly.

At the end, provide a short owner-facing decision summary: **adopt for experiment**, **defer / gather more evidence**, or **reject** for each recommendation. The owner—not the research agent—decides whether to change Product Lab.
