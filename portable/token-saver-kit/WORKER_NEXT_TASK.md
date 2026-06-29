# Worker: Do This Task Now

This is a placeholder starter task. The reviewer will replace it with a real task when planning the first round.

## How this file works

- The reviewer writes bounded tasks here.
- Recommended path: run `token-saver-kit/tools/tsl-run.ps1` first, then give the worker model the generated `round_NNN/worker_prompt.md`.
- Manual path: the worker model may read this file directly, but must still write the required reports under the current round path provided by the prompt.
- DeepSeek, GLM, Qwen, Kimi, or another compatible model can be used if it follows the same limits and report paths.
- After each round, the reviewer updates this file with the next task.

## Current task

Initialize the workflow kit and confirm the project structure is understood.

1. Read `START_HERE.md`.
2. Read `.ai/active_task/state.md`.
3. Inspect the parent project root (the folder containing `token-saver-kit/`).
4. Produce a brief project summary in `.ai/active_task/progress.md`.
5. Run any safe validation commands available in the parent project.

## Limits

- Tier: T0 (inspect and report only; do not modify code).
- Parent-project source/config/doc file limit: 0.
- Allowed workflow writes: round report files and `.ai/active_task/progress.md`.
- Do not modify the parent project's source code.


