# Gpt2Whatever

A portable **Kimi-Codex workflow kit** for applying adaptive Kimi execution + Codex review to any coding project.

Turn any repository into a Kimi-Codex managed project by generating the required directory structure, state files, tool scripts, and local worker skills.

## Status

This project is pivoting from its earlier "LLM-to-structured-output converter" direction into a reusable workflow installer.

Current capabilities:
- Preview project configuration (`--show-config`)
- Preview generated worker skill (`--show-project-skill`)
- List planned install paths (`--list-install-paths`)
- Parse Kimi session JSONL for token usage totals (`--parse-kimi-usage-jsonl`)
- Record manual Codex usage snapshot (`--record-codex-usage`)
- Summarize mixed token usage JSONL (`--summarize-token-usage-jsonl`)
- Append metrics records to a JSONL file (`--append-metrics`, `--append-default-metrics`)
- Show summary after appending (`--summary-after-append`)
- Preview installer dry-run (`--install --dry-run`)

**Real file-system installation is not yet implemented.** Use preview flags to inspect what would be installed.

## Quick Start

```bash
# Preview the config for a new project
gpt2whatever --project-name MyApp --test-command "pytest" --show-config

# Preview the generated worker skill
gpt2whatever --project-name MyApp --test-command "npm test" --show-project-skill

# List paths that a future installer would create
gpt2whatever --list-install-paths
```

## Token Usage Preview

Kimi Code for VS Code does **not** display token usage in the UI. However, local Kimi session files may contain `_usage` records with total token counts.

You can preview token usage for a round by pointing the CLI at a Kimi `context.jsonl` file:

```bash
gpt2whatever \
  --parse-kimi-usage-jsonl ~/.kimi/sessions/<session>/<uuid>/context.jsonl \
  --round-name round_005 \
  --tier T2
```

This prints a JSON record with `start_token_count`, `end_token_count`, `delta_token_count`, and `peak_token_count`.

> **Privacy note:** The parser only extracts lines where `role == "_usage"`. It does not return or store conversation content.

## Manual Codex Usage Snapshot

Codex token usage cannot be read automatically yet. You can record a manual snapshot from your Codex Profile page:

```bash
gpt2whatever \
  --record-codex-usage \
  --codex-input-tokens 2300000 \
  --codex-output-tokens 44000 \
  --codex-total-tokens 2344000 \
  --codex-requests 71
```

This prints a JSON snapshot you can append to your metrics JSONL file.

## Summarize Token Usage

If you have a JSONL file with mixed Kimi and Codex usage records, you can summarize it:

```bash
gpt2whatever --summarize-token-usage-jsonl path/to/token_usage.jsonl
```

This prints aggregated totals: Kimi delta sum and latest Codex totals.

## Appending Metrics

When you generate a token usage record, you can append it directly to a metrics JSONL file instead of copying it manually.

Append a Codex snapshot to the default metrics file:

```bash
gpt2whatever \
  --record-codex-usage \
  --codex-input-tokens 2300000 \
  --codex-output-tokens 44000 \
  --codex-total-tokens 2344000 \
  --codex-requests 71 \
  --append-default-metrics
```

Append a Kimi record and print a summary of the whole metrics file:

```bash
gpt2whatever \
  --parse-kimi-usage-jsonl path/to/context.jsonl \
  --round-name round_008 \
  --tier T2 \
  --append-default-metrics \
  --summary-after-append
```

The default metrics path is `.ai/metrics/token_usage.jsonl`. You can also use `--append-metrics <path>` to target a custom file. The two append flags are mutually exclusive.

## Installation (dev)

Requires Python 3.10+.

```bash
pip install -e .
```

## Usage

```
gpt2whatever [--project-name NAME] [--test-command CMD]
             [--show-config] [--show-project-skill] [--list-install-paths]
             [--parse-kimi-usage-jsonl PATH] [--round-name NAME] [--tier TIER]
             [--record-codex-usage]
             [--codex-input-tokens N] [--codex-output-tokens N]
             [--codex-total-tokens N] [--codex-requests N] [--codex-notes TEXT]
             [--summarize-token-usage-jsonl PATH]
             [--append-metrics PATH] [--append-default-metrics]
             [--summary-after-append]
```

### Options

- `--project-name` — Target project name used in config and skill generation
- `--test-command` — Default test command to embed in the project worker skill
- `--show-config` — Print the default project config JSON and exit
- `--show-project-skill` — Print the generated worker SKILL.md content and exit
- `--list-install-paths` — List planned installation paths and exit
- `--parse-kimi-usage-jsonl` — Parse a Kimi context.jsonl for `_usage` token counts
- `--round-name` — Round label for the token usage record (default: `unknown`)
- `--tier` — Tier label for the token usage record (default: `unknown`)
- `--record-codex-usage` — Print a Codex usage snapshot JSON
- `--codex-input-tokens` — Input tokens for the Codex snapshot
- `--codex-output-tokens` — Output tokens for the Codex snapshot
- `--codex-total-tokens` — Total tokens for the Codex snapshot
- `--codex-requests` — Request count for the Codex snapshot
- `--codex-notes` — Optional notes for the Codex snapshot
- `--summarize-token-usage-jsonl` — Summarize a token usage JSONL file
- `--append-metrics` — Append the generated record to a custom JSONL file
- `--append-default-metrics` — Append the generated record to `.ai/metrics/token_usage.jsonl`
- `--summary-after-append` — After appending, print `{"appended": ..., "summary": ...}`
- `--install` — Install the Kimi-Codex workflow kit (requires `--dry-run` for now)
- `--project-name` — Must contain only letters, digits, underscores, and hyphens when used with `--install`

## Examples

```bash
# Preview config for a Python project
gpt2whatever --project-name MyBackend --test-command "python -m pytest" --show-config

# Preview skill for a Node project
gpt2whatever --project-name MyFrontend --test-command "npm test" --show-project-skill

# See all paths the installer would touch
gpt2whatever --list-install-paths

# Preview token usage from a Kimi session JSONL
gpt2whatever \
  --parse-kimi-usage-jsonl path/to/context.jsonl \
  --round-name round_005 \
  --tier T2

# Record a manual Codex snapshot
gpt2whatever \
  --record-codex-usage \
  --codex-input-tokens 2300000 \
  --codex-output-tokens 44000 \
  --codex-total-tokens 2344000 \
  --codex-requests 71

# Summarize mixed usage JSONL
gpt2whatever --summarize-token-usage-jsonl path/to/token_usage.jsonl

# Append Codex snapshot to default metrics path
gpt2whatever \
  --record-codex-usage \
  --codex-input-tokens 2300000 \
  --codex-output-tokens 44000 \
  --codex-total-tokens 2344000 \
  --codex-requests 71 \
  --append-default-metrics

# Append Kimi record with summary
gpt2whatever \
  --parse-kimi-usage-jsonl path/to/context.jsonl \
  --round-name round_008 \
  --tier T2 \
  --append-default-metrics \
  --summary-after-append

# Preview installer dry-run
gpt2whatever \
  --install --dry-run \
  --project-name MyApp \
  --test-command "pytest"
```
