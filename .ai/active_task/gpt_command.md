# GPT Task Command For Kimi

If you are unsure what to do, open `KIMI_NEXT_TASK.md` at the repository root and execute it.

Shortcut phrase from user: `读取GPT命令`

## Critical Instruction

This file is **not** asking you to summarize CLI commands, argparse help, README commands, or token lookup commands.

When the user says `读取GPT命令`, your job is to **execute the current Kimi-Codex task below**, not to report available project commands.

## Current Command

Use the `kimi-codex-worker` skill and run the narrow same-tier Round 011 fix.

## Read First

- `.ai/active_task/state.md`
- `.ai/active_task/codex_plan.md`
- `.ai/active_task/rounds/round_010/codex_review.md`
- `.ai/active_task/rounds/round_010/verdict.json`
- `.kimi-code/skills/kimi-codex-worker/SKILL.md`

## Important Context

- There is already an accidental `.ai/active_task/rounds/round_011/` directory created by a prior `-NoRun` validation.
- Reuse `.ai/active_task/rounds/round_011/` for this fix round. Do not create `round_012` unless explicitly instructed by Codex or the user.

## Goal

Fix Round 010 workflow artifact issues only.

## Required Fixes

1. Fix `tools/ai-kimi-run.ps1` so safe validation/dry-run checks do not pollute the real round sequence by default.
2. Include `tests.txt` in `state.md` Latest artifacts when the runner captures it.
3. Add a short trusted-input comment/note for workflow test command execution, or constrain it if a small safe patch is obvious.
4. Handle the accidental `.ai/active_task/rounds/round_011` prompt artifact safely. Do not delete user data; if cleanup is ambiguous, report and leave it.

## Validation

- Run `python -m unittest discover -s tests -v`.
- Run a PowerShell validation that does not create another real round.

## Limits

- Tier: T2.
- Max changed files: 4.
- Do not implement installer behavior.
- Do not add dependencies.
- Do not commit.
- Do not delete user data.

## Required Reports

- `.ai/active_task/rounds/round_011/kimi_log.md`
- `.ai/active_task/rounds/round_011/kimi_report.json`
