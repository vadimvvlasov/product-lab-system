# Graph Engine — Architecture & Implementation Specification

**Project:** Product Lab System (PLS)
**Status:** Approved for implementation planning
**Target:** OpenCode coding agent
**Scope:** Universal DAG workflow execution engine inside PLS

---

# 1. Objective

Implement a generic Graph Engine that executes predefined workflows as Directed Acyclic Graphs (DAGs).

The engine must coordinate tasks, executors, dependencies, artifacts, verification, retries, approvals, and execution state.

The Graph Engine is infrastructure. It must not contain product-specific business logic.

It will initially be used by Product Lab System, including its product-development workflows and Research Loop.

## 1.1. Core principles

1. **Project-agnostic:** the engine must not depend on a particular product, workflow, or development methodology.
2. **Static workflow structure:** workflow topology is defined in YAML before execution.
3. **DAG-only dependencies:** dependencies are explicit and acyclic.
4. **Task-centric:** graph nodes represent work, not agents.
5. **Executor-independent:** tasks use a generic executor interface.
6. **Explicit data flow:** tasks receive only declared inputs.
7. **Verifiable completion:** successful executor execution alone does not mean a task is completed.
8. **Recoverable execution:** completed tasks and their valid artifacts can be reused after interruption.
9. **File-based persistence:** no database or event-sourcing infrastructure.
10. **Simple first:** no dynamic graph generation, autonomous routing, or distributed orchestration.

## 1.2. Relationship with Product Lifecycle

The existing PLS Product Lifecycle remains a separate system.

The Graph Engine must not replace lifecycle stages such as:

- Sweep
- Screen
- Experiment
- Deliver / Live
- Review / Decision

The lifecycle may invoke Graph Engine workflows, but Graph Engine must not import or depend on lifecycle-specific modules.

Research Loop is also a workflow implemented using the same Graph Engine.

---

# 2. Scope and Non-goals

## 2.1. In scope

- YAML workflow templates.
- DAG validation.
- Task scheduling and dependency management.
- Parallel task execution.
- Generic executor interface and adapters.
- Explicit task inputs and outputs.
- Artifact storage.
- Task completion verification.
- Bounded retries.
- Failure handling.
- Resume and recovery.
- Human approval gates.
- Per-run workflow snapshots.
- Structured execution metrics and logs.
- CLI interface.
- Unit, integration, and end-to-end tests.

## 2.2. Out of scope

Do not implement:

- Dynamic graph generation by agents.
- LLM-based executor routing.
- LLM-based dependency discovery.
- Cyclic graphs.
- Distributed execution across multiple machines.
- A web UI or dashboard.
- A database.
- Event sourcing.
- A general-purpose agent memory platform.
- Automatic modification of workflow templates based on research.
- Automatic approval of sensitive external actions.
- A full OpenTelemetry / Prometheus / Grafana stack.

The architecture may allow future extensions, but they must not complicate the initial implementation.

---

# 3. Architecture

## 3.1. Main components

Implement the Graph Engine as a separate logical module inside PLS.

Suggested structure:

```text
product_lab_system/
├── graph_engine/
│   ├── models/
│   ├── parser/
│   ├── validation/
│   ├── scheduler/
│   ├── execution/
│   ├── executors/
│   ├── verification/
│   ├── artifacts/
│   ├── persistence/
│   ├── recovery/
│   ├── observability/
│   └── cli/
│
├── workflows/
│   └── ...
│
├── product_lifecycle/
│   └── ...
│
├── tests/
│   └── graph_engine/
│
└── ...
```

The exact package layout may be adapted to the existing repository conventions.

The dependency direction must remain:

```text
Product Lifecycle ───────┐
                         │
Research Loop ───────────┼──> Graph Engine
                         │
Other workflows ─────────┘
```

Graph Engine must not import `product_lifecycle`.

## 3.2. Component responsibilities

