# Token Saver Loop Portable Kit

A no-install, drop-in workflow kit for AI-assisted development.

## 60-Second Quickstart

Follow this 60-second quickstart to get started:

1. **Copy** `token-saver-kit/` into your project root.
2. **Initialize** a task:
   ```powershell
   powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-init.ps1 -Task "Refactor auth module" -Tier T2
   ```
3. **Run** a worker round:
   ```powershell
   powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-run.ps1
   ```
4. **Review** the output, then ask the reviewer to review the round.
5. **Record** a verdict:
   ```powershell
   powershell -ExecutionPolicy Bypass -File token-saver-kit/tools/tsl-verdict.ps1 -Verdict pass
   ```

That's it. No Python, no dependencies, no installation.

Tip: `tsl-run.ps1 -NoRun` creates a `_validate` preview prompt only. Use it to check the prompt text, not as the real worker round. A real round uses a `round_NNN` directory.

Choose any compatible worker CLI with
`-WorkerCommand deepseek`, `-WorkerCommand glm`, `-WorkerCommand qwen`, or another
compatible CLI when you want a different execution model.

## What you get

- **Tiered execution**: T3 free / T2 bounded / T1 precise / T0 inspect-only.
- **Round tracking**: every round produces logs, reports, and diffs inside `token-saver-kit/.ai/`.
- **Reviewer review**: structured verdicts with pass / same-tier-fix / downgrade / stop.
- **Parent project focus**: the reviewer and worker work on the project that contains this kit, not the kit itself.

## Requirements

- PowerShell (Windows) or pwsh (macOS/Linux).
- A compatible worker CLI is needed only if you want automatic worker execution. You can also copy the generated prompt and run it manually.

## Learn more

- `START_HERE.md` — overview and concepts.
- `TOKEN_SAVER_LOOP.md` — full workflow documentation.
- `REVIEWER_CONTINUE.md` — how to bootstrap a fresh reviewer thread.


