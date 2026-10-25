# Product Lab System — Agent Entry Point

Before changing this repository, read `_docs/process.md` and the relevant role in `_docs/team/roles.md`.

## Source of truth
- `system/00-model.md` is the canonical source for shared stages, statuses, gates, evidence levels, and terminology. Do not redefine them elsewhere.
- `system/` defines methodology and rules.
- `templates/` defines fields and checklists.
- `projects/` contains project-specific records and instances.
- Do not copy field lists into `system/` when they belong in a template; link to the canonical template instead.

## Working rules
- Process one Product Lab review issue at a time.
- Use GitHub Issues labelled `product-lab-review` as the only active backlog for this workflow. Do not create a parallel local backlog.
- Follow `_docs/process.md`; use the role contracts in `_docs/team/roles.md`.
- Preserve unrelated and pre-existing worktree changes. Never reset, stash, overwrite, or clean them.
- Do not silently widen scope or change acceptance criteria during implementation.
- QA is independent and read-only. An issue is not implementation-complete without QA `PASS` evidence.
- Never claim a command/test ran unless it actually ran. Do not invent evidence, user outcomes, or citations.
- Commit all in-scope changes on the issue branch before independent QA. After QA returns a verdict, add an issue comment with the verdict, evidence, reviewed SHA, and limitations. Do not merge, tag, deploy, force-push, or push changes that lack explicit owner approval for that specific change set.
- An issue may be closed only after acceptance criteria are verified, independent QA returns `PASS`, the implementation commit is pushed to the remote repository, and the owner approves closure. Record the reviewed commit SHA and the QA verdict in the issue before closing it. Issues blocked on an owner decision stay open until that decision is recorded.
- If subagents or resumable goal loops are unavailable, say so and use the safest available fallback. Do not pretend an unavailable capability exists.
