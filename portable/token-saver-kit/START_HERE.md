# START HERE

This is a **no-install, drop-in Token Saver Loop workflow kit**.

## What this is

- A folder you copy into any project.
- No Python, no npm, no dependencies.
- Works with any coding project: Python, JavaScript, Go, Rust, etc.

## How to use it

1. **Copy** the `token-saver-kit/` folder into your project root.
2. **Tell the reviewer model**: "Read `token-saver-kit/START_HERE.md` and manage this project."
3. **Create a real worker round**: run `powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-run.ps1`, or ask the reviewer to prepare the exact round prompt.
4. **Tell the worker model**: use the prompt from the latest `round_NNN/worker_prompt.md`, or say "Read `token-saver-kit/WORKER_NEXT_TASK.md` and execute the task against this project."

`tsl-run.ps1 -NoRun` creates a `_validate` preview prompt only. It is useful for checking the prompt, but it is not a real worker round.

## Important concepts

- **Parent project**: the folder that contains `token-saver-kit/`. That is the project the reviewer and worker models will work on.
- **Kit-local state**: workflow history lives inside `token-saver-kit/.ai/active_task/`. It does not pollute your parent project.
- **Worker model**: DeepSeek, GLM, Qwen, Kimi, or another CLI/model can be used if it follows the same prompt and writes the same reports.
- **Reviewer model**: any strong reviewer model can plan and review the round evidence.
- **Scripts**: PowerShell scripts in `token-saver-kit/tools/` initialize rounds, run the worker, and record reviewer verdicts.

## Files inside the kit

| File | Purpose |
|---|---|
| `START_HERE.md` | This file. Read me first. |
| `README.md` | 60-second quickstart for new users. |
| `TOKEN_SAVER_LOOP.md` | How the Token Saver Loop workflow works. |
| `REVIEWER_CONTINUE.md` | Bootstrap for fresh reviewer threads. |
| `WORKER_NEXT_TASK.md` | Current task for the worker to execute. |
| `tools/tsl-init.ps1` | Initialize a new task. |
| `tools/tsl-run.ps1` | Run a worker round. |
| `tools/tsl-review-pack.ps1` | Print the latest round summary. |
| `tools/tsl-verdict.ps1` | Record a reviewer verdict. |
| `skills/worker.md` | worker skill reference. |

## Next step

Open `README.md` for the 60-second quickstart.


