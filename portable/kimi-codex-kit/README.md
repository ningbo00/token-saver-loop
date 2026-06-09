# Kimi-Codex Kit

A no-install, drop-in workflow kit for AI-assisted development.

## 60-Second Quickstart

Follow this 60-second quickstart to get started:

1. **Copy** `kimi-codex-kit/` into your project root.
2. **Initialize** a task:
   ```powershell
   powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-init.ps1 -Task "Refactor auth module" -Tier T2
   ```
3. **Run** a Kimi round:
   ```powershell
   powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-run.ps1
   ```
4. **Review** the output, then ask Codex to review the round.
5. **Record** a verdict:
   ```powershell
   powershell -ExecutionPolicy Bypass -File kimi-codex-kit/tools/ai-kimi-verdict.ps1 -Verdict pass
   ```

That's it. No Python, no dependencies, no installation.

## What you get

- **Tiered execution**: T3 free / T2 bounded / T1 precise / T0 inspect-only.
- **Round tracking**: every round produces logs, reports, and diffs inside `kimi-codex-kit/.ai/`.
- **Codex review**: structured verdicts with pass / same-tier-fix / downgrade / stop.
- **Parent project focus**: Codex and Kimi work on the project that contains this kit, not the kit itself.

## Requirements

- PowerShell (Windows) or pwsh (macOS/Linux).
- Kimi CLI installed if you want to run Kimi rounds automatically. You can also copy the generated prompt and run it manually.

## Learn more

- `START_HERE.md` — overview and concepts.
- `KIMI_CODEX_LOOP.md` — full workflow documentation.
- `CODEX_CONTINUE.md` — how to bootstrap a fresh Codex thread.
