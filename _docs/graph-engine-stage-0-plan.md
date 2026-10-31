# Graph Engine — Stage 0 Repository Inspection and Implementation Plan

**Status:** Stage 0 deliverable — planning only. No engine code has been written.
**Date:** 2026-10-31
**Specification:** [`_docs/graph-engine-implementation-spec.md`](graph-engine-implementation-spec.md)
**Repository:** `/home/vadim/work/Obsidian/product-lab-system`

---

## 1. Repository baseline

Recorded before any change:

- Branch: `main`
- HEAD: `e040929` (`docs(agents): add Claude agent reference stub`)
- `git status --short`:
  - `?? _docs/graph-engine-implementation-spec.md`
  - `?? _docs/handoffs/`
- Existing worktree not touched: `/tmp/opencode/pls-cawk` (prunable, branch
  `project/coding-agent-workflow-kit`, commit `29a9d60`).
- No commits, pushes, merges, tags, deployments, or issue changes were made.

### 1.1 What the repository actually contains

The repository is an Obsidian methodology vault, not an application codebase.

| Expected by the spec | Actual state |
|---|---|
| Python package layout (`product_lab_system/`) | No Python package, no `pyproject.toml`, no `setup.py` |
| Existing CLI | None |
| Existing configuration system | None |
| Existing logging system | None |
| Existing test suite / test runner configuration | None |
| Existing CI | None (no `.github/workflows/`) |
| `product_lifecycle/` module | None; lifecycle is documentation in `system/*.md` |
| `research/` module | None; only `system/modules/llm-research.md` methodology |
| `workflows/` directory | None |
| `runs/` runtime directory | None |

Available local tooling (observed, not a project dependency):

- Python 3.14.4
- PyYAML 6.0.3
- pytest 9.0.2
- uv 0.9.22
- OpenCode CLI 2.1.4
- `gh` 2.98.0

The only existing Python code is a small example on the
`project/coding-agent-workflow-kit` branch
(`projects/coding-agent-workflow-kit/product/examples/demo-task/`). It is not on
`main`, is a documentation example rather than a library, and must not become an
engine dependency. The only other executable asset is the vendored Obsidian
plugin `.obsidian/plugins/mermaid-beauty/main.js`, which is unrelated.

### 1.2 Consequence

There are no existing code conventions to adapt to. The spec says the package
layout "may be adapted to the existing repository conventions"; in this
repository that sentence currently has no referent. The first decision is
therefore structural, not technical: whether the engine lives in this vault or
in a separate code repository.

---

## 2. Conflicts, risks, and owner decisions

These must be resolved before Stage 1. They are presented as conflicts, not as
silent design changes.

### C1 — No codebase exists in the repository (blocking)

**Evidence:** repository file listing; no `.py`, `pyproject.toml`, tests, or CI.
**Impact:** every build, test, and packaging convention must be introduced.
**Options:**

- **A (recommended):** add a top-level Python package to this repository,
  keep the vault and the engine in one review/QA surface.
- **B:** create a separate `pls-graph-engine` repository and keep this vault
  documentation-only. This keeps the Obsidian vault clean but adds a second
  repository, second issue/QA flow, and cross-repo versioning.

**Recommendation:** A, with runtime state gitignored and engine docs kept under
`_docs/graph-engine/`. This matches the spec's "inside PLS" intent and keeps
independent QA on one tree. If the owner wants the vault to stay code-free,
choose B and the plan's paths move to the new repository unchanged.

### C2 — "Product Lifecycle can invoke it" cannot be implemented literally (blocking interpretation)

**Evidence:** `system/00-model.md` defines the lifecycle as methodology; there is
no `product_lifecycle` module or stable API.
**Impact:** acceptance A3 cannot be satisfied by a real integration in this
repository today.
**Recommended interpretation:** define a stable public Python API
(`graph_engine.api`) plus the CLI, and prove the contract with a test-only stub
consumer that imports only that API. The real lifecycle adopts it when it gains
code. This satisfies the architectural intent without inventing a fake
`product_lifecycle` package.
**Alternative:** mark A3 deferred until a lifecycle implementation exists. That
would make the MVP acceptance checklist incomplete.

### C3 — Research Loop is not implemented (scope decision)

**Evidence:** only `system/modules/llm-research.md` exists; no Research Loop
workflow or code.
**Impact:** spec §18 says Research Loop must be implemented as a normal workflow,
but the acceptance list does not name it explicitly.
**Recommended scope:** ship one declarative `workflows/research-loop/` workflow
plus a policy document for evidence depth, using the same engine with no special
logic. Do not build a research agent adapter for the MVP. Treat the workflow as
a compatibility proof, not as a new engine feature.
**Alternative:** defer the workflow YAML to a follow-up and prove compatibility
only with the mock E2E workflow. This keeps Stage 8 smaller but leaves §18
partially unproven.

### C4 — Runtime state inside an Obsidian vault (blocking hygiene)

**Evidence:** the repository root is the vault; `.gitignore` currently covers
Obsidian runtime files only.
**Impact:** `runs/`, `.venv/`, caches, and test output would pollute the vault
and git history.
**Recommendation:** default runs directory `./runs`, configurable with
`--runs-dir`/`PLS_RUNS_DIR`; add `runs/`, `.venv/`, `__pycache__/`,
`.pytest_cache/`, and `*.pyc` to `.gitignore`. Do not modify `.obsidian/`
settings by default; the owner can exclude the code folders from Obsidian
search if desired.

### C5 — Status vocabulary collision (documentation risk)

**Evidence:** PLS uses `status: draft/ready/building/live/review/closed` for
experiments and `inbox/researching/screened/testing/scaling/parked/killed` for
ideas (`system/00-model.md`). The engine uses `ready`, `running`, `verifying`,
`completed`, `blocked`, etc.
**Impact:** a reader can confuse `experiment.status = ready` with
`task.status = ready`.
**Recommendation:** always qualify engine fields as `task.status` and
`run.status`; keep engine statuses in `_docs/graph-engine/`, never in
`system/00-model.md`. The engine does not read or write PLS note statuses.

### C6 — Evidence-level namespace collision (semantic risk)

**Evidence:** spec §18 proposes evidence levels **A — Abstract, F — Full text,
C — Code, E — Experiment**. PLS already uses confidence **A/B/C** and signal
ladder **L0–L5** (`system/00-model.md`).
**Impact:** "A" and "C" would mean different things in the same document set.
**Recommendation:** call the spec's scale `evidence_depth` with values
`A/F/C/E`, and state explicitly that it is not PLS `confidence` and not the
`L0–L5` signal ladder. This belongs to Research Loop workflow policy, not to the
engine. Do not add it to `system/00-model.md` without a separate methodology
change.

### C7 — Human approval has no clean terminal-state model (blocking design)

**Evidence:** spec §8.4 defines only `completed`, `completed_with_blockers`, and
`failed` run states, while §12 and §16 require pausing for approval. A paused run
is not finished, yet none of the three states describes it honestly.
**Recommendation:** add a non-terminal `run.status = awaiting_approval`, keep the
task in `verifying` (approval point `before_publish`) or `ready`
(`before_execution`), persist an approval request, and exit the process. Add
`pls graph approve|reject` commands; `resume` continues after a decision.
`completed_with_blockers` is not used for an approval pause because that would
misreport a normal gate as a failure.
**Impact:** one new run status and two CLI commands beyond the spec's suggested
five. This requires explicit owner approval.

### C8 — Static DAG vs iterative implementer-reviewer repair loop (design)

