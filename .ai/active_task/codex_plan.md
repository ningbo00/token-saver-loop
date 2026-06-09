# Codex Plan

## Round 017 Goal
Run an accelerated but gated pressure test toward a preview-only 1.0 release candidate.

## Current Suggested Batch Size
- Size: medium-small, about 2x the previous narrow fix.
- Subtasks: 2 gated checkpoints.
- File limit: 7 changed files, including report artifacts.
- Tier: T1 because Round 016 had a P1 bug; acceleration comes from more checkpoints, not higher freedom.

## Required Scope
- Checkpoint A: fix duplicate target detection during `apply_install_plan` preflight.
- Checkpoint A: detection must use resolved targets under `target_root`, not raw strings only.
- Checkpoint A: if duplicate targets exist, raise before writing anything.
- Checkpoint A: add a temp-dir test proving duplicate targets fail and no file is written.
- Checkpoint B: after Checkpoint A tests pass, prepare a concise 1.0 release readiness checklist for the preview-only product.
- Checkpoint B: document that real CLI install writes remain intentionally disabled for 1.0 preview-only unless Codex later changes the release definition.
- Create standard Round 017 artifacts: `kimi_log.md` and `kimi_report.json`.

## Required Checkpoints
1. Read `.ai/active_task/rounds/round_016/codex_review.md` and `verdict.json`.
2. Add or update the duplicate-target test first if practical.
3. Implement the smallest core fix.
4. Run `python -m unittest discover -s tests -v`; stop if it fails.
5. Add/update release readiness checklist only after Checkpoint A passes.
6. Run `python -m unittest discover -s tests -v` again.
7. Stop if any validation is unclear after one focused fix attempt per checkpoint.

## Forbidden Changes
- Do not expose user-facing real `--install` writes.
- Do not use installer helpers to install into the current repo.
- Do not overwrite user files.
- Do not delete files.
- Do not add dependencies.
- Do not commit.
- Do not weaken or delete tests.

## Reporting
- Write `.ai/active_task/rounds/round_017/kimi_log.md`.
- Write `.ai/active_task/rounds/round_017/kimi_report.json`.
- Include a concise Decision Trace; do not save full chain-of-thought.
- Report Checkpoint A and Checkpoint B separately.
