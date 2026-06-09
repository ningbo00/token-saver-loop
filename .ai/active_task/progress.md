# User Progress Board

Purpose: user-facing rough progress board written by Kimi/Codex to reduce status-reading cost.

Trust level: orientation only. This file is not a source of truth and must not be used to decide pass, release readiness, or bug correctness.

Codex may read this file to decide where to inspect next, but must verify with `state.md`, latest reports, diff, tests, and actual files.

## Current Position

- Phase: commit-ready after portable kit + real installer + GitHub README work
- Latest accepted round: round_023
- Current tier: T2 for docs/portable work; T1 should be used for future installer/security-sensitive changes
- Product scope: portable-first Kimi-Codex workflow kit, with optional Python CLI installer
- Real installer writes: available only with explicit `--yes`; all-or-nothing safety checks and real PS1 script content verified
- Portable kit: `portable/kimi-codex-kit/` works as a no-install drop-in kit; state stays kit-local

## Completed

| Item | Codex Verified? | Evidence |
|---|---:|---|
| CLI preview/config/worker-skill/list-path commands | yes | `TestCLIWorkflowKit` |
| Kimi token usage parsing and metrics helpers | yes | token/metrics tests |
| Installer dry-run safety | yes | `TestCLIInstallerDryRun` |
| Real installer writes gated by `--yes` | yes | Round 020 review + installer tests |
| Installed PS1 scripts are real content, not placeholders | yes | Round 020 review + `test_install_yes_scripts_contain_real_content` |
| Portable no-install kit exists | yes | Round 021/022 review |
| Portable scripts work in Windows PowerShell | yes | Round 022 review + final temp smoke |
| Root README is GitHub-first and portable-first | yes | Round 023 review |
| Handoff/release docs updated to current installer reality | yes | Codex final cleanup |

## In Progress / Next

- Next user action: commit this batch.
- Do not ask Kimi for another implementation round until after the commit.

## Last Verification

- Round: round_023 Codex review
- Result: pass
- Tests: `python -m unittest discover -s tests -v` -> 151 OK
- Whitespace: `git diff --check` -> clean, LF-to-CRLF warnings only
- README sanity: required phrases present; non-ASCII count 0
- Portable smoke: temp copy init and `-NoRun` pass; parent `.ai/` absent