**Evidence:** spec §4 forbids cycles and dynamic edges; §13.2 requires the
implementer to fix reviewer findings and submit another attempt for review.
**Impact:** a literal `implementation -> review -> implementation` edge is a
cycle and cannot be expressed.
**Recommended resolution:** implement the repair loop as an **agent verification
criterion on the implementation task**, not as a cycle. The verifier is a separate
executor run with a fresh context; its findings become retry feedback for the next
implementation attempt. A separate downstream `review` task remains valid for a
one-shot independent review artifact, but it is not the repair loop.
**Alternative:** allow a review task to block and require a new run. That loses
the retry accounting the spec asks for.

### C9 — `failed` vs `blocked` task semantics are underspecified (design)

**Evidence:** the state diagram shows `running -> failed`; §7 says exhausted
retries end in `blocked`; §6 says missing approval and dependency failure are
blockers.
**Recommended mapping:**

- `blocked`: dependency failure, exhausted retry budget, approval rejection,
  missing approval, run cancellation, unsafe recovery requiring a human.
- `failed`: a non-retryable task-level error that is not one of the above
  (for example, a corrupted adapter result that cannot be retried safely).
- Run-level `failed`: orchestration/system failure, persistence failure, or run
  timeout. Ordinary task failures never make the run `failed`.

Document this table in `_docs/graph-engine/operations.md` and test every
transition.

### C10 — Run timeout semantics across pauses and resumes (design)

**Evidence:** `max_run_duration_minutes` is defined but not whether wall-clock
time spent waiting for human approval counts.
**Impact:** a two-day approval wait would instantly exhaust a 120-minute run.
**Recommendation:** measure **active execution time** (time with at least one
task running), not wall-clock time since `started_at`. Persist accumulated active
time in `run.json`. This is a documented deviation from a naive wall-clock
reading; it makes human gates usable. On timeout: stop scheduling, request
cancellation, persist, status `failed` with `error.category = run_timeout`, and
leave the run resumable. `resume` refuses to schedule further unless the owner
passes an explicit `--extend-run-timeout-minutes N`; the extension is recorded as
an event and never applied silently.

### C11 — Code work has no issue/branch lane in the current process (process blocker)

**Evidence:** `AGENTS.md` and `_docs/process.md` define `issue/<number>-<slug>`
for GitHub issues and `docs/`, `process/`, or `project/` for owner-directed work.
There is no `feat/` lane, and no issue is referenced in the request or spec.
**Impact:** Stage 1 cannot follow the repository's normal handoff/QA protocol
without either an issue or an explicit owner-directed branch convention.
**Recommendation:** the owner creates a normal GitHub issue (not necessarily
labelled `product-lab-review`, because this is not a review finding) or
explicitly authorizes a branch such as `feat/graph-engine`. Do not create a
parallel local backlog. Stage 0 itself is uncommitted planning work on `main`.

### C12 — Executor configuration may contain secrets (security)

**Evidence:** spec §5.2 shows `executors.<name>.config` and §10.2 requires an
executor configuration snapshot.
**Impact:** naively snapshotting config can persist API keys in `run.json` or
`executor_config.json`.
**Recommendation:** executor config must reference environment variables using
`env:NAME` values, never literal secrets. Validation rejects keys matching
`token|secret|password|api_key` unless the value is an `env:NAME` reference; the
snapshot stores names and hashes, not values. Document the limitation that
changing an environment variable is not detectable from the config hash.

### C13 — Real adapter contract is not defined (Stage 8 dependency)

**Evidence:** no existing OpenCode/Claude Code/Codex adapter in the repository.
OpenCode CLI 2.1.4 is available locally and supports `opencode run --format json`.
**Impact:** Stage 8 needs an exact invocation, result contract, permission model,
and a no-cost smoke path.
**Recommendation:** implement a generic `CommandExecutor` adapter that runs a
configured argv in the attempt staging directory and reads a structured
`result.json`; add an `opencode` preset that uses `opencode run --format json`.
Do not grant `--auto` permissions by default. Keep real-agent tests opt-in and
excluded from the mandatory mock suite; record the real smoke result separately.

### C14 — No CI, no license, no code QA lane (process/distribution)

**Evidence:** no `.github/workflows/`, no `LICENSE`, QA role contract is written
for methodology documents.
**Impact:** "tests pass" is a local claim only; redistribution terms are unclear.
**Recommendation:** for the MVP, local `pytest` is the gate and independent QA
records exact commands/results. Add CI only with owner approval. Do not add a
license without an owner decision; local implementation does not require one.

---

## 3. Recommended repository layout

Assuming C1 option A (engine in this repository):

```text
product-lab-system/
├── pyproject.toml                     # package metadata, pytest config
├── .gitignore                         # add runs/, .venv/, caches
├── graph_engine/
│   ├── __init__.py
│   ├── version.py
│   ├── errors.py
│   ├── api.py                         # stable public interface for lifecycle/CLI
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   ├── workflow.py
│   │   ├── run.py
│   │   ├── artifacts.py
│   │   ├── verification.py
│   │   └── transitions.py
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── yaml_loader.py
│   │   └── workflow_parser.py
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   ├── references.py
│   │   ├── dag.py
│   │   ├── executors.py
│   │   └── report.py
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── readiness.py
│   │   └── scheduler.py
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── context.py
│   │   ├── result.py
│   │   ├── lifecycle.py
│   │   ├── limits.py
│   │   └── controller.py
│   ├── executors/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── mock.py
│   │   ├── command.py                 # generic subprocess adapter (Stage 8)
│   │   └── opencode.py                # preset/wrapper (Stage 8)
│   ├── verification/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── command.py
│   │   ├── agent.py
│   │   ├── human.py
│   │   ├── feedback.py
│   │   └── runner.py
│   ├── artifacts/
│   │   ├── __init__.py
│   │   ├── paths.py
│   │   ├── metadata.py
│   │   └── manager.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── layout.py
│   │   ├── atomic.py
│   │   ├── snapshot.py
│   │   ├── run_store.py
│   │   ├── task_store.py
│   │   ├── attempt_store.py
│   │   └── lock.py
│   ├── recovery/
│   │   ├── __init__.py
│   │   ├── reconcile.py
│   │   └── recovery.py
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── events.py
│   │   └── metrics.py
│   └── cli/
│       ├── __init__.py
│       ├── main.py
│       ├── commands.py
│       └── output.py
├── tests/
│   └── graph_engine/
│       ├── conftest.py
│       ├── fake_executors.py
│       ├── fixtures/
│       │   ├── workflows/
│       │   └── projects/
│       ├── test_package_boundary.py
│       ├── unit/
│       ├── scheduler/
│       ├── execution/
│       ├── verification/
│       ├── artifacts/
│       ├── persistence/
│       ├── recovery/
│       ├── executors/
│       ├── observability/
│       ├── cli/
│       └── e2e/
├── workflows/
│   ├── examples/
│   │   ├── example-workflow.yaml
│   │   └── parallel-mock-e2e.yaml
│   └── research-loop/
│       └── monthly-review.yaml        # Stage 8, if C3 is approved
└── _docs/
    └── graph-engine/
        ├── README.md
        ├── architecture.md
        ├── workflow-format.md
        ├── operations.md
        ├── executors.md
        ├── testing.md
        └── acceptance-checklist.md
```

### 3.1 Why top-level `graph_engine/` and not `product_lab_system/graph_engine/`

- There is no `product_lab_system` package to nest inside; creating one would be a
  fake parent package.
