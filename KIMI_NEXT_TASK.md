# Kimi: Do This Task Now

This is the current task from GPT/Codex.

Do **not** summarize CLI commands.
Do **not** ask which command to run.
Do **not** inspect `gpt2whatever --help` unless the task explicitly asks for it.

## Task

Run Round 017 as an accelerated but gated pressure test for a preview-only 1.0 release candidate.

## Read First

- `.kimi-code/skills/kimi-codex-worker/SKILL.md`
- `.ai/active_task/state.md`
- `.ai/active_task/codex_plan.md`
- `.ai/active_task/rounds/round_016/codex_review.md`
- `.ai/active_task/rounds/round_016/verdict.json`

## Critical Context

- Round 016 did not pass Codex review.
- Existing tests pass, but Codex manually reproduced an all-or-nothing bug.
- First fix the P1 duplicate-target bug. If that fix or its tests fail, stop immediately.
- If and only if Checkpoint A passes, continue to Checkpoint B release-gate preparation.
- Real user-facing CLI installer writes remain disabled for this round.

## Goal

Do roughly 2x the previous safe batch by completing two small checkpoints in order:

1. Fix the known `apply_install_plan` duplicate-target all-or-nothing bug.
2. Prepare objective 1.0 release readiness gates for the current preview-only product.

## Required Work

### Checkpoint A - Mandatory Bug Fix

1. Add duplicate target detection during `apply_install_plan` preflight.
2. Compare resolved targets under `target_root`, not raw strings only.
3. If duplicate targets exist, raise before writing any file.
4. Add a temp-dir test proving duplicate targets fail and no file is written.
5. Run `python -m unittest discover -s tests -v`.
6. Stop if Checkpoint A does not pass.

### Checkpoint B - 1.0 Release Gate Prep

Only start this after Checkpoint A passes.

1. Add or update a concise release readiness document, for example `docs/RELEASE_1_0_CHECKLIST.md`.
2. Define what "1.0 preview-only release" means:
   - workflow preview/config/skill commands work
   - token/metrics helpers work
   - `--install --dry-run` works and reports safety
   - real `--install` writes are intentionally disabled
3. Add CLI/core tests for any release-gate behavior that is currently undocumented or weakly covered, but do not invent large new features.
4. Do not bump package version unless every release gate is already satisfied and the rationale is written in the report.
5. Run `python -m unittest discover -s tests -v` again after Checkpoint B.

## Validation

- Required after Checkpoint A: `python -m unittest discover -s tests -v`.
- Required after Checkpoint B: `python -m unittest discover -s tests -v`.

## Limits

- Tier: T1.
- Pressure-test batch size: medium-small, two gated checkpoints.
- Max changed files: 7, including report artifacts.
- Normal source/test/docs/artifact edits are allowed.
- Do not use installer helpers to install into the current repo.
- Do not expose CLI real writes.
- Do not overwrite/delete user files.
- Do not add dependencies.
- Do not commit.
- Do not perform broad refactors.
- Do not weaken or delete tests.

## Required Reports

- `.ai/active_task/rounds/round_017/kimi_log.md`
- `.ai/active_task/rounds/round_017/kimi_report.json`

## Final Self-Assessment

Report each checkpoint separately and recommend whether the next batch should stay accelerated, shrink, or expand.
