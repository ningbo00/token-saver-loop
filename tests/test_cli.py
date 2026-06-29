"""Tests for Token Saver Loop CLI."""

import sys
from pathlib import Path

# Allow importing Token Saver Loop from src/ without installing.
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from token_saver_loop.cli import main


# ---------- Legacy tests ----------


class TestCLILegacy(unittest.TestCase):
    def test_version_flag(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(["--version"])
            self.assertEqual(code, 0)
            self.assertEqual(mock_stdout.getvalue().strip(), "token-saver-loop 1.0.0")

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


    def test_legacy_dry_run_still_works(self) -> None:
        with patch.object(sys, "stdin", io.StringIO("hello world")):
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(["--dry-run", "--format", "json"])
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                messages = json.loads(output)
                self.assertEqual(len(messages), 2)
# ---------- Workflow-kit tests ----------


class TestCLIWorkflowKit(unittest.TestCase):
    def test_show_config(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(["--project-name", "MyApp", "--show-config"])
            self.assertEqual(code, 0)
            output = mock_stdout.getvalue()
            config = json.loads(output)
            self.assertEqual(config["project_name"], "MyApp")
            self.assertEqual(config["workflow_name"], "token-saver-loop")
            self.assertIn("deepseek", config["worker_model_examples"])
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
            self.assertIn("Token Saver Loop Worker Skill", output)
            self.assertIn("DeepSeek", output)
            self.assertIn("Qwen", output)
            self.assertIn("MyApp", output)
            self.assertIn("worker_log.md", output)
            self.assertIn("worker_report.json", output)

    def test_doctor_reports_missing_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                    code = main(["--doctor"])
                    self.assertEqual(code, 0)
                    report = json.loads(mock_stdout.getvalue())
                    self.assertEqual(report["mode"], "missing")
                    self.assertEqual(report["next_action"], "copy_portable_kit")
            finally:
                os.chdir(original_cwd)

    def test_doctor_reports_portable_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            kit = Path(tmpdir) / "token-saver-kit"
            (kit / "tools").mkdir(parents=True)
            (kit / "START_HERE.md").write_text("# start\n", encoding="utf-8")
            (kit / "tools" / "tsl-run.ps1").write_text("param()\n", encoding="utf-8")
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                    code = main(["--doctor"])
                    self.assertEqual(code, 0)
                    report = json.loads(mock_stdout.getvalue())
                    self.assertEqual(report["mode"], "portable")
                    self.assertEqual(report["next_action"], "initialize_task")
            finally:
                os.chdir(original_cwd)

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
    def test_parse_worker_usage_jsonl_prints_record(self) -> None:
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
                        "--parse-worker-usage-jsonl",
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

    def test_parse_worker_usage_jsonl_missing_file(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--parse-worker-usage-jsonl", "/nonexistent/context.jsonl"])
            self.assertEqual(code, 1)
            self.assertIn("not found", mock_stderr.getvalue())

    def test_parse_worker_usage_jsonl_empty_file(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write("")
            tmp_path = f.name
        try:
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(
                    [
                        "--parse-worker-usage-jsonl",
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
    def test_record_reviewer_usage_prints_snapshot(self) -> None:
        with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
            code = main(
                [
                    "--record-reviewer-usage",
                    "--reviewer-input-tokens",
                    "2300000",
                    "--reviewer-output-tokens",
                    "44000",
                    "--reviewer-total-tokens",
                    "2344000",
                    "--reviewer-requests",
                    "71",
                ]
            )
            self.assertEqual(code, 0)
            output = mock_stdout.getvalue()
            snapshot = json.loads(output)
            self.assertEqual(snapshot["actor"], "reviewer")
            self.assertEqual(snapshot["input_tokens"], 2300000)
            self.assertEqual(snapshot["output_tokens"], 44000)
            self.assertEqual(snapshot["total_tokens"], 2344000)
            self.assertEqual(snapshot["requests"], 71)

    def test_record_reviewer_usage_missing_fields(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(["--record-reviewer-usage"])
            self.assertEqual(code, 1)
            err = mock_stderr.getvalue()
            self.assertIn("Missing required fields", err)
            self.assertIn("--reviewer-input-tokens", err)
            self.assertIn("--reviewer-output-tokens", err)
            self.assertIn("--reviewer-total-tokens", err)
            self.assertIn("--reviewer-requests", err)

    def test_record_reviewer_usage_rejects_negative(self) -> None:
        with patch.object(sys, "stderr", new_callable=io.StringIO) as mock_stderr:
            code = main(
                [
                    "--record-reviewer-usage",
                    "--reviewer-input-tokens",
                    "-1",
                    "--reviewer-output-tokens",
                    "0",
                    "--reviewer-total-tokens",
                    "0",
                    "--reviewer-requests",
                    "0",
                ]
            )
            self.assertEqual(code, 1)
            self.assertIn("input_tokens", mock_stderr.getvalue())

    def test_summarize_token_usage_jsonl(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write('{"actor": "worker", "delta_token_count": 100}\n')
            f.write(
                '{"actor": "reviewer", "input_tokens": 1000, "output_tokens": 200, "total_tokens": 1200, "requests": 5}\n'
            )
            f.write('{"actor": "worker", "delta_token_count": 200}\n')
            tmp_path = f.name
        try:
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(["--summarize-token-usage-jsonl", tmp_path])
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                summary = json.loads(output)
                self.assertEqual(summary["worker_delta_tokens_total"], 300)
                self.assertEqual(summary["reviewer_latest_total_tokens"], 1200)
                self.assertEqual(summary["reviewer_latest_input_tokens"], 1000)
                self.assertEqual(summary["reviewer_latest_output_tokens"], 200)
                self.assertEqual(summary["reviewer_latest_requests"], 5)
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
    def test_record_reviewer_usage_with_append_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_path = Path(tmpdir) / "metrics.jsonl"
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(
                    [
                        "--record-reviewer-usage",
                        "--reviewer-input-tokens",
                        "1000",
                        "--reviewer-output-tokens",
                        "200",
                        "--reviewer-total-tokens",
                        "1200",
                        "--reviewer-requests",
                        "5",
                        "--append-metrics",
                        str(metrics_path),
                    ]
                )
                self.assertEqual(code, 0)
                output = mock_stdout.getvalue()
                snapshot = json.loads(output)
                self.assertEqual(snapshot["actor"], "reviewer")
            lines = metrics_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["total_tokens"], 1200)

    def test_parse_worker_usage_jsonl_with_append_metrics(self) -> None:
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
                            "--parse-worker-usage-jsonl",
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
                            "--record-reviewer-usage",
                            "--reviewer-input-tokens",
                            "500",
                            "--reviewer-output-tokens",
                            "100",
                            "--reviewer-total-tokens",
                            "600",
                            "--reviewer-requests",
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
                    "--record-reviewer-usage",
                    "--reviewer-input-tokens",
                    "0",
                    "--reviewer-output-tokens",
                    "0",
                    "--reviewer-total-tokens",
                    "0",
                    "--reviewer-requests",
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
            # Pre-seed with a worker record
            metrics_path.write_text(
                '{"actor": "worker", "delta_token_count": 50}\n',
                encoding="utf-8",
            )
            with patch.object(sys, "stdout", new_callable=io.StringIO) as mock_stdout:
                code = main(
                    [
                        "--record-reviewer-usage",
                        "--reviewer-input-tokens",
                        "1000",
                        "--reviewer-output-tokens",
                        "200",
                        "--reviewer-total-tokens",
                        "1200",
                        "--reviewer-requests",
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
                self.assertEqual(result["summary"]["worker_delta_tokens_total"], 50)
                self.assertEqual(result["summary"]["reviewer_latest_total_tokens"], 1200)
                self.assertEqual(result["summary"]["records_count"], 2)

    def test_summary_after_append_for_worker_record(self) -> None:
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
                            "--parse-worker-usage-jsonl",
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
                    self.assertEqual(result["summary"]["worker_delta_tokens_total"], 200)
                    self.assertEqual(result["summary"]["records_count"], 1)
        finally:
            os.unlink(context_path)


if __name__ == "__main__":
    unittest.main()








