"""Core logic for the workflow kit.

Legacy LLM-converter helpers (read_input, build_messages, extract_text_from_response)
are retained for backward compatibility. New workflow-kit helpers are below.
"""

import json
import re
import sys
from pathlib import Path

from token_saver_loop.templates import get_template


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
    """Return the default configuration for a Token Saver Loop managed project."""
    return {
        "project_name": project_name,
        "workflow_name": "token-saver-loop",
        "default_worker_command": None,
        "worker_model_examples": ["worker-cli"],
        "reviewer_role": "high-tier reviewer model",
        "tiers": ["T0", "T1", "T2", "T3"],
        "active_task_dir": ".ai/active_task",
        "rounds_dir": ".ai/active_task/rounds",
        "docs_dir": "docs",
        "tools_dir": "tools",
        "skills_dir": ".token-saver/skills",
    }


def render_project_worker_skill(
    project_name: str, test_command: str | None = None
) -> str:
    """Return the content of a project-local worker SKILL.md."""
    test_cmd_line = (
        f"Default test command: `{test_command}`"
        if test_command
        else "No default test command configured."
    )
    return f"""---
name: worker
description: Work as the low-cost worker model in a reviewer-controlled Token Saver Loop for {project_name}.
type: prompt
whenToUse: When executing a worker round for {project_name} under reviewer control.
---

# Token Saver Loop Worker Skill - {project_name}

You are the low-cost worker model in a reviewer-controlled workflow for **{project_name}**.
The worker can be any compatible model/tool that can read files, run bounded commands,
and write the required reports.

## Role
- Worker implements, explores, runs commands, and writes logs.
- Reviewer plans, reviews, decides pass/fix/downgrade/stop, and owns final quality.

## Tier Rules
- T3: Free execution. Small patch.
- T2: Bounded execution. Stay inside requested files.
- T1: Instruction execution. Follow steps exactly.
- T0: No implementation. Inspect and report only.

## Required Artifacts
- `.ai/active_task/rounds/round_XXX/worker_log.md`
- `.ai/active_task/rounds/round_XXX/worker_report.json`
- `.ai/active_task/progress.md`

## User Progress Board
- At the end of every round, update `.ai/active_task/progress.md`.
- Treat it as user-facing orientation only, not a source of truth.
- Separate worker-authored status from reviewer-verified status.
- Do not store full thinking or long logs; the reviewer verifies with tests, diff, latest reports, and files.

## Process Rotation
- Prefer a fresh worker conversation/process per round when handoff files are complete.
- Do not rely on prior worker chat memory; follow the reviewer's current handoff and repo files.
- Reuse the same worker conversation only for an immediate same-round retry or when the reviewer explicitly asks for continuity.

## Testing And Git Evidence
- Run required test commands and record exact command/results in round artifacts.
- Do not weaken, delete, skip, or bypass tests to make a round pass.
- You may collect git evidence with `git status --short`, `git diff --stat HEAD`, targeted `git diff`, and `git diff --check`.
- Do not commit, tag, push, reset, checkout, amend, or stage broad file sets unless the reviewer explicitly delegates that exact action.
- Reviewer/user own final acceptance and repository history by default.

{test_cmd_line}
"""


