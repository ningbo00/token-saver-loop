# Codex Plan

## Round 014 Goal
Prepare real installer write safety without implementing real writes.

## Dynamic Batch Policy
- Increase batch size only after clean passes with matching reports, passing tests, and no scope drift.
- Decrease batch size and increase Codex/Kimi communication when a round has unclear failures, scope drift, missing tests, report mismatch, or safety concerns.
- Batch size should be dynamic, but execution inside the batch must be small-step: checkpoint, validate, log, then continue.
- Do not ask Kimi to take one large leap. Ask for multiple small completed steps in one round.

## Current Suggested Batch Size
- Size: medium.
- Subtasks: 4-5 related items.
- File limit: 8 changed files.
- Tier: T2 for design/tests only. First real write implementation should use T1 or smaller T2.

## Round 014 Required Scope
- Draft/write installer write-safety policy: conflict fail by default, no overwrite by default, no deletion, no binary/generated writes, no writes outside repo root.
- Add or update docs for real install safety expectations.
- Add test skeletons or helper tests for future conflict/no-overwrite behavior if practical, but keep them passing.
- Add preview-only helper structure if useful, but do not write files.
- Keep `--install` without `--dry-run` rejected.
- Do not implement real file writes.

## Required Checkpoints
1. Before changes: read the latest Codex review/verdict and run `git status --short`.
2. After each subtask: record what changed and whether it needs tests.
3. After docs/helper changes: run targeted tests if practical.
4. If adding tests, keep them passing and do not skip expected future behavior.
5. End of round: run `python -m unittest discover -s tests -v`.
6. If any checkpoint fails for unclear reasons after one focused fix attempt, stop and report.

## Forbidden Changes
- Do not implement real `--install` writes.
- Do not overwrite user files.
- Do not parse or store Kimi conversation content.
- Do not add dependencies.
- Do not commit.
- Do not weaken or delete tests.

## Reporting
- Write `kimi_log.md` and `kimi_report.json` in the next round directory.
- Report each subtask separately with status, files changed, commands run, and uncertainty.
- Include whether the next batch should be larger, same size, or smaller.
