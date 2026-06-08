"""Command-line interface for gpt2whatever."""

import argparse
import json
import sys
from pathlib import Path

from gpt2whatever.core import (
    append_jsonl_record,
    build_codex_usage_snapshot,
    build_install_dry_run_plan,
    build_messages,
    build_round_token_usage_record,
    default_metrics_path,
    default_project_config,
    load_jsonl_records_from_file,
    parse_jsonl_records,
    parse_kimi_usage_counts_from_jsonl_file,
    planned_install_paths,
    read_input,
    render_project_worker_skill,
    summarize_token_usage_records,
    validate_project_name,
)
from gpt2whatever.templates import list_templates


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gpt2whatever",
        description="Portable Kimi-Codex workflow kit for any project.",
    )

    # Legacy LLM-converter flags (retained for backward compatibility)
    parser.add_argument(
        "-i", "--input", default=None, help="Input file path (default: stdin)"
    )
    parser.add_argument(
        "-f", "--format", default="json", help="Output format template"
    )
    parser.add_argument(
        "--instruction",
        default=None,
        help="Extra instruction appended to the system prompt",
    )
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List available formats and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the built messages without calling the API",
    )

    # New workflow-kit flags
    parser.add_argument(
        "--project-name",
        default=None,
        help="Target project name for config and skill generation",
    )
    parser.add_argument(
        "--test-command",
        default=None,
        help="Default test command to embed in the project worker skill",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Print the default project config JSON and exit",
    )
    parser.add_argument(
        "--show-project-skill",
        action="store_true",
        help="Print the generated worker SKILL.md content and exit",
    )
    parser.add_argument(
        "--list-install-paths",
        action="store_true",
        help="List planned installation paths and exit",
    )

    # Token usage flags
    parser.add_argument(
        "--parse-kimi-usage-jsonl",
        default=None,
        help="Path to a Kimi context.jsonl file to parse for token usage",
    )
    parser.add_argument(
        "--round-name",
        default="unknown",
        help="Round name for the token usage record",
    )
    parser.add_argument(
        "--tier",
        default="unknown",
        help="Tier for the token usage record",
    )

    # Metrics aggregation flags
    parser.add_argument(
        "--record-codex-usage",
        action="store_true",
        help="Print a Codex usage snapshot JSON to stdout",
    )
    parser.add_argument(
        "--codex-input-tokens",
        type=int,
        default=None,
        help="Codex input tokens for the snapshot",
    )
    parser.add_argument(
        "--codex-output-tokens",
        type=int,
        default=None,
        help="Codex output tokens for the snapshot",
    )
    parser.add_argument(
        "--codex-total-tokens",
        type=int,
        default=None,
        help="Codex total tokens for the snapshot",
    )
    parser.add_argument(
        "--codex-requests",
        type=int,
        default=None,
        help="Codex request count for the snapshot",
    )
    parser.add_argument(
        "--codex-notes",
        default=None,
        help="Optional notes for the Codex snapshot",
    )
    parser.add_argument(
        "--summarize-token-usage-jsonl",
        default=None,
        help="Path to a token usage JSONL file to summarize",
    )

    # Metrics append flags
    parser.add_argument(
        "--append-metrics",
        default=None,
        help="Path to a JSONL file to append the generated record to",
    )
    parser.add_argument(
        "--append-default-metrics",
        action="store_true",
        help="Append the generated record to the default metrics path",
    )
    parser.add_argument(
        "--summary-after-append",
        action="store_true",
        help="After appending, print an object with 'appended' and 'summary' keys",
    )

    # Installer flags
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install the Kimi-Codex workflow kit into the current project",
    )

    return parser


def _resolve_append_path(parsed) -> str | None:
    """Return the metrics file path to append to, or None if not appending."""
    if parsed.append_metrics and parsed.append_default_metrics:
        return "both"
    if parsed.append_metrics:
        return parsed.append_metrics
    if parsed.append_default_metrics:
        return default_metrics_path()
    return None


def _maybe_append_and_print(record: dict, append_path: str | None, summary_after: bool) -> None:
    """Optionally append *record* to *append_path*, then print record or appended+summary object."""
    if append_path:
        append_jsonl_record(append_path, record)
    if summary_after and append_path:
        records = load_jsonl_records_from_file(append_path)
        summary = summarize_token_usage_records(records)
        output = {"appended": record, "summary": summary}
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(record, indent=2, ensure_ascii=False))


