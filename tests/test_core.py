"""Tests for gpt2whatever core functions."""

import sys
from pathlib import Path

# Allow importing gpt2whatever from src/ without installing.
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from gpt2whatever.core import (
    append_jsonl_record,
    apply_install_action,
    apply_install_plan,
    build_codex_usage_snapshot,
    build_install_dry_run_plan,
    check_install_safety,
    build_messages,
    build_round_token_usage_record,
    default_metrics_path,
    default_project_config,
    extract_text_from_response,
    load_jsonl_records_from_file,
    parse_jsonl_records,
    parse_kimi_usage_counts_from_jsonl,
    parse_kimi_usage_counts_from_jsonl_file,
    planned_install_paths,
    read_input,
    render_project_worker_skill,
    summarize_kimi_usage_counts,
    summarize_token_usage_records,
    validate_project_name,
)
from gpt2whatever.templates import get_template, list_templates


# ---------- Legacy tests ----------


class TestTemplates(unittest.TestCase):
    def test_list_templates(self) -> None:
        templates = list_templates()
        self.assertEqual(set(templates), {"json", "yaml", "markdown-table", "todo-list"})

    def test_get_template_unknown(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            get_template("unknown-format")
        self.assertIn("Unknown format", str(ctx.exception))


class TestReadInput(unittest.TestCase):
    def test_read_input_from_stdin(self) -> None:
        with patch.object(sys, "stdin", io.StringIO("hello from stdin")):
            result = read_input(None)
            self.assertEqual(result, "hello from stdin")

    def test_read_input_from_file(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write("hello from file")
            tmp_path = f.name
        try:
            result = read_input(tmp_path)
            self.assertEqual(result, "hello from file")
        finally:
            os.unlink(tmp_path)

    def test_read_input_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            read_input("/nonexistent/path/to/file.txt")


class TestBuildMessages(unittest.TestCase):
    def test_build_messages_basic(self) -> None:
        messages = build_messages("Some notes", "json")
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("JSON", messages[0]["content"])
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], "Some notes")

    def test_build_messages_with_extra_instruction(self) -> None:
        messages = build_messages(
            "Some notes", "yaml", extra_instruction="Use compact style"
        )
        self.assertEqual(len(messages), 2)
        self.assertIn("compact style", messages[0]["content"])
        self.assertEqual(messages[1]["content"], "Some notes")


