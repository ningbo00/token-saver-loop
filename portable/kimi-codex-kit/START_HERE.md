# START HERE

This is a **no-install, drop-in Kimi-Codex workflow kit**.

## What this is

- A folder you copy into any project.
- No Python, no npm, no dependencies.
- Works with any coding project: Python, JavaScript, Go, Rust, etc.

## How to use it

1. **Copy** the `kimi-codex-kit/` folder into your project root.
2. **Tell Codex**: "Read `kimi-codex-kit/START_HERE.md` and manage this project."
3. **Tell Kimi**: "Read `kimi-codex-kit/KIMI_NEXT_TASK.md` and execute the task against this project."

## Important concepts

- **Parent project**: the folder that contains `kimi-codex-kit/`. That is the project Codex and Kimi will work on.
- **Kit-local state**: workflow history lives inside `kimi-codex-kit/.ai/active_task/`. It does not pollute your parent project.
- **Scripts**: PowerShell scripts in `kimi-codex-kit/tools/` initialize rounds, run Kimi, and record Codex verdicts.

## Files inside the kit

| File | Purpose |
|---|---|
| `START_HERE.md` | This file. Read me first. |
| `README.md` | 60-second quickstart for new users. |
| `KIMI_CODEX_LOOP.md` | How the Kimi-Codex workflow works. |
| `CODEX_CONTINUE.md` | Bootstrap for fresh Codex threads. |
| `KIMI_NEXT_TASK.md` | Current task for Kimi to execute. |
| `tools/ai-kimi-init.ps1` | Initialize a new task. |
| `tools/ai-kimi-run.ps1` | Run a Kimi round. |
| `tools/ai-kimi-review-pack.ps1` | Print the latest round summary. |
| `tools/ai-kimi-verdict.ps1` | Record a Codex review verdict. |
| `skills/kimi-codex-worker.md` | Kimi worker skill reference. |

## Next step

Open `README.md` for the 60-second quickstart.