- A top-level package makes the import boundary enforceable: `graph_engine` must
  not import `product_lifecycle`, `system`, `templates`, `projects`, or the CLI.
- `src/` layout is a valid alternative, but it adds a path convention the
  repository does not otherwise use. Keep the simpler root package for the MVP.

### 3.2 Package metadata

`pyproject.toml` (proposed):

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "pls-graph-engine"
version = "0.1.0"
description = "Project-agnostic DAG workflow execution engine for Product Lab System"
requires-python = ">=3.11"
dependencies = ["PyYAML>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=8"]

[project.scripts]
pls = "graph_engine.cli.main:main"

[tool.setuptools.packages.find]
include = ["graph_engine*"]

[tool.pytest.ini_options]
testpaths = ["tests/graph_engine"]
addopts = "-q"
```

No Pydantic, no SQLite, no web framework, no orchestration library. Schema
validation is handwritten dataclass validation so unknown fields and error
messages stay explicit and dependency-free. PyYAML is the only runtime
dependency; pytest is the only dev dependency.

---

## 4. Core model and schema decisions

### 4.1 Workflow schema (version 1)

Top-level allowed keys: `version`, `workflow`, `execution`, `executors`,
`executor_mapping`, `tasks`, `context` (see 4.4). Unknown keys are errors.

`workflow`:
```yaml
workflow:
  id: example-workflow
  description: Example DAG workflow
```

`execution`:
```yaml
execution:
  max_concurrency: 3        # int >= 1, required
  max_retries: 2            # int >= 0, required
  max_run_duration_minutes: 120  # int > 0, optional but recommended
```

`executors`:
```yaml
executors:
  researcher:
    adapter: opencode
    config: {}
```

`executor_mapping`:
```yaml
executor_mapping:
  research: researcher
```

`tasks` is a non-empty list. Allowed task keys:

| Field | Required | Rule |
|---|---|---|
| `id` | yes | unique, filesystem-safe slug |
| `type` | yes | non-empty string; project-specific values allowed |
| `executor` | no | explicit executor name; must exist |
| `depends_on` | no | list of existing task IDs; default `[]` |
| `inputs` | no | list of `{name, from, artifact}`; default `[]` |
| `outputs` | no | list of `{name, path, min_bytes?}`; default `[]` |
| `verification` | yes | non-empty list of criteria |
| `approval` | no | `not_required` (default) or `required` |
| `approval_point` | no | `before_publish` (default) or `before_execution` |
| `max_retries` | no | int >= 0; overrides `execution.max_retries` |
| `timeout_minutes` | no | int > 0; executor wall-clock limit |
| `side_effects` | no | `none` (default), `idempotent`, `unsafe` |
| `idempotency_key` | no | string; required only for `idempotent`/`unsafe` if the adapter supports it |

Design choices that need owner confirmation because they extend the illustrative
schema:

- `approval_point` is a separate key so the example's `approval: required` form
  stays valid. Default `before_publish`.
- `max_retries` per task is an explicit override, not a silent increase. Effective
  value is `task.max_retries ?? execution.max_retries`.
- `verification` must contain at least one criterion; artifact existence alone is
  not treated as a verification criterion.
- `side_effects`, `idempotency_key`, and `timeout_minutes` exist to satisfy
  safety/recovery acceptance. They are optional and default to the least
  dangerous behavior.
- Output `path` must be relative, normalized, start with `artifacts/`, contain no
  `..`, no absolute path, and no `artifacts/.staging/` prefix. Output paths must
  be unique across the whole workflow to prevent publish races.
- Artifact names must be unique within a producing task. An input must reference
  a declared output of a **direct dependency**.

Verification criteria:

```yaml
verification:
  - id: tests_pass
    method: command          # command | agent | human
    command: "pytest -q"     # required for command
    timeout_seconds: 300     # optional, default 300
  - id: independent_review
    method: agent
    executor: reviewer       # required for agent
    acceptance_criteria: "Review the diff against the task criteria."
  - id: owner_signoff
    method: human
    prompt: "Approve the reviewed deliverable."
```

For `command`, the command is parsed with `shlex.split` and executed without a
shell. Pipelines, redirection, and unquoted shell metacharacters (`|`, `&&`, `;`,
`>`, `<`) require an explicit future opt-in; the MVP rejects them at validation
time with a clear error so a command does not silently behave differently. The
working directory is the attempt staging root, so paths in the workflow are
relative to that root (see 5.3).

### 4.2 Run and task states

Task states from the spec: `pending`, `ready`, `running`, `verifying`,
`retrying`, `completed`, `blocked`, `failed`.

Run states: `running`, `awaiting_approval` (extension for C7), `completed`,
`completed_with_blockers`, `failed`, `cancelled` (extension for §16.5).

Central transition table (enforced in `models/transitions.py`):

| From | To | Trigger |
|---|---|---|
| `pending` | `ready` | all dependencies completed and inputs available |
| `pending` | `blocked` | dependency blocked/failed, or run cancelled |
| `ready` | `running` | scheduler grants a concurrency slot |
| `ready` | `blocked` | approval rejected before execution, or run cancelled |
| `running` | `verifying` | executor returned success |
| `running` | `retrying` | executor returned failure and retries remain |
| `running` | `blocked` | executor failed with no retries left, or cancellation |
| `verifying` | `completed` | all criteria pass, approval granted, artifacts published |
| `verifying` | `retrying` | verification failed and retries remain |
| `verifying` | `blocked` | verification failed with no retries, approval rejected, missing approval, or cancellation |
| `retrying` | `running` | next attempt starts with fresh context and feedback |
| `running`/`verifying` | `failed` | non-retryable task-level error, recorded with a category |
| `completed`/`blocked`/`failed` | — | terminal task state; run terminal calculation is in 5.6. Recovery may apply the explicit `completed -> pending` invalidation below if artifacts are untrustworthy |

The spec diagram shows `running -> verifying` and `verifying -> retrying`; the
extra `running -> retrying/blocked` edges are required so executor failures are
retried without pretending verification ran. This deviation is documented and
tested.

Recovery-only exception: `completed -> pending` is allowed only through
`task_invalidated` when a completed task's artifacts fail checksum/existence
checks and the task is safe to re-run. It is not a normal scheduler transition.

### 4.3 Status and error categories

`ErrorCategory`: `task_execution`, `verification`, `artifact_missing`,
`artifact_invalid`, `dependency_failed`, `executor_configuration`,
`approval_rejected`, `orchestration`, `run_timeout`, `cancellation`.

Every error record has `category`, `message`, `timestamp`, `task_id`/`attempt`
when applicable, and diagnostic data. Adapters may catch exceptions to normalize
them, but must record the exception type, message, and truncated traceback; no
bare `except: pass` is allowed.

### 4.4 Context package (extension for §13.1)

The spec requires a reproducible, inspectable context package. The illustrative
workflow has no field for project instructions, so the plan adds an optional
workflow-level block:

```yaml
context:
  instructions:
    - AGENTS.md
  references:
    - _docs/process.md