def main(args: list[str] | None = None) -> int:
    parser = create_parser()
    parsed = parser.parse_args(args)

    append_path = _resolve_append_path(parsed)
    if append_path == "both":
        print(
            "Error: --append-metrics and --append-default-metrics are mutually exclusive.",
            file=sys.stderr,
        )
        return 1

    # Validate append flags are paired with a record-producing command
    record_producing = parsed.record_codex_usage or parsed.parse_kimi_usage_jsonl
    if append_path and not record_producing:
        print(
            "Error: --append-metrics / --append-default-metrics require a record-producing command "
            "such as --record-codex-usage or --parse-kimi-usage-jsonl.",
            file=sys.stderr,
        )
        return 1

    # Metrics aggregation handlers (checked first)
    if parsed.record_codex_usage:
        missing = []
        for name, value in [
            ("--codex-input-tokens", parsed.codex_input_tokens),
            ("--codex-output-tokens", parsed.codex_output_tokens),
            ("--codex-total-tokens", parsed.codex_total_tokens),
            ("--codex-requests", parsed.codex_requests),
        ]:
            if value is None:
                missing.append(name)
        if missing:
            print(
                f"Error: Missing required fields: {', '.join(missing)}",
                file=sys.stderr,
            )
            return 1
        try:
            snapshot = build_codex_usage_snapshot(
                input_tokens=parsed.codex_input_tokens,
                output_tokens=parsed.codex_output_tokens,
                total_tokens=parsed.codex_total_tokens,
                requests=parsed.codex_requests,
                notes=parsed.codex_notes,
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        _maybe_append_and_print(snapshot, append_path, parsed.summary_after_append)
        return 0

    if parsed.summarize_token_usage_jsonl:
        p = Path(parsed.summarize_token_usage_jsonl)
        if not p.exists():
            print(
                f"Error: File not found: {parsed.summarize_token_usage_jsonl}",
                file=sys.stderr,
            )
            return 1
        jsonl_text = p.read_text(encoding="utf-8")
        records = parse_jsonl_records(jsonl_text)
        summary = summarize_token_usage_records(records)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    # Token usage handler
    if parsed.parse_kimi_usage_jsonl:
        p = Path(parsed.parse_kimi_usage_jsonl)
        if not p.exists():
            print(
                f"Error: File not found: {parsed.parse_kimi_usage_jsonl}",
                file=sys.stderr,
            )
            return 1
        counts = parse_kimi_usage_counts_from_jsonl_file(p)
        record = build_round_token_usage_record(
            round_name=parsed.round_name,
            tier=parsed.tier,
            counts=counts,
        )
        _maybe_append_and_print(record, append_path, parsed.summary_after_append)
        return 0

    # Workflow-kit handlers
    if parsed.list_install_paths:
        for path in planned_install_paths():
            print(path)
        return 0

    if parsed.show_config:
        if not parsed.project_name:
            print("Error: --show-config requires --project-name.", file=sys.stderr)
            return 1
        config = default_project_config(parsed.project_name)
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return 0

    if parsed.show_project_skill:
        if not parsed.project_name:
            print(
                "Error: --show-project-skill requires --project-name.",
                file=sys.stderr,
            )
            return 1
        skill_text = render_project_worker_skill(
            parsed.project_name, parsed.test_command
        )
        print(skill_text)
        return 0

    # Installer handler
    if parsed.install:
        if not parsed.dry_run:
            print(
                "Error: Real installation is not implemented yet. "
                "Use --install --dry-run to preview.",
                file=sys.stderr,
            )
            return 1
        if parsed.project_name is None:
            print(
                "Error: --install --dry-run requires --project-name.",
                file=sys.stderr,
            )
            return 1
        try:
            validate_project_name(parsed.project_name)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        plan = build_install_dry_run_plan(
            project_name=parsed.project_name,
            test_command=parsed.test_command,
        )
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0

    # Legacy LLM-converter handlers
    if parsed.list_formats:
        for fmt in list_templates():
            print(fmt)
        return 0

    try:
        input_text = read_input(parsed.input)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    messages = build_messages(input_text, parsed.format, parsed.instruction)

    if parsed.dry_run:
        print(json.dumps(messages, indent=2, ensure_ascii=False))
        return 0

    print(
        "Error: API call is not implemented yet. Use --dry-run for now.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
