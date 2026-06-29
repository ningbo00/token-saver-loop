# Beginner Guide: Use Token Saver Loop

This guide assumes you are new to the project. You do not need to understand
the Python package first. Start with the portable folder.

## What You Are Building

Token Saver Loop uses two AI roles:

| Role | Job | Default tool |
|---|---|---|
| Reviewer | Plans tasks, sets limits, reviews evidence, decides pass/fix/stop. | Any strong reviewer model. |
| Worker | Executes one bounded task, runs checks, writes a report. | Any compatible worker model or CLI. |

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
portable/token-saver-kit/
```

into your target project, so the target project contains:

```text
D:\MyProject\token-saver-kit\
```

You can copy it with File Explorer. You do not need Git for this step.

## Step 2: Start With a Safe Inspect-Only Task

Open the reviewer model in the target project and say:

```text
Read token-saver-kit/START_HERE.md and create a T0 inspect-only first task.
The worker should summarize the project structure and must not modify source code.
```

T0 means "look only, do not change code." This is the safest first run.

The reviewer should update:

```text
token-saver-kit/WORKER_NEXT_TASK.md
```

## Step 3: Ask the worker model To Execute

Recommended path: from the target project root, generate a real round prompt:

```powershell
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-run.ps1
```

Then give the worker model the generated prompt from the latest `round_NNN/worker_prompt.md`.
To use another worker CLI, pass it explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-run.ps1 -WorkerCommand deepseek
```

Manual path: open the worker model in the same target project and say:

```text
Read token-saver-kit/WORKER_NEXT_TASK.md and execute it against this project.
Follow the limits exactly and write the required round report.
```

For the first run, the worker should inspect and report. It should not edit source
code if the reviewer created a T0 task.

## Step 4: Ask the reviewer model To Review

When the worker finishes, go back to the reviewer and say:

```text
The worker is done. Review the latest round evidence under
token-saver-kit/.ai/active_task/rounds/.
```

The reviewer should check the report, any diff, and any test output before deciding:

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
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-init.ps1 -Task "Inspect this project and summarize the structure" -Tier T0
```

Generate a worker prompt without running the worker:

```powershell
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-run.ps1 -NoRun
```

This creates a `_validate` preview prompt only. Use it to inspect the prompt text.
For a real worker round, run the same script without `-NoRun` so it creates a
`round_NNN` directory.

## What Files Matter?

| File | Why it matters |
|---|---|
| `token-saver-kit/START_HERE.md` | First explanation for both models. |
| `token-saver-kit/WORKER_NEXT_TASK.md` | The task the worker should do now. |
| `token-saver-kit/.ai/active_task/progress.md` | Human-readable progress board. |
| `token-saver-kit/.ai/active_task/rounds/` | Evidence from each worker round. |
| `token-saver-kit/REVIEWER_CONTINUE.md` | How a fresh reviewer thread can resume. |

## Recommended First Three Rounds

1. **T0 inspect-only**: summarize the project, identify test command, no edits.
2. **T1 tiny fix**: one precise change, one or two files max.
3. **T2 bounded task**: small feature or refactor with tests.

Do not start with a broad T3 task. Build trust first.

## Common Mistakes

- Do not ask the worker to "fix everything" in the first round.
- Do not accept a round just because the worker says it passed.
- Do not skip the reviewer review step.
- Do not let the worker commit unless you explicitly want that.
- Do not paste long chat history when the handoff files already contain state.

## If You Get Lost

If the Python CLI is available in your dev environment, run:

```text
token-saver-loop --doctor
```

It prints a JSON health report and a recommended next action.

Ask the reviewer model:

```text
Read token-saver-kit/START_HERE.md, token-saver-kit/.ai/active_task/state.md,
and token-saver-kit/.ai/active_task/progress.md. Tell me the next safest step.
```

That is the recovery path.


