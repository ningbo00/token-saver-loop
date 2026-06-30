# Token Saver Loop Portable Kit

A no-install, drop-in workflow kit for reviewer/worker AI collaboration.

## Quickstart

1. Copy `token-saver-kit/` into your project root.
2. Send this to the reviewer model:

   ```text
   Read token-saver-kit/START_HERE.md and act as reviewer only.
   ```

3. Send this to the worker model after the reviewer prepares a round:

   ```text
   Read token-saver-kit/LATEST_WORKER_PROMPT.md and execute it.
   ```

4. Send this back to the reviewer after the worker finishes:

   ```text
   Review the latest worker evidence in token-saver-kit and decide the next step.
   ```

## Optional AI Automation Tools

Ordinary users do not need to run these manually. Reviewer/worker agents may use
them to reduce repeated bookkeeping and path mistakes.

| Tool | Purpose |
|---|---|
| `tools/tsl-new-round.ps1` | Create the next round prompt and refresh `LATEST_WORKER_PROMPT.md`. |
| `tools/tsl-latest.ps1` | Print latest round and prompt/report paths. |
| `tools/tsl-status.ps1` | Print the next short prompt to copy. |
| `tools/tsl-memory.ps1` | Initialize project memory and refresh latest evidence. |
| `tools/tsl-review.ps1` | Print a compact latest-round review pack and write `verdict.json`. |
| `tools/tsl-redflags.ps1` | Check common scope, evidence, and generated-file problems. |
| `tools/tsl-doctor.ps1` | Check kit health. |
| `tools/tsl-archive.ps1` | Archive the active task. |

## Removal

When you no longer need the workflow, delete the `token-saver-kit/` folder from
your project root.
