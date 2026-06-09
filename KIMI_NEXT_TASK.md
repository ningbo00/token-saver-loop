# Kimi: Do This Task Now

This is the current task from GPT/Codex.

Do **not** summarize CLI commands.
Do **not** ask which command to run.
Do **not** inspect `gpt2whatever --help` unless the task explicitly asks for it.

## Task

Run Round 018 as an independent preview-only 1.0 release-readiness audit.

## Read First

- `.kimi-code/skills/kimi-codex-worker/SKILL.md`
- `.ai/active_task/state.md`
- `.ai/active_task/progress.md`
- `docs/AGENT_CONTEXT.md`
- `docs/REPO_MAP.md`
- `docs/RELEASE_1_0_CHECKLIST.md`

## Critical Context

- Round 017 passed Codex review.
- Codex then made a small release-finalization update:
  - package version set to `1.0.0`
  - `--version` CLI flag added
  - README and release checklist updated
  - JSON output schemas remain `version: 1`
- Real user-facing CLI installer writes must remain disabled.
- This round is an audit/review round, not a feature round.

## Goal

Verify whether the current uncommitted preview-only 1.0 finalization diff is ready for Codex review and commit.

## Required Work

1. Inspect the current diff with targeted commands:
   - `git status --short`
   - `git diff --stat HEAD`
   - targeted `git diff` for changed source/test/docs files
2. Verify version consistency:
   - `pyproject.toml` package version is `1.0.0`
   - `src/gpt2whatever/__init__.py` `__version__` is `1.0.0`
   - `gpt2whatever --version` behavior is covered by tests
   - JSON output schema versions are not accidentally bumped from `version: 1`
3. Verify installer safety posture:
   - CLI real `--install` writes remain rejected without `--dry-run`
   - `--install --dry-run` remains preview-only
   - no new code path applies install actions to the current repo
4. Run validation:
   - `python -m unittest discover -s tests -v`
   - `git diff --check`
5. Update `.ai/active_task/progress.md` at the end with a concise user-facing status board.

## Limits

- Tier: T2.
- Audit only unless a clear release-blocking typo/test failure is found.
- If you find a release blocker, make the smallest possible fix and explain it.
- Max changed files: 3, excluding required round report artifacts.
- Do not expose CLI real writes.
- Do not add dependencies.
- Do not commit.
- Do not perform broad refactors.
- Do not overwrite/delete user files.
- Do not rewrite existing docs for style only.
- Do not decide final release approval; Codex makes the final verdict after review.

## Required Reports

- `.ai/active_task/rounds/round_018/kimi_log.md`
- `.ai/active_task/rounds/round_018/kimi_report.json`

## Final Self-Assessment

Report:
- pass/fail recommendation for Codex review
- exact commands run and results
- any files changed
- whether real installer writes stayed disabled
- whether package version and JSON schema version strategy are consistent
