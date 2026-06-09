# AGENT_CONTEXT

Project: Gpt2Whatever

Status:
- Portable Kimi-Codex workflow kit in active development.
- CLI supports project config preview, worker skill preview, planned install paths, Kimi token usage parsing, manual Codex usage snapshots, metrics summarization, and metrics append/write.
- Real file-system installer writes are intentionally not implemented yet.
- Codex plans/reviews; KimiCode executes bounded rounds.

Current Goal:
- Stabilize existing CLI and metrics helpers.
- Harden installer dry-run safety before any real file writes.

Rules:
- Keep tasks small.
- Trust diff, files, and tests over model claims.
- Kimi must write round logs under `.ai/active_task/rounds/`.
- Batch size is dynamic: increase after clean Kimi passes, reduce after failures or drift.
- Larger batches must still be executed as multiple small checkpointed steps, not one large leap.
- Codex thread rotation: suggest a fresh Codex thread after commits, phase boundaries, release decisions, or 2-3 clean Kimi passes; not after every same-tier fix.
- Kimi process rotation: prefer a fresh Kimi conversation per round when handoff files are current; Kimi should follow repo handoff, not chat memory.
- Fresh Codex threads can start by reading root `CODEX_CONTINUE.md`.
