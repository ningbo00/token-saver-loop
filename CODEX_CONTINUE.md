# Codex Continue Bootstrap

This file is the stable bootstrap for a fresh Codex thread.

## Copy/Paste Prompt

```text
继续 G:\AI\BaiduSyncdisk\Gpt2Whatever 项目。请读取仓库根目录的 CODEX_CONTINUE.md 并照做，保持低 token，不要读取完整历史聊天。
```

## Fresh Thread Protocol

1. Keep context lean.
2. Read only these files first:
   - `AGENTS.md`
   - `docs/AGENT_CONTEXT.md`
   - `docs/REPO_MAP.md`
   - `.ai/active_task/state.md`
3. Then inspect only the latest round artifacts named by `.ai/active_task/state.md`:
   - `codex_review.md`
   - `verdict.json`
   - `kimi_report.json`
   - `kimi_log.md` only if report/diff raises questions
4. Run `git status --short` and `git diff --stat HEAD`.
5. Continue from the `Next action` section in `.ai/active_task/state.md`.
6. Trust tests, diff, and files over chat history or model claims.
7. If handing work to Kimi, update `KIMI_NEXT_TASK.md` with a bounded round.
8. If reviewing Kimi work, run `python -m unittest discover -s tests -v` unless clearly unnecessary.

## Rotation Rules

- Start a fresh Codex thread after commits, phase boundaries, release decisions, or 2-3 clean Kimi passes.
- Do not start a fresh Codex thread for every same-tier fix.
- Prefer a fresh Kimi conversation/process per round when handoff files are current.
- Kimi should follow repo handoff files, not long-term chat memory.
