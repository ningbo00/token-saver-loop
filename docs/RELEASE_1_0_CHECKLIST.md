# 1.0 Workflow Kit Release Readiness Checklist

## Release Definition

The 1.0 release is a portable-first Kimi-Codex workflow kit:
- The primary user path is copying `portable/kimi-codex-kit/` into a project.
- All preview, config, skill, token, and metrics commands work.
- `--install --dry-run` generates a versioned plan with a safety report.
- Real `--install` writes are available only with explicit `--yes` and all-or-nothing safety checks.
- Python package version is `1.0.0`; JSON output schemas remain separately versioned as `version: 1`.

## Version Strategy

- Package release version: `1.0.0` for the workflow kit.
- Output schema versions: keep existing `version: 1` values for token, metrics, and installer-plan JSON records.
- Future installer improvements should preserve `--yes` confirmation and all-or-nothing safety behavior.

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
| 8 | Installer real writes require `--yes`: `--install` without `--dry-run` or `--yes` returns error | OK | `test_install_without_dry_run_rejected` |
| 9 | Core write helpers (`apply_install_action`, `apply_install_plan`) exist and are tested | OK | `TestApplyInstallAction`, `TestApplyInstallPlan` |
| 10 | Core write helpers enforce root containment, no-overwrite, all-or-nothing, no duplicates | OK | `TestApplyInstallPlan` |

## Safety Gates

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | No CLI path exposes real installer writes to the repo root without `--yes` | OK | CLI requires `--yes` for real install |
| 2 | `validate_project_name` blocks traversal and path separators | OK | `TestValidateProjectName` |
| 3 | `check_install_safety` blocks generated/binary areas and absolute paths | OK | `TestCheckInstallSafety` |
| 4 | `apply_install_plan` detects duplicate resolved targets before writing | OK | `test_duplicate_target_aborts_all` |
| 5 | All write-helper tests use isolated temp directories | OK | Every `TestApplyInstall*` test |

## Non-Functional Gates

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | Zero external test dependencies (stdlib `unittest` only) | OK | `tests/` imports |
| 2 | Console script entry point defined in `pyproject.toml` | OK | `gpt2whatever = gpt2whatever.cli:main` |
| 3 | Package metadata declares preview 1.0 version and README | OK | `pyproject.toml`, `--version` |
| 4 | No committed secrets or session content | OK | `.gitignore`, privacy boundary rules |

## Post-1.0 Candidates

- Doctor command for checking kit health and common setup issues.
- Packaged release paths such as PyPI and standalone zip.
- Example projects showing T1/T2/T3 rounds.
