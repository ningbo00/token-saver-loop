# Kimi Codex Loop

This kit provides a semi-automatic workflow where Codex plans/reviews and KimiCode implements in bounded rounds.

## Kit mode

In kit mode:
- The kit lives inside a parent project (the project being worked on).
- Workflow state lives inside `kimi-codex-kit/.ai/active_task/`.
- Scripts are run from the parent project root, but paths are resolved relative to the kit directory.

## Files

- `tools/ai-kimi-init.ps1` initializes `kimi-codex-kit/.ai/active_task/`.
- `tools/ai-kimi-run.ps1` creates a numbered Kimi round, runs Kimi when available, and captures artifacts.
- `tools/ai-kimi-review-pack.ps1` prints the latest compact review pack.
- `tools/ai-kimi-verdict.ps1` records a Codex review verdict.

## Basic Flow

Initialize a task:

```powershell
powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-init.ps1 -Task "Implement X" -Tier T2 -TestCommands "npm test"
```

Run Kimi:

```powershell
powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-run.ps1
```

Prepare review summary:

```powershell
powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-review-pack.ps1
```

Then ask Codex to review `kimi-codex-kit/.ai/active_task/state.md` and the latest round artifacts.

Record verdict:

```powershell
powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-verdict.ps1 -Verdict downgrade -CurrentTier T2 -NextTier T1 -Reasons "scope violation","tests missing"
```

## Tiers

- `T3`: free execution for low-risk docs, tests, styles, and small features.
- `T2`: bounded execution for ordinary local fixes.
- `T1`: instruction execution for precise or failed tasks.
- `T0`: no implementation; inspect and report only.

Trust `git diff`, tests, and file contents over Kimi's explanation.


## Testing Responsibility Split

Kimi may own routine test execution and evidence collection; Codex owns acceptance.

- Kimi should run the requested test commands, record exact commands/results, and save evidence in round artifacts.
- Kimi may add or improve tests in T2/T3 rounds when coverage is weak and the scope allows it.
- Codex does not need to rerun every Kimi test for low-risk clean rounds, but must verify the report against diff and logs.
- Codex should rerun key tests for T1 work, release decisions, commits, installer/security/data logic, or any suspicious report/diff mismatch.
- Never accept a green run if tests were weakened, skipped, or changed without a clear reason.

## Git Archive Responsibility Split

Kimi may prepare git evidence, but Codex/user own repository history by default.

- Kimi may run read-only git commands, save diffstats/patches, and draft commit messages or release notes.
- Kimi must not run `git commit`, `git tag`, `git push`, `git reset`, `git checkout`, or amend commits unless Codex/user explicitly allows that exact action.
- If commit delegation is explicitly allowed later, Kimi must stage only Codex-specified files, make a local commit only, and report `git show --stat --oneline HEAD`.
- Destructive history or working-tree operations remain forbidden by default.

## Dynamic Batch Size

Use dynamic batch rounds to reduce Codex review overhead:

- Increase Kimi's batch size after clean passes with matching reports, passing tests, and no scope drift.
- Reduce batch size and communicate more often after unclear failures, missing tests, report mismatch, scope drift, or safety concerns.
- Larger batches must still be small-step execution: checkpoint, validate, log, then continue.
- Do not turn a batch into one large leap. Prefer 3-5 related subtasks with per-subtask acceptance checks.

## Conversation / Process Rotation

Use rotation to reduce token bloat without losing source-of-truth context:

- Codex: start a fresh Codex thread after a git commit, phase boundary, release decision, or 2-3 clean Kimi passes.
- Codex: do not start a fresh thread for every small same-tier fix; restart overhead can exceed savings.
- Kimi: prefer a fresh Kimi conversation/process per round when `KIMI_NEXT_TASK.md` or `kimi-codex-kit/.ai/active_task/*` handoff files are current.
- Kimi: reuse the same conversation only for immediate same-round retries or tool debugging.
- Source of truth: repo files, latest round artifacts, tests, and Codex handoff. Do not rely on chat memory for requirements.

## User Progress Board

Kimi should update `kimi-codex-kit/.ai/active_task/progress.md` at the end of every round.

- Purpose: give the user a cheap, approximate view of where development stands.
- Codex may use it only as navigation for what to inspect next.
- Keep it concise: current position, completed work, next work, rough remaining work, last update.
- Do not store full thinking, old logs, or detailed chain-of-thought.
- It is not a source of truth. Codex must not decide pass, release readiness, or bug correctness from it.
- Codex still verifies with state, latest reports, diff, tests, and files.
