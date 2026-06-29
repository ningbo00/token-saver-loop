# START HERE

This is a **no-install, drop-in Token Saver Loop workflow kit**.

## What this is

- A folder you copy into any project.
- No Python, no npm, no dependencies.
- Works with any coding project: Python, JavaScript, Go, Rust, etc.

## How to use it

1. **Copy** the `token-saver-kit/` folder into your project root.
2. **Tell the reviewer model**: "Read `token-saver-kit/START_HERE.md` and act as reviewer only."
3. **Tell the worker model**: "Read the latest `token-saver-kit/.ai/active_task/rounds/round_NNN/worker_prompt.md` and execute it."
4. **Return to the reviewer model**: "Review the latest `token-saver-kit/.ai/active_task/rounds/round_NNN` evidence."

The reviewer may prepare worker handoff files directly or use the optional scripts in `token-saver-kit/tools/` for workflow bookkeeping.

Detailed role rules live in:

- `token-saver-kit/skills/reviewer.md`
- `token-saver-kit/skills/worker.md`

## Important concepts

- **Parent project**: the folder that contains `token-saver-kit/`. That is the project the reviewer and worker models will work on.
- **Kit-local state**: workflow history lives inside `token-saver-kit/.ai/active_task/`. It does not pollute your parent project.
- **Worker model**: any compatible CLI/model can be used if it follows the same prompt and writes the same reports.
- **Reviewer model**: any strong reviewer model can plan and review the round evidence.
- **Scripts**: optional AI/advanced automation helpers. They reduce repeated bookkeeping, but ordinary users do not need to run them manually.

## Role boundaries

Reviewer model:

- Plans bounded worker tasks.
- Creates or updates `WORKER_NEXT_TASK.md`, active task state, and worker handoff files.
- Reviews worker reports, tests, diffs, and changed files.
- Decides pass, fix, downgrade, or stop.
- Must not directly modify parent-project source code.

Worker model:

- Executes only the latest worker prompt.
- Changes parent-project files only inside the stated task scope.
- Writes the required worker reports under the current `round_NNN/` directory.
- Does not commit unless explicitly delegated by the reviewer/user.

Tools:

- May be used for workflow bookkeeping such as task initialization, round prompt creation, review-pack printing, and verdict recording.
- Must not be treated as an installer.
- Must not be used to bypass the reviewer/worker role split.

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
| `skills/reviewer.md` | reviewer skill reference. |
| `skills/worker.md` | worker skill reference. |

## Next step

Open `README.md` for the 60-second quickstart.


