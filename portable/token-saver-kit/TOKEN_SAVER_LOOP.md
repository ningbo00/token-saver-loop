# Token Saver Loop

This kit keeps reviewer planning and worker execution separated. The user only
needs short prompts; detailed rules live in `START_HERE.md` and `skills/`.

## Source Of Truth

- Reviewer rules: `skills/reviewer.md`
- Worker rules: `skills/worker.md`
- Current worker task: `WORKER_NEXT_TASK.md`
- Active task state: `.ai/active_task/`
- Round evidence: `.ai/active_task/rounds/round_NNN/`

## Tool Model

Tools are optional bookkeeping helpers for AI agents and advanced users. They are
not installers and are not required for manual use.

| Tool | Purpose |
|---|---|
| `tsl-new-round.ps1` | Create the next worker handoff prompt. |
| `tsl-latest.ps1` | Find latest round paths without guessing `round_NNN`. |
| `tsl-review.ps1` | Summarize latest worker evidence for reviewer inspection. |
| `tsl-redflags.ps1` | Detect common evidence/scope/generated-file issues. |
| `tsl-doctor.ps1` | Check kit health. |
| `tsl-archive.ps1` | Archive the active task when a phase is done. |
| `tsl-clean.ps1` | Remove preview/temp/cache artifacts. |

## Review Loop

1. Reviewer reads `START_HERE.md`.
2. Reviewer creates a bounded worker task and handoff.
3. Worker executes the latest `round_NNN/worker_prompt.md`.
4. Worker writes reports and validation evidence.
5. Reviewer reviews objective evidence and decides pass, fix, downgrade, or stop.

Trust files, tests, diffs, and reports over chat claims.
