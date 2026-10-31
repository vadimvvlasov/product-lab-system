# Graph Engine Stage 0 — Owner Decisions

**Date:** 2026-10-31
**Status:** ✅ Approved, Stage 1 unblocked
**Branch:** `feat/graph-engine`

## Must-decide items (blocking)

| ID | Decision | Rationale |
|---|---|---|
| C1 | Engine in this repository | Recommended: single QA surface, one issue flow, matches spec intent |
| C2 | Public API + stub consumer for A3 | Proves contract without fake lifecycle package |
| C3 | Research Loop workflow deferred to post-MVP | Reduces Stage 8 scope; compatibility proven with mock E2E only |
| C7 | Add `awaiting_approval` run status + `approve`/`reject` CLI commands | Required for human approval gates |
| C11 | Owner-directed branch `feat/graph-engine` | Owner-directed architectural work; no GitHub issue required |
| Schema extensions | Accept all: `approval_point`, `max_retries` override, `timeout_minutes`, `side_effects`, `idempotency_key`, `context` block | Necessary for safety, retry control, and reproducible context |

## Recommended defaults (non-blocking)

| ID | Decision |
|---|---|
| C4 | `runs/` gitignored at repo root, configurable via `--runs-dir`/`PLS_RUNS_DIR` | ✅ Accept |
| C5 | Qualify `task.status`/`run.status`; keep engine docs separate from `system/00-model.md` | ✅ Accept |
| C6 | Research Loop evidence scale named `evidence_depth` (A/F/C/E), separate from PLS confidence/L0–L5 | ✅ Accept (deferred with C3) |
| C8 | Implementer-reviewer repair loop as agent verification, not DAG cycle | ✅ Accept |
| C9 | `blocked` vs `failed` mapping per §4.2 of plan | ✅ Accept |
| C10 | Active-execution timeout accounting; `resume` requires explicit `--extend-run-timeout-minutes` | ✅ Accept |
| C12 | `env:NAME` executor config references; reject literal secrets | ✅ Accept |
| C13 | Generic `CommandExecutor` + OpenCode preset for Stage 8 | ✅ Accept |
| C14 | Local pytest gate; CI/license as separate owner decisions | ✅ Accept |

## Implementation protocol

- **Branch:** `feat/graph-engine`
- **Commit strategy:** Thematic commits per logical component (not one-per-file); group related modules
- **Commit prefix:** `feat(graph):`
- **Stages:** 1–8, checkpoint commits at meaningful boundaries within each stage
- **Execution:** Work through all stages 1-8 continuously (Option 3)
- **Merge:** Agent merges by owner command after QA PASS (Variant B)
- **No external actions:** no push, merge (without command), deploy, tag, or issue operations
- **QA:** after Stage 8, create independent QA handoff; owner reviews verdict, then commands merge
- **Preservation:** untracked files (`_docs/arxiv-review-2026-10-31.md`, `_docs/handoffs/`, `system/modules/arxiv-review-*`) remain untouched

## Stage 0 exit

✅ All must-decide items recorded. Stage 1 (core models + validation) may proceed.
