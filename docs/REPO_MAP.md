# REPO_MAP

Current structure:
- `docs/`: Planning and context documents.
  - `AGENT_CONTEXT.md`: compact project handoff context.
  - `BEGINNER_GUIDE.md`: step-by-step beginner guide for the portable workflow.
  - `GITHUB_PROMOTION_KIT.md`: copy-ready GitHub/social launch text, suggested topics, and release draft.
  - `REPO_MAP.md`: compact repo map.
  - `assets/token-saver-loop-demo.gif`: README first-screen animated workflow demo.
  - `assets/demo-loop-animation.html`: web animation source for the README demo.
  - `assets/demo-loop.svg`: static workflow visual fallback.
  - `PRODUCT_BRIEF.md`: product direction (portable Token Saver Loop).
  - `IMPLEMENTATION_OPTIONS.md`: technical options and trade-offs.
  - `RELEASE_1_0_CHECKLIST.md`: 1.0 release gates for the portable-only kit.
  - `releases/v1.08.md`: GitHub release notes draft for the current public tag.
- `README.md`: GitHub-first, portable-first landing page for the Token Saver Loop.
- `README.zh-CN.md`, `README.ja.md`, `README.ko.md`: localized README files linked from the English README.
- `LICENSE`: MIT license for GitHub license detection.
- `CODE_OF_CONDUCT.md`: community behavior expectations.
- `CONTRIBUTING.md`: contribution workflow and project direction.
- `SECURITY.md`: security reporting and boundaries.
- `examples/`: starter and promotion-facing workflow examples.
  - `minimal-task.md`: inspect-only starter example for first-time users.
  - `codex-worker-round.md`: bounded code-edit worker round example.
  - `bugfix-loop.md`: focused debug/fix loop example.
  - `docs-i18n-loop.md`: documentation and localization batch example.
- `pyproject.toml`: Python package metadata (`1.0.8` preview-only) and console script entry point.
- `scripts/render_demo_gif.py`: renders the README animated workflow GIF from Pillow drawing commands.
- `.github/ISSUE_TEMPLATE/`: GitHub issue forms for bug reports and feature requests.
- `.github/PULL_REQUEST_TEMPLATE.md`: pull request checklist and validation prompt.
- `src/token_saver_loop/`: Python source package.
  - `__init__.py`: package init and package version.
  - `templates.py`: built-in format templates (legacy, retained for compatibility).
  - `core.py`: input reading, message building, response extraction (legacy); workflow-kit helpers (`default_project_config`, `render_project_worker_skill`, `build_doctor_report`); token usage helpers (`parse_worker_usage_counts_from_jsonl`, `summarize_worker_usage_counts`, `build_round_token_usage_record`); metrics aggregation helpers (`parse_jsonl_records`, `build_reviewer_usage_snapshot`, `summarize_token_usage_records`); metrics file I/O helpers (`default_metrics_path`, `append_jsonl_record`, `load_jsonl_records_from_file`).
  - `cli.py`: argparse-based CLI supporting `--version`, legacy flags, workflow-kit flags, setup doctor (`--doctor`), token usage preview flags, metrics aggregation flags (`--record-reviewer-usage`, `--summarize-token-usage-jsonl`), and metrics append flags (`--append-metrics`, `--append-default-metrics`, `--summary-after-append`).
- `tests/`: unit tests (stdlib unittest).
  - `test_core.py`: tests for templates, core functions, workflow-kit helpers, token usage helpers, and metrics aggregation helpers.
  - `test_cli.py`: tests for CLI behavior including workflow-kit, token usage, and metrics aggregation flags.
- `portable/token-saver-kit/`: no-install drop-in kit; state lives under the kit-local `.ai/active_task/`.
  - `START_HERE.md`: minimal entry point and role boundary rules.
  - `LATEST_WORKER_PROMPT.md`: stable copy of the newest worker prompt.
  - `.ai/project_memory/`: compact goal, architecture, completed work, risks, and latest evidence memory files.
  - `WORKER_NEXT_TASK.md`: current bounded worker task.
  - `REVIEWER_CONTINUE.md`: reviewer continuation protocol.
  - `TOKEN_SAVER_LOOP.md`: workflow notes.
  - `skills/reviewer.md`: reviewer skill reference.
  - `skills/worker.md`: worker skill reference.
  - `tools/`: optional AI/advanced automation helpers for workflow bookkeeping, status prompts, project memory, evidence verdicts, compact review packs, and key-risk checks.
    - `tsl-new-round.ps1`: creates round prompts plus `round_status.json` lifecycle marker.
    - `tsl-review.ps1` / `tsl-redflags.ps1`: summarize evidence, respect `round_status.json`, and keep verdicts non-final.

Generated during tasks:
- `.ai/active_task/`: active worker/reviewer task state and logs; local-only, not intended for GitHub publishing.
  - `progress.md`: user-facing rough progress board updated after each worker round; navigation only, not a verification source.
  - `rounds/round_XXX/round_status.json`: lifecycle marker (`prompt_ready`, worker `in_progress`, final `done`) used to avoid reviewing half-written reports.