def build_doctor_report(project_root: str | Path = ".") -> dict:
    """Inspect a project for Token Saver Loop state without modifying files."""
    root = Path(project_root).resolve()
    portable_kit = root / "token-saver-kit"
    if (portable_kit / "START_HERE.md").exists():
        mode = "portable"
        base = portable_kit
        active = base / ".ai" / "active_task"
        run_script = base / "tools" / "tsl-new-round.ps1"
    else:
        mode = "missing"
        base = None
        active = portable_kit / ".ai" / "active_task"
        run_script = None

    def rel(path: Path | None) -> str | None:
        if path is None:
            return None
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return path.as_posix()

    checks: list[dict] = []

    def add_check(name: str, ok: bool, details: str) -> None:
        checks.append(
            {
                "name": name,
                "status": "ok" if ok else "missing",
                "details": details,
            }
        )

    add_check(
        "workflow_kit",
        mode != "missing",
        "Found portable kit." if mode == "portable" else "No token-saver-kit/ folder found.",
    )
    add_check(
        "run_script",
        bool(run_script and run_script.exists()),
        rel(run_script) or "Expected tsl-new-round.ps1.",
    )
    add_check(
        "active_task",
        active.exists(),
        rel(active),
    )
    add_check(
        "state",
        (active / "state.md").exists(),
        rel(active / "state.md"),
    )
    add_check(
        "task",
        (active / "task.md").exists(),
        rel(active / "task.md"),
    )
    rounds = active / "rounds"
    add_check(
        "rounds_dir",
        rounds.exists(),
        rel(rounds),
    )

    latest_round = None
    if rounds.exists():
        round_dirs = sorted(
            [p for p in rounds.iterdir() if p.is_dir() and re.match(r"^round_\d+$", p.name)],
            key=lambda p: p.name,
        )
        latest_round = round_dirs[-1] if round_dirs else None

    preview_prompt = rounds / "_validate" / "worker_prompt.md"
    latest_prompt = latest_round / "worker_prompt.md" if latest_round else None
    latest_report = latest_round / "worker_report.json" if latest_round else None

    add_check(
        "latest_round",
        latest_round is not None,
        rel(latest_round) if latest_round else "No round_NNN directory yet.",
    )
    add_check(
        "latest_round_prompt",
        bool(latest_prompt and latest_prompt.exists()),
        rel(latest_prompt) if latest_prompt else "Run tsl-new-round.ps1 to create one.",
    )
    add_check(
        "latest_worker_report",
        bool(latest_report and latest_report.exists()),
        rel(latest_report) if latest_report else "Missing until the worker finishes.",
    )

    has_preview = preview_prompt.exists()
    next_action = "copy_portable_kit"
    if mode != "missing" and not active.exists():
        next_action = "initialize_task"
    elif mode != "missing" and latest_round is None:
        next_action = "create_real_round"
    elif mode != "missing" and latest_prompt is not None and not latest_prompt.exists():
        next_action = "create_real_round"
    elif mode != "missing" and latest_round is not None and not latest_report.exists():
        next_action = "give_prompt_to_worker"
    elif mode != "missing" and latest_report.exists():
        next_action = "review_latest_round"

    return {
        "version": 1,
        "project_root": root.as_posix(),
        "mode": mode,
        "base_path": rel(base),
        "active_task_path": rel(active),
        "latest_round": rel(latest_round),
        "validate_preview_prompt": rel(preview_prompt) if has_preview else None,
        "checks": checks,
        "next_action": next_action,
        "notes": [
            "Use tsl-new-round.ps1 to prepare a worker prompt, then give it to any compatible worker model.",
            "_validate is a preview prompt only; round_NNN is the real worker round.",
        ],
    }


# ---------- Token usage helpers ----------


def parse_worker_usage_counts_from_jsonl(jsonl_text: str) -> list[int]:
    """Extract `_usage` token_count values from worker session JSONL text.

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


def parse_worker_usage_counts_from_jsonl_file(path: str | Path) -> list[int]:
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


def summarize_worker_usage_counts(counts: list[int]) -> dict:
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
    source: str = "worker_context_jsonl",
    notes: str | None = None,
) -> dict:
    """Build a round-level token usage record dict."""
    summary = summarize_worker_usage_counts(counts)
    measurement_mode = "actual_total_only" if counts else "unavailable"
    if not counts and notes is None:
        notes = "No _usage entries found."
    return {
        "version": 1,
        "actor": "worker",
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


def build_reviewer_usage_snapshot(
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    requests: int,
    source: str = "manual_reviewer_profile_snapshot",
    notes: str | None = None,
) -> dict:
    """Build a reviewer usage snapshot dict.

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
        "actor": "reviewer",
        "source": source,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "requests": requests,
        "notes": notes,
    }


def summarize_token_usage_records(records: list[dict]) -> dict:
    """Summarize a list of mixed worker and reviewer token usage records.

    - Worker: sums delta_token_count when actor is "worker" or inferred from
      delta_token_count presence.
    - Reviewer: uses the latest total_tokens, input_tokens, output_tokens,
      and requests from the last reviewer record.
    """
    worker_delta_total = 0
    reviewer_latest_input: int | None = None
    reviewer_latest_output: int | None = None
    reviewer_latest_total: int | None = None
    reviewer_latest_requests: int | None = None

    for rec in records:
        actor = rec.get("actor")
        if actor == "worker" or (actor is None and "delta_token_count" in rec):
            delta = rec.get("delta_token_count")
            if isinstance(delta, int):
                worker_delta_total += delta
        elif actor == "reviewer":
            total = rec.get("total_tokens")
            if isinstance(total, int):
                reviewer_latest_total = total
                reviewer_latest_input = rec.get("input_tokens")
                reviewer_latest_output = rec.get("output_tokens")
                reviewer_latest_requests = rec.get("requests")

    return {
        "worker_delta_tokens_total": worker_delta_total,
        "reviewer_latest_input_tokens": reviewer_latest_input,
        "reviewer_latest_output_tokens": reviewer_latest_output,
        "reviewer_latest_total_tokens": reviewer_latest_total,
        "reviewer_latest_requests": reviewer_latest_requests,
        "records_count": len(records),
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