```

Rules:

- Paths are relative to the project root: `--project-root` when supplied,
  otherwise the git repository root, otherwise the workflow file's directory.
- At run creation, referenced files are copied into `runs/<run-id>/context/` and
  hashed. Attempts use the snapshot, not live files.
- A missing referenced file is a validation error.
- The package contains only: task definition, acceptance criteria, declared input
  artifacts, snapshotted instructions/references, previous-attempt feedback (on
  retry), and output requirements. It never contains undeclared dependency
  outputs or a previous conversation.
- `AGENTS.md`, `_docs/process.md`, and role docs are referenced as text; the
  engine does not execute instructions found in them.

This is an extension to the illustrative schema and needs owner approval.

---

## 5. Component design

### 5.1 Parser

- `yaml_loader.py`: `SafeLoader` subclass that rejects duplicate mapping keys
  (PyYAML otherwise silently overwrites them) and rejects multiple documents.
- `workflow_parser.py`: reads bytes, parses to `WorkflowDefinition`, preserves the
  raw bytes for the snapshot.
- No environment interpolation, no includes, no dynamic expressions. A workflow
  file is the complete definition.

### 5.2 Validation

- `schema.py`: required fields, types, enums, unknown-key rejection, version check,
  limits validation, path safety, approval/verification combinations.
- `references.py`: duplicate task IDs, dependency existence, self-dependency,
  input source existence, artifact declaration, direct-dependency rule, unique
  artifact names, unique output paths, executor references, mapping targets.
- `dag.py`: Kahn's algorithm; returns deterministic topological order and a cycle
  path on failure.
- `executors.py`: explicit executor wins; otherwise `task.type -> executor_mapping`;
  otherwise error. No LLM routing. Unused executors/mappings are warnings.
- `report.py`: `ValidationReport` with `errors` and `warnings`; CLI exit code 4
  for errors.

Validation is run by `pls graph validate` and again at run creation. An invalid
workflow never creates a run directory.

### 5.3 Artifacts and paths

Canonical mapping:

- Run root: `runs/<run-id>/`.
- Output `path` is relative to the run root and must start with `artifacts/`.
- Final artifact path: `runs/<run-id>/<output.path>`.
- Attempt staging root: `runs/<run-id>/artifacts/.staging/<task-id>/attempt-<NNN>/`.
- Executor and command verifier working directory: the attempt staging root.
- Staged artifact path: `<staging-root>/<output.path>`.
- Declared inputs are copied into `<staging-root>/inputs/<artifact-name>/<artifact-relative-path>`
  (preserving the producer's relative path) and passed read-only in the context;
  the source artifacts are never mutated.
- Publication: after all criteria and approval pass, each staged artifact is
  `os.replace`d to `runs/<run-id>/<output.path>` (same filesystem), parent
  directories created, checksum verified before and after. A failure mid-publish
  blocks the task and records which artifacts were published; recovery reconciles
  the set. Partial outputs are never exposed as completed artifacts.

`ArtifactRecord` fields: `name`, `path`, `producer_task`, `producer_attempt`,
`created_at`, `size_bytes`, `sha256`, `validation_status`.
`ArtifactManager` validates existence, non-empty (`min_bytes`, default 1),
regular file, symlink escape, and checksum.

### 5.4 Persistence

Run layout:

```text
runs/<run-id>/
  workflow.yaml              # immutable snapshot, SHA-256 recorded
  executor_config.json       # normalized, secret-free snapshot + hash
  context/                   # optional snapshotted instructions/references
  run.json                   # authoritative run/task status snapshot
  run.lock                   # advisory flock held by the active process
  cancel.requested           # sentinel, present only during cancellation
  tasks/<task-id>/task.json  # projection of task state
  tasks/<task-id>/attempts/001.json
  approvals/<task-id>.json   # decision history
  artifacts/.staging/<task-id>/attempt-001/...
  artifacts/<...>            # published outputs
  logs/events.jsonl
  metrics.json
```

- `run.json` is authoritative for run/task statuses. `task.json` is a projection
  rewritten from run state; attempt files are append-only audit records. Recovery
  uses `run.json` plus attempt files and ignores stale projections.
- Every JSON write uses the same-directory temporary file, `flush`, `os.fsync`,
  `os.replace`, and a directory `fsync`. The previous content remains intact if
  the write fails.
- `run.json` includes `schema_version`, `run_id`, `workflow_id`, `workflow_version`,
  `status`, timestamps, `git_sha` (`null` when git is unavailable), `git_dirty`,
  `engine_version`, snapshot paths and hashes, execution limits, task statuses,
  block reasons, and error records.
- Run IDs: `<workflow-id>-YYYYMMDDTHHMMSSZ-<6 hex>`; validated against a safe slug.
- A `run.lock` advisory lock prevents two controllers mutating the same run. A
  stale lock is reported, not silently stolen.
- Workflow snapshots are copied before execution and never rewritten. On resume,
  the snapshot is parsed, its hash is compared, and a mismatch refuses resume.

### 5.5 Executors

```python
class Executor(Protocol):
    name: str
    adapter: str

    def execute(self, task: TaskDefinition, context: ExecutionContext) -> ExecutionResult: ...
    def cancel(self) -> None: ...  # optional