| Component | Responsibility |
|---|---|
| Parser | Load YAML templates and create internal models |
| Validator | Validate schema, references, DAG topology and executor configuration |
| Scheduler | Determine which tasks are ready to execute |
| Executor Manager | Resolve and invoke task executors |
| Executor Adapters | Integrate external agents and local tools |
| Verification | Evaluate task completion criteria |
| Artifact Manager | Stage, validate and publish task outputs |
| Persistence | Save run state and attempt records |
| Recovery | Resume interrupted workflows safely |
| Observability | Record structured logs and execution metrics |
| CLI | Expose workflow operations |

Keep these components small and independently testable.

---

# 4. Workflow Model

## 4.1. Static DAG

A workflow is a static directed acyclic graph.

- Nodes represent tasks.
- Edges represent dependencies.
- An edge from A to B means B cannot start until A is successfully completed.
- The graph structure cannot be changed by an executor during a run.
- Conditional behavior is expressed through task results, policies, and downstream readiness—not conditional edges.

Example:

```text
        A
       / \
      B   C
       \ /
        D
```

B and C may execute in parallel after A completes.

D becomes ready only after both B and C complete.

## 4.2. Task definition

A task describes:

- What must be done.
- Which executor type should perform the work.
- Which dependencies must be completed.
- Which artifacts it consumes.
- Which artifacts it produces.
- How completion is verified.
- Whether human approval is required.
- How many retries are allowed.

An agent is not a graph node.

The executor assigned to a task can be changed without changing the workflow structure.

## 4.3. Example workflow YAML

The following is an illustrative target format. The implementer should create and document a formal schema.

```yaml
version: 1

workflow:
  id: example-workflow
  description: Example DAG workflow

execution:
  max_concurrency: 3
  max_retries: 2
  max_run_duration_minutes: 120

tasks:
  - id: research
    type: research
    executor: researcher

    depends_on: []

    inputs: []

    outputs:
      - name: research_report
        path: artifacts/research/report.md

    verification:
      - id: report_exists
        method: command
        command: "test -s artifacts/research/report.md"

    approval: not_required

  - id: implementation
    type: implementation

    depends_on:
      - research

    inputs:
      - name: research_report
        from: research
        artifact: research_report

    outputs:
      - name: implementation_report
        path: artifacts/implementation/report.md

    verification:
      - id: tests_pass
        method: command
        command: "pytest -q"

    approval: not_required

  - id: review
    type: review
    executor: reviewer

    depends_on:
      - implementation

    inputs:
      - name: implementation_report
        from: implementation
        artifact: implementation_report

    outputs:
      - name: review_report
        path: artifacts/review/report.md

    verification:
      - id: review_report_exists
        method: command
        command: "test -s artifacts/review/report.md"

    approval: not_required
```

The schema must be strict and versioned.

Unknown fields should produce a validation error rather than silently being ignored.

---

# 5. Executor Assignment

## 5.1. Task types

A task must declare its `type`.

Examples:

- `research`
- `implementation`
- `review`
- `evaluation`
- `analysis`
- `generic`

These are examples, not a closed list. The engine must permit project-specific task types.

## 5.2. Executor resolution

Use a hybrid deterministic assignment mechanism.

Resolution order:

1. If a task declares an explicit `executor`, use it.
2. Otherwise resolve the executor using project-level mapping `task.type -> executor`.
3. If no mapping exists, fail validation or execution before starting the task.

Example:

```yaml
executors:
  researcher:
    adapter: opencode
    config: {}

  implementer:
    adapter: opencode
    config: {}

  reviewer:
    adapter: opencode
    config: {}

  python:
    adapter: python
    config: {}

executor_mapping:
  research: researcher
  implementation: implementer
  review: reviewer
  evaluation: python
```

No LLM-based executor routing.

## 5.3. Generic executor interface

All adapters must implement the same interface.

Conceptually:

```python
class Executor:
    def execute(
        self,
        task: TaskDefinition,
        context: ExecutionContext,
    ) -> ExecutionResult:
        ...
```

The actual implementation may use synchronous or asynchronous methods, depending on the existing runtime.

`ExecutionResult` must contain at least:

- status
- summary
- produced artifacts
- structured metadata
- error information, if applicable
- usage information, if available

Possible adapters:

