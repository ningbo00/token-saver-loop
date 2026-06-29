# Reviewer Continue Bootstrap

This file is the stable bootstrap for a fresh reviewer thread in kit mode.

## Copy/Paste Prompt

```text
Continue the project that contains this token-saver-kit. Read the kit's REVIEWER_CONTINUE.md and follow it. Keep context lean.
```

## Fresh Thread Protocol

1. Keep context lean.
2. Read only these files first:
   - `token-saver-kit/START_HERE.md`
   - `token-saver-kit/.ai/active_task/state.md`
   - `token-saver-kit/.ai/active_task/progress.md`
3. Then inspect only the latest round artifacts named by state:
   - `token-saver-kit/.ai/active_task/rounds/round_*/reviewer_review.md`
   - `token-saver-kit/.ai/active_task/rounds/round_*/verdict.json`
   - `token-saver-kit/.ai/active_task/rounds/round_*/worker_report.json`
4. Run `git status --short` and `git diff --stat HEAD` in the parent project root.
5. Continue from the `Next action` section in `token-saver-kit/.ai/active_task/state.md`.
6. Use `progress.md` only as navigation; do not decide pass, release readiness, or bug correctness from it.
7. Trust tests, diff, latest reports, and files over chat history, `progress.md`, or model claims.
8. If handing work to the worker, update `token-saver-kit/WORKER_NEXT_TASK.md` with a bounded round, required test evidence, and git archive limits.
9. If reviewing worker work, verify diff/tests/logs; rerun key tests for T1, release, commit, security/data work, or suspicious reports.

## Reviewer Role Boundary

- Act as reviewer/planner only.
- Do not modify parent-project source code directly.
- You may update kit workflow files and use `token-saver-kit/tools/` only for bookkeeping.
- If implementation is needed, create a bounded worker task and hand it to the worker model.
- Accept work only from evidence: tests, diffs, reports, and changed files.

## Rotation Rules

- Start a fresh reviewer thread after commits, phase boundaries, release decisions, or 2-3 clean worker passes.
- Do not start a fresh reviewer thread for every same-tier fix.
- Prefer a fresh worker conversation/process per round when handoff files are current.
- The worker should follow repo handoff files, not long-term chat memory.
- The worker may collect test and git evidence, but reviewer/user own final acceptance and git history unless explicitly delegated.


