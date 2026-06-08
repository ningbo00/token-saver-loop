"""Core logic for the workflow kit.

Legacy LLM-converter helpers (read_input, build_messages, extract_text_from_response)
are retained for backward compatibility. New workflow-kit helpers are below.
"""

import json
import sys
from pathlib import Path

from gpt2whatever.templates import get_template


# ---------- Legacy LLM-converter helpers ----------


def read_input(input_path: str | None) -> str:
    """Read text from a file or stdin."""
    if input_path is None:
        return sys.stdin.read()
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    return p.read_text(encoding="utf-8")


def build_messages(
    input_text: str, format_name: str, extra_instruction: str | None = None
) -> list[dict[str, str]]:
    """Build OpenAI-compatible messages using the selected template."""
    template = get_template(format_name)
    system_content = template
    if extra_instruction:
        system_content = f"{template}\n\nAdditional instruction: {extra_instruction}"
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": input_text},
    ]


def extract_text_from_response(response: dict) -> str:
    """Extract the assistant's text from an OpenAI-style chat completion response."""
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"Invalid response structure: {exc}") from exc


# ---------- Workflow-kit helpers ----------


def default_project_config(project_name: str) -> dict:
    """Return the default configuration for a new Kimi-Codex managed project."""
    return {
        "project_name": project_name,
        "workflow_name": "kimi-codex",
        "tiers": ["T0", "T1", "T2", "T3"],
        "active_task_dir": ".ai/active_task",
        "rounds_dir": ".ai/active_task/rounds",
        "docs_dir": "docs",
        "tools_dir": "tools",
        "skills_dir": ".kimi-code/skills",
    }


def render_project_worker_skill(
    project_name: str, test_command: str | None = None
) -> str:
    """Return the content of a project-local kimi-codex-worker SKILL.md."""
    test_cmd_line = (
        f"Default test command: `{test_command}`"
        if test_command
        else "No default test command configured."
    )
    return f"""---
name: kimi-codex-worker
description: Work as the Kimi executor in a Codex-reviewed loop for {project_name}.
type: prompt
whenToUse: When executing a Kimi round for {project_name} under Codex review.
---

# Kimi-Codex Worker Skill — {project_name}

You are the Kimi executor in a Codex-reviewed workflow for **{project_name}**.

## Role
- Kimi implements, explores, runs commands, and writes logs.
- Codex plans, reviews, decides pass/fix/downgrade/stop, and owns final quality.

## Tier Rules
- T3: Free execution. Small patch.
- T2: Bounded execution. Stay inside requested files.
- T1: Instruction execution. Follow steps exactly.
- T0: No implementation. Inspect and report only.

## Required Artifacts
- `.ai/active_task/rounds/round_XXX/kimi_log.md`
- `.ai/active_task/rounds/round_XXX/kimi_report.json`

{test_cmd_line}
"""


def planned_install_paths() -> list[str]:
    """Return the list of paths that a future installer would create."""
    return [
        ".ai/active_task/state.md",
        ".ai/active_task/task.md",
        "docs/AGENT_CONTEXT.md",
        "docs/REPO_MAP.md",
        "tools/ai-kimi-init.ps1",
        "tools/ai-kimi-run.ps1",
        "tools/ai-kimi-review-pack.ps1",
        "tools/ai-kimi-verdict.ps1",
        ".kimi-code/skills/kimi-codex-worker/SKILL.md",
    ]


# ---------- Token usage helpers ----------


def parse_kimi_usage_counts_from_jsonl(jsonl_text: str) -> list[int]:
    """Extract `_usage` token_count values from Kimi session JSONL text.

    Only inspects lines where role == "_usage". Ignores invalid JSON,
    non-dict lines, and any non-numeric token_count values.
    Does not return or expose conversation content.
    """
    counts: list[int] = []
    for line in jsonl_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if obj.get("role") != "_usage":
            continue
        tc = obj.get("token_count")
        if isinstance(tc, int):
            counts.append(tc)
        elif isinstance(tc, str):
            try:
                counts.append(int(tc))
            except ValueError:
                continue
    return counts


def parse_kimi_usage_counts_from_jsonl_file(path: str | Path) -> list[int]:
    """Stream a JSONL file and extract only `_usage` token_count values.

    Reads line-by-line to avoid loading the entire file into memory.
    Only inspects lines where role == "_usage". Ignores invalid JSON,
    non-dict lines, and any non-numeric token_count values.
    Does not return or expose conversation content.
    """
    counts: list[int] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            if obj.get("role") != "_usage":
                continue
            tc = obj.get("token_count")
            if isinstance(tc, int):
                counts.append(tc)
            elif isinstance(tc, str):
                try:
                    counts.append(int(tc))
                except ValueError:
                    continue
    return counts


def summarize_kimi_usage_counts(counts: list[int]) -> dict:
    """Return a summary dict for a list of usage counts."""
    if not counts:
        return {
            "start_token_count": None,
            "end_token_count": None,
            "delta_token_count": None,
            "peak_token_count": None,
            "usage_entries": 0,
        }
    return {
        "start_token_count": counts[0],
        "end_token_count": counts[-1],
        "delta_token_count": max(0, counts[-1] - counts[0]),
        "peak_token_count": max(counts),
        "usage_entries": len(counts),
    }