- OpenCode
- Claude Code
- Codex
- Python
- Future external executors

Graph Engine must not contain platform-specific logic outside adapters.

An adapter must not directly modify graph state. It returns a result; the engine decides whether to accept it.

---

# 6. Task Execution and Completion

## 6.1. Task lifecycle

Use the following task states:

```text
pending
  |
  v
ready
  |
  v
running
  |
  +------> verifying
  |           |
  |           +------> completed
  |           |
  |           +------> retrying
  |           |
  |           +------> blocked
  |
  +------> failed
```

Additional state:

- `blocked`: the task cannot complete because of an exhausted retry budget, failed dependency, missing approval, or another explicit blocker.
- `skipped`: optional future extension; do not implement unless required by a concrete workflow.

Keep state transitions centralized in the engine.

## 6.2. Completion criteria

Executor success is necessary but not sufficient.

A task becomes `completed` only when:

1. Executor reports successful execution.
2. Required output artifacts exist.
3. Output artifacts pass basic validation.
4. All mandatory verification criteria pass.
5. Any required human approval has been granted.

If any mandatory criterion fails, the task must not be marked completed.

## 6.3. Verification methods

Support three verification methods:

### `command`

Run a configured command and evaluate its exit status.

Commands must be executed using a controlled subprocess interface.

Capture:

- command
- exit code
- stdout
- stderr
- execution duration

### `agent`

Invoke a configured verification executor with a fresh context.

The verifier must receive:

- Task definition
- Acceptance criteria
- Relevant inputs and outputs
- Required evidence

It must not rely solely on the original executor's claims.

### `human`

Pause the workflow until the owner explicitly approves or rejects the result.

Store the decision, timestamp, and optional comment.

All mandatory criteria must pass.

Verification results must be persisted.

---

# 7. Retry Policy

Retries happen inside a task. Do not create new graph nodes for retries.

## 7.1. Rules

- Every attempt must be recorded separately.
- The previous attempt's failure feedback must be passed to the next attempt.
- Each attempt receives a fresh execution context.
- `max_retries` means retries in addition to the initial attempt.
- Therefore, `max_retries: 2` allows at most three total attempts.
- After the retry budget is exhausted, mark the task `blocked`.
- Notify the owner through the available CLI/logging mechanism.

Example:

```text
Attempt 1: failed verification
Attempt 2: failed verification
Attempt 3: failed verification
Task: blocked
```

The engine must not silently increase retry limits.

## 7.2. Retry feedback

The next attempt should receive a concise structured summary:

- Previous attempt number.
- Error or verification failures.
- Relevant logs.
- Missing or invalid artifacts.
- Reviewer feedback, if available.
- Explicit instructions to fix the identified issues.

Do not pass the entire previous conversation by default.

---

# 8. Dependency Scheduling and Parallelism

## 8.1. Ready tasks

A task is ready when:

- Its state is `pending`.
- All dependencies are `completed`.
- Required inputs are available.
- The workflow has not been cancelled.
- Execution limits permit another task to start.

## 8.2. Scheduler behavior

Use automatic DAG scheduling.

At each scheduling cycle:

1. Inspect task states.
2. Identify all ready tasks.
3. Start ready tasks until `max_concurrency` is reached.
4. Wait for task completion or state changes.
5. Recalculate readiness.
6. Continue until no further task can start.

Do not implement manual task ordering beyond DAG dependencies.

## 8.3. Independent branches

A failure must not stop independent branches.

Example:

```text
        A
       / \
      B   C
      |   |
      D   E
```

If B becomes blocked:

- D must become blocked because its dependency cannot complete.
- C and E must continue normally.

This is essential: one failed branch must not unnecessarily stop the whole workflow.

## 8.4. Run terminal states

A run may finish in one of three states:

| State | Meaning |
|---|---|
| `completed` | All required tasks completed |
| `completed_with_blockers` | Execution finished, but one or more tasks remain blocked |
| `failed` | The orchestration itself failed due to a system-level error |

An ordinary task failure must not automatically make the entire run `failed`.

---

# 9. Inputs and Artifacts

