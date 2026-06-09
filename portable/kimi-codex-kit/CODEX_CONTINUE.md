# Codex Continue Bootstrap

This file is the stable bootstrap for a fresh Codex thread in kit mode.

## Copy/Paste Prompt

```text
Continue the project that contains this kimi-codex-kit. Read the kit's CODEX_CONTINUE.md and follow it. Keep context lean.
```

## Fresh Thread Protocol

1. Keep context lean.
2. Read only these files first:
   - `kimi-codex-kit/START_HERE.md`
   - `kimi-codex-kit/.ai/active_task/state.md`
   - `kimi-codex-kit/.ai/active_task/progress.md`
3. Then inspect only the latest round artifacts named by state:
   - `kimi-codex-kit/.ai/active_task/rounds/round_*/codex_review.md`
   - `kimi-codex-kit/.ai/active_task/rounds/round_*/verdict.json`
   - `kimi-codex-kit/.ai/active_task/rounds/round_*/kimi_report.json`
4. Run `git status --short` and `git diff --stat HEAD` in the parent project root.
5. Continue from the `Next action` section in `kimi-codex-kit/.ai/active_task/state.md`.
6. Use `progress.md` only as navigation; do not decide pass, release readiness, or bug correctness from it.
7. Trust tests, diff, latest reports, and files over chat history, `progress.md`, or model claims.
8. If handing work to Kimi, update `kimi-codex-kit/KIMI_NEXT_TASK.md` with a bounded round, required test evidence, and git archive limits.
9. If reviewing Kimi work, verify diff/tests/logs; rerun key tests for T1, release, commit, installer/security/data work, or suspicious reports.

## Rotation Rules

- Start a fresh Codex thread after commits, phase boundaries, release decisions, or 2-3 clean Kimi passes.
- Do not start a fresh Codex thread for every same-tier fix.
- Prefer a fresh Kimi conversation/process per round when handoff files are current.
- Kimi should follow repo handoff files, not long-term chat memory.
- Kimi may collect test and git evidence, but Codex/user own final acceptance and git history unless explicitly delegated.