def build_round_token_usage_record(
    round_name: str,
    tier: str,
    counts: list[int],
    source: str = "kimi_context_jsonl",
    notes: str | None = None,
) -> dict:
    """Build a round-level token usage record dict."""
    summary = summarize_kimi_usage_counts(counts)
    measurement_mode = "actual_total_only" if counts else "unavailable"
    if not counts and notes is None:
        notes = "No _usage entries found."
    return {
        "version": 1,
        "actor": "kimi",
        "round": round_name,
        "tier": tier,
        "source": source,
        "measurement_mode": measurement_mode,
        "start_token_count": summary["start_token_count"],
        "end_token_count": summary["end_token_count"],
        "delta_token_count": summary["delta_token_count"],
        "peak_token_count": summary["peak_token_count"],
        "usage_entries": summary["usage_entries"],
        "prompt_tokens": None,
        "completion_tokens": None,
        "notes": notes,
    }


# ---------- Metrics aggregation helpers ----------


def parse_jsonl_records(jsonl_text: str) -> list[dict]:
    """Parse JSONL text into a list of dict records.

    Ignores invalid JSON lines and non-dict JSON values.
    """
    records: list[dict] = []
    for line in jsonl_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        records.append(obj)
    return records


def build_codex_usage_snapshot(
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    requests: int,
    source: str = "manual_codex_profile_snapshot",
    notes: str | None = None,
) -> dict:
    """Build a Codex usage snapshot dict.

    Validates that all numeric fields are non-negative ints.
    """
    for name, value in [
        ("input_tokens", input_tokens),
        ("output_tokens", output_tokens),
        ("total_tokens", total_tokens),
        ("requests", requests),
    ]:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative int, got {value!r}")
    return {
        "version": 1,
        "actor": "codex",
        "source": source,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "requests": requests,
        "notes": notes,
    }


def summarize_token_usage_records(records: list[dict]) -> dict:
    """Summarize a list of mixed Kimi and Codex token usage records.

    - Kimi: sums delta_token_count when actor is "kimi" (or inferred from
      delta_token_count presence for backward compatibility).
    - Codex: uses the latest total_tokens, input_tokens, output_tokens,
      and requests from the last codex record.
    """
    kimi_delta_total = 0
    codex_latest_input: int | None = None
    codex_latest_output: int | None = None
    codex_latest_total: int | None = None
    codex_latest_requests: int | None = None

    for rec in records:
        actor = rec.get("actor")
        if actor == "kimi" or (actor is None and "delta_token_count" in rec):
            delta = rec.get("delta_token_count")
            if isinstance(delta, int):
                kimi_delta_total += delta
        elif actor == "codex":
            total = rec.get("total_tokens")
            if isinstance(total, int):
                codex_latest_total = total
                codex_latest_input = rec.get("input_tokens")
                codex_latest_output = rec.get("output_tokens")
                codex_latest_requests = rec.get("requests")

    return {
        "kimi_delta_tokens_total": kimi_delta_total,
        "codex_latest_input_tokens": codex_latest_input,
        "codex_latest_output_tokens": codex_latest_output,
        "codex_latest_total_tokens": codex_latest_total,
        "codex_latest_requests": codex_latest_requests,
        "records_count": len(records),
    }


# ---------- Installer dry-run helpers ----------


import re

_PROJECT_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def validate_project_name(name: str) -> str:
    """Validate a project name for use in generated paths.

    Rejects empty, whitespace-only, or names containing path separators,
    traversal sequences, or other unsafe characters.

    Allowed characters: letters, digits, underscore, and hyphen.
    """
    if not isinstance(name, str):
        raise ValueError(f"project_name must be a string, got {type(name).__name__}")
    stripped = name.strip()
    if not stripped:
        raise ValueError("project_name must be a non-empty string")
    if stripped != name:
        raise ValueError("project_name must not have leading or trailing whitespace")
    if ".." in stripped:
        raise ValueError("project_name must not contain '..'")
    if not _PROJECT_NAME_RE.match(stripped):
        raise ValueError(
            "project_name must contain only letters, digits, underscores, and hyphens"
        )
    return stripped


def build_install_dry_run_plan(
    project_name: str,
    test_command: str | None = None,
) -> dict:
    """Build a dry-run install plan dict without writing any files.

    Returns a versioned JSON-ready dict with one action entry per planned
    install path. Existing files are flagged as conflicts.
    """
    project_name = validate_project_name(project_name)
    paths = planned_install_paths()
    # Project-specific skill path
    skill_path = f".kimi-code/skills/{project_name}-kimi-codex-worker/SKILL.md"
    all_paths = paths + [skill_path]

    actions: list[dict] = []
    for path in all_paths:
        p = Path(path)
        exists = p.exists()
        action = "modify" if exists else "create"
        conflict = "existing" if exists else None
        reason = "Planned install path"
        if path == skill_path:
            reason = "Project-specific worker skill"
        actions.append(
            {
                "path": path,
                "action": action,
                "reason": reason,
                "conflict": conflict,
            }
        )

    return {
        "version": 1,
        "project_name": project_name,
        "test_command": test_command,
        "actions": actions,
    }


# ---------- Metrics file I/O helpers ----------


def default_metrics_path() -> str:
    """Return the default path for the token usage metrics JSONL file."""
    return ".ai/metrics/token_usage.jsonl"


def append_jsonl_record(path: str | Path, record: dict) -> None:
    """Append a single JSON record as one line to a JSONL file.

    Creates parent directories if needed. Validates that *record* is a dict.
    Does not overwrite existing content.
    """
    if not isinstance(record, dict):
        raise ValueError(f"record must be a dict, got {type(record).__name__}")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_jsonl_records_from_file(path: str | Path) -> list[dict]:
    """Load JSONL records from a file.

    Returns an empty list if the file does not exist.
    Reuses ``parse_jsonl_records`` for parsing.
    """
    p = Path(path)
    if not p.exists():
        return []
    return parse_jsonl_records(p.read_text(encoding="utf-8"))