## 9.1. File-based handoff

Tasks exchange data through files.

Do not automatically pass all outputs from dependency tasks.

Each input must explicitly identify its source.

Example:

```yaml
inputs:
  - name: research_report
    from: research
    artifact: research_report
```

The engine must validate that:

- The referenced task exists.
- The referenced artifact is declared.
- The source task is a dependency, directly or through a documented dependency policy.
- The artifact is available before execution.

Prefer requiring the source task to be a direct dependency for the initial implementation. This makes data flow explicit and validation straightforward.

## 9.2. Output declaration

Each task must declare its expected outputs.

The engine must validate that required outputs exist and are non-empty when appropriate.

Artifact metadata should include:

- Artifact name.
- Relative path.
- Producing task.
- Producing attempt.
- Creation timestamp.
- File size.
- Checksum.
- Validation status.

## 9.3. Atomic publication

Tasks must write outputs into an attempt-specific temporary directory.

Example:

```text
runs/<run-id>/
  artifacts/
    .staging/
      implementation/
        attempt-1/
    implementation/
```

After successful verification, publish the artifacts into their final location.

Do not expose partially written outputs as completed task artifacts.

Use atomic filesystem operations where supported.

---

# 10. Persistence and Run Directory

Use YAML for workflow definitions and JSON for runtime state.

Do not introduce SQLite or event sourcing.

## 10.1. Suggested run directory

```text
runs/
  <run-id>/
    workflow.yaml
    run.json
    tasks/
      research/
        task.json
        attempts/
          001.json
          002.json
      implementation/
        task.json
        attempts/
          001.json
    artifacts/
      research/
      implementation/
    logs/
      events.jsonl
    metrics.json
```

Adapt naming and placement to repository conventions, but preserve the logical separation.

## 10.2. Run snapshot

At run creation, copy the exact workflow YAML into the run directory.

The snapshot is immutable for the lifetime of that run.

Record:

- Workflow ID and version.
- Workflow snapshot path.
- Git SHA.
- Engine version.
- Executor configuration snapshot/version.
- Creation timestamp.
- Execution limits.

A later change to the original YAML must not change an existing run.

## 10.3. Run state example

```json
{
  "run_id": "example-run",
  "workflow_id": "example-workflow",
  "status": "running",
  "created_at": "2026-10-31T10:00:00Z",
  "started_at": "2026-10-31T10:00:01Z",
  "finished_at": null,
  "git_sha": "abc123",
  "workflow_snapshot": "workflow.yaml",
  "execution": {
    "max_concurrency": 3,
    "max_retries": 2,
    "max_run_duration_minutes": 120
  },
  "tasks": {
    "research": "completed",
    "implementation": "running",
    "review": "pending"
  }
}
```

This is illustrative; define typed internal models and validate persisted data.

## 10.4. Atomic state updates

State writes must be crash-safe where possible:

1. Write new content to a temporary file.
2. Flush and close it.
3. Replace the previous file atomically.

Do not leave partially written JSON as the only copy of run state.

---

# 11. Recovery and Resume

The engine must support resuming interrupted runs.

## 11.1. Resume rules

On resume:

1. Load the persisted run state.
2. Validate the workflow snapshot.
3. Inspect task states and attempt records.
4. Reconcile interrupted `running` or `verifying` tasks.
5. Reuse artifacts from successfully completed and verified tasks.
6. Schedule remaining eligible tasks.

A task may be reused only if its completion state and required artifacts are trustworthy.

Incomplete attempts must never be treated as successful.

## 11.2. External side effects

The engine cannot guarantee exactly-once execution of external actions.

For operations such as API calls, publishing, sending messages, or deployments:

- Use idempotency keys when supported.
- Check whether an action already occurred before repeating it when possible.
- Record external action identifiers.
- If safe recovery cannot be established, stop and require human intervention.

Never silently repeat potentially destructive actions.

## 11.3. Recovery consistency

A run must not be resumed against a different workflow definition.

Use the immutable snapshot.

Executor configuration changes must also be detected and handled explicitly rather than silently applied.

---

# 12. Human Approval and Safety

