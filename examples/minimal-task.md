# Minimal Kimi-Codex Task Example

Use this when you want to test the kit in a small repository without giving
Kimi broad permission to change code.

## 1. Copy the kit

Copy `portable/kimi-codex-kit/` into the target project root as
`kimi-codex-kit/`.

## 2. Ask Codex to create the first task

```text
Read kimi-codex-kit/START_HERE.md and create a T0 task that only inspects this
project, summarizes the structure, and recommends one safe next step.
```

## 3. Expected Kimi task shape

Codex should write a small task into `kimi-codex-kit/KIMI_NEXT_TASK.md`:

```markdown
# Kimi: Do This Task Now

## Current task

Inspect the parent project and write a concise project summary.

1. Read `kimi-codex-kit/START_HERE.md`.
2. Inspect the parent project root.
3. Identify the main language/framework, test command if obvious, and risky
   generated folders to avoid.
4. Update `kimi-codex-kit/.ai/active_task/progress.md` with the summary.

## Limits

- Tier: T0 (inspect and report only).
- Do not modify source code.
- Do not commit changes.
```

## 4. Run or copy the prompt

```powershell
powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-run.ps1 -NoRun
```

Copy the generated prompt into Kimi manually, or remove `-NoRun` if your Kimi
CLI is installed and configured.

## 5. Ask Codex to review

```text
Kimi is done. Review the latest round under kimi-codex-kit/.ai/active_task/rounds/.
```

Codex should check the round report, git diff, and progress board before
writing a verdict.

