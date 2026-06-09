# Beginner Guide: Use Token Saver Loop

This guide assumes you are new to the project. You do not need to understand
the Python package first. Start with the portable folder.

## What You Are Building

Token Saver Loop uses two AI roles:

| Role | Job | Default tool |
|---|---|---|
| Reviewer | Plans tasks, sets limits, reviews evidence, decides pass/fix/stop. | Codex |
| Worker | Executes one bounded task, runs checks, writes a report. | Kimi |

The goal is simple: do not spend your best model on every search and retry.
Use the strong model for judgment, and use the worker model for execution.

## Why This Can Save Tokens

The saved tokens mainly come from the expensive reviewer model **not** doing
these jobs anymore:

- searching the repo broadly
- trying edits that may fail
- reading long command outputs during debug loops
- replaying a long chat history every turn
- narrating every small progress update

The worker does that noisy work and writes compact evidence. The reviewer reads:

- the task file
- the worker report
- git diff or diff summary
- test output
- the latest progress/state files

This should not cause much quality loss because the worker does not approve its
own work. The reviewer still decides pass/fix/stop from evidence, and can always
make the next round stricter.

## Step 0: Pick a Target Project

Choose the project where you want AI help. Example:

```text
D:\MyProject
```

In this guide, "target project" means that folder.

## Step 1: Copy the Kit

From this repo, copy:

```text
portable/kimi-codex-kit/
```

into your target project, so the target project contains:

```text
D:\MyProject\kimi-codex-kit\
```

You can copy it with File Explorer. You do not need Git for this step.

## Step 2: Start With a Safe Inspect-Only Task

Open Codex in the target project and say:

```text
Read kimi-codex-kit/START_HERE.md and create a T0 inspect-only first task.
The worker should summarize the project structure and must not modify source code.
```

T0 means "look only, do not change code." This is the safest first run.

Codex should update:

```text
kimi-codex-kit/KIMI_NEXT_TASK.md
```

## Step 3: Ask Kimi To Execute

Open Kimi in the same target project and say:

```text
Read kimi-codex-kit/KIMI_NEXT_TASK.md and execute it against this project.
Follow the limits exactly and write the required round report.
```

For the first run, Kimi should inspect and report. It should not edit source
code if Codex created a T0 task.

## Step 4: Ask Codex To Review

When Kimi finishes, go back to Codex and say:

```text
The worker is done. Review the latest round evidence under
kimi-codex-kit/.ai/active_task/rounds/.
```

Codex should check the report, any diff, and any test output before deciding:

| Verdict | Meaning |
|---|---|
| `pass` | The round is accepted. |
| `same-tier-fix` | Retry with similar freedom. |
| `downgrade` | Retry with stricter limits. |
| `stop` | Human decision needed. |

## Optional: Use The PowerShell Helpers

If you are on Windows and comfortable with PowerShell, you can initialize a task
from the target project root:

```powershell
powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-init.ps1 -Task "Inspect this project and summarize the structure" -Tier T0
```

Generate a Kimi prompt without running Kimi:

```powershell
powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-run.ps1 -NoRun
```

Copy the printed prompt into Kimi manually.

## What Files Matter?

| File | Why it matters |
|---|---|
| `kimi-codex-kit/START_HERE.md` | First explanation for both models. |
| `kimi-codex-kit/KIMI_NEXT_TASK.md` | The task the worker should do now. |
| `kimi-codex-kit/.ai/active_task/progress.md` | Human-readable progress board. |
| `kimi-codex-kit/.ai/active_task/rounds/` | Evidence from each worker round. |
| `kimi-codex-kit/CODEX_CONTINUE.md` | How a fresh Codex thread can resume. |

## Recommended First Three Rounds

1. **T0 inspect-only**: summarize the project, identify test command, no edits.
2. **T1 tiny fix**: one precise change, one or two files max.
3. **T2 bounded task**: small feature or refactor with tests.

Do not start with a broad T3 task. Build trust first.

## Common Mistakes

- Do not ask the worker to "fix everything" in the first round.
- Do not accept a round just because the worker says it passed.
- Do not skip the Codex/reviewer review step.
- Do not let the worker commit unless you explicitly want that.
- Do not paste long chat history when the handoff files already contain state.

## If You Get Lost

Ask Codex:

```text
Read kimi-codex-kit/START_HERE.md, kimi-codex-kit/.ai/active_task/state.md,
and kimi-codex-kit/.ai/active_task/progress.md. Tell me the next safest step.
```

That is the recovery path.
