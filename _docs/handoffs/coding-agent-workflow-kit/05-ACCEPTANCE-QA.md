# Acceptance criteria and independent QA

## A. Product Lab System change (only if audit confirms a real gap)

- [ ] Auditor references actual current source paths/headings and compares them with the proposed flow.
- [ ] The team explains why filling existing templates/rules is insufficient.
- [ ] Any change is limited to a worked example or the smallest necessary documented rule; no duplicate field schema/template is added without strong evidence.
- [ ] `system/00-model.md` remains the canonical source for stages, statuses, gates, IDs, and L0–L5 terms.
- [ ] Existing `templates/idea.md`, `templates/experiment-s.md`, `templates/experiment.md`, `system/20-screen.md`, `system/30-experiment.md` and `system/40-deliver.md` remain cross-file consistent.
- [ ] The example distinguishes views/likes/downloads/waitlist from confirmed payment/L5.
- [ ] The example defines qualified exposure, attribution, primary metric, timebox, review condition and stop rule before launch.
- [ ] It does not weaken payment, owner-approval, stop, or scale constraints.
- [ ] QA is independent/read-only and states evidence, actual checks, limitations and PASS/FAIL.

If no real gap exists, acceptance is a documented `no change needed` decision with evidence, not an unnecessary code/document change.

## B. Commercial experiment records

- [ ] Existing project slug, record IDs, registry links and active experiment slots were checked before creating records.
- [ ] Notes use the current canonical templates and accepted frontmatter fields.
- [ ] Evidence includes real sources, date and quotation/extract where required; no invented demand or customer responses.
- [ ] Score/confidence are set only after the model's required screen; a proposed price is explicitly labelled hypothesis.
- [ ] `budget_until` and `budget_signal` exist before idea status becomes `testing`.
- [ ] S experiment includes all required G2 data; `method: post`, `post_goal: pricing` is used only if still appropriate under the current model.
- [ ] For a post, the current `exposure_floor` and definition are fixed before launch and are not reduced after observing results.
- [ ] `timebox_hours`, review condition, `stop_rule` and `owner` are set before `ready/live`.
- [ ] One campaign identifier/UTM path is specified; metric numerator and denominator are explicit.
- [ ] Gross revenue, direct cash cost, hours and refunds are separate; blank hours are not treated as zero.
- [ ] The experiment includes decisions for insufficient exposure, no conversion, confirmed payment and refund.

## C. Product kit

- [ ] MVP files are standalone and work in a clean demo repository with no private project context.
- [ ] User problem and promise are concrete and do not overclaim.
- [ ] PM/spec and Engineer responsibilities do not overlap; QA is explicitly read-only.
- [ ] Acceptance criteria can be evaluated from a diff and observable test output.
- [ ] Safety/approval boundaries are explicit.
- [ ] The example and documentation are consistent with actual commands/capabilities; no unrun checks are claimed.
- [ ] Redistribution/licensing status is checked before public sale.
- [ ] Product can actually be delivered before any customer is charged.

## D. Operational safety

- [ ] Initial and final `git status --short` recorded.
- [ ] Pre-existing/unrelated work is unchanged.
- [ ] Only relevant paths are staged; pathspec is explicit.
- [ ] No post, DM, checkout, payment, deploy, push, merge, force-push or issue closure occurred without the required approval/state.
- [ ] All subagent use is accurately reported; if separate contexts were unavailable, QA independence limitation is disclosed.
- [ ] No issue is closed while the commit is only local.