class TestExtractTextFromResponse(unittest.TestCase):
    def test_extract_text_normal(self) -> None:
        response = {"choices": [{"message": {"content": "extracted text"}}]}
        self.assertEqual(extract_text_from_response(response), "extracted text")

    def test_extract_text_missing_choices(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            extract_text_from_response({})
        self.assertIn("Invalid response structure", str(ctx.exception))

    def test_extract_text_missing_message(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            extract_text_from_response({"choices": [{}]})
        self.assertIn("Invalid response structure", str(ctx.exception))

    def test_extract_text_empty_choices(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            extract_text_from_response({"choices": []})
        self.assertIn("Invalid response structure", str(ctx.exception))


# ---------- Workflow-kit tests ----------


class TestDefaultProjectConfig(unittest.TestCase):
    def test_returns_dict(self) -> None:
        config = default_project_config("MyApp")
        self.assertIsInstance(config, dict)

    def test_contains_project_name(self) -> None:
        config = default_project_config("MyApp")
        self.assertEqual(config["project_name"], "MyApp")

    def test_has_expected_keys(self) -> None:
        config = default_project_config("X")
        expected_keys = {
            "project_name",
            "workflow_name",
            "tiers",
            "active_task_dir",
            "rounds_dir",
            "docs_dir",
            "tools_dir",
            "skills_dir",
        }
        self.assertEqual(set(config.keys()), expected_keys)

    def test_tiers_list(self) -> None:
        config = default_project_config("X")
        self.assertEqual(config["tiers"], ["T0", "T1", "T2", "T3"])


class TestRenderProjectWorkerSkill(unittest.TestCase):
    def test_includes_project_name(self) -> None:
        text = render_project_worker_skill("MyApp")
        self.assertIn("MyApp", text)

    def test_includes_kimi_codex_rules(self) -> None:
        text = render_project_worker_skill("MyApp")
        self.assertIn("Kimi-Codex Worker Skill", text)
        self.assertIn("Tier Rules", text)
        self.assertIn("T0", text)
        self.assertIn("T1", text)
        self.assertIn("T2", text)
        self.assertIn("T3", text)
        self.assertIn("kimi_log.md", text)
        self.assertIn("kimi_report.json", text)

    def test_generated_worker_skill_includes_process_rotation_rules(self) -> None:
        text = render_project_worker_skill("MyApp")
        self.assertIn("fresh Kimi conversation/process per round", text)
        self.assertIn("Do not rely on prior Kimi chat memory", text)

    def test_generated_worker_skill_includes_progress_snapshot_rules(self) -> None:
        text = render_project_worker_skill("MyApp")
        self.assertIn(".ai/active_task/progress.md", text)
        self.assertIn("user-facing orientation only", text)
        self.assertIn("Separate Kimi-authored status from Codex-verified status", text)

    def test_generated_worker_skill_includes_testing_and_git_limits(self) -> None:
        text = render_project_worker_skill("MyApp")
        self.assertIn("Run required test commands", text)
        self.assertIn("git diff --check", text)
        self.assertIn("Do not commit, tag, push, reset, checkout, amend", text)

    def test_includes_test_command_when_provided(self) -> None:
        text = render_project_worker_skill("MyApp", test_command="pytest")
        self.assertIn("pytest", text)

    def test_shows_no_test_command_when_none(self) -> None:
        text = render_project_worker_skill("MyApp")
        self.assertIn("No default test command configured", text)


class TestPlannedInstallPaths(unittest.TestCase):
    def test_returns_list(self) -> None:
        paths = planned_install_paths()
        self.assertIsInstance(paths, list)

    def test_includes_ai_paths(self) -> None:
        paths = planned_install_paths()
        self.assertIn(".ai/active_task/state.md", paths)
        self.assertIn(".ai/active_task/task.md", paths)

    def test_includes_docs_paths(self) -> None:
        paths = planned_install_paths()
        self.assertIn("docs/AGENT_CONTEXT.md", paths)
        self.assertIn("docs/REPO_MAP.md", paths)

    def test_includes_tools_paths(self) -> None:
        paths = planned_install_paths()
        self.assertIn("tools/ai-kimi-init.ps1", paths)
        self.assertIn("tools/ai-kimi-run.ps1", paths)
        self.assertIn("tools/ai-kimi-review-pack.ps1", paths)
        self.assertIn("tools/ai-kimi-verdict.ps1", paths)

    def test_includes_skill_path(self) -> None:
        paths = planned_install_paths()
        self.assertIn(".kimi-code/skills/kimi-codex-worker/SKILL.md", paths)


# ---------- Token usage tests ----------


class TestParseKimiUsageCountsFromJsonl(unittest.TestCase):
    def test_extracts_usage_rows(self) -> None:
        jsonl = '{"role": "_usage", "token_count": 100}\n{"role": "_usage", "token_count": 200}\n'
        counts = parse_kimi_usage_counts_from_jsonl(jsonl)
        self.assertEqual(counts, [100, 200])

    def test_ignores_normal_conversation_rows(self) -> None:
        jsonl = (
            '{"role": "user", "content": "hello"}\n'
            '{"role": "_usage", "token_count": 150}\n'
            '{"role": "assistant", "content": "hi"}\n'
        )
        counts = parse_kimi_usage_counts_from_jsonl(jsonl)
        self.assertEqual(counts, [150])

    def test_ignores_invalid_json(self) -> None:
        jsonl = '{"role": "_usage", "token_count": 100}\nnot json\n{"role": "_usage", "token_count": 200}\n'
        counts = parse_kimi_usage_counts_from_jsonl(jsonl)
        self.assertEqual(counts, [100, 200])

    def test_accepts_numeric_string_token_count(self) -> None:
        jsonl = '{"role": "_usage", "token_count": "300"}\n'
        counts = parse_kimi_usage_counts_from_jsonl(jsonl)
        self.assertEqual(counts, [300])

    def test_ignores_non_numeric_token_count(self) -> None:
        jsonl = '{"role": "_usage", "token_count": "abc"}\n{"role": "_usage", "token_count": 400}\n'
        counts = parse_kimi_usage_counts_from_jsonl(jsonl)
        self.assertEqual(counts, [400])

    def test_ignores_non_dict_lines(self) -> None:
        jsonl = '[1, 2, 3]\n{"role": "_usage", "token_count": 500}\n'
        counts = parse_kimi_usage_counts_from_jsonl(jsonl)
        self.assertEqual(counts, [500])

    def test_empty_input(self) -> None:
        counts = parse_kimi_usage_counts_from_jsonl("")
        self.assertEqual(counts, [])


class TestParseKimiUsageCountsFromJsonlFile(unittest.TestCase):
    def test_extracts_usage_rows_from_file(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write('{"role": "_usage", "token_count": 100}\n')
            f.write('{"role": "user", "content": "secret conversation"}\n')
            f.write('{"role": "_usage", "token_count": 200}\n')
            tmp_path = f.name
        try:
            counts = parse_kimi_usage_counts_from_jsonl_file(tmp_path)
            self.assertEqual(counts, [100, 200])
        finally:
            os.unlink(tmp_path)

    def test_ignores_invalid_json_in_file(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write('{"role": "_usage", "token_count": 100}\n')
            f.write('not json\n')
            f.write('{"role": "_usage", "token_count": 200}\n')
            tmp_path = f.name
        try:
            counts = parse_kimi_usage_counts_from_jsonl_file(tmp_path)
            self.assertEqual(counts, [100, 200])
        finally:
            os.unlink(tmp_path)

    def test_empty_file(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write("")
            tmp_path = f.name
        try:
            counts = parse_kimi_usage_counts_from_jsonl_file(tmp_path)
            self.assertEqual(counts, [])
        finally:
            os.unlink(tmp_path)


class TestSummarizeKimiUsageCounts(unittest.TestCase):
    def test_empty_counts(self) -> None:
        summary = summarize_kimi_usage_counts([])
        self.assertIsNone(summary["start_token_count"])
        self.assertIsNone(summary["end_token_count"])
        self.assertIsNone(summary["delta_token_count"])
        self.assertIsNone(summary["peak_token_count"])
        self.assertEqual(summary["usage_entries"], 0)

    def test_non_empty_counts(self) -> None:
        summary = summarize_kimi_usage_counts([100, 200, 150])
        self.assertEqual(summary["start_token_count"], 100)
        self.assertEqual(summary["end_token_count"], 150)
        self.assertEqual(summary["delta_token_count"], 50)
        self.assertEqual(summary["peak_token_count"], 200)
        self.assertEqual(summary["usage_entries"], 3)

    def test_delta_is_zero_when_end_less_than_start(self) -> None:
        summary = summarize_kimi_usage_counts([300, 200])
        self.assertEqual(summary["delta_token_count"], 0)


class TestBuildRoundTokenUsageRecord(unittest.TestCase):
    def test_with_counts(self) -> None:
        record = build_round_token_usage_record(
            round_name="round_005", tier="T2", counts=[100, 200]
        )
        self.assertEqual(record["version"], 1)
        self.assertEqual(record["actor"], "kimi")
        self.assertEqual(record["round"], "round_005")
        self.assertEqual(record["tier"], "T2")
        self.assertEqual(record["source"], "kimi_context_jsonl")
        self.assertEqual(record["measurement_mode"], "actual_total_only")
        self.assertEqual(record["start_token_count"], 100)
        self.assertEqual(record["end_token_count"], 200)
        self.assertEqual(record["delta_token_count"], 100)
        self.assertEqual(record["peak_token_count"], 200)
        self.assertEqual(record["usage_entries"], 2)
        self.assertIsNone(record["prompt_tokens"])
        self.assertIsNone(record["completion_tokens"])
        self.assertIsNone(record["notes"])

    def test_without_counts(self) -> None:
        record = build_round_token_usage_record(
            round_name="round_005", tier="T2", counts=[]
        )
        self.assertEqual(record["measurement_mode"], "unavailable")
        self.assertIsNone(record["start_token_count"])
        self.assertIsNone(record["end_token_count"])
        self.assertEqual(record["usage_entries"], 0)
        self.assertEqual(record["notes"], "No _usage entries found.")

    def test_without_counts_with_explicit_notes(self) -> None:
        record = build_round_token_usage_record(
            round_name="round_005", tier="T2", counts=[], notes="Custom note"
        )
        self.assertEqual(record["notes"], "Custom note")

    def test_with_custom_source_and_notes(self) -> None:
        record = build_round_token_usage_record(
            round_name="round_005",
            tier="T2",
            counts=[100],
            source="manual",
            notes="User provided",
        )
        self.assertEqual(record["source"], "manual")
        self.assertEqual(record["notes"], "User provided")


# ---------- Metrics aggregation tests ----------


class TestParseJsonlRecords(unittest.TestCase):
    def test_parses_valid_dicts(self) -> None:
        jsonl = '{"a": 1}\n{"b": 2}\n'
        records = parse_jsonl_records(jsonl)
        self.assertEqual(records, [{"a": 1}, {"b": 2}])

    def test_ignores_invalid_json(self) -> None:
        jsonl = '{"a": 1}\nnot json\n{"b": 2}\n'
        records = parse_jsonl_records(jsonl)
        self.assertEqual(records, [{"a": 1}, {"b": 2}])

    def test_ignores_non_dict_values(self) -> None:
        jsonl = '[1, 2, 3]\n{"a": 1}\n"string"\n'
        records = parse_jsonl_records(jsonl)
        self.assertEqual(records, [{"a": 1}])

    def test_empty_input(self) -> None:
        records = parse_jsonl_records("")
        self.assertEqual(records, [])


class TestBuildCodexUsageSnapshot(unittest.TestCase):
    def test_valid_snapshot(self) -> None:
        snapshot = build_codex_usage_snapshot(
            input_tokens=1000,
            output_tokens=200,
            total_tokens=1200,
            requests=5,
            notes="Test",
        )
        self.assertEqual(snapshot["version"], 1)
        self.assertEqual(snapshot["actor"], "codex")
        self.assertEqual(snapshot["input_tokens"], 1000)
        self.assertEqual(snapshot["output_tokens"], 200)
        self.assertEqual(snapshot["total_tokens"], 1200)
        self.assertEqual(snapshot["requests"], 5)
        self.assertEqual(snapshot["notes"], "Test")

    def test_rejects_negative_input_tokens(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            build_codex_usage_snapshot(-1, 0, 0, 0)
        self.assertIn("input_tokens", str(ctx.exception))

    def test_rejects_negative_output_tokens(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            build_codex_usage_snapshot(0, -1, 0, 0)
        self.assertIn("output_tokens", str(ctx.exception))

    def test_rejects_negative_total_tokens(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            build_codex_usage_snapshot(0, 0, -1, 0)
        self.assertIn("total_tokens", str(ctx.exception))

    def test_rejects_negative_requests(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            build_codex_usage_snapshot(0, 0, 0, -1)
        self.assertIn("requests", str(ctx.exception))


class TestSummarizeTokenUsageRecords(unittest.TestCase):
    def test_kimi_only(self) -> None:
        records = [
            {"actor": "kimi", "delta_token_count": 100},
            {"actor": "kimi", "delta_token_count": 200},
        ]
        summary = summarize_token_usage_records(records)
        self.assertEqual(summary["kimi_delta_tokens_total"], 300)
        self.assertIsNone(summary["codex_latest_total_tokens"])
        self.assertIsNone(summary["codex_latest_input_tokens"])
        self.assertIsNone(summary["codex_latest_output_tokens"])
        self.assertIsNone(summary["codex_latest_requests"])
        self.assertEqual(summary["records_count"], 2)

    def test_codex_only(self) -> None:
        records = [
            {
                "actor": "codex",
                "input_tokens": 1000,
                "output_tokens": 200,
                "total_tokens": 1200,
                "requests": 5,
            },
        ]
        summary = summarize_token_usage_records(records)
        self.assertEqual(summary["kimi_delta_tokens_total"], 0)
        self.assertEqual(summary["codex_latest_total_tokens"], 1200)
        self.assertEqual(summary["codex_latest_input_tokens"], 1000)
        self.assertEqual(summary["codex_latest_output_tokens"], 200)
        self.assertEqual(summary["codex_latest_requests"], 5)
        self.assertEqual(summary["records_count"], 1)

    def test_mixed_records(self) -> None:
        records = [
            {"actor": "kimi", "delta_token_count": 100},
            {
                "actor": "codex",
                "input_tokens": 1000,
                "output_tokens": 200,
                "total_tokens": 1200,
                "requests": 5,
            },
            {"actor": "kimi", "delta_token_count": 50},
            {
                "actor": "codex",
                "input_tokens": 2000,
                "output_tokens": 400,
                "total_tokens": 2400,
                "requests": 10,
            },
        ]
        summary = summarize_token_usage_records(records)
        self.assertEqual(summary["kimi_delta_tokens_total"], 150)
        self.assertEqual(summary["codex_latest_total_tokens"], 2400)
        self.assertEqual(summary["codex_latest_input_tokens"], 2000)
        self.assertEqual(summary["codex_latest_output_tokens"], 400)
        self.assertEqual(summary["codex_latest_requests"], 10)
        self.assertEqual(summary["records_count"], 4)

    def test_backward_compat_no_actor(self) -> None:
        records = [
            {"delta_token_count": 100},
            {"delta_token_count": 200},
        ]
        summary = summarize_token_usage_records(records)
        self.assertEqual(summary["kimi_delta_tokens_total"], 300)

    def test_ignores_non_int_delta(self) -> None:
        records = [
            {"actor": "kimi", "delta_token_count": 100},
            {"actor": "kimi", "delta_token_count": "bad"},
        ]
        summary = summarize_token_usage_records(records)
        self.assertEqual(summary["kimi_delta_tokens_total"], 100)

    def test_empty_records(self) -> None:
        summary = summarize_token_usage_records([])
        self.assertEqual(summary["kimi_delta_tokens_total"], 0)
        self.assertIsNone(summary["codex_latest_total_tokens"])
        self.assertEqual(summary["records_count"], 0)


# ---------- Metrics file I/O tests ----------


# ---------- Installer dry-run tests ----------


class TestValidateProjectName(unittest.TestCase):
    def test_valid_name(self) -> None:
        self.assertEqual(validate_project_name("MyApp"), "MyApp")

    def test_valid_name_with_hyphen(self) -> None:
        self.assertEqual(validate_project_name("my-app"), "my-app")

    def test_valid_name_with_underscore(self) -> None:
        self.assertEqual(validate_project_name("my_app"), "my_app")

    def test_rejects_empty_string(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_project_name("")
        self.assertIn("non-empty", str(ctx.exception))

    def test_rejects_whitespace_only(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_project_name("   ")
        self.assertIn("non-empty", str(ctx.exception))

    def test_rejects_leading_whitespace(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_project_name(" MyApp")
        self.assertIn("whitespace", str(ctx.exception))

    def test_rejects_trailing_whitespace(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_project_name("MyApp ")
        self.assertIn("whitespace", str(ctx.exception))

    def test_rejects_path_separator_slash(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_project_name("My/App")
        self.assertIn("letters", str(ctx.exception))

    def test_rejects_path_separator_backslash(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_project_name("My\\App")
        self.assertIn("letters", str(ctx.exception))

    def test_rejects_dotdot(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_project_name("My..App")
        self.assertIn("'..'", str(ctx.exception))

    def test_rejects_non_string(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_project_name(123)  # type: ignore[arg-type]
        self.assertIn("string", str(ctx.exception))


class TestBuildInstallDryRunPlan(unittest.TestCase):
    def test_returns_versioned_plan(self) -> None:
        plan = build_install_dry_run_plan("MyApp")
        self.assertEqual(plan["version"], 1)
        self.assertEqual(plan["project_name"], "MyApp")

    def test_includes_planned_paths(self) -> None:
        plan = build_install_dry_run_plan("MyApp")
        paths = {a["path"] for a in plan["actions"]}
        for expected in planned_install_paths():
            self.assertIn(expected, paths)

    def test_includes_project_skill_path(self) -> None:
        plan = build_install_dry_run_plan("MyApp")
        paths = [a["path"] for a in plan["actions"]]
        self.assertIn(".kimi-code/skills/MyApp-kimi-codex-worker/SKILL.md", paths)

    def test_action_structure(self) -> None:
        plan = build_install_dry_run_plan("MyApp")
        for action in plan["actions"]:
            self.assertIn("path", action)
            self.assertIn("action", action)
            self.assertIn("reason", action)
            self.assertIn("conflict", action)
            self.assertIn(action["action"], {"create", "modify"})

    def test_test_command_included(self) -> None:
        plan = build_install_dry_run_plan("MyApp", test_command="pytest")
        self.assertEqual(plan["test_command"], "pytest")

    def test_no_test_command_when_none(self) -> None:
        plan = build_install_dry_run_plan("MyApp")
        self.assertIsNone(plan["test_command"])

    def test_existing_files_flagged_as_conflict(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write("existing")
            tmp_path = f.name
        try:
            # Temporarily patch planned_install_paths to include our temp file
            from unittest.mock import patch
            with patch(
                "gpt2whatever.core.planned_install_paths", return_value=[tmp_path]
            ):
                plan = build_install_dry_run_plan("MyApp")
                action = next(a for a in plan["actions"] if a["path"] == tmp_path)
                self.assertEqual(action["action"], "modify")
                self.assertEqual(action["conflict"], "existing")
        finally:
            os.unlink(tmp_path)

    def test_non_existing_files_have_no_conflict(self) -> None:
        plan = build_install_dry_run_plan("MyApp")
        # Use a path that is very unlikely to exist
        fake_path = ".this_should_not_exist_99999"
        with patch(
            "gpt2whatever.core.planned_install_paths", return_value=[fake_path]
        ):
            plan = build_install_dry_run_plan("MyApp")
            action = next(a for a in plan["actions"] if a["path"] == fake_path)
            self.assertEqual(action["action"], "create")
            self.assertIsNone(action["conflict"])


class TestApplyInstallAction(unittest.TestCase):
    def test_creates_file_under_target_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            action = {
                "path": "docs/README.md",
                "action": "create",
                "content": "# Hello",
            }
            apply_install_action(action, tmpdir)
            p = Path(tmpdir) / "docs" / "README.md"
            self.assertTrue(p.exists())
            self.assertEqual(p.read_text(encoding="utf-8"), "# Hello")

    def test_rejects_outside_root_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            action = {
                "path": "../escape.md",
                "action": "create",
                "content": "x",
            }
            with self.assertRaises(ValueError) as ctx:
                apply_install_action(action, tmpdir)
            self.assertIn("escapes", str(ctx.exception))

    def test_rejects_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "existing.md"
            target.write_text("old", encoding="utf-8")
            action = {
                "path": "existing.md",
                "action": "create",
                "content": "new",
            }
            with self.assertRaises(FileExistsError) as ctx:
                apply_install_action(action, tmpdir)
            self.assertIn("already exists", str(ctx.exception))

    def test_rejects_non_create_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            action = {
                "path": "x.md",
                "action": "modify",
                "content": "x",
            }
            with self.assertRaises(ValueError) as ctx:
                apply_install_action(action, tmpdir)
            self.assertIn("create", str(ctx.exception))

    def test_rejects_missing_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            action = {"action": "create", "content": "x"}
            with self.assertRaises(ValueError) as ctx:
                apply_install_action(action, tmpdir)
            self.assertIn("missing", str(ctx.exception))

    def test_no_writes_to_current_repo(self) -> None:
        # The helper requires an explicit target_root argument.
        # Calling it without target_root raises TypeError, preventing
        # accidental writes to the current working directory.
        with self.assertRaises(TypeError):
            apply_install_action({"path": "x", "action": "create"})

    def test_rejects_non_directory_target_root(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            tmp_path = f.name
        try:
            action = {"path": "x.md", "action": "create", "content": "x"}
            with self.assertRaises(ValueError) as ctx:
                apply_install_action(action, tmp_path)
            self.assertIn("directory", str(ctx.exception))
        finally:
            os.unlink(tmp_path)


class TestApplyInstallPlan(unittest.TestCase):
    def test_creates_multiple_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            actions = [
                {"path": "a.md", "action": "create", "content": "A"},
                {"path": "b/c.md", "action": "create", "content": "C"},
            ]
            apply_install_plan(actions, tmpdir)
            self.assertEqual((Path(tmpdir) / "a.md").read_text(encoding="utf-8"), "A")
            self.assertEqual((Path(tmpdir) / "b" / "c.md").read_text(encoding="utf-8"), "C")

    def test_conflict_aborts_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "existing.md").write_text("old", encoding="utf-8")
            actions = [
                {"path": "new.md", "action": "create", "content": "new"},
                {"path": "existing.md", "action": "create", "content": "overwrite"},
            ]
            with self.assertRaises(FileExistsError):
                apply_install_plan(actions, tmpdir)
            self.assertFalse((Path(tmpdir) / "new.md").exists())

    def test_traversal_aborts_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            actions = [
                {"path": "a.md", "action": "create", "content": "A"},
                {"path": "../escape.md", "action": "create", "content": "E"},
            ]
            with self.assertRaises(ValueError):
                apply_install_plan(actions, tmpdir)
            self.assertFalse((Path(tmpdir) / "a.md").exists())

    def test_missing_content_aborts_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            actions = [
                {"path": "a.md", "action": "create", "content": "A"},
                {"path": "b.md", "action": "create"},
            ]
            with self.assertRaises(ValueError):
                apply_install_plan(actions, tmpdir)
            self.assertFalse((Path(tmpdir) / "a.md").exists())

    def test_non_create_action_aborts_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            actions = [
                {"path": "a.md", "action": "create", "content": "A"},
                {"path": "b.md", "action": "modify", "content": "B"},
            ]
            with self.assertRaises(ValueError):
                apply_install_plan(actions, tmpdir)
            self.assertFalse((Path(tmpdir) / "a.md").exists())

    def test_empty_content_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            actions = [{"path": "empty.md", "action": "create", "content": ""}]
            apply_install_plan(actions, tmpdir)
            self.assertEqual((Path(tmpdir) / "empty.md").read_text(encoding="utf-8"), "")

    def test_duplicate_target_aborts_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            actions = [
                {"path": "a.md", "action": "create", "content": "first"},
                {"path": "a.md", "action": "create", "content": "second"},
            ]
            with self.assertRaises(ValueError) as ctx:
                apply_install_plan(actions, tmpdir)
            self.assertIn("Duplicate target", str(ctx.exception))
            self.assertFalse((Path(tmpdir) / "a.md").exists())

    def test_duplicate_target_via_alias_aborts_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            actions = [
                {"path": "sub/x.md", "action": "create", "content": "first"},
                {"path": "sub/../sub/x.md", "action": "create", "content": "second"},
            ]
            with self.assertRaises(ValueError) as ctx:
                apply_install_plan(actions, tmpdir)
            self.assertIn("Duplicate target", str(ctx.exception))
            self.assertFalse((Path(tmpdir) / "sub" / "x.md").exists())

    def test_rejects_non_list_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(TypeError) as ctx:
                apply_install_plan("not-a-list", tmpdir)  # type: ignore[arg-type]
            self.assertIn("list", str(ctx.exception))

    def test_empty_actions_list_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            apply_install_plan([], tmpdir)
            # No files should be created
            self.assertEqual(list(Path(tmpdir).iterdir()), [])


class TestCheckInstallSafety(unittest.TestCase):
    def test_safe_plan(self) -> None:
        plan = build_install_dry_run_plan("MyApp")
        report = check_install_safety(plan)
        self.assertIsInstance(report["safe"], bool)
        self.assertIsInstance(report["concerns"], list)
        self.assertIsInstance(report["blocked_actions"], list)

    def test_blocks_existing_files(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write("existing")
            tmp_path = f.name
        try:
            plan = {
                "actions": [
                    {
                        "path": tmp_path,
                        "action": "modify",
                        "reason": "test",
                        "conflict": "existing",
                    }
                ]
            }
            report = check_install_safety(plan)
            self.assertFalse(report["safe"])
            self.assertEqual(len(report["concerns"]), 1)
            self.assertIn("already exists", report["concerns"][0])
            self.assertEqual(len(report["blocked_actions"]), 1)
        finally:
            os.unlink(tmp_path)

    def test_blocks_path_traversal(self) -> None:
        plan = {
            "actions": [
                {"path": "../escape", "action": "create", "reason": "test"}
            ]
        }
        report = check_install_safety(plan)
        self.assertFalse(report["safe"])
        self.assertIn("escapes repo root", report["concerns"][0])

    def test_blocks_absolute_path(self) -> None:
        plan = {
            "actions": [
                {"path": "/etc/passwd", "action": "create", "reason": "test"}
            ]
        }
        report = check_install_safety(plan)
        self.assertFalse(report["safe"])
        self.assertIn("escapes repo root", report["concerns"][0])

    def test_blocks_generated_areas(self) -> None:
        for forbidden in (".git/config", "node_modules/x", "__pycache__/x", "dist/x", "build/x"):
            plan = {
                "actions": [
                    {"path": forbidden, "action": "create", "reason": "test"}
                ]
            }
            report = check_install_safety(plan)
            self.assertFalse(report["safe"], f"Expected {forbidden} to be blocked")
            self.assertIn("generated/binary", report["concerns"][0])

    def test_allows_normal_paths(self) -> None:
        plan = {
            "actions": [
                {"path": "docs/README.md", "action": "create", "reason": "test"}
            ]
        }
        report = check_install_safety(plan)
        self.assertTrue(report["safe"])
        self.assertEqual(report["concerns"], [])
        self.assertEqual(report["blocked_actions"], [])


class TestDefaultMetricsPath(unittest.TestCase):
    def test_returns_expected_path(self) -> None:
        self.assertEqual(default_metrics_path(), ".ai/metrics/token_usage.jsonl")


class TestAppendJsonlRecord(unittest.TestCase):
    def test_creates_parent_dir_and_appends_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "metrics.jsonl"
            record = {"actor": "kimi", "delta": 100}
            append_jsonl_record(path, record)
            self.assertTrue(path.exists())
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0]), record)

    def test_appends_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metrics.jsonl"
            path.write_text('{"existing": true}\n', encoding="utf-8")
            append_jsonl_record(path, {"new": True})
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0]), {"existing": True})
            self.assertEqual(json.loads(lines[1]), {"new": True})

    def test_rejects_non_dict(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metrics.jsonl"
            with self.assertRaises(ValueError) as ctx:
                append_jsonl_record(path, "not a dict")
            self.assertIn("dict", str(ctx.exception))


class TestLoadJsonlRecordsFromFile(unittest.TestCase):
    def test_returns_empty_list_for_missing_file(self) -> None:
        result = load_jsonl_records_from_file("/nonexistent/path/file.jsonl")
        self.assertEqual(result, [])

    def test_reads_valid_records(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write('{"a": 1}\n')
            f.write('{"b": 2}\n')
            tmp_path = f.name
        try:
            records = load_jsonl_records_from_file(tmp_path)
            self.assertEqual(records, [{"a": 1}, {"b": 2}])
        finally:
            os.unlink(tmp_path)

    def test_ignores_invalid_lines(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write('{"a": 1}\n')
            f.write('not json\n')
            f.write('[1, 2, 3]\n')
            tmp_path = f.name
        try:
            records = load_jsonl_records_from_file(tmp_path)
            self.assertEqual(records, [{"a": 1}])
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
