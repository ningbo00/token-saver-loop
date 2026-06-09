# 1.0 Preview-Only Release Readiness Checklist

## Release Definition

The 1.0 preview-only release is a **read-only / dry-run capable** workflow kit:
- All preview, config, skill, token, and metrics commands work.
- `--install --dry-run` generates a versioned plan with a safety report.
- **Real `--install` writes are intentionally disabled.**

## Functional Gates

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | Workflow preview commands (`--show-config`, `--show-project-skill`, `--list-install-paths`) work | OK | `TestCLIWorkflowKit` |
| 2 | Token usage parsing (`--parse-kimi-usage-jsonl`) works and respects privacy boundary | OK | `TestCLITokenUsage` |
| 3 | Metrics append/write (`--append-metrics`, `--append-default-metrics`) work | OK | `TestCLIMetricsAppend` |
| 4 | Metrics aggregation (`--record-codex-usage`, `--summarize-token-usage-jsonl`) works | OK | `TestCLIMetricsAggregation` |
| 5 | Installer dry-run (`--install --dry-run`) produces versioned JSON plan | OK | `TestCLIInstallerDryRun` |
| 6 | Installer dry-run reports safety check (`safe`, `concerns`, `blocked_actions`) | OK | `test_install_dry_run_succeeds_with_project_name` |
| 7 | Installer rejects unsafe project names (empty, separators, `..`) | OK | `TestCLIInstallerDryRun` rejection tests |
| 8 | Installer real writes blocked: `--install` without `--dry-run` returns error | OK | `test_install_without_dry_run_rejected` |
| 9 | Core write helpers (`apply_install_action`, `apply_install_plan`) exist and are tested | OK | `TestApplyInstallAction`, `TestApplyInstallPlan` |
| 10 | Core write helpers enforce root containment, no-overwrite, all-or-nothing, no duplicates | OK | `TestApplyInstallPlan` |

## Safety Gates

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | No CLI path exposes real installer writes to the repo root | OK | CLI returns "not implemented yet" |
| 2 | `validate_project_name` blocks traversal and path separators | OK | `TestValidateProjectName` |
| 3 | `check_install_safety` blocks generated/binary areas and absolute paths | OK | `TestCheckInstallSafety` |
| 4 | `apply_install_plan` detects duplicate resolved targets before writing | OK | `test_duplicate_target_aborts_all` |
| 5 | All write-helper tests use isolated temp directories | OK | Every `TestApplyInstall*` test |

## Non-Functional Gates

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | Zero external test dependencies (stdlib `unittest` only) | OK | `tests/` imports |
| 2 | Console script entry point defined in `pyproject.toml` | OK | `gpt2whatever = gpt2whatever.cli:main` |
| 3 | No committed secrets or session content | OK | `.gitignore`, privacy boundary rules |

## Intentionally Deferred Post-1.0

- Real `--install` apply with user confirmation or `--force` flag.
- Package version bump (deferred until all gates above are satisfied and Codex approves).
