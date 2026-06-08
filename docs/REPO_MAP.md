# REPO_MAP

Current structure:
- `tools/`: PowerShell scripts for the Kimi-Codex semi-automatic workflow.
- `docs/`: Planning and context documents.
  - `AGENT_CONTEXT.md`: compact project handoff context.
  - `REPO_MAP.md`: compact repo map.
  - `PRODUCT_BRIEF.md`: product direction (portable Kimi-Codex workflow kit).
  - `IMPLEMENTATION_OPTIONS.md`: technical options and trade-offs.
  - `KIMI_TOKEN_USAGE_RESEARCH.md`: token usage availability research.
- `KIMI_CODEX_LOOP.md`: human-readable workflow notes.
- `README.md`: project overview, quick-start, token usage preview, and metrics examples.
- `pyproject.toml`: Python package metadata and console script entry point.
- `src/gpt2whatever/`: Python source package.
  - `__init__.py`: package init.
  - `templates.py`: built-in format templates (legacy, retained for compatibility).
  - `core.py`: input reading, message building, response extraction (legacy); workflow-kit helpers (`default_project_config`, `render_project_worker_skill`, `planned_install_paths`); token usage helpers (`parse_kimi_usage_counts_from_jsonl`, `summarize_kimi_usage_counts`, `build_round_token_usage_record`); metrics aggregation helpers (`parse_jsonl_records`, `build_codex_usage_snapshot`, `summarize_token_usage_records`); metrics file I/O helpers (`default_metrics_path`, `append_jsonl_record`, `load_jsonl_records_from_file`); installer dry-run helper (`build_install_dry_run_plan`).
  - `cli.py`: argparse-based CLI supporting legacy flags, workflow-kit flags, token usage preview flags, metrics aggregation flags (`--record-codex-usage`, `--summarize-token-usage-jsonl`), metrics append flags (`--append-metrics`, `--append-default-metrics`, `--summary-after-append`), and installer dry-run flag (`--install --dry-run`).
- `tests/`: unit tests (stdlib unittest).
  - `test_core.py`: tests for templates, core functions, workflow-kit helpers, token usage helpers, and metrics aggregation helpers.
  - `test_cli.py`: tests for CLI behavior including workflow-kit, token usage, and metrics aggregation flags.

Generated during tasks:
- `.ai/active_task/`: active Kimi-Codex task state and logs.
