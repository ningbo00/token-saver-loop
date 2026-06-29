# Minimal Token Saver Loop Task Example

Use this when you want to test the kit in a small repository without giving
the worker broad permission to change code.

## 1. Copy the kit

Copy `portable/token-saver-kit/` into the target project root as
`token-saver-kit/`.

## 2. Ask the reviewer model to create the first task

```text
Read token-saver-kit/START_HERE.md and create a T0 task that only inspects this
project, summarizes the structure, and recommends one safe next step.
```

## 3. Expected worker task shape

The reviewer should write a small task into `token-saver-kit/WORKER_NEXT_TASK.md`:

```markdown
# Worker: Do This Task Now

## Current task

Inspect the parent project and write a concise project summary.

1. Read `token-saver-kit/START_HERE.md`.
2. Inspect the parent project root.
3. Identify the main language/framework, test command if obvious, and risky
   generated folders to avoid.
4. Update `token-saver-kit/.ai/active_task/progress.md` with the summary.

## Limits

- Tier: T0 (inspect and report only).
- Do not modify source code.
- Do not commit changes.
```

## 4. Run or copy the prompt

```powershell
powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-run.ps1 -NoRun
```

Copy the generated prompt into the worker manually, or remove `-NoRun` if your worker
CLI is installed and configured.

## 5. Ask the reviewer model to review

```text
The worker is done. Review the latest round under token-saver-kit/.ai/active_task/rounds/.
```

The reviewer should check the round report, git diff, and progress board before
writing a verdict.