Human approval is opt-in at the task level.

Example:

```yaml
approval: required
```

When required:

1. Execute the task.
2. Run applicable verification.
3. Pause before final completion or before the protected action, according to the task's defined approval point.
4. Record the owner's decision.
5. Continue only after approval.

The implementation must clearly define whether approval is required before execution or before publishing/committing an output. Support the latter as the default for reviewable deliverables.

Global PLS safety rules override workflow settings.

In particular:

- No push without explicit owner approval.
- No merge without explicit owner approval.
- No deployment without explicit owner approval.

An executor cannot grant its own approval.

---

# 13. Agent Context and Collaboration

## 13.1. Fresh context

Every task and every retry receives a fresh agent context.

Do not reuse the previous agent conversation as implicit memory.

The engine should provide an explicit context package containing:

- Task definition.
- Acceptance criteria.
- Declared input artifacts.
- Relevant project instructions.
- Explicit memory/document references.
- Previous attempt feedback, if retrying.
- Output requirements.

The context package must be reproducible and inspectable.

## 13.2. Implementer-reviewer pattern

When a workflow requires independent review:

- Implementer and reviewer are separate executor runs.
- Reviewer receives a fresh context.
- Reviewer independently examines the implementation, diff, acceptance criteria, and relevant tests.
- Reviewer must not rely solely on the implementer's summary.
- Reviewer returns a structured result with findings and evidence.

The implementer may fix defects and submit another attempt for review.

Use the existing PLS policy:

- Implementer fixes reviewer findings.
- Reviewer rechecks.
- After three review cycles, or when disagreement is systemic, escalate to the owner.

Do not force a reviewer node after every task. Review is defined by the workflow where necessary.

## 13.3. Structured agent results

Agent adapters should return machine-readable results.

Suggested structure:

```json
{
  "status": "success",
  "summary": "Implementation completed",
  "artifacts": [
    {
      "name": "implementation_report",
      "path": "artifacts/implementation/report.md"
    }
  ],
  "metadata": {
    "executor": "opencode"
  },
  "usage": {
    "input_tokens": null,
    "output_tokens": null,
    "estimated_cost": null
  }
}
```

The engine must validate returned data before accepting it.

---

# 14. Observability

Implement structured execution metrics and logs.

Do not introduce a separate observability platform.

## 14.1. Events

Record at least:

- Run created.
- Run started.
- Run completed.
- Run failed.
- Run resumed.
- Task ready.
- Task started.
- Task attempt completed.
- Verification started.
- Verification completed.
- Task completed.
- Task blocked.
- Approval requested.
- Approval granted or rejected.
- Artifact published.

Store event records in JSON Lines format.

## 14.2. Metrics

Record per run and per task:

- Duration.
- Number of attempts.
- Retry count.
- Verification results.
- Executor used.
- Token usage, if reported.
- Estimated cost, if reported.
- Number of blocked tasks.
- Failure reasons.
- Artifact metadata.

Do not invent token usage or costs when the executor cannot report them. Use `null` or mark them unavailable.

## 14.3. Metrics file

Provide a machine-readable `metrics.json` summary per run.

The format should support future aggregation across runs without requiring a database.

---

# 15. Execution Limits

Support the following configuration:

```yaml
execution:
  max_concurrency: 3
  max_retries: 2
  max_run_duration_minutes: 120
```

Rules:

- `max_concurrency` is enforced by the scheduler.
- `max_retries` is enforced by the engine.
- `max_run_duration_minutes` is enforced by the run controller.
- An executor prompt is not a substitute for enforcement.

If the run duration limit is reached:

- Stop scheduling new tasks.
- Request cancellation of running tasks where supported.
- Persist state.
- Leave the run recoverable.
- Record the reason.

Optional token and cost limits may be added only if executor usage data is available and reliable. Do not make them mandatory for the initial implementation.

---

# 16. CLI

The CLI is the only initial user-facing interface to Graph Engine.

Suggested commands:

```bash
pls graph validate <workflow>
pls graph run <workflow>
pls graph status <run-id>
pls graph resume <run-id>
pls graph cancel <run-id>
```

