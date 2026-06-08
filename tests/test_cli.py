"""Tests for gpt2whatever CLI."""

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

from gpt2whatever.cli import main


# ---------- Legacy tests ----------


class TestCLILegacy(unittest.TestCase):
    def test_list_formats(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(["--list-formats"])
            self.assertEqual(code, 0)
            output = mock_stdout.getvalue()
            self.assertIn("json", output)
            self.assertIn("yaml", output)
            self.assertIn("markdown-table", output)
            self.assertIn("todo-list", output)

    def test_dry_run(self) -> None:
        with patch.object(sys, "stdin", io.StringIO("hello world")):
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(["--dry-run", "--format", "json"])
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                messages = json.loads(output)
                self.assertEqual(len(messages), 2)
                self.assertEqual(messages[0]["role"], "system")
                self.assertEqual(messages[1]["role"], "user")
                self.assertEqual(messages[1]["content"], "hello world")

    def test_dry_run_with_instruction(self) -> None:
        with patch.object(sys, "stdin", io.StringIO("test input")):
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(["--dry-run", "--instruction", "Be concise"])
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                messages = json.loads(output)
                self.assertIn("Be concise", messages[0]["content"])

    def test_missing_input_file(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--input", "/nonexistent/file.txt"])
            self.assertEqual(code, 1)
            self.assertIn("not found", mock_stderr.getvalue())

    def test_no_dry_run_shows_not_implemented(self) -> None:
        with patch.object(sys, "stdin", io.StringIO("hello")):
            with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
                code = main([])
                self.assertEqual(code, 1)
                self.assertIn("not implemented yet", mock_stderr.getvalue())


# ---------- Workflow-kit tests ----------


class TestCLIWorkflowKit(unittest.TestCase):
    def test_list_install_paths(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(["--list-install-paths"])
            self.assertEqual(code, 0)
            output = mock_stdout.getvalue()
            self.assertIn(".ai/active_task/state.md", output)
            self.assertIn("docs/AGENT_CONTEXT.md", output)
            self.assertIn("tools/ai-kimi-init.ps1", output)
            self.assertIn(".kimi-code/skills/kimi-codex-worker/SKILL.md", output)

    def test_show_config(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(["--project-name", "MyApp", "--show-config"])
            self.assertEqual(code, 0)
            output = mock_stdout.getvalue()
            config = json.loads(output)
            self.assertEqual(config["project_name"], "MyApp")
            self.assertEqual(config["workflow_name"], "kimi-codex")
            self.assertIn("T0", config["tiers"])

    def test_show_config_requires_project_name(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--show-config"])
            self.assertEqual(code, 1)
            self.assertIn("--show-config requires --project-name", mock_stderr.getvalue())

    def test_show_project_skill(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(["--project-name", "MyApp", "--show-project-skill"])
            self.assertEqual(code, 0)
            output = mock_stdout.getvalue()
            self.assertIn("Kimi-Codex Worker Skill", output)
            self.assertIn("MyApp", output)
            self.assertIn("kimi_log.md", output)
            self.assertIn("kimi_report.json", output)

    def test_show_project_skill_with_test_command(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(
                [
                    "--project-name",
                    "MyApp",
                    "--test-command",
                    "pytest",
                    "--show-project-skill",
                ]
            )
            self.assertEqual(code, 0)
            output = mock_stdout.getvalue()
            self.assertIn("pytest", output)

    def test_show_project_skill_requires_project_name(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--show-project-skill"])
            self.assertEqual(code, 1)
            self.assertIn(
                "--show-project-skill requires --project-name",
                mock_stderr.getvalue(),
            )


# ---------- Token usage CLI tests ----------


class TestCLITokenUsage(unittest.TestCase):
    def test_parse_kimi_usage_jsonl_prints_record(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write('{"role": "_usage", "token_count": 1000}\n')
            f.write('{"role": "user", "content": "secret conversation"}\n')
            f.write('{"role": "_usage", "token_count": 2500}\n')
            tmp_path = f.name
        try:
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(
                    [
                        "--parse-kimi-usage-jsonl",
                        tmp_path,
                        "--round-name",
                        "round_005",
                        "--tier",
                        "T2",
                    ]
                )
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                record = json.loads(output)
                self.assertEqual(record["round"], "round_005")
                self.assertEqual(record["tier"], "T2")
                self.assertEqual(record["start_token_count"], 1000)
                self.assertEqual(record["end_token_count"], 2500)
                self.assertEqual(record["delta_token_count"], 1500)
                self.assertEqual(record["peak_token_count"], 2500)
                self.assertEqual(record["usage_entries"], 2)
                self.assertEqual(record["measurement_mode"], "actual_total_only")
                # Ensure conversation content does not leak into output
                self.assertNotIn("secret conversation", output)
        finally:
            os.unlink(tmp_path)

    def test_parse_kimi_usage_jsonl_missing_file(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--parse-kimi-usage-jsonl", "/nonexistent/context.jsonl"])
            self.assertEqual(code, 1)
            self.assertIn("not found", mock_stderr.getvalue())

    def test_parse_kimi_usage_jsonl_empty_file(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write("")
            tmp_path = f.name
        try:
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(
                    [
                        "--parse-kimi-usage-jsonl",
                        tmp_path,
                        "--round-name",
                        "round_005",
                        "--tier",
                        "T2",
                    ]
                )
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                record = json.loads(output)
                self.assertEqual(record["measurement_mode"], "unavailable")
                self.assertIsNone(record["start_token_count"])
                self.assertEqual(record["usage_entries"], 0)
                self.assertEqual(record["notes"], "No _usage entries found.")
        finally:
            os.unlink(tmp_path)


# ---------- Metrics aggregation CLI tests ----------


class TestCLIMetricsAggregation(unittest.TestCase):
    def test_record_codex_usage_prints_snapshot(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(
                [
                    "--record-codex-usage",
                    "--codex-input-tokens",
                    "2300000",
                    "--codex-output-tokens",
                    "44000",
                    "--codex-total-tokens",
                    "2344000",
                    "--codex-requests",
                    "71",
                ]
            )
            self.assertEqual(code, 0)
            output = mock_stdout.getvalue()
            snapshot = json.loads(output)
            self.assertEqual(snapshot["actor"], "codex")
            self.assertEqual(snapshot["input_tokens"], 2300000)
            self.assertEqual(snapshot["output_tokens"], 44000)
            self.assertEqual(snapshot["total_tokens"], 2344000)
            self.assertEqual(snapshot["requests"], 71)

    def test_record_codex_usage_missing_fields(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--record-codex-usage"])
            self.assertEqual(code, 1)
            err = mock_stderr.getvalue()
            self.assertIn("Missing required fields", err)
            self.assertIn("--codex-input-tokens", err)
            self.assertIn("--codex-output-tokens", err)
            self.assertIn("--codex-total-tokens", err)
            self.assertIn("--codex-requests", err)

    def test_record_codex_usage_rejects_negative(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(
                [
                    "--record-codex-usage",
                    "--codex-input-tokens",
                    "-1",
                    "--codex-output-tokens",
                    "0",
                    "--codex-total-tokens",
                    "0",
                    "--codex-requests",
                    "0",
                ]
            )
            self.assertEqual(code, 1)
            self.assertIn("input_tokens", mock_stderr.getvalue())

    def test_summarize_token_usage_jsonl(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write('{"actor": "kimi", "delta_token_count": 100}\n')
            f.write(
                '{"actor": "codex", "input_tokens": 1000, "output_tokens": 200, "total_tokens": 1200, "requests": 5}\n'
            )
            f.write('{"actor": "kimi", "delta_token_count": 200}\n')
            tmp_path = f.name
        try:
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(["--summarize-token-usage-jsonl", tmp_path])
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                summary = json.loads(output)
                self.assertEqual(summary["kimi_delta_tokens_total"], 300)
                self.assertEqual(summary["codex_latest_total_tokens"], 1200)
                self.assertEqual(summary["codex_latest_input_tokens"], 1000)
                self.assertEqual(summary["codex_latest_output_tokens"], 200)
                self.assertEqual(summary["codex_latest_requests"], 5)
                self.assertEqual(summary["records_count"], 3)
        finally:
            os.unlink(tmp_path)

    def test_summarize_token_usage_jsonl_missing_file(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--summarize-token-usage-jsonl", "/nonexistent/metrics.jsonl"])
            self.assertEqual(code, 1)
            self.assertIn("not found", mock_stderr.getvalue())


# ---------- Metrics append CLI tests ----------


class TestCLIMetricsAppend(unittest.TestCase):
    def test_record_codex_usage_with_append_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_path = Path(tmpdir) / "metrics.jsonl"
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(
                    [
                        "--record-codex-usage",
                        "--codex-input-tokens",
                        "1000",
                        "--codex-output-tokens",
                        "200",
                        "--codex-total-tokens",
                        "1200",
                        "--codex-requests",
                        "5",
                        "--append-metrics",
                        str(metrics_path),
                    ]
                )
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                snapshot = json.loads(output)
                self.assertEqual(snapshot["actor"], "codex")
            lines = metrics_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["total_tokens"], 1200)

    def test_parse_kimi_usage_jsonl_with_append_metrics(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write('{"role": "_usage", "token_count": 100}\n')
            f.write('{"role": "_usage", "token_count": 200}\n')
            context_path = f.name
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                metrics_path = Path(tmpdir) / "metrics.jsonl"
                with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                    code = main(
                        [
                            "--parse-kimi-usage-jsonl",
                            context_path,
                            "--round-name",
                            "round_008",
                            "--tier",
                            "T2",
                            "--append-metrics",
                            str(metrics_path),
                        ]
                    )
                    self.assertEqual(code, 0)
                    output = mock_stdout.getvalue()
                    record = json.loads(output)
                    self.assertEqual(record["round"], "round_008")
                lines = metrics_path.read_text(encoding="utf-8").strip().splitlines()
                self.assertEqual(len(lines), 1)
                self.assertEqual(json.loads(lines[0])["delta_token_count"], 100)
        finally:
            os.unlink(context_path)

    def test_append_default_metrics_uses_default_path(self) -> None:
        # Change cwd to a temp dir so we don't touch the real project metrics
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                    code = main(
                        [
                            "--record-codex-usage",
                            "--codex-input-tokens",
                            "500",
                            "--codex-output-tokens",
                            "100",
                            "--codex-total-tokens",
                            "600",
                            "--codex-requests",
                            "3",
                            "--append-default-metrics",
                        ]
                    )
                    self.assertEqual(code, 0)
                    output = mock_stdout.getvalue()
                    snapshot = json.loads(output)
                    self.assertEqual(snapshot["total_tokens"], 600)
                default_path = Path(tmpdir) / ".ai" / "metrics" / "token_usage.jsonl"
                self.assertTrue(default_path.exists())
                lines = default_path.read_text(encoding="utf-8").strip().splitlines()
                self.assertEqual(len(lines), 1)
                self.assertEqual(json.loads(lines[0])["requests"], 3)
            finally:
                os.chdir(original_cwd)

    def test_rejects_both_append_flags(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(
                [
                    "--record-codex-usage",
                    "--codex-input-tokens",
                    "0",
                    "--codex-output-tokens",
                    "0",
                    "--codex-total-tokens",
                    "0",
                    "--codex-requests",
                    "0",
                    "--append-metrics",
                    "/tmp/m.jsonl",
                    "--append-default-metrics",
                ]
            )
            self.assertEqual(code, 1)
            err = mock_stderr.getvalue()
            self.assertIn("mutually exclusive", err)

    def test_rejects_append_without_record_producing_command(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--append-metrics", "/tmp/m.jsonl"])
            self.assertEqual(code, 1)
            err = mock_stderr.getvalue()
            self.assertIn("require a record-producing command", err)

    def test_summary_after_append_returns_appended_plus_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_path = Path(tmpdir) / "metrics.jsonl"
            # Pre-seed with a kimi record
            metrics_path.write_text(
                '{"actor": "kimi", "delta_token_count": 50}\n',
                encoding="utf-8",
            )
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(
                    [
                        "--record-codex-usage",
                        "--codex-input-tokens",
                        "1000",
                        "--codex-output-tokens",
                        "200",
                        "--codex-total-tokens",
                        "1200",
                        "--codex-requests",
                        "5",
                        "--append-metrics",
                        str(metrics_path),
                        "--summary-after-append",
                    ]
                )
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                result = json.loads(output)
                self.assertIn("appended", result)
                self.assertIn("summary", result)
                self.assertEqual(result["appended"]["total_tokens"], 1200)
                self.assertEqual(result["summary"]["kimi_delta_tokens_total"], 50)
                self.assertEqual(result["summary"]["codex_latest_total_tokens"], 1200)
                self.assertEqual(result["summary"]["records_count"], 2)

    def test_summary_after_append_for_kimi_record(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write('{"role": "_usage", "token_count": 100}\n')
            f.write('{"role": "_usage", "token_count": 300}\n')
            context_path = f.name
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                metrics_path = Path(tmpdir) / "metrics.jsonl"
                with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                    code = main(
                        [
                            "--parse-kimi-usage-jsonl",
                            context_path,
                            "--round-name",
                            "round_008",
                            "--tier",
                            "T2",
                            "--append-metrics",
                            str(metrics_path),
                            "--summary-after-append",
                        ]
                    )
                    self.assertEqual(code, 0)
                    output = mock_stdout.getvalue()
                    result = json.loads(output)
                    self.assertEqual(result["appended"]["delta_token_count"], 200)
                    self.assertEqual(result["summary"]["kimi_delta_tokens_total"], 200)
                    self.assertEqual(result["summary"]["records_count"], 1)
        finally:
            os.unlink(context_path)


# ---------- Installer dry-run CLI tests ----------


class TestCLIInstallerDryRun(unittest.TestCase):
    def test_install_dry_run_succeeds_with_project_name(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(["--install", "--dry-run", "--project-name", "MyApp"])
            self.assertEqual(code, 0)
            output = mock_stdout.getvalue()
            plan = json.loads(output)
            self.assertEqual(plan["version"], 1)
            self.assertEqual(plan["project_name"], "MyApp")
            self.assertIn("actions", plan)
            paths = {a["path"] for a in plan["actions"]}
            self.assertIn(".ai/active_task/state.md", paths)
            self.assertIn(".kimi-code/skills/MyApp-kimi-codex-worker/SKILL.md", paths)

    def test_install_dry_run_requires_project_name(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--install", "--dry-run"])
            self.assertEqual(code, 1)
            self.assertIn("requires --project-name", mock_stderr.getvalue())

    def test_install_without_dry_run_rejected(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--install", "--project-name", "MyApp"])
            self.assertEqual(code, 1)
            err = mock_stderr.getvalue()
            self.assertIn("not implemented yet", err)
            self.assertIn("--dry-run", err)

    def test_install_dry_run_flags_existing_files_as_conflicts(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write("existing")
            tmp_path = f.name
        try:
            from unittest.mock import patch as mock_patch
            with mock_patch(
                "gpt2whatever.core.planned_install_paths", return_value=[tmp_path]
            ):
                with patch.object(
                    sys, "stdout", new_callable=io.StringIO
                ) as mock_stdout:
                    code = main(["--install", "--dry-run", "--project-name", "X"])
                    self.assertEqual(code, 0)
                    plan = json.loads(mock_stdout.getvalue())
                    action = next(a for a in plan["actions"] if a["path"] == tmp_path)
                    self.assertEqual(action["action"], "modify")
                    self.assertEqual(action["conflict"], "existing")
        finally:
            os.unlink(tmp_path)

    def test_install_dry_run_does_not_create_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_path = os.path.join(tmpdir, "should_not_be_created")
            from unittest.mock import patch as mock_patch
            with mock_patch(
                "gpt2whatever.core.planned_install_paths",
                return_value=[fake_path],
            ):
                with patch.object(
                    sys, "stdout", new_callable=io.StringIO
                ) as mock_stdout:
                    code = main(["--install", "--dry-run", "--project-name", "X"])
                    self.assertEqual(code, 0)
            self.assertFalse(os.path.exists(fake_path))

    def test_legacy_dry_run_still_works(self) -> None:
        with patch.object(sys, "stdin", io.StringIO("hello world")):
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(["--dry-run", "--format", "json"])
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                messages = json.loads(output)
                self.assertEqual(len(messages), 2)

    def test_install_dry_run_rejects_empty_project_name(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--install", "--dry-run", "--project-name", ""])
            self.assertEqual(code, 1)
            err = mock_stderr.getvalue()
            self.assertIn("non-empty", err)

    def test_install_dry_run_rejects_path_separator(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--install", "--dry-run", "--project-name", "a/b"])
            self.assertEqual(code, 1)
            err = mock_stderr.getvalue()
            self.assertIn("letters", err)

    def test_install_dry_run_rejects_dotdot(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--install", "--dry-run", "--project-name", "a..b"])
            self.assertEqual(code, 1)
            err = mock_stderr.getvalue()
            self.assertIn("'..'", err)

    def test_install_dry_run_accepts_valid_name(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(["--install", "--dry-run", "--project-name", "MyApp_123"])
            self.assertEqual(code, 0)
            plan = json.loads(mock_stdout.getvalue())
            self.assertEqual(plan["project_name"], "MyApp_123")


if __name__ == "__main__":
    unittest.main()
