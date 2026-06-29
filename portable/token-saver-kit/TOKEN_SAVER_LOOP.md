# Token Saver Loop

This kit keeps reviewer planning and worker execution separated. The user only
needs short prompts; detailed rules live in `START_HERE.md` and `skills/`.

## Source Of Truth

- Reviewer rules: `skills/reviewer.md`
- Worker rules: `skills/worker.md`
- Current worker task: `WORKER_NEXT_TASK.md`
- Stable latest worker handoff: `LATEST_WORKER_PROMPT.md`
- Active task state: `.ai/active_task/`
- Project memory: `.ai/project_memory/`
- Round evidence: `.ai/active_task/rounds/round_NNN/`

## Tool Model

Tools are optional bookkeeping helpers for AI agents and advanced users. They are
not installers and are not required for manual use.

| Tool | Purpose |
|---|---|
| `tsl-new-round.ps1` | Create the next worker handoff prompt and refresh `LATEST_WORKER_PROMPT.md`. |
| `tsl-latest.ps1` | Find latest round paths without guessing `round_NNN`. |
| `tsl-status.ps1` | Print the next short prompt to copy. |
| `tsl-memory.ps1` | Initialize project memory and refresh latest evidence. |
| `tsl-review.ps1` | Summarize latest worker evidence and write `verdict.json`. |
| `tsl-redflags.ps1` | Detect common evidence/scope/generated-file issues. |
| `tsl-doctor.ps1` | Check kit health. |
| `tsl-archive.ps1` | Archive the active task when a phase is done. |

## Review Loop

1. Reviewer reads `START_HERE.md`.
2. Reviewer creates a bounded worker task and handoff.
3. Worker executes `token-saver-kit/LATEST_WORKER_PROMPT.md`.
4. Worker writes reports and validation evidence.
5. Reviewer reviews objective evidence and decides pass, fix, downgrade, or stop.

## Evidence Verdicts

`tsl-review.ps1` may write `round_NNN/verdict.json` with one of:

| Verdict | Meaning |
|---|---|
| `PASS` | Evidence is complete enough for reviewer fast diff/test spot-check. |
| `FIX_SAME_TIER` | Evidence gaps or validation issues can be fixed at the same tier. |
| `DOWNGRADE` | Scope control is weak; next round should be narrower and stricter. |
| `STOP` | Dangerous, conflicting, or invalid evidence requires human/reviewer decision. |

The verdict is an evidence verdict only. It never replaces reviewer acceptance.

## Project Memory

Project memory is a compact navigation layer, not a transcript:

| File | Purpose |
|---|---|
| `.ai/project_memory/current_goal.md` | Current project or phase goal. |
| `.ai/project_memory/architecture.md` | Small project map, run command, and test command. |
| `.ai/project_memory/completed.md` | Reviewer-accepted completed work only. |
| `.ai/project_memory/risks.md` | Open risks, constraints, and human decisions needed. |
| `.ai/project_memory/latest_evidence.md` | Auto-refreshed compact summary of the latest worker evidence. |

Read only the memory files needed for the current decision.

Trust files, tests, diffs, and reports over chat claims.
