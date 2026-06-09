"""Command-line interface for gpt2whatever."""

import argparse
import json
import sys
from pathlib import Path

from gpt2whatever import __version__
from gpt2whatever.core import (
    append_jsonl_record,
    apply_install_plan,
    build_codex_usage_snapshot,
    build_install_dry_run_plan,
    check_install_safety,
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
        "--version",
        action="store_true",
        help="Print package version and exit",
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
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm real install (required when not using --dry-run)",
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


# ---------- Embedded tool script contents for real install ----------

_AI_KIMI_INIT_PS1 = r"""
param(
  [Parameter(Mandatory=$true)]
  [string]$Task,

  [ValidateSet('T3','T2','T1','T0')]
  [string]$Tier = 'T2',

  [int]$MaxFiles = 8,

  [string]$TestCommands = 'No explicit test command provided. Inspect project scripts and run the narrowest relevant validation if safe.',

  [switch]$ArchiveExisting
)

$ErrorActionPreference = 'Stop'

function Write-Utf8File($Path, $Content) {
  $dir = Split-Path -Parent $Path
  if ($dir) { New-Item -ItemType Directory -Force $dir | Out-Null }
  $Content | Set-Content -Path $Path -Encoding utf8
}

$active = Join-Path '.ai' 'active_task'
if ((Test-Path $active) -and $ArchiveExisting) {
  $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $archiveRoot = Join-Path '.ai' 'archive'
  New-Item -ItemType Directory -Force $archiveRoot | Out-Null
  Move-Item -Path $active -Destination (Join-Path $archiveRoot $stamp)
}

New-Item -ItemType Directory -Force $active, (Join-Path $active 'rounds') | Out-Null

Write-Utf8File (Join-Path $active 'task.md') "# Task`n`n$Task`n"

$context = @"
# Context Pack

## User Goal
$Task

## Starting Tier
$Tier

## Constraints
- Use Kimi as a bounded executor, not as final reviewer.
- Trust diff and tests over model explanations.
- Keep changes small. Default max changed files: $MaxFiles.
- Do not commit from Kimi.

## Repo Context
- If present, read AGENTS.md, docs/AGENT_CONTEXT.md, and docs/REPO_MAP.md before broad exploration.
- Avoid generated or binary areas unless directly required.

## Acceptance Criteria
- [ ] Implement the requested behavior.
- [ ] Stay within the agreed scope.
- [ ] Run relevant validation or explain why it cannot be run.
- [ ] Produce Kimi log and JSON report for Codex review.
"@
Write-Utf8File (Join-Path $active 'context_pack.md') $context

$plan = @"
# Codex Plan

## Delegation Strategy
- Initial Kimi tier: $Tier
- Max changed files before stopping: $MaxFiles
- Kimi may execute according to the tier rules, then Codex reviews objective artifacts.

## Test Commands
$TestCommands

## Review Inputs
Codex should review the latest round's:
- diffstat.txt
- diff.patch
- tests.txt
- kimi_report.json
- changed files only when needed
"@
Write-Utf8File (Join-Path $active 'codex_plan.md') $plan

$state = @"
# State

Status: initialized
Current phase: kimi_implementation
Current tier: $Tier
Max files: $MaxFiles

Latest artifacts: none yet

Next action:
- Run tools/ai-kimi-run.ps1
"@
Write-Utf8File (Join-Path $active 'state.md') $state

$capability = Join-Path $active 'capability_notes.md'
if (!(Test-Path $capability)) {
  Write-Utf8File $capability @'
# Kimi Capability Notes

## Works Well
- TBD

## Needs Constraints
- TBD

## Avoid
- TBD

## Downgrade Patterns
- TBD
'@
}

Write-Host "Initialized .ai/active_task"
Write-Host "Task: $Task"
Write-Host "Tier: $Tier"
Write-Host "Next: powershell -ExecutionPolicy Bypass -File tools/ai-kimi-run.ps1"
"""

_AI_KIMI_RUN_PS1 = r"""
param(
  [ValidateSet('T3','T2','T1','T0')]
  [string]$Tier = '',

  [int]$MaxFiles = 8,

  [string]$TestCommands = '',

  [switch]$NoRun,

  [string]$KimiCommand = 'kimi'
)

$ErrorActionPreference = 'Stop'

function Write-Utf8File($Path, $Content) {
  $dir = Split-Path -Parent $Path
  if ($dir) { New-Item -ItemType Directory -Force $dir | Out-Null }
  $Content | Set-Content -Path $Path -Encoding utf8
}

function Get-NextRoundDir($RoundsRoot) {
  New-Item -ItemType Directory -Force $RoundsRoot | Out-Null
  $max = 0
  Get-ChildItem -Path $RoundsRoot -Directory -Filter 'round_*' | ForEach-Object {
    if ($_.Name -match '^round_(\d+)$') {
      $n = [int]$Matches[1]
      if ($n -gt $max) { $max = $n }
    }
  }
  $next = $max + 1
  $name = 'round_{0:D3}' -f $next
  return Join-Path $RoundsRoot $name
}

function Test-GitRepo {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { return $false }
  $oldPreference = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try {
    $output = & git rev-parse --is-inside-work-tree 2>$null
    return (($LASTEXITCODE -eq 0) -and ($output -match 'true'))
  } finally {
    $ErrorActionPreference = $oldPreference
  }
}

$active = Join-Path '.ai' 'active_task'
if (!(Test-Path $active)) {
  throw 'Missing .ai/active_task. Run tools/ai-kimi-init.ps1 first.'
}

$statePath = Join-Path $active 'state.md'
$stateText = if (Test-Path $statePath) { Get-Content $statePath -Raw } else { '' }
if (-not $Tier) {
  if ($stateText -match 'Current tier:\s*(T[0-3])') { $Tier = $Matches[1] } else { $Tier = 'T2' }
}
if (-not $TestCommands) {
  $TestCommands = 'Run the narrowest relevant validation if safe; otherwise explain why validation was skipped.'
}

# When -NoRun is set, use a fixed validation directory so safe checks do not
# pollute the real round sequence or advance the round counter.
$validateDir = Join-Path (Join-Path $active 'rounds') '_validate'
if ($NoRun) {
    $roundDir = $validateDir
    New-Item -ItemType Directory -Force $roundDir | Out-Null
    # Remove prior validation artifacts to avoid confusion, but never touch real round_NNN dirs.
    Get-ChildItem -Path $roundDir -File -ErrorAction SilentlyContinue | Remove-Item -Force
} else {
    $roundDir = Get-NextRoundDir (Join-Path $active 'rounds')
    New-Item -ItemType Directory -Force $roundDir | Out-Null
}

$roundRel = $roundDir.Replace('\','/')
Write-Utf8File (Join-Path $roundDir 'tier.md') "# Tier`n`n$Tier`n"

$task = Get-Content (Join-Path $active 'task.md') -Raw
$contextPack = Get-Content (Join-Path $active 'context_pack.md') -Raw
$codexPlan = Get-Content (Join-Path $active 'codex_plan.md') -Raw

$allowedScope = switch ($Tier) {
  'T3' { 'Explore relevant files, but keep the patch small and stop before changing more than the max file limit.' }
  'T2' { 'Stay within files and areas implied by the task/context pack. Do not expand into unrelated modules.' }
  'T1' { 'Only perform direct, mechanical changes required by the task/context. If steps are unclear, stop and report.' }
  'T0' { 'Do not modify code. Inspect, run safe commands, and produce a report only.' }
}

$prompt = @"
You are KimiCode working as a bounded executor in the Kimi-Codex loop.

## Tier

Tier: $Tier

Tier rules:
- T3: You may explore relevant files and choose a local implementation, but keep scope small.
- T2: Stay inside the listed scope and make local implementation decisions only.
- T1: Follow the implementation steps exactly. Do not improvise.
- T0: Do not modify code. Only inspect, run commands, and report.

## Task

$task

## Context Pack

$contextPack

## Codex Plan

$codexPlan

## Allowed Scope

$allowedScope

## Forbidden Actions

- Do not commit.
- Do not modify lock files, generated files, binary files, archives, executables, dist/, build/, .git/, node_modules/, or __pycache__/ unless explicitly allowed.
- Do not make unrelated refactors.
- Do not weaken, delete, or bypass tests to pass.
- Do not claim success without command evidence.
- If you need to modify more than $MaxFiles files, stop and report why.

## Stop Conditions

Stop and report instead of guessing if:
- requirements conflict with the code
- required files are missing
- the fix requires architecture, security, permission, database, or migration decisions
- tests fail for reasons you cannot explain after one focused attempt
- you need to expand beyond allowed scope

## Required Commands

Before changes:
- git status --short if this is a git repository

After changes:
$TestCommands

## Required Reports

Write a detailed Markdown log to:
- $roundRel/kimi_log.md

Write a structured JSON report to:
- $roundRel/kimi_report.json

Markdown log format:

# Kimi Round Log

## Round
- Tier:
- Task:
- Intended scope:
- Final status: done / partial / blocked / failed

## Files Inspected
| File | Reason |
|---|---|

## Files Changed
| File | Change | Reason | Risk |
|---|---|---|---|

## Commands Run
| Command | Result | Evidence |
|---|---|---|

## Acceptance Checklist
| Criterion | Status | Evidence |
|---|---|---|

## Deviations
| Planned | Actual | Reason |
|---|---|---|

## Uncertainty
| Question | What I Did |
|---|---|

## Self Review
- Potential bug:
- Missing test:
- Risk area:
- Needs Codex attention:

JSON report shape:

{
  "status": "done | partial | blocked | failed",
  "tier": "$Tier",
  "summary": "",
  "files_read": [{"path": "", "reason": ""}],
  "files_changed": [{"path": "", "change_type": "add | modify | delete | rename", "summary": "", "risk": "low | medium | high"}],
  "commands_run": [{"command": "", "result": "passed | failed | skipped", "notes": ""}],
  "acceptance": [{"item": "", "status": "passed | failed | unknown", "evidence": ""}],
  "risks": [{"level": "low | medium | high", "area": "", "description": "", "recommended_review": ""}],
  "deviations": [],
  "open_questions": [],
  "next_action": "codex_review | kimi_fix | ask_user | split_task"
}
"@

$promptPath = Join-Path $roundDir 'kimi_prompt.md'
Write-Utf8File $promptPath $prompt
Copy-Item -Path $promptPath -Destination (Join-Path $active 'kimi_prompt.md') -Force

if (Test-GitRepo) {
  try { git status --short | Set-Content (Join-Path $roundDir 'git_status_before.txt') -Encoding utf8 } catch { $_ | Out-String | Set-Content (Join-Path $roundDir 'git_status_before.txt') -Encoding utf8 }
}

if ($NoRun) {
  Write-Host "Prepared Kimi prompt only: $promptPath"
  exit 0
}

$cmd = Get-Command $KimiCommand -ErrorAction SilentlyContinue
if (-not $cmd) {
  Write-Warning "Kimi command '$KimiCommand' was not found. Prompt prepared at $promptPath"
  Write-Host "After installing/login, run the prompt manually or re-run this script."
  exit 2
}

$kimiInput = Get-Content $promptPath -Raw
& $KimiCommand -p $kimiInput --output-format text 1> (Join-Path $roundDir 'kimi_stdout.txt') 2> (Join-Path $roundDir 'kimi_stderr.txt')
$exitCode = $LASTEXITCODE
Write-Utf8File (Join-Path $roundDir 'kimi_exit_code.txt') "$exitCode"

# Capture test command output if an explicit command is configured
$testsPath = Join-Path $roundDir 'tests.txt'
$effectiveTestCmd = $TestCommands
if ($codexPlan -match '## Test Commands\s*\r?\n([^#\r\n]+)') {
    $planTestCmd = $Matches[1].Trim()
    if ($planTestCmd -and ($planTestCmd -notmatch 'explain|Inspect|if safe|No explicit test command')) {
        $effectiveTestCmd = $planTestCmd
    }
}
if ($effectiveTestCmd -and ($effectiveTestCmd -notmatch 'explain|Inspect|if safe|No explicit test command')) {
    try {
        # TestCommands comes from the project's own codex_plan.md or an explicit script
# parameter; it is trusted workflow input controlled by the user/team.
$testOutput = Invoke-Expression $effectiveTestCmd 2>&1
        $testOutput | Out-String | Set-Content $testsPath -Encoding utf8
    } catch {
        "Test command failed: $_" | Set-Content $testsPath -Encoding utf8
    }
} else {
    "No explicit test command was configured for this round." | Set-Content $testsPath -Encoding utf8
}

if (Test-GitRepo) {
  try { git status --short | Set-Content (Join-Path $roundDir 'git_status_after.txt') -Encoding utf8 } catch { $_ | Out-String | Set-Content (Join-Path $roundDir 'git_status_after.txt') -Encoding utf8 }
  try { git diff --stat | Set-Content (Join-Path $roundDir 'diffstat.txt') -Encoding utf8 } catch { $_ | Out-String | Set-Content (Join-Path $roundDir 'diffstat.txt') -Encoding utf8 }
  try { git diff | Set-Content (Join-Path $roundDir 'diff.patch') -Encoding utf8 } catch { $_ | Out-String | Set-Content (Join-Path $roundDir 'diff.patch') -Encoding utf8 }
}

$state = @"
# State

Status: kimi_round_completed
Current phase: codex_review
Current tier: $Tier
Latest round: $roundRel

Latest artifacts:
- $roundRel/diffstat.txt
- $roundRel/diff.patch
- $roundRel/tests.txt
- $roundRel/kimi_report.json
- $roundRel/kimi_log.md

Next action:
- Ask Codex to review the latest round using kimi-codex-loop.
"@
Write-Utf8File $statePath $state

if ($exitCode -ne 0) {
  Write-Warning "Kimi exited with code $exitCode. See $roundDir/kimi_stderr.txt"
} else {
  Write-Host "Kimi round completed: $roundDir"
}
"""

_AI_KIMI_REVIEW_PACK_PS1 = r"""
param(
  [string]$Round = ''
)

$ErrorActionPreference = 'Stop'

$active = Join-Path '.ai' 'active_task'
$rounds = Join-Path $active 'rounds'
if (!(Test-Path $rounds)) { throw 'Missing .ai/active_task/rounds.' }

if ($Round) {
  $roundDir = Join-Path $rounds $Round
} else {
  $roundDir = Get-ChildItem -Path $rounds -Directory -Filter 'round_*' | Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (!(Test-Path $roundDir)) { throw "Round not found: $roundDir" }

Write-Host "Round: $roundDir"
Write-Host '--- diffstat'
if (Test-Path (Join-Path $roundDir 'diffstat.txt')) { Get-Content (Join-Path $roundDir 'diffstat.txt') } else { Write-Host '(missing)' }
Write-Host '--- kimi_report.json'
if (Test-Path (Join-Path $roundDir 'kimi_report.json')) { Get-Content (Join-Path $roundDir 'kimi_report.json') } else { Write-Host '(missing)' }
Write-Host '--- tests / stdout summary'
if (Test-Path (Join-Path $roundDir 'tests.txt')) { Get-Content (Join-Path $roundDir 'tests.txt') -TotalCount 120 }
elseif (Test-Path (Join-Path $roundDir 'kimi_stdout.txt')) { Get-Content (Join-Path $roundDir 'kimi_stdout.txt') -TotalCount 120 }
else { Write-Host '(missing)' }
Write-Host '--- files for Codex review'
Get-ChildItem $roundDir | Select-Object Name,Length | Format-Table -AutoSize
"""

_AI_KIMI_VERDICT_PS1 = r"""
param(
  [Parameter(Mandatory=$true)]
  [ValidateSet('pass','same-tier-fix','downgrade','stop')]
  [string]$Verdict,

  [ValidateSet('T3','T2','T1','T0')]
  [string]$CurrentTier = 'T2',

  [ValidateSet('T3','T2','T1','T0')]
  [string]$NextTier = 'T2',

  [string[]]$Reasons = @(),

  [string]$ReviewMarkdown = ''
)

$ErrorActionPreference = 'Stop'

function Write-Utf8File($Path, $Content) {
  $dir = Split-Path -Parent $Path
  if ($dir) { New-Item -ItemType Directory -Force $dir | Out-Null }
  $Content | Set-Content -Path $Path -Encoding utf8
}

$active = Join-Path '.ai' 'active_task'
$rounds = Join-Path $active 'rounds'
$roundDir = Get-ChildItem -Path $rounds -Directory -Filter 'round_*' | Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty FullName
if (!$roundDir) { throw 'No round found.' }

if (-not $ReviewMarkdown) {
  $ReviewMarkdown = @"
# Codex Review

## Verdict
$Verdict

## Findings
- TBD

## Report Verification
- report matches diff: TBD
- test claims verified: TBD
- scope followed: TBD

## Next Tier
$NextTier

## Next Prompt
TBD
"@
}
Write-Utf8File (Join-Path $roundDir 'codex_review.md') $ReviewMarkdown

$obj = [ordered]@{
  verdict = $Verdict
  current_tier = $CurrentTier
  next_tier = $NextTier
  reasons = $Reasons
  findings = @()
  kimi_reliability = [ordered]@{
    followed_scope = $null
    tests_verified = $null
    report_matches_diff = $null
    needs_downgrade = ($Verdict -eq 'downgrade' -or $Verdict -eq 'stop')
  }
}
$obj | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $roundDir 'verdict.json') -Encoding utf8

$nextAction = switch ($Verdict) {
  'pass' { 'Commit or archive this task.' }
  'same-tier-fix' { 'Prepare another Kimi round at the same tier.' }
  'downgrade' { 'Prepare another Kimi round with lower freedom.' }
  'stop' { 'Stop Kimi and let Codex or user decide.' }
}
$phase = if ($Verdict -eq 'pass') { 'done' } elseif ($Verdict -eq 'stop') { 'stopped' } else { 'kimi_implementation' }
$state = @"
# State

Status: $Verdict
Current phase: $phase
Current tier: $NextTier
Latest round: $($roundDir.Replace('\','/'))

Next action:
- $nextAction
"@
Write-Utf8File (Join-Path $active 'state.md') $state

Write-Host "Wrote review and verdict to $roundDir"
"""


def _build_install_actions_with_content(plan: dict) -> list[dict]:
    """Return actions with content ready for ``apply_install_plan``."""
    project_name = plan["project_name"]
    test_command = plan["test_command"]
    actions = []
    for action in plan["actions"]:
        path = action["path"]
        content = _render_install_content(path, project_name, test_command)
        actions.append(
            {
                "path": path,
                "action": "create",
                "content": content,
            }
        )
    return actions


def _render_install_content(path: str, project_name: str, test_command: str | None) -> str:
    """Render the initial content for a planned install path."""
    if path.endswith("/SKILL.md") and "kimi-codex-worker" in path:
        return render_project_worker_skill(project_name, test_command)
    if path == ".ai/active_task/state.md":
        return f"# State\n\nStatus: ready\nProject: {project_name}\n"
    if path == ".ai/active_task/task.md":
        return f"# Task\n\nActive task for {project_name}.\n"
    if path == "docs/AGENT_CONTEXT.md":
        return f"# AGENT_CONTEXT\n\nProject: {project_name}\n"
    if path == "docs/REPO_MAP.md":
        return "# REPO_MAP\n\nCurrent structure:\n"
    if path == "tools/ai-kimi-init.ps1":
        return _AI_KIMI_INIT_PS1
    if path == "tools/ai-kimi-run.ps1":
        return _AI_KIMI_RUN_PS1
    if path == "tools/ai-kimi-review-pack.ps1":
        return _AI_KIMI_REVIEW_PACK_PS1
    if path == "tools/ai-kimi-verdict.ps1":
        return _AI_KIMI_VERDICT_PS1
    return ""


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

    if parsed.version:
        print(f"gpt2whatever {__version__}")
        return 0

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
        if parsed.project_name is None:
            print(
                "Error: --install requires --project-name.",
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
        if parsed.dry_run:
            safety = check_install_safety(plan)
            output = {
                "version": plan["version"],
                "project_name": plan["project_name"],
                "test_command": plan["test_command"],
                "safety_check": safety,
                "actions": plan["actions"],
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
            return 0
        if not parsed.yes:
            print(
                "Error: Real install requires --yes or --dry-run.",
                file=sys.stderr,
            )
            return 1
        safety = check_install_safety(plan)
        if not safety["safe"]:
            print(
                f"Error: Install blocked by safety check: {safety['concerns']}",
                file=sys.stderr,
            )
            return 1
        actions_with_content = _build_install_actions_with_content(plan)
        try:
            apply_install_plan(actions_with_content, Path.cwd())
        except (ValueError, FileExistsError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        output = {
            "version": plan["version"],
            "project_name": plan["project_name"],
            "test_command": plan["test_command"],
            "installed": True,
            "actions": plan["actions"],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
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
