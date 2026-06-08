# Capability Notes

## Observed Kimi Strengths
- T2 works well for small stdlib Python CLI features with clear file scope and explicit unittest validation.
- T2 works well for README/REPO_MAP updates when acceptance criteria are concrete.
- T2 handled narrow metadata cleanup cleanly with no unnecessary file changes.
- T1 works well for narrow corrective changes after Codex identifies a specific privacy or implementation issue.
- Structured `kimi_log.md` and `kimi_report.json` are sufficient for efficient Codex review when paired with tests and targeted file reads.

## Lower-Tier Triggers
- Use T1 for privacy/content-minimization changes involving Kimi session files.
- Use T1 when a previous round passed tests but violated an architectural or safety boundary.
- Use T0 for research over local tool internals, session metadata, or any area where code changes are not yet safe.

## Reliability Notes
- Kimi reports are useful but still need verification against file contents and test output.
- Rounds not launched through `tools/ai-kimi-run.ps1` may miss diff/test artifacts, increasing Codex review cost.
- Product metadata consistency should be included in cleanup prompts after a pivot.
- Batch size should adapt to observed reliability: grow after clean passes, shrink after scope drift, missing tests, report mismatch, or unclear failures.
- Even in larger batches, Kimi should work in stable small steps with checkpoints rather than making one broad change.

## Prompt Patterns That Helped
- Explicit file-count limits.
- Explicit forbidden actions: no commits, no generated/binary files, no test weakening.
- Required report paths under `.ai/active_task/rounds/round_NNN/`.
- Test command named directly: `python -m unittest discover -s tests -v`.
- For continued efficiency, group related low-risk tasks into one batch round and let Codex review once at the end.
- Batch prompts should require per-subtask status, checkpoint validation, and a recommendation to increase, keep, or reduce the next batch size.
