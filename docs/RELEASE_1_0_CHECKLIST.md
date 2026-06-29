# 1.0 Portable Kit Release Checklist

## Release Definition

The 1.0 release is portable-only:
- The primary user path is copying `portable/token-saver-kit/` into a project.
- Runtime state stays inside `token-saver-kit/.ai/active_task/`.
- No CLI command writes workflow files into a target project.
- `--doctor` reports portable kit health and next action without modifying files.
- Python CLI helpers are limited to config preview, skill preview, token metrics, and diagnostics.

## Functional Gates

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | Config preview (`--show-config`) works | OK | `TestCLIWorkflowKit` |
| 2 | Worker skill preview (`--show-project-skill`) works | OK | `TestCLIWorkflowKit` |
| 3 | Doctor reports missing/portable setup state without writes | OK | `TestBuildDoctorReport`, `test_doctor_*` |
| 4 | Token usage parsing (`--parse-worker-usage-jsonl`) works and respects privacy boundary | OK | `TestCLITokenUsage` |
| 5 | Metrics append/write works | OK | `TestCLIMetricsAppend` |
| 6 | Metrics aggregation works | OK | `TestCLIMetricsAggregation` |
| 7 | Worker command can be swapped with `-WorkerCommand` | OK | portable script preview check |

## Safety Gates

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | No installer or target-project write command exists | OK | CLI parser and tests |
| 2 | T0 first-run workflow keeps source/config/doc file limit at 0 | OK | script template tests |
| 3 | `_validate` prompt is clearly preview-only | OK | script template tests |
| 4 | Portable kit state is kit-local | OK | `token-saver-kit/.ai/active_task/` |

## Post-1.0 Candidates

- Packaged release paths such as PyPI and standalone zip.
- Example projects showing T1/T2/T3 rounds.
