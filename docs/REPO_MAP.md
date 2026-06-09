# REPO_MAP

Current structure:
- `tools/`: PowerShell scripts for the Kimi-Codex semi-automatic workflow.
- `docs/`: Planning and context documents.
  - `AGENT_CONTEXT.md`: compact project handoff context.
  - `BEGINNER_GUIDE.md`: step-by-step beginner guide for the portable workflow.
  - `REPO_MAP.md`: compact repo map.
  - `PRODUCT_BRIEF.md`: product direction (portable Token Saver Loop).
  - `IMPLEMENTATION_OPTIONS.md`: technical options and trade-offs.
  - `KIMI_TOKEN_USAGE_RESEARCH.md`: token usage availability research.
  - `RELEASE_1_0_CHECKLIST.md`: 1.0 release gates for portable kit, dry-run, and gated real install.
- `KIMI_CODEX_LOOP.md`: human-readable workflow notes.
- `CODEX_CONTINUE.md`: stable fresh-thread bootstrap prompt and low-token continuation protocol.
- `README.md`: GitHub-first, portable-first landing page for the Token Saver Loop.
- `README.zh-CN.md`, `README.ja.md`, `README.ko.md`: localized README files linked from the English README.
- `LICENSE`: MIT license for GitHub license detection.
- `examples/minimal-task.md`: inspect-only starter example for first-time users.
- `pyproject.toml`: Python package metadata (`1.0.0` preview-only) and console script entry point.
- `src/token_saver_loop/`: Python source package.
  - `__init__.py`: package init and package version.
  - `templates.py`: built-in format templates (legacy, retained for compatibility).
  - `core.py`: input reading, message building, response extraction (legacy); workflow-kit helpers (`default_project_config`, `render_project_worker_skill`, `planned_install_paths`); token usage helpers (`parse_kimi_usage_counts_from_jsonl`, `summarize_kimi_usage_counts`, `build_round_token_usage_record`); metrics aggregation helpers (`parse_jsonl_records`, `build_codex_usage_snapshot`, `summarize_token_usage_records`); metrics file I/O helpers (`default_metrics_path`, `append_jsonl_record`, `load_jsonl_records_from_file`); installer dry-run helper (`build_install_dry_run_plan`) and install apply helpers.
  - `cli.py`: argparse-based CLI supporting `--version`, legacy flags, workflow-kit flags, token usage preview flags, metrics aggregation flags (`--record-codex-usage`, `--summarize-token-usage-jsonl`), metrics append flags (`--append-metrics`, `--append-default-metrics`, `--summary-after-append`), installer dry-run flag (`--install --dry-run`), and gated real install (`--install --yes`).
- `tests/`: unit tests (stdlib unittest).
  - `test_core.py`: tests for templates, core functions, workflow-kit helpers, token usage helpers, and metrics aggregation helpers.
  - `test_cli.py`: tests for CLI behavior including workflow-kit, token usage, and metrics aggregation flags.

Generated during tasks:
- `.ai/active_task/`: active Kimi-Codex task state and logs; local-only, not intended for GitHub publishing.
  - `progress.md`: user-facing rough progress board updated after each Kimi round; navigation only, not a verification source.
- `portable/kimi-codex-kit/`: no-install drop-in kit; state lives under the kit-local `.ai/active_task/`.