```

- `ExecutionResult`: `status` (`success`, `failure`, `cancelled`), `summary`,
  `artifacts`, `metadata`, `usage`, `error`.
- `Usage`: `input_tokens`, `output_tokens`, `estimated_cost`, `available`; all
  unknown values are `None`, never invented.
- `ExecutorRegistry`: builds adapters from `executors` config deterministically.
  Unknown adapter or executor name is a validation error; runtime construction
  failure is a task `blocked` with `executor_configuration` (or a run failure if
  the state cannot be preserved).
- `MockExecutor`: scripted results, call log, bars/events for deterministic
  concurrency tests.
- `CommandExecutor` (Stage 8): runs a configured argv in the staging directory,
  with a timeout, an allowlisted environment, no shell, and a required structured
  `result.json` in the staging root. This is the generic adapter for local tools
  and the basis of the OpenCode preset.
- `OpenCodeExecutor` (Stage 8): preset/wrapper around `opencode run --format json`
  with no `--auto` by default, a fresh session per attempt, and the result
  contract above. Adapter tests mock the process; one opt-in real smoke run is
  recorded separately.
- Engine validates every result: status enum, JSON-serializable metadata, declared
  artifact names only, paths inside the staging root, non-negative usage. An
  adapter cannot mutate graph state; it only returns a result.

### 5.6 Scheduler and controller

- `scheduler/readiness.py` is pure: given workflow + run state, return ready task
  IDs and newly blocked task IDs. Ready means `pending`, all dependencies
  `completed`, required inputs available, run not cancelled/timed out, and a
  concurrency slot available. A `ready` task with `approval_pending = true`
  (approval point `before_execution`) is never dispatchable.
- `scheduler/scheduler.py` selects ready tasks in workflow declaration order, up to
  `max_concurrency`. No manual order beyond DAG dependencies.
- `execution/controller.py` owns all state mutations. Workers only execute and
  return results. A single controller thread updates state, persists, and emits
  events, which avoids concurrent writes.
- Execution model: synchronous controller + `ThreadPoolExecutor(max_workers=max_concurrency)`.
  The executor interface is synchronous; an adapter may wrap async internals.
  This is the simplest model compatible with subprocess-based agents and
  deterministic tests. `ExecutorPool` is injectable so scheduler/controller tests
  can run without real threads.
- Loop: check cancel/timeout -> propagate blocked dependencies -> compute ready ->
  dispatch up to slots -> wait for one or more completions -> verify/retry/persist
  -> repeat. Independent branches continue after a failure; downstream tasks are
  marked blocked with `dependency_failed` and are never dispatched.
- Terminal calculation:
  - all tasks `completed` -> `completed`;
  - at least one `blocked` or `failed` task and no runnable work ->
    `completed_with_blockers`;
  - orchestration/persistence failure -> `failed`;
  - cancellation requested and honored -> `cancelled`;
  - timeout -> `failed` with `run_timeout`; timeout takes precedence over a
    concurrent cancellation request so the cause is recorded honestly.
- A task failure never crashes the scheduler. A scheduler/persistence failure is
  surfaced as run-level `failed` while preserving recoverable state.

### 5.7 Verification, retries, approval

- `CommandVerifier`: controlled `subprocess.run(argv, shell=False, cwd=staging,
  capture_output=True, text=True, timeout=...)`; captures argv, exit code,
  stdout, stderr, duration; truncates large output in JSON and writes full output
  under `logs/`. Kills the process group on timeout.
- `AgentVerifier`: invokes a configured executor with a fresh context containing
  the task definition, acceptance criteria, declared inputs/outputs, and evidence
  requirements. It must return a structured `pass|fail` verdict plus findings. It
  does not see the implementer's conversation.
- `HumanVerifier`: creates an approval request and pauses; the decision is stored
  with timestamp, actor (from `PLS_APPROVER` or OS user), comment, and attempt.
- `VerificationEngine`: runs criteria in declaration order; a failure stops the
  remaining criteria and becomes retry feedback. Human criteria pause the run.
  Task-level `approval` runs after non-human verification and before publication;
  if both a human criterion and task approval are present, the validation report
  warns about the double gate.
- Retry accounting: effective budget = task override or global `max_retries`;
  `max_retries: 2` means at most 3 attempts. Every attempt gets a new attempt
  number, staging directory, context object, and persisted record. The next
  attempt receives a concise `RetryFeedback` (previous attempt number, failures,
  truncated relevant logs, missing/invalid artifacts, reviewer findings, explicit
  fix instructions), never the full conversation.
- Exhausted budget -> task `blocked`, downstream blocked, owner notified through
  the event log and CLI status.
- Approval semantics:
  - `approval: required` + `before_publish` (default): execute, verify, then pause
    before publication. Task remains `verifying`; run is `awaiting_approval`.
  - `before_execution`: pause before dispatch. Task remains `ready`; run is
    `awaiting_approval`.
  - `pls graph approve|reject` writes the decision. Executors cannot approve their
    own work; any approval flag in an executor result is ignored and rejected by
    result validation.
  - A rejection blocks the task and downstream; it does not delete evidence.
  - Engine approval is workflow-local. It never replaces the owner approval
    required for push, merge, deploy, publication, payment, or issue closure;
    adapters expose no such actions and run without credentials by default.

### 5.8 Recovery and safety

`RecoveryManager` loads `run.json`, validates schema, verifies the snapshot hash,
the executor-config hash, and artifact checksums, then produces a resume plan:

- `completed`: reuse only if every declared artifact exists and matches its
  checksum. Otherwise invalidate the task (event `task_invalidated`), reset it to
  `pending`, and reset downstream tasks. If `side_effects: unsafe`, do not reset;
  block for human intervention.
- `running`/`verifying`: mark the attempt `interrupted`; never treat it as
  successful. Safe tasks return to `pending`; unsafe tasks become `blocked`.
- `retrying`: return to `pending` with the existing attempt count and feedback.
- `ready`: return to `pending` and recompute.
- `blocked`: keep blocked; only approval/transient blockers can be cleared by an
  explicit decision.
- `failed`: keep failed; run remains `completed_with_blockers` or `failed`.
- `cancelled` run: `resume` is allowed; tasks blocked with `run_cancelled` become
  `pending`, interrupted attempts are reconciled as above.

Resume consistency:

- Workflow snapshot: never replaced. A hash mismatch refuses resume.
- Executor config: hash mismatch refuses resume unless the owner passes
  `--accept-executor-config-change`, which records an event and updates the
  snapshot hash. The change is never silent.
- Environment values: not detectable from the config hash; documented limitation.
- External side effects: `side_effects: unsafe` tasks require explicit approval
  before retry, record `external_action_id` in attempt metadata when the adapter
  provides it, and are never silently repeated. `idempotent` tasks pass the
  idempotency key in the context and record it.
- Run lock prevents concurrent resume; cancellation uses a sentinel file and, when
  the run records a live PID, an optional signal. A controller checks the sentinel
  between scheduling cycles and asks executors to cancel.

### 5.9 Observability

JSONL event schema:

```json
{"ts":"2026-10-31T10:00:00Z","event":"task_started","run_id":"...","task_id":"...","attempt":1,"data":{}}
```

Required events: run created/started/completed/failed/resumed/cancelled/timed_out;
task ready/started/attempt completed/retrying/completed/blocked/invalidated;
verification started/completed; approval requested/granted/rejected; artifact
published; executor config mismatch.

`metrics.json` per run and per task: duration, attempts, retry count, verification
results, executor, usage (or `null` with `usage_available: false`), estimated cost
(or `null`), blocked task count, failure reasons, artifact metadata. Metrics are
written atomically at pause/terminal points; `status` only reads them.

### 5.10 CLI

```bash
pls graph validate <workflow> [--json]
pls graph run <workflow> [--runs-dir PATH] [--run-id ID] [--json]
pls graph status <run-id> [--runs-dir PATH] [--json] [--events N]
pls graph resume <run-id> [--runs-dir PATH] [--accept-executor-config-change] [--extend-run-timeout-minutes N]
pls graph cancel <run-id> [--runs-dir PATH]
pls graph approve <run-id> <task-id> [--comment TEXT]   # extension for human gates
pls graph reject <run-id> <task-id> [--comment TEXT]    # extension for human gates
```

`status` prints run status, task statuses, current attempts, blocked tasks and
reasons, recent events, and the metrics summary; `--json` is the machine-readable
contract used by tests and future lifecycle integration. `run` prints the run ID
and final/paused status. `validate` returns non-zero on invalid input.

Exit codes: `0` completed, `1` failed, `2` completed_with_blockers, `3`
awaiting_approval, `4` invalid workflow/usage, `5` resume refused, `130`
interrupted/cancelled.

---

## 6. Reusable components in the current repository

There is no engine code to reuse. The reusable assets are policy, terminology,
and role contracts. They should be referenced, not copied into engine modules.

| Existing asset | Reuse | How | Constraint |
|---|---|---|---|
| `AGENTS.md` | Safety and approval policy | Engine docs restate the no-push/merge/deploy rule and approval gate | Do not import or parse at runtime |
| `_docs/process.md` | Stage/QA handoff discipline | Stage exit criteria and independent QA checklist | Engine must not depend on GitHub Issues |
| `_docs/team/roles.md` | Independent reviewer context | Agent-verifier prompt design: read-only reviewer, fresh context, PASS/FAIL evidence | The existing QA contract is methodology-oriented; add a graph-engine QA checklist in `_docs/graph-engine/testing.md`, do not rewrite roles |
| `_docs/task-template.md` | Task/acceptance criteria fields | Context package and workflow documentation use the same vocabulary (goal, criteria, verification) | Do not duplicate fields into `system/` |
| `system/00-model.md` | Canonical PLS terminology | Link to it; qualify engine `task.status` vs experiment `status`; keep evidence ladder separate | Never redefine PLS stages/statuses/gates inside the engine |
| `system/modules/llm-research.md` | Research Loop policy | Workflow YAML and evidence-depth doc reference its rules | No special engine logic; no automatic research |
| `templates/system-change.md` | Change-record format | Stage reports can follow its scope/verification style | Not a runtime input |
| `projects/coding-agent-workflow-kit/product/` (branch `project/coding-agent-workflow-kit`) | Role prompts, safety text, repair-loop pattern | Read-only inspiration if the owner wants; do not depend on the branch | Not on `main`; no imports or copied assets without review |
| Python stdlib, PyYAML, pytest | Runtime/test foundation | `pyproject.toml` | Only dependency additions; no pydantic/click/etc. |
| OpenCode CLI 2.1.4 | First real adapter target | `opencode run --format json` behind `CommandExecutor` preset | No `--auto`; no credentials in config; opt-in smoke only |

Explicitly **not** reusable: there is no `research/` package, no scheduler, no
artifact store, no CLI, no logging, and no test fixture to import.

---

## 7. Acceptance criteria mapping

Test paths below are proposed. "Unit" means `tests/graph_engine/unit/`, etc.
The mapping is the contract for Stage 8 acceptance review.

### A. Architecture

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| A1 | Separate logical module | `graph_engine/` top-level package; no imports from vault folders | `test_package_boundary.py::test_engine_package_is_standalone` |
| A2 | No imports from `product_lifecycle` | Import-boundary rule; AST scan | `test_package_boundary.py::test_no_product_lifecycle_import` |
| A3 | Lifecycle can invoke stable interface | `graph_engine/api.py` (`validate_workflow`, `run_workflow`, `resume_run`, `cancel_run`, `get_status`); CLI uses same API | `test_package_boundary.py::test_public_api_contract` + `tests/graph_engine/stub_lifecycle_consumer.py` importing only the public API |
| A4 | No product-specific business logic | Engine modules contain only generic orchestration; no project names/statuses | `test_package_boundary.py::test_no_product_specific_imports` + independent QA review |

### B. Workflow validation

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| B1 | Load and validate YAML | `parser/`, `validation/schema.py` | `unit/test_parser.py`, `unit/test_schema_validation.py` |
| B2 | Reject invalid schemas | Strict allowed-key sets, type/enum/version checks, duplicate-key loader | `unit/test_schema_validation.py::test_unknown_fields_rejected`, `test_missing_required_rejected`, `test_duplicate_yaml_keys_rejected` |
| B3 | Reject missing references | `validation/references.py` | `unit/test_reference_validation.py` (duplicate task IDs, dependency, input, artifact, executor) |
| B4 | Detect/reject cycles | `validation/dag.py` Kahn + cycle path | `unit/test_dag_validation.py` (self, 2-node, larger, cycle path) |
| B5 | Deterministic executor resolution | `validation/executors.py`: explicit > mapping > error; declaration order | `unit/test_executor_resolution.py` |
| B6 | Invalid workflows cannot start | API/CLI validate before `RunLayout.create`; invalid run leaves no run directory | `execution/test_run_rejects_invalid.py`, `cli/test_run.py::test_invalid_workflow_creates_no_run` |

### C. Execution

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| C1 | Execute according to DAG dependencies | `scheduler/readiness.py`, `scheduler/scheduler.py` | `scheduler/test_readiness.py` |
| C2 | Independent tasks in parallel | `execution/controller.py` + thread pool | `execution/test_controller_parallel.py` with barrier fake executor |
| C3 | `max_concurrency` enforced | Scheduler slot accounting | `scheduler/test_concurrency.py` (peak concurrency never exceeds N) |
| C4 | Failed branch does not stop independent branch | Blocked propagation only along descendants | `scheduler/test_independent_branches.py` |
| C5 | Downstream cannot execute after dependency failure | Readiness excludes pending tasks with non-completed deps; mark blocked | `scheduler/test_downstream_blocking.py` (executor invocation count 0) |

### D. Verification and retries

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| D1 | All mandatory criteria enforced | `execution/controller.py` completion gate + `verification/` | `verification/test_completion_criteria.py` |
| D2 | Command, agent, human methods work | `verification/command.py`, `agent.py`, `human.py` | `verification/test_command_verifier.py`, `test_agent_verifier.py`, `test_human_verifier.py` |
| D3 | Every attempt persisted | `persistence/attempt_store.py`; attempt number in path | `execution/test_retry.py::test_every_attempt_has_json` |
| D4 | Retry feedback reaches next attempt | `verification/feedback.py`; `ExecutionContext.previous_attempt` | `execution/test_retry.py::test_feedback_in_next_context` |
| D5 | Retry limits enforced | `execution/limits.py`; global + task override | `unit/test_limits.py`, `execution/test_retry.py::test_max_retries_is_additional` |
| D6 | Exhausted tasks blocked | Controller transition to `blocked`; downstream propagation | `execution/test_retry.py::test_exhausted_retries_block` |

### E. Data and artifacts

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| E1 | Inputs explicitly declared | Schema + context builder only includes declared inputs | `unit/test_reference_validation.py`, `execution/test_context.py` |
| E2 | Undeclared dependency outputs not passed | Context builder has no dependency-output discovery | `execution/test_context.py::test_undeclared_output_not_in_context` |
| E3 | Required artifacts validated | `artifacts/manager.py`: exists, non-empty, regular file, path safe | `artifacts/test_validation.py` |
| E4 | Publish only after successful verification | Publication after completion gate; failed attempt discards staging | `artifacts/test_publication.py::test_no_publish_on_failed_verification` |
| E5 | Checksums and provenance | `ArtifactRecord` with producer task/attempt, timestamp, size, SHA-256 | `artifacts/test_metadata.py` |

### F. Persistence and recovery

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| F1 | Run state JSON | `persistence/run_store.py` | `persistence/test_run_store.py` |
| F2 | Workflow templates YAML | Parser + immutable `workflow.yaml` snapshot | `persistence/test_snapshot.py` |
| F3 | Atomic writes where supported | `persistence/atomic.py` temp + fsync + replace | `persistence/test_atomic_json.py` (failure injection preserves old state) |
| F4 | Immutable workflow snapshot | Hash recorded; resume parses snapshot; mismatch refuses | `recovery/test_snapshot_immutability.py` |
| F5 | Completed verified tasks reused | Recovery reuses only checksum-valid completed tasks | `recovery/test_reuse_completed.py` (executor not called again) |
| F6 | Incomplete attempts never reused | Interrupted attempt marked `interrupted`; task re-executed | `recovery/test_interrupted.py` |
| F7 | Unsafe external side effects not repeated | `side_effects` policy + approval + external action IDs | `recovery/test_side_effects.py` |

### G. Agent collaboration

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| G1 | Common executor interface | `executors/base.py` protocol/ABC | `executors/test_contract.py` |
| G2 | Fresh context per task/retry | `execution/context.py` builds a new object and staging dir per attempt | `execution/test_context.py::test_fresh_context_per_attempt` |
| G3 | Context only declared inputs/references | Context builder allowlist; snapshotted instructions | `execution/test_context.py::test_context_allowlist` |
| G4 | Implementer/reviewer independent | Agent verifier runs separately with fresh context; optional downstream review task | `verification/test_agent_verifier.py::test_reviewer_does_not_see_implementer_transcript` |
| G5 | Reviewer feedback used in next implementation attempt | Agent-verifier failure produces retry feedback; next attempt receives findings | `execution/test_retry.py::test_reviewer_findings_in_retry_feedback` |

### H. Safety

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| H1 | Human approval per task | `approval`/`approval_point` schema; `verification/human.py`; `approve/reject` CLI | `verification/test_human_verifier.py`, `cli/test_approve.py` |
| H2 | Executors cannot approve own actions | Approval only through approval store/CLI; result `approved` field rejected | `verification/test_human_verifier.py::test_executor_cannot_approve` |
| H3 | Push/merge/deploy protected | Engine exposes no such action; adapters run without credentials/`--auto`; docs state owner approval remains external | `test_safety.py::test_no_protected_action_capability` + QA review of docs/adapters |
| H4 | Execution limits enforced | Concurrency, retry, timeout enforced by controller, not prompts | `scheduler/test_concurrency.py`, `unit/test_limits.py`, `execution/test_timeout.py` |

### I. Observability

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| I1 | Structured JSONL events | `observability/events.py`; one JSON object per line | `observability/test_events.py` (schema, required event names) |
| I2 | Per-run metrics persisted | `observability/metrics.py`, `metrics.json` | `observability/test_metrics.py` |
| I3 | Durations and retry counts | Metrics from attempt timestamps and counts | `observability/test_metrics.py::test_durations_and_retries` |
| I4 | Verification results and failure reasons | Attempt records + metrics include category/message | `observability/test_metrics.py::test_failure_reasons` |
| I5 | Usage/cost recorded when available | Adapter `Usage`; metrics copies values | `executors/test_usage.py` |
| I6 | Missing usage represented honestly | `null` + `usage_available: false`; no invented values | `executors/test_usage.py::test_unavailable_usage_is_null` |

### J. CLI and quality

| AC | Requirement | Proposed implementation | Verification |
|---|---|---|---|
| J1 | `validate`, `run`, `status`, `resume`, `cancel` work | `cli/main.py`, `commands.py` | `cli/test_validate.py`, `test_run.py`, `test_status.py`, `test_resume.py`, `test_cancel.py` |
| J2 | Unit tests pass | `tests/graph_engine/unit/` | `python -m pytest tests/graph_engine/unit -q` |
| J3 | Scheduler tests pass | `tests/graph_engine/scheduler/` | `python -m pytest tests/graph_engine/scheduler -q` |
| J4 | Recovery tests pass | `tests/graph_engine/recovery/` | `python -m pytest tests/graph_engine/recovery -q` |
| J5 | End-to-end test passes | `tests/graph_engine/e2e/` with mock executors | `python -m pytest tests/graph_engine/e2e -q` |
| J6 | Documentation explains format/operations | `_docs/graph-engine/*` | Independent QA reads docs against the running CLI; no skipped mandatory test |

### Specification §19 test-strategy cross-check

These are not additional acceptance criteria; they are the mandatory tests named
by the specification's testing section.

| §19 requirement | Proposed test |
|---|---|
| YAML parsing, schema, duplicate IDs, missing references, cycles, executor resolution | `unit/test_parser.py`, `test_schema_validation.py`, `test_reference_validation.py`, `test_dag_validation.py`, `test_executor_resolution.py` |
| Task state transitions | `unit/test_transitions.py` (every allowed edge and representative forbidden edges) |
| Retry accounting | `unit/test_limits.py`, `execution/test_retry.py` |
| Verification evaluation | `verification/test_completion_criteria.py`, `test_command_verifier.py`, `test_agent_verifier.py`, `test_human_verifier.py` |
| Artifact validation | `artifacts/test_validation.py`, `test_publication.py` |
| Atomic state persistence | `persistence/test_atomic_json.py` |
| Run terminal-state calculation | `scheduler/test_terminal_state.py`, `execution/test_controller_sequential.py` |
| Metrics aggregation | `observability/test_metrics.py` |
| Sequential tasks | `scheduler/test_sequential.py` |
| Independent parallel tasks | `scheduler/test_independent_parallel.py`, `execution/test_controller_parallel.py` |
| Fan-out/fan-in | `scheduler/test_fan_in_out.py` |
| Concurrency limit | `scheduler/test_concurrency.py` |
| Independent branches after failure | `scheduler/test_independent_branches.py` |
| Downstream blocked after dependency failure | `scheduler/test_downstream_blocking.py` |
| Multiple simultaneously ready tasks | `scheduler/test_multiple_ready.py` |
| Run timeout | `execution/test_timeout.py` |
| Cancellation | `execution/test_cancel.py` |
| Resume after interruption | `recovery/test_resume.py` |
| Completed-task reuse | `recovery/test_reuse_completed.py` |
| Incomplete attempts rejected as success | `recovery/test_interrupted.py` |
| Interrupted-task recovery | `recovery/test_resume.py` |
| Missing artifact detection | `recovery/test_missing_artifact.py` |
| Snapshot immutability | `recovery/test_snapshot_immutability.py` |
| Executor configuration mismatch | `recovery/test_executor_config_mismatch.py` |
| Repeated external actions | `recovery/test_side_effects.py` |
| Adapter context construction | `execution/test_context.py` |
| Adapter result parsing | `executors/test_result_validation.py` |
| Adapter error handling | `executors/test_mock.py`, `test_command.py` |
| Adapter cancellation | `executors/test_cancellation.py` |
| Adapter usage metadata | `executors/test_usage.py` |
| E2E parallelism/dependency/artifact handoff | `e2e/test_parallel_workflow.py` |
| E2E retry, exhaustion, branch continuation, terminal state | `e2e/test_retry_blocking.py` |
| E2E resume after simulated interruption | `e2e/test_resume_workflow.py` |
| E2E events and metrics completeness | `e2e/test_events_metrics.py` |

---

## 8. Implementation stages

Each stage ends with a checkpoint commit only if the owner has authorized a
branch/issue lane (C11). No stage may push, merge, deploy, tag, or close issues.

### Stage 0 — this document

**Deliverable:** this plan, plus owner decisions on C1–C3, C7, C11, C14 and the
schema extensions. **No code.**
**Exit:** owner approves the plan or records required changes.

### Stage 1 — Core models and workflow validation

**Files:** `pyproject.toml`, `.gitignore`, `graph_engine/{__init__,version,errors,api}.py`,
`graph_engine/models/*`, `graph_engine/parser/*`, `graph_engine/validation/*`,
`tests/graph_engine/{conftest.py,fake_executors.py}`, `tests/graph_engine/unit/*`,
`tests/graph_engine/fixtures/workflows/*`.

**Work:** dataclasses/enums, strict schema, YAML loader with duplicate-key
rejection, reference validation, DAG/cycle detection, executor resolution,
validation report, public `validate_workflow`.

**Exit:** all unit validation tests pass; invalid workflow produces no run state;
no imports from vault folders.

### Stage 2 — Persistence and artifact management

**Files:** `persistence/*`, `artifacts/*`, minimal `observability/events.py`,
`tests/graph_engine/{persistence,artifacts}/*`.

**Work:** run layout/ID, snapshot + hashes, atomic JSON, run/task/attempt stores,
lock, staging, input copying, output validation, checksums, publication,
manifest, minimal event emission.

**Exit:** persistence/artifact tests pass; simulated write failure preserves the
previous state; failed verification leaves no published artifact.

### Stage 3 — Executor interface and mock executor

**Files:** `execution/{context,result}.py`, `executors/{base,registry,mock}.py`,
`errors.py` additions, `tests/graph_engine/executors/*`,
`tests/graph_engine/execution/test_context.py`.

**Work:** protocol, context package, result/usage validation, registry, mock,
error normalization, cancellation hook.

**Exit:** adapter contract tests pass; malformed result is rejected; an adapter
exception becomes a normalized failure, not a crash.

### Stage 4 — Scheduler and execution engine

**Files:** `scheduler/*`, `execution/{lifecycle,limits,controller}.py`,
`graph_engine/api.py` additions, `tests/graph_engine/{scheduler,execution}/*`.

**Work:** readiness, deterministic ordering, concurrency slots, run loop,
lifecycle transitions, independent branches, downstream blocking, terminal-state
calculation, injectable executor pool, timeout/cancel hooks.

**Exit:** scheduler tests cover sequential, parallel, fan-out/fan-in, concurrency
limit, branch failure, downstream block, timeout, cancellation.

### Stage 5 — Verification, retries, and approvals

**Files:** `verification/*`, `execution/controller.py` integration,
`persistence/approval_store.py` (or `approvals.py`), `tests/graph_engine/verification/*`,
`tests/graph_engine/execution/test_retry.py`.

**Work:** command/agent/human verifiers, completion gate, retry accounting,
feedback builder, approval pause/resume, artifact publication gate.

**Exit:** all completion criteria tests pass; every attempt persisted; retry
feedback verified; exhausted tasks blocked; executor cannot self-approve.

### Stage 6 — Recovery and safety

**Files:** `recovery/*`, `persistence/lock.py` integration, `execution/limits.py`
timeout extension, `tests/graph_engine/recovery/*`, `tests/graph_engine/execution/test_timeout.py`.

**Work:** load/validate/reconcile, completed-task reuse, interrupted attempts,
missing/corrupt artifacts, snapshot/config mismatch, cancellation sentinel, run
timeout, side-effect policy.

**Exit:** recovery tests cover all F-criteria; unsafe tasks block rather than
repeat; cancelled runs are resumable.

### Stage 7 — Observability and CLI

**Files:** `observability/{events,metrics}.py`, `cli/*`, `_docs/graph-engine/*`,
`tests/graph_engine/{observability,cli}/*`.

**Work:** full event catalog, metrics aggregation, argparse CLI, status output,
operational docs, exit codes.

**Exit:** CLI tests pass; events/metrics complete for an E2E run; docs match CLI.

### Stage 8 — Real executor integration and E2E

**Files:** `executors/command.py`, `executors/opencode.py`,
`workflows/examples/*`, optional `workflows/research-loop/monthly-review.yaml`,
`tests/graph_engine/e2e/*`, `tests/graph_engine/executors/test_command.py`,
`_docs/graph-engine/acceptance-checklist.md`.

**Work:** generic command adapter, OpenCode preset, mock E2E A/B/C/D, retry/block
E2E, resume E2E, optional real smoke, Research Loop workflow if approved, fill
the acceptance checklist.

**Exit:** full `python -m pytest tests/graph_engine -q` passes; E2E proves
parallelism, dependency waiting, artifact handoff, retry, downstream block,
independent branch continuation, terminal state, resume, events, metrics; one
real adapter smoke is recorded with exact command/result or explicitly reported
as not run.

---

## 9. Test strategy and deterministic controls

- `tests/graph_engine/conftest.py`: temp run dirs, workflow factory, fake clock,
  fake executor pool, event/metric readers.
- `fake_executors.py`: scripted results; `threading.Barrier`/`Event` to prove
  overlap; call logs; failure injection; optional delay.
- Scheduler tests use the pure readiness/scheduler functions, not real threads.
- Controller tests inject a `FakeExecutorPool` that runs tasks synchronously or in
  a controlled order; one dedicated test uses real threads + barrier to prove
  parallel execution and concurrency limit.
- Timeout tests inject a monotonic fake clock; no `sleep`-based assertions.
- Subprocess verifier tests use short local commands (`python -c ...`) and assert
  exit code/stdout/stderr/duration; no network.
- Real adapter tests are marked `@pytest.mark.integration` and skipped only when
  the binary is absent. A skipped real-adapter test is not counted as PASS for
  the mock-based mandatory suite; Definition of Done item 4 requires a separately
  recorded real smoke.
- Commands:
  - `python -m pytest tests/graph_engine/unit -q`
  - `python -m pytest tests/graph_engine/scheduler -q`
  - `python -m pytest tests/graph_engine/recovery -q`
  - `python -m pytest tests/graph_engine/e2e -q`
  - `python -m pytest tests/graph_engine -q`
- No test may require a paid LLM service or external network. No test may write
  outside its temp directory.

---

## 10. Risks and limitations

| Risk | Mitigation |
|---|---|
| Thread-based cancellation cannot forcibly stop a Python executor | Executors are subprocess-based in practice; `cancel()` is cooperative; timeout kills the process group; document the limitation |
| Multi-file artifact publication is not truly atomic | Publish one artifact at a time via `os.replace`; record per-artifact state; recovery reconciles; never mark complete until all are present |
| Human approval is local and unauthenticated | Record actor/timestamp/comment; document that this is a local trust boundary, not cryptographic approval |
| Executor config hash cannot detect env-var changes | Store env-var names, not values; document; require explicit config change for structural changes |
| Real agent can perform protected actions despite prompt rules | No credentials/`--auto` by default; adapters expose no push/merge/deploy; owner approval remains external; QA reviews prompts |
| Obsidian vault performance with code/tests | Keep runtime dirs gitignored; owner may exclude code folders from Obsidian search |
| Status vocabulary confusion | Qualify `task.status`/`run.status`; keep engine docs separate from `system/00-model.md` |
| Static DAG cannot express arbitrary review loops | Use agent verification for the implementer-reviewer repair loop (C8); one-shot review remains a task |
| Blocked tasks are terminal for a run | Document that a new run is required after retry exhaustion; do not silently reset budgets |
| No CI means local-only evidence | Independent QA records exact commands/results; CI is a separate owner decision |

**Out of scope for the MVP:** dynamic graphs, LLM routing/dependency discovery,
cyclic graphs, distributed execution, web UI/dashboard, database/event sourcing,
general agent memory, automatic template modification, automatic sensitive-action
approval, OpenTelemetry/Prometheus/Grafana, token/cost budgets as mandatory
limits, multi-tenant auth, and a hosted service.

---

## 11. What Stage 0 changes in the repository

- Adds this plan file: `_docs/graph-engine-stage-0-plan.md`.
- Does not modify `system/`, `templates/`, `projects/`, `AGENTS.md`,
  `_docs/process.md`, `_docs/team/roles.md`, or the untracked specification.
- Does not create branches, commits, pushes, merges, tags, deployments, or issues.
- Does not install dependencies or run the future test suite.

## 12. Stage 0 exit criteria

Stage 0 is complete when the owner has reviewed this plan and recorded the
following.

**Must decide before Stage 1:**

1. C1 — engine in this repository (recommended) or a separate repository.
2. C2 — public API + stub consumer as the A3 interpretation, or defer A3.
3. C3 — Research Loop workflow in MVP scope or deferred.
4. C7 — `awaiting_approval` run status and `approve`/`reject` CLI commands.
5. C11 — issue/branch lane for implementation.
6. The schema extensions in 4.1/4.4 (`approval_point`, `max_retries` override,
   `timeout_minutes`, `side_effects`, `idempotency_key`, `context`).

**Recommended defaults to confirm or veto (non-blocking if accepted):**

7. C4 — `runs/` gitignored at the repository root, configurable by flag/env.
8. C5 — qualify `task.status`/`run.status`; do not add engine statuses to
   `system/00-model.md`.
9. C6 — name the Research Loop scale `evidence_depth` (`A/F/C/E`), separate from
   PLS confidence and `L0–L5`.
10. C8 — implement the implementer-reviewer repair loop as agent verification,
    not as a DAG cycle.
11. C9 — `blocked` vs `failed` mapping in 4.2.
12. C10 — active-execution timeout accounting with explicit `resume` extension.
13. C12 — `env:NAME` executor config references and secret-key rejection.
14. C13 — generic `CommandExecutor` + OpenCode preset for Stage 8.
15. C14 — local pytest gate now; CI/license as separate owner decisions.

Until the must-decide items are recorded, implementation must not start.