## 16.1. `validate`

Must:

- Parse the YAML.
- Validate schema and required fields.
- Check task IDs and references.
- Check artifact declarations.
- Validate executor resolution.
- Detect cycles.
- Validate verification definitions.
- Check execution limits.

Return a non-zero exit code for invalid workflows.

## 16.2. `run`

Must:

- Validate the workflow.
- Create a run directory.
- Snapshot the workflow and executor configuration.
- Initialize run state.
- Start the scheduler.
- Persist state and events throughout execution.
- Return the final run status and run ID.

## 16.3. `status`

Display:

- Run status.
- Task status.
- Current attempts.
- Blocked tasks and reasons.
- Recent events.
- Metrics summary.

## 16.4. `resume`

Resume a persisted run according to the recovery rules.

Do not silently overwrite its workflow snapshot.

## 16.5. `cancel`

Stop scheduling new work, request cancellation of active tasks where supported, persist state, and leave the run in a recoverable state.

Define a clear cancellation state or status field in the internal model.

---

# 17. Error Handling

Distinguish between:

1. Task execution failure.
2. Verification failure.
3. Missing or invalid artifact.
4. Dependency failure.
5. Executor configuration failure.
6. Human approval rejection.
7. Orchestration/system failure.
8. Run timeout.
9. Cancellation.

Every failure must have:

- A machine-readable category.
- A human-readable message.
- Timestamp.
- Task and attempt references where applicable.
- Relevant diagnostic information.

Do not swallow exceptions.

A task failure must not crash the entire scheduler.

A scheduler or persistence failure must be surfaced as a run-level failure and preserve as much recoverable state as possible.

---

# 18. Research Loop Compatibility

Research Loop must be implemented as a normal workflow using Graph Engine.

It must not require special engine logic.

The workflow can support:

- Targeted research before a relevant implementation task.
- Periodic monthly review of publications and observed problems.
- Deeper quarterly evaluation.
- Hypothesis creation.
- Experiment design and execution.
- Evidence collection.
- Explicit decision to adopt, reject, or defer an improvement.

Research findings must not automatically modify Graph Engine architecture or workflow templates.

A research artifact should distinguish evidence levels:

- **A — Abstract:** only abstract or summary reviewed.
- **F — Full text:** full paper or article reviewed.
- **C — Code:** associated code, configuration, or model inspected.
- **E — Experiment:** independently reproduced or tested.

The workflow should record sources, evidence level, hypothesis, expected benefit, experiment result, and decision.

This is workflow policy, not a special feature of the engine.

---

# 19. Testing Strategy

Implement tests at several levels.

## 19.1. Unit tests

At minimum:

- YAML parsing.
- Schema validation.
- Duplicate task IDs.
- Missing dependencies.
- Missing artifact references.
- Cycle detection.
- Executor resolution.
- Task state transitions.
- Retry accounting.
- Verification evaluation.
- Artifact validation.
- Atomic state persistence.
- Run terminal-state calculation.
- Metrics aggregation.

## 19.2. Scheduler tests

Test:

1. Sequential tasks.
2. Independent parallel tasks.
3. Fan-out and fan-in.
4. Concurrency limit enforcement.
5. Independent branches continuing after failure.
6. Downstream tasks blocked after dependency failure.
7. Multiple simultaneously ready tasks.
8. Run timeout.
9. Cancellation.

Use deterministic mock executors. Do not rely on external LLM services for scheduler tests.

## 19.3. Recovery tests

Test:

- Resume after process interruption.
- Reuse of completed tasks.
- Rejection of incomplete attempts as successful results.
- Recovery of interrupted tasks.
- Missing artifact detection.
- Workflow snapshot immutability.
- Detection of incompatible executor configuration.
- Safe handling of potentially repeated external actions.

## 19.4. Executor adapter tests

Test each adapter independently with mocked external processes or APIs.

Validate:

- Input context construction.
- Result parsing.
- Error handling.
- Cancellation behavior where supported.
- Usage metadata handling.

## 19.5. End-to-end test

