# Graph Engine — Current Status and Acceptance Checklist

**Status:** Implemented through Stage 7 with mock executors. Stage 8 real
adapters are out of scope. Independent QA is pending.

**Date:** 2026-11-01  
**Branch:** `issue/17-graph-engine-integrity`  
**Base:** `feat/graph-engine-stages-5-8` (not `main`; the Stage 5-6 code under
repair is not on `main`)  
**Code under test:** branch tip (QA records the reviewed SHA in issue #17)  
**Version:** 0.1.0

This is the only current status document. It replaces the earlier
`graph-engine-qa-handoff.md`, which described a branch and test count that no
longer existed.

---

## What works

- Workflow YAML parsing, schema/reference/DAG validation
- Immutable workflow and executor-config snapshots with hash verification
- Atomic run state persistence and artifact management
- Executor registry with a deterministic mock adapter
- Sequential run controller: dependencies, retries with feedback, verification,
  artifact publication, blocking on failed dependencies, cancellation, run timeout
- Command, agent, and human verification methods
- Approval pause/resume at `before_execution` and `before_publish`
- Recovery and reconciliation of interrupted runs, including artifact size and
  checksum checks
- Public API and CLI: `validate`, `run`, `status`, `resume`, `approve`, `reject`,
  `cancel`
- Structured JSONL events

## What does not work yet

- Independent tasks do not execute in parallel. The controller is sequential;
  `max_concurrency` only caps how many tasks are selected per iteration.
- Only the `mock` adapter exists. `command` and `opencode` executor adapters are
  Stage 8 work.
- `metrics.json` is not written. Usage and estimated cost from executor results
  are not persisted.
- Per-task durations are not recorded. `run.json` stores total active execution
  seconds only.
- Human approval is file-based. The engine trusts the run directory; this is not
  a security boundary against a hostile executor.
- Command verification is not a sandbox. Workflow commands are trusted input.

---

## Test evidence

Command:

```bash
python3 -m pytest tests/graph_engine
```

Result at the branch tip: **144 passed** (0 failed, 0 skipped).

| Area | Tests |
|---|---:|
| `unit/` (parser, schema, references, DAG) | 25 |
| `persistence/` | 24 |
| `artifacts/` | 7 |
| `executors/` | 8 |
| `execution/` (controller E2E) | 11 |
| `scheduler/` | 4 |
| `verification/` | 25 |
| `recovery/` | 31 |
| `cli/` | 5 |
| `test_api.py` | 4 |
| **Total** | **144** |

The end-to-end tests use real `RunStore`, `RunLayout`, `ExecutorRegistry`, and
the run controller. They cover run → verify → retry → complete, approval
pause/resume, cancellation, timeout, and recovery.

---

## Acceptance criteria

Legend: PASS = implemented and covered by tests; PARTIAL = implemented with a
documented limit; DEFERRED = not implemented.

### A. Architecture

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| A1 | Separate logical module | PASS | `graph_engine/` package |
| A2 | No imports from `product_lifecycle` | PASS | No such imports in `graph_engine/` or its tests |
| A3 | Stable interface for Product Lifecycle | PASS | `graph_engine.api` |
| A4 | No product-specific business logic | PASS | Generic orchestration only |

### B. Workflow validation

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| B1 | Load and validate YAML | PASS | Parser tests |
| B2 | Reject invalid schemas | PASS | Schema tests |
| B3 | Reject missing references | PASS | Reference tests |
| B4 | Detect and reject cycles | PASS | DAG tests |
| B5 | Deterministic executor resolution | PASS | Registry tests |
| B6 | Invalid workflows cannot start | PASS | `create_run()` validates first |

### C. Execution

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| C1 | Tasks execute in DAG order | PASS | Controller E2E |
| C2 | Independent tasks run in parallel | DEFERRED | Sequential controller |
| C3 | `max_concurrency` enforced | PASS | Readiness caps selected tasks |
| C4 | Failed branch does not stop independent branches | PASS | Controller continues until no ready tasks |
| C5 | Downstream blocked after dependency failure | PASS | Readiness propagates blocking |

### D. Verification and retries

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| D1 | Mandatory completion criteria enforced | PASS | Verification engine |
| D2 | Command, agent, human methods work | PASS | Verifier tests |
| D3 | Every attempt persisted | PASS | `tasks/<id>/attempts/NNN.json` |
| D4 | Retry feedback reaches next attempt | PASS | Retry feedback tests |
| D5 | Retry limits enforced | PASS | Controller tests |
| D6 | Exhausted tasks become blocked | PASS | Controller tests |

### E. Data and artifacts

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| E1 | Inputs explicitly declared | PASS | Schema validation |
| E2 | Undeclared outputs are not passed | PASS | Context builder |
| E3 | Required artifacts validated | PASS | Artifact manager tests |
| E4 | Publish only after verification | PASS | Controller E2E |
| E5 | Checksums and provenance | PASS | `ArtifactRecord`; checksums persisted in `TaskState` |

### F. Persistence and recovery

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| F1 | Run state stored in JSON | PASS | `RunState` |
| F2 | Workflow templates stored in YAML | PASS | Snapshot |
| F3 | Atomic writes | PASS | fsync + `os.replace` |
| F4 | Immutable workflow snapshot | PASS | Hash verification |
| F5 | Completed verified tasks reused | PASS | Recovery tests; size and checksum checked |
| F6 | Incomplete attempts never reused | PASS | Recovery tests |
| F7 | Unsafe side effects not repeated | PASS | Recovery blocks unsafe tasks |

### G. Agent collaboration

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| G1 | Common executor interface | PASS | `Executor` protocol |
| G2 | Fresh context per task and retry | PASS | Context built per attempt |
| G3 | Context only declared inputs and references | PASS | Context builder |
| G4 | Implementer and reviewer independent | PASS | Agent verifier uses its own configured executor |
| G5 | Reviewer feedback used in next attempt | PASS | Retry feedback tests |

### H. Safety

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| H1 | Human approval can be required per task | PASS | Approval gate tests |
| H2 | Executors cannot approve their own actions | PASS | Decisions come from `ApprovalStore`; no executor approval API |
| H3 | Push, merge, deploy need owner approval | PASS | Process rule in `AGENTS.md`, not engine code |
| H4 | Execution limits enforced | PASS | Retries, timeout, cancellation |

### I. Observability

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| I1 | Structured JSONL events | PASS | `logs/events.jsonl` |
| I2 | Per-run metrics persisted | DEFERRED | `metrics.json` is not written |
| I3 | Durations and retry counts available | PARTIAL | Retry counts and total active seconds; no per-task duration |
| I4 | Verification results and failure reasons recorded | PASS | Attempt records and events |
| I5 | Usage and estimated cost recorded when available | DEFERRED | `Usage` is returned but not persisted |
| I6 | Missing usage represented honestly | PARTIAL | Nothing is claimed; usage is simply absent |

### J. CLI and quality

| AC | Requirement | Status | Evidence |
|---|---|---|---|
| J1 | `validate`, `run`, `status`, `resume`, `cancel` work | PASS | CLI tests; `approve` and `reject` also work |
| J2 | Unit tests pass | PASS | 25 unit tests |
| J3 | Scheduler tests pass | PASS | 4 tests |
| J4 | Recovery tests pass | PASS | 31 tests |
| J5 | End-to-end test passes | PASS | Controller, API, and CLI E2E |
| J6 | Documentation explains format and operations | PASS | This document |

**Overall:** Stages 1-7 are implemented for mock executors. Full acceptance is
blocked by C2 (parallel execution), I2/I5 (metrics and cost persistence), and
Stage 8 real adapters. Those are out of scope for issue #17.

---

## CLI examples

The fixture below is runnable with the mock executor:

```bash
python3 -m graph_engine.cli.main validate \
  tests/graph_engine/fixtures/workflows/valid-simple.yaml

python3 -m graph_engine.cli.main run \
  tests/graph_engine/fixtures/workflows/valid-simple.yaml \
  --runs-dir /tmp/pls-runs

python3 -m graph_engine.cli.main status /tmp/pls-runs/<run-id>
```

Exit codes: `0` completed, `1` error, `2` usage, `3` awaiting approval or
completed with blockers, `4` invalid workflow.

Approval flow:

```bash
python3 -m graph_engine.cli.main approve <run-dir> <task-id> --approver owner
python3 -m graph_engine.cli.main resume <run-dir>
```

---

## QA procedure

QA is independent and read-only. Review the exact branch-tip SHA in a separate
worktree with `git status --short` empty.

```bash
git worktree add /tmp/opencode/pls-qa <sha>
cd /tmp/opencode/pls-qa
python3 -m pytest tests/graph_engine
python3 -m graph_engine.cli.main validate \
  tests/graph_engine/fixtures/workflows/valid-simple.yaml
```

Record in issue #17: verdict, evidence, reviewed SHA, and limitations. Do not
push, merge, tag, deploy, or close the issue without explicit owner approval.

---

## Sign-off

**Implementer:** Coding agent  
**QA status:** Pending independent review  
**Owner approval:** Pending  
**Push/merge:** Not performed
