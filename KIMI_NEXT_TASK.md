# Kimi: Do This Task Now

This is the current task from GPT/Codex.

Do **not** summarize CLI commands.
Do **not** ask which command to run.
Do **not** inspect `gpt2whatever --help` unless the task explicitly asks for it.

## Task

Run Round 014 as a medium T2 batch: prepare real installer write safety without implementing real writes.

## Read First

- `.kimi-code/skills/kimi-codex-worker/SKILL.md`
- `.ai/active_task/gpt_command.md`
- `.ai/active_task/state.md`
- `.ai/active_task/codex_plan.md`
- `.ai/active_task/rounds/round_013/codex_review.md`
- `.ai/active_task/rounds/round_013/verdict.json`
- `docs/INSTALL_DRY_RUN_CRITERIA.md`

## Critical Context

- Round 013 passed.
- The next real round should be `.ai/active_task/rounds/round_014/`.
- Kimi has several clean passes, but real installer writes are safety-sensitive.
- This is a medium batch, not large. Execution must remain small-step with checkpoints.

## Goal

Prepare real installer write safety. This must not perform real installation writes.

## Required Work

1. Draft/write installer write-safety policy in docs:
   - conflict fail by default
   - no overwrite by default
   - no deletion
   - no writes outside repo root
   - no generated/binary writes unless explicitly allowed
   - preview before write
2. Add or update tests/helper structure for future conflict/no-overwrite behavior if practical, but keep all tests passing.
3. Add preview-only install action/helper structure only if it does not write files.
4. Keep `--install` without `--dry-run` rejected.
5. Update README, `docs/AGENT_CONTEXT.md`, and `docs/REPO_MAP.md` if needed.
6. Do not implement real file writes.

## Checkpoints

1. Read required files and inspect current install helper/tests.
2. Draft safety policy and decide whether helper/test scaffolding is useful.
3. Add small helper/test scaffolding only if it stays preview-only and passing.
4. Update docs after policy/helper work is stable.
5. Run full validation.

## Validation

- Run `python -m unittest discover -s tests -v`.

## Limits

- Tier: T2.
- Max changed files: 8.
- Do not implement installer behavior.
- Do not write install target files.
- Do not overwrite user files.
- Do not add dependencies.
- Do not commit.
- Do not delete user data.

## Required Reports

- `.ai/active_task/rounds/round_014/kimi_log.md`
- `.ai/active_task/rounds/round_014/kimi_report.json`

## Final Self-Assessment

In the report, recommend whether the next batch should be larger, same size, or smaller.