Create a small workflow using mock executors:

```text
A: Generate artifact
      |
      +------+
      |      |
B: Process  C: Review
      |      |
      +------+
         |
D: Finalize
```

Verify:

- B and C execute in parallel.
- D waits for both.
- All artifacts are correctly passed.
- A failed task triggers retry.
- An exhausted retry budget blocks downstream tasks.
- Independent branches continue.
- The run reaches the correct terminal state.
- The run can be resumed after simulated interruption.
- Metrics and event logs are complete.

No paid external agent service should be required to run this test suite.

---

# 20. Acceptance Criteria

Implementation is accepted only when all mandatory criteria below are satisfied.

## A. Architecture

- [ ] Graph Engine exists as a separate logical module.
- [ ] It has no imports from `product_lifecycle`.
- [ ] Product Lifecycle can invoke it through a stable interface.
- [ ] No product-specific business logic exists inside the engine.

## B. Workflow validation

- [ ] YAML workflows can be loaded and validated.
- [ ] Invalid schemas are rejected.
- [ ] Missing references are rejected.
- [ ] Cycles are detected and rejected.
- [ ] Executor resolution is deterministic.
- [ ] Invalid workflows cannot start.

## C. Execution

- [ ] Tasks execute according to DAG dependencies.
- [ ] Independent tasks execute in parallel.
- [ ] `max_concurrency` is enforced.
- [ ] Failed branches do not stop independent branches.
- [ ] Downstream tasks cannot execute after dependency failure.

## D. Verification and retries

- [ ] All mandatory completion criteria are enforced.
- [ ] Command, agent, and human verification methods work.
- [ ] Every attempt is persisted.
- [ ] Retry feedback reaches the next attempt.
- [ ] Retry limits are enforced.
- [ ] Exhausted tasks become blocked.

## E. Data and artifacts

- [ ] Inputs are explicitly declared.
- [ ] Undeclared dependency outputs are not passed automatically.
- [ ] Required artifacts are validated.
- [ ] Artifacts are published only after successful verification.
- [ ] Artifact metadata includes checksums and provenance.

## F. Persistence and recovery

- [ ] Run state is stored in JSON.
- [ ] Workflow templates are stored in YAML.
- [ ] Writes are atomic where supported.
- [ ] Each run has an immutable workflow snapshot.
- [ ] Completed verified tasks can be reused after interruption.
- [ ] Incomplete attempts are never reused as completed tasks.
- [ ] Unsafe external side effects are not silently repeated.

## G. Agent collaboration

- [ ] Executor adapters implement a common interface.
- [ ] Each task and retry receives a fresh context.
- [ ] Context includes only declared inputs and relevant references.
- [ ] Implementer and reviewer can run independently.
- [ ] Reviewer feedback can be used in a subsequent implementation attempt.

## H. Safety

- [ ] Human approval can be required per task.
- [ ] Executors cannot approve their own actions.
- [ ] Push, merge, and deploy remain protected by owner approval.
- [ ] Execution limits are enforced by the engine.

## I. Observability

- [ ] Structured JSONL events are recorded.
- [ ] Per-run metrics are persisted.
- [ ] Durations and retry counts are available.
- [ ] Verification results and failure reasons are recorded.
- [ ] Executor usage and estimated cost are recorded when available.
- [ ] Missing usage data is represented honestly.

## J. CLI and quality

- [ ] `validate`, `run`, `status`, `resume`, and `cancel` work.
- [ ] Unit tests pass.
- [ ] Scheduler tests pass.
- [ ] Recovery tests pass.
- [ ] End-to-end test passes.
- [ ] Documentation explains workflow format and operational behavior.

A skipped mandatory test is not a PASS.

---

# 21. Implementation Plan

Implement in small, independently verifiable stages.

Do not attempt to build the entire engine in one large change.

## Stage 0 — Repository inspection and implementation plan

- Inspect current repository structure and conventions.
- Inspect existing CLI, configuration, logging, and testing infrastructure.
- Inspect `research/` and other potentially reusable modules.
- Identify reusable components without modifying unrelated legacy code.
- Propose exact module layout and implementation sequence.
- Identify dependencies and compatibility constraints.

