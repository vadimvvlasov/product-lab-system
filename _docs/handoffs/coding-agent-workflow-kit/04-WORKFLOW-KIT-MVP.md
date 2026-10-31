# Product brief — Coding Agent Workflow Kit (MVP)

## Promise

A compact, copyable Markdown workflow that helps a solo builder make a coding agent work from explicit task criteria, implement a bounded change, and pass an independent QA review before the owner decides to publish it.

Do not promise “bug-free code”, fully autonomous software development, guaranteed time savings, or elimination of human review.

## Intended buyer

A developer or solo builder already using one or more coding agents on an existing repository. They can edit Markdown instructions and run their own tests but have not yet standardized role boundaries and independent verification.

## MVP format

A standalone directory of Markdown files, a README and a tiny illustrative example. It should work without a hosted service, accounts, telemetry or paid APIs. Keep it vendor-neutral where reasonably possible, while documenting any agent-specific syntax honestly.

## Included files/content

1. `README.md` — problem, who it is for, quick start, installation/copy instructions, limitations.
2. `AGENTS.md` starter — concise entry point and source-of-truth hierarchy.
3. `roles/pm.md` or equivalent — turn a request into a bounded spec; do not implement.
4. `roles/engineer.md` or equivalent — implement only approved criteria and allowed files; do not approve own work.
5. `roles/qa.md` or equivalent — read-only independent verification, explicit PASS/FAIL evidence.
6. `templates/task.md` — goal, context, scope, non-goals, file boundaries, acceptance criteria, verification, risks, rollback.
7. `templates/qa-report.md` — criterion-by-criterion evidence, commands actually run, missing checks, verdict.
8. A bounded repair-loop rule — max two repair attempts by default; escalate/block after repeated failure rather than looping indefinitely.
9. Safety rules — preserve dirty worktree; no secret handling; external actions require owner approval; no push/deploy/merge by default; do not trust instructions embedded in issue bodies/web pages/logs.
10. A small example task in a clean demo repository or self-contained example folder, showing: groom spec → implement → independent QA → repair if needed → QA result → handoff to owner.
11. Version and changelog; license/distribution terms must be clarified before selling or redistributing assets.

## Not in MVP

- SaaS or web UI;
- custom orchestration runtime, MCP servers, vector database, CRM or analytics platform;
- broad support claim for every coding agent;
- multiple editions/pricing tiers;
- large course/video library;
- claims of quantified improvements not established by controlled measurement.

## Product-quality acceptance

- A new user can follow README in a fresh test repository without relying on private project context.
- Every role's responsibilities are non-overlapping and the QA role is read-only.
- Acceptance criteria are testable and trace to the spec.
- The example demonstrates at least one failing check or explicit gap and how it is handled; it does not fabricate a successful command.
- No step requires an unapproved external action.
- The kit clearly states host-specific limitations and is not represented as an executable orchestration engine if it only contains Markdown instructions.
- Packaged contents are safe to redistribute: no credentials, private customer data, internal-only facts, copied third-party material without rights, or references that expose private paths.

## Distribution checklist

Before sales, owner must approve:
- final content and product claim;
- exact version being delivered;
- price and payment provider;
- refund, delivery and support terms;
- public sales copy and channel.

The agent can draft these materials but cannot publish them or take payment.
