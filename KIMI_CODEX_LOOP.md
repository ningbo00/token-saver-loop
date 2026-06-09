# Kimi Codex Loop

This repo contains a semi-automatic workflow where Codex plans/reviews and KimiCode implements in bounded rounds.

## Files

- `tools/ai-kimi-init.ps1` initializes `.ai/active_task/`.
- `tools/ai-kimi-run.ps1` creates a numbered Kimi round, runs Kimi when available, and captures artifacts.
- `tools/ai-kimi-review-pack.ps1` prints the latest compact review pack.
- `tools/ai-kimi-verdict.ps1` records a Codex review verdict.

## Basic Flow

Initialize a task:

```powershell
powershell -ExecutionPolicy Bypass -File tools/ai-kimi-init.ps1 -Task "Implement X" -Tier T2 -TestCommands "npm test"
```

Run Kimi:

```powershell
powershell -ExecutionPolicy Bypass -File tools/ai-kimi-run.ps1
```

Prepare review summary:

```powershell
powershell -ExecutionPolicy Bypass -File tools/ai-kimi-review-pack.ps1
```

Then ask Codex to review `.ai/active_task/state.md` and the latest round artifacts.

Record verdict:

```powershell
powershell -ExecutionPolicy Bypass -File tools/ai-kimi-verdict.ps1 -Verdict downgrade -CurrentTier T2 -NextTier T1 -Reasons "scope violation","tests missing"
```

## Tiers

- `T3`: free execution for low-risk docs, tests, styles, and small features.
- `T2`: bounded execution for ordinary local fixes.
- `T1`: instruction execution for precise or failed tasks.
- `T0`: no implementation; inspect and report only.

Trust `git diff`, tests, and file contents over Kimi's explanation.

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
- Kimi: prefer a fresh Kimi conversation/process per round when `KIMI_NEXT_TASK.md` or `.ai/active_task/*` handoff files are current.
- Kimi: reuse the same conversation only for immediate same-round retries or tool debugging.
- Source of truth: repo files, latest round artifacts, tests, and Codex handoff. Do not rely on chat memory for requirements.