**Deliverable:** implementation plan with file-level changes and acceptance mapping.

Stop for owner review if implementation requires changes outside the approved scope.

## Stage 1 — Core models and workflow validation

Implement:

- Typed workflow models.
- YAML parser.
- Schema validation.
- Task and artifact references.
- DAG validation and cycle detection.
- Executor resolution.

**Verification:** unit tests for all validation rules.

## Stage 2 — Persistence and artifact management

Implement:

- Run directory creation.
- Workflow snapshots.
- Run and task state JSON.
- Attempt records.
- Atomic persistence.
- Artifact staging and publication.
- Checksums and metadata.

**Verification:** persistence and artifact tests.

## Stage 3 — Executor interface and mock executor

Implement:

- Generic executor interface.
- Execution context.
- Execution result.
- Executor registry.
- Mock executor.
- Error normalization.

**Verification:** adapter contract tests.

Do not integrate real external agents before the generic interface is stable.

## Stage 4 — Scheduler and execution engine

Implement:

- Dependency readiness.
- Parallel scheduling.
- Concurrency limits.
- Task lifecycle.
- Run lifecycle.
- Independent branch continuation.
- Downstream blocking.

**Verification:** deterministic scheduler tests.

## Stage 5 — Verification, retries, and approvals

Implement:

- Command verification.
- Agent verification interface.
- Human verification mechanism.
- Retry policy.
- Feedback construction.
- Approval gates.

**Verification:** task completion and retry tests.

## Stage 6 — Recovery and safety

Implement:

- Resume.
- Interrupted-task reconciliation.
- Completed-task reuse.
- Artifact consistency checks.
- Run timeout.
- Cancellation.
- External side-effect safeguards.

**Verification:** recovery and interruption tests.

## Stage 7 — Observability and CLI

Implement:

- Structured event logging.
- Metrics aggregation.
- CLI commands.
- Status reporting.
- Operational documentation.

**Verification:** CLI and observability tests.

## Stage 8 — Real executor integration and E2E

Integrate the first real executor adapter, preferably the one already used by the PLS development workflow.

Then run the full mock-based E2E suite and a small real-agent workflow.

**Verification:** complete acceptance checklist.

---

# 22. Implementation Governance

Follow the existing PLS implementer-reviewer policy.

1. The implementer creates a plan for each stage.
2. The owner approves the overall implementation plan once.
3. The implementer executes checkable stages automatically.
4. The reviewer runs in a separate independent context.
5. The reviewer examines the actual diff and acceptance criteria.
6. The reviewer independently runs relevant tests.
7. GPU or external-service checks are required only when relevant and available; skipped mandatory checks are not PASS.
8. The implementer fixes defects and requests another review.
9. After three review cycles or systemic disagreement, escalate to the owner.
10. Stop on blockers or material scope changes.

Repository safety:

- Local commits are allowed.
- Do not push.
- Do not merge.
- Do not deploy.
- Do not close issues.
- Do not modify unrelated legacy modules.

These actions require explicit owner approval.

Every completed stage must record:

- Commit SHA, if committed.
- Changed files.
- Tests executed.
- Test results.
- Reviewer findings.
- Remaining blockers.
- Acceptance criteria status.

---

# 23. Definition of Done

Graph Engine MVP is done when:

1. All mandatory acceptance criteria pass.
2. The full automated test suite passes.
3. A mock-based E2E workflow executes correctly.
4. A real executor can execute a small workflow through the generic interface.
5. A run can be interrupted and safely resumed.
6. Structured logs and metrics are available.
7. CLI documentation is complete.
8. Independent reviewer reports PASS.
9. No unapproved changes to legacy code or external systems were made.

Do not add a dashboard, database, distributed runtime, dynamic graph generation, or other future capabilities to achieve MVP completion.

**Final implementation principle: build the smallest reliable DAG execution engine that can run PLS workflows. Keep orchestration generic, workflow policy declarative, agent behavior behind adapters, and all important execution decisions observable and recoverable.**
