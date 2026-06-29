# Token Saver Loop

This kit provides a semi-automatic workflow where a reviewer model plans/reviews and a worker model implements in bounded rounds. Both roles are model-agnostic; the worker can be any compatible CLI/model that follows the prompt and writes the required reports.

## Kit mode

In kit mode:
- The kit lives inside a parent project (the project being worked on).
- Workflow state lives inside `token-saver-kit/.ai/active_task/`.
- Scripts are run from the parent project root, but paths are resolved relative to the kit directory.

## Files

- `tools/tsl-init.ps1` initializes `token-saver-kit/.ai/active_task/`.
- `tools/tsl-run.ps1` creates a numbered worker round, runs the configured worker command when available, and captures artifacts.
- `tools/tsl-review-pack.ps1` prints the latest compact review pack.
- `tools/tsl-verdict.ps1` records a reviewer verdict.

## Basic Flow

Initialize a task:

```powershell
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-init.ps1 -Task "Implement X" -Tier T2 -TestCommands "npm test"
```

Run the worker:

```powershell
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-run.ps1
# Or choose another compatible worker CLI
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-run.ps1 -WorkerCommand deepseek
```

Prepare review summary:

```powershell
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-review-pack.ps1
```

Then ask the reviewer to review `token-saver-kit/.ai/active_task/state.md` and the latest round artifacts.

Record verdict:

```powershell
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-verdict.ps1 -Verdict downgrade -CurrentTier T2 -NextTier T1 -Reasons "scope violation","tests missing"
```

## Tiers

- `T3`: free execution for low-risk docs, tests, styles, and small features.
- `T2`: bounded execution for ordinary local fixes.
- `T1`: instruction execution for precise or failed tasks.
- `T0`: no implementation; inspect and report only.

Trust `git diff`, tests, and file contents over the worker's explanation.


## Testing Responsibility Split

The worker may own routine test execution and evidence collection; the reviewer owns acceptance.

- The worker should run the requested test commands, record exact commands/results, and save evidence in round artifacts.
- The worker may add or improve tests in T2/T3 rounds when coverage is weak and the scope allows it.
- The reviewer does not need to rerun every worker test for low-risk clean rounds, but must verify the report against diff and logs.
- The reviewer should rerun key tests for T1 work, release decisions, commits, security/data logic, or any suspicious report/diff mismatch.
- Never accept a green run if tests were weakened, skipped, or changed without a clear reason.

## Git Archive Responsibility Split

The worker may prepare git evidence, but the reviewer/user own repository history by default.

- The worker may run read-only git commands, save diffstats/patches, and draft commit messages or release notes.
- The worker must not run `git commit`, `git tag`, `git push`, `git reset`, `git checkout`, or amend commits unless the reviewer/user explicitly allows that exact action.
- If commit delegation is explicitly allowed later, the worker must stage only reviewer-specified files, make a local commit only, and report `git show --stat --oneline HEAD`.
- Destructive history or working-tree operations remain forbidden by default.

## Dynamic Batch Size

Use dynamic batch rounds to reduce reviewer overhead:

- Increase the worker's batch size after clean passes with matching reports, passing tests, and no scope drift.
- Reduce batch size and communicate more often after unclear failures, missing tests, report mismatch, scope drift, or safety concerns.
- Larger batches must still be small-step execution: checkpoint, validate, log, then continue.
- Do not turn a batch into one large leap. Prefer 3-5 related subtasks with per-subtask acceptance checks.

## Conversation / Process Rotation

Use rotation to reduce token bloat without losing source-of-truth context:

- Reviewer: start a fresh reviewer thread after a git commit, phase boundary, release decision, or 2-3 clean worker passes.
- Reviewer: do not start a fresh thread for every small same-tier fix; restart overhead can exceed savings.
- Worker: prefer a fresh worker conversation/process per round when `WORKER_NEXT_TASK.md` or `token-saver-kit/.ai/active_task/*` handoff files are current.
- Worker: reuse the same conversation only for immediate same-round retries or tool debugging.
- Source of truth: repo files, latest round artifacts, tests, and reviewer handoff. Do not rely on chat memory for requirements.

## User Progress Board

The worker should update `token-saver-kit/.ai/active_task/progress.md` at the end of every round.

- Purpose: give the user a cheap, approximate view of where development stands.
- The reviewer may use it only as navigation for what to inspect next.
- Keep it concise: current position, completed work, next work, rough remaining work, last update.
- Do not store full thinking, old logs, or detailed chain-of-thought.
- It is not a source of truth. The reviewer must not decide pass, release readiness, or bug correctness from it.
- The reviewer still verifies with state, latest reports, diff, tests, and files.


