# Context Pack

## Project
- `Gpt2Whatever` has pivoted into a portable Kimi-Codex workflow kit.
- The CLI is stdlib Python with tests under `tests/`.
- Current capabilities include project config previews, worker skill preview, planned install paths, Kimi token usage parsing, manual Codex usage snapshots, metrics summarization, metrics append/write support, and Kimi-Codex round artifacts.
- Real file-system installer writes are still intentionally not implemented.

## Important Files
- `tools/ai-kimi-run.ps1`: creates Kimi rounds and should capture review artifacts.
- `README.md`: user-facing overview and CLI examples.
- `src/gpt2whatever/core.py`: workflow-kit helpers and metrics helpers.
- `src/gpt2whatever/cli.py`: argparse CLI.
- `docs/AGENT_CONTEXT.md`: compact project handoff context.
- `docs/REPO_MAP.md`: compact repository map.
- `.ai/active_task/codex_plan.md`: current Codex instructions for the next round.
- `.ai/active_task/rounds/round_009/codex_review.md`: latest Codex review.

## Latest Status
- Round 009 passed.
- Verified locally: `python -m unittest discover -s tests -v` -> 89 tests OK.
- Metadata cleanup completed: README wording, `pyproject.toml` description, and package docstring now match the workflow-kit direction.
- Round 009 Kimi token usage recorded: 54,598 -> 62,294 (delta 7,696).
- Current phase: prepare Round 010 dynamic batch round.

## Round 010 Direction
- Medium T2 batch with small-step checkpoints.
- Improve future artifact capture if small, especially saving test command output to `tests.txt` in `tools/ai-kimi-run.ps1`.
- Update short handoff docs only if stale.
- Draft acceptance criteria for a future `--install --dry-run` workflow, but do not implement real installer writes.

## Constraints
- Batch size can grow after clean passes, but execution must remain small-step with checkpoints.
- Do not implement real installer writes.
- Do not overwrite user files.
- Do not parse or store Kimi conversation content.
- Keep changes stdlib-only and run `python -m unittest discover -s tests -v` after changes.
