# User Progress Board

Purpose: user-facing rough progress board written by Kimi/Codex to reduce status-reading cost.

Trust level: orientation only. This file is not a source of truth and must not be used to decide pass, release readiness, or bug correctness.

Codex may read this file to decide where to inspect next, but must verify with `state.md`, latest reports, diff, tests, and actual files.

## Current Position

- Phase: preview-only 1.0 ready for commit; release decision after commit/fresh thread
- Latest accepted round: round_018
- Audit round: round_018 passed Codex review
- Current tier: T2 for audit; T1 for any real installer write exposure
- Product scope: portable Kimi-Codex workflow kit with preview/dry-run install behavior
- Real installer writes: intentionally disabled

## Completed

| Item | Status Source | Codex Verified? | Evidence |
|---|---|---:|---|
| CLI preview/config/worker-skill/list-path commands exist | tests/docs | yes | `TestCLIWorkflowKit` |
| Kimi token usage parsing and metrics helpers exist | tests/docs | yes | token/metrics test classes |
| Installer dry-run emits versioned JSON with safety checks | tests/docs | yes | `TestCLIInstallerDryRun` |
| Installer safety policy and preview-only release checklist exist | docs | yes | `docs/RELEASE_1_0_CHECKLIST.md` |
| `apply_install_action` and `apply_install_plan` have temp-dir tests | tests | yes | `TestApplyInstallAction`, `TestApplyInstallPlan` |
| `apply_install_plan` rejects duplicate resolved targets before writing | tests/Codex review | yes | round_017 verdict |
| Kimi/Codex conversation rotation rules are documented | docs/skills | yes | `KIMI_CODEX_LOOP.md`, worker skill |
| Fresh Codex threads can bootstrap from `CODEX_CONTINUE.md` | docs | yes | `CODEX_CONTINUE.md` |
| Preview-only package version set to 1.0.0 | Kimi audit/Codex review | yes | `pyproject.toml`, `src/gpt2whatever/__init__.py`, `--version` |
| JSON schema versions remain version 1 | Kimi audit/Codex review | yes | `docs/RELEASE_1_0_CHECKLIST.md`, `core.py` grep |
| `--version` CLI flag and regression test added | Kimi audit/Codex review | yes | `src/gpt2whatever/cli.py`, `tests/test_cli.py` |
| Round 018 release-readiness audit passed | Kimi/Codex review | yes | `round_018/codex_review.md`, `round_018/verdict.json` |
| Testing/git responsibility rules documented | Codex/tests/docs | yes | `KIMI_CODEX_LOOP.md`, worker skill, generated skill test |
| All 147 tests pass | Kimi audit/Codex review | yes | `python -m unittest discover -s tests -v` |
| `git diff --check` clean | Kimi audit/Codex review | yes | no whitespace errors |

## In Progress / Next

- Review and commit preview-only 1.0 finalization plus workflow-rule diff.
- Use a fresh Codex thread after commit or before final 1.0 release decision.
- Keep real `--install` writes disabled unless a separate T1 round explicitly opens that scope.

## Rough Remaining Work

| Area | Rough Status | Likely Next Step | Confidence | Needs Codex Verification |
|---|---|---|---|---|
| Preview CLI | mostly done | final docs/metadata pass | medium | yes |
| Token/metrics helpers | mostly done | final examples sanity check | medium | yes |
| Installer dry-run safety | mostly done | final release checklist review | medium | yes |
| Real installer writes | deferred | design later in T1 | high | yes |
| 1.0 packaging/release | audited and Codex-reviewed | commit then release decision | medium | no for commit, yes for release |

## Last Update

- Round: round_018
- Result: audit pass; tests pass; release decision not made yet
- Tests: `python -m unittest discover -s tests -v` -> 147 OK
- Updated by: Codex after Round 018 review
