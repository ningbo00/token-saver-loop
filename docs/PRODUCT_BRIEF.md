# Product Brief - Token Saver Loop

## Product Position

Token Saver Loop is a portable workflow kit for splitting AI development work into two roles:
- **Reviewer**: plans, bounds risk, reviews evidence, and decides pass/fix/stop.
- **Worker**: performs bounded execution, runs checks, and writes compact evidence.

The product is portable-only. Users copy `portable/token-saver-kit/` into a target project. The Python CLI provides diagnostics and metrics, but it does not write workflow files into projects.

## Core User Flow

1. Copy `portable/token-saver-kit/` into a project root.
2. Ask a reviewer model to create a bounded task.
3. Generate or copy the worker prompt.
4. Let a worker model execute within the tier limits.
5. Ask the reviewer to verify reports, diffs, tests, and state.

## Non-Goals

- No installer mode.
- No project-root file scattering.
- No SaaS, database, or agent runtime.
- No model lock-in.

## CLI Scope

Allowed CLI helpers:
- `--doctor`
- `--show-config`
- `--show-project-skill`
- `--parse-worker-usage-jsonl`
- `--record-reviewer-usage`
- metrics append and summary commands

The CLI should remain read-only with respect to workflow files in target projects.
