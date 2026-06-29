param(
  [ValidateSet('T3','T2','T1','T0')]
  [string]$Tier = '',

  [int]$MaxFiles = 8,

  [string]$TestCommands = '',

  [string]$WorkerCommand = '',

  [switch]$NoRun
)

$KitDir = Split-Path -Parent $PSScriptRoot

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

$active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
if (!(Test-Path $active)) {
  throw 'Missing .ai/active_task. Run tools/tsl-init.ps1 first.'
}

$statePath = Join-Path $active 'state.md'
$stateText = if (Test-Path $statePath) { Get-Content $statePath -Raw } else { '' }
if (-not $Tier) {
  if ($stateText -match 'Current tier:\s*(T[0-3])') { $Tier = $Matches[1] } else { $Tier = 'T2' }
}
if (-not $TestCommands) {
  $TestCommands = 'Run the narrowest relevant validation if safe; otherwise explain why validation was skipped.'
}
$workerCommandLabel = if ($WorkerCommand) { $WorkerCommand } else { 'manual/no CLI configured' }

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
$progressRel = (Join-Path $active 'progress.md').Replace('\','/')

$task = Get-Content (Join-Path $active 'task.md') -Raw
$contextPack = Get-Content (Join-Path $active 'context_pack.md') -Raw
$reviewerPlan = Get-Content (Join-Path $active 'reviewer_plan.md') -Raw

$allowedScope = switch ($Tier) {
  'T3' { 'Explore relevant files, but keep the patch small and stop before changing more than the max file limit.' }
  'T2' { 'Stay within files and areas implied by the task/context pack. Do not expand into unrelated modules.' }
  'T1' { 'Only perform direct, mechanical changes required by the task/context. If steps are unclear, stop and report.' }
  'T0' { 'Do not modify code. Inspect, run safe commands, and produce a report only.' }
}

$workflowWriteLimit = if ($Tier -eq 'T0') {
  "T0 file limit: do not modify parent-project source/config/doc files. You may write only the required workflow report files and $progressRel."
} else {
  "Source/config/doc file limit: stop before changing more than $MaxFiles parent-project files. Required workflow report files and $progressRel do not count against this limit."
}

$previewNotice = if ($NoRun) {
  "Preview notice: this prompt was generated with -NoRun and writes to _validate only. Use it to inspect the prompt. For a real worker round, rerun this script without -NoRun so it creates a round_NNN directory."
} else {
  "Real round notice: this prompt belongs to an actual round_NNN directory. Write reports only to the exact paths below."
}

$prompt = @"
You are the worker model working as a bounded executor in the Token Saver Loop.
The worker can be any compatible CLI/model. Current worker command: $workerCommandLabel.

## Round Mode

$previewNotice

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

## Reviewer Plan

$reviewerPlan

## Allowed Scope

$allowedScope

## Forbidden Actions

- Do not commit.
- Do not modify lock files, generated files, binary files, archives, executables, dist/, build/, .git/, node_modules/, or __pycache__/ unless explicitly allowed.
- Do not make unrelated refactors.
- Do not weaken, delete, or bypass tests to pass.
- Do not claim success without command evidence.
- $workflowWriteLimit

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
- $roundRel/worker_log.md

Write a structured JSON report to:
- $roundRel/worker_report.json

Also update the brief user-facing progress board:
- $progressRel

Markdown log format:

# Worker Round Log

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
- Needs reviewer attention:

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
  "next_action": "reviewer_review | worker_fix | ask_user | split_task"
}
"@

$promptPath = Join-Path $roundDir 'worker_prompt.md'
Write-Utf8File $promptPath $prompt
Copy-Item -Path $promptPath -Destination (Join-Path $active 'worker_prompt.md') -Force

if (Test-GitRepo) {
  try { git status --short | Set-Content (Join-Path $roundDir 'git_status_before.txt') -Encoding utf8 } catch { $_ | Out-String | Set-Content (Join-Path $roundDir 'git_status_before.txt') -Encoding utf8 }
}

if ($NoRun) {
  Write-Host "Prepared preview worker prompt only: $promptPath"
  Write-Host "This is a _validate preview and should not be used as a real worker round."
  Write-Host "For a real round, rerun without -NoRun so a round_NNN directory is created."
  exit 0
}

if (-not $WorkerCommand) {
  Write-Warning "No worker command configured. Prompt prepared at $promptPath"
  Write-Host "Run manually, or re-run with -WorkerCommand <command>."
  exit 2
}

$cmd = Get-Command $WorkerCommand -ErrorAction SilentlyContinue
if (-not $cmd) {
  Write-Warning "Worker command '$WorkerCommand' was not found. Prompt prepared at $promptPath"
  Write-Host "After installing/login, run the prompt manually or re-run this script with -WorkerCommand <command>."
  exit 2
}

$workerInput = Get-Content $promptPath -Raw
& $WorkerCommand -p $workerInput --output-format text 1> (Join-Path $roundDir 'worker_stdout.txt') 2> (Join-Path $roundDir 'worker_stderr.txt')
$exitCode = $LASTEXITCODE
Write-Utf8File (Join-Path $roundDir 'worker_exit_code.txt') "$exitCode"

# Capture test command output if an explicit command is configured
$testsPath = Join-Path $roundDir 'tests.txt'
$effectiveTestCmd = $TestCommands
if ($reviewerPlan -match '## Test Commands\s*\r?\n([^#\r\n]+)') {
    $planTestCmd = $Matches[1].Trim()
    if ($planTestCmd -and ($planTestCmd -notmatch 'explain|Inspect|if safe|No explicit test command')) {
        $effectiveTestCmd = $planTestCmd
    }
}
if ($effectiveTestCmd -and ($effectiveTestCmd -notmatch 'explain|Inspect|if safe|No explicit test command')) {
    try {
        # TestCommands comes from the project's own reviewer_plan.md or an explicit script
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

Status: worker_round_completed
Current phase: reviewer_review
Current tier: $Tier
Latest round: $roundRel

Latest artifacts:
- $roundRel/diffstat.txt
- $roundRel/diff.patch
- $roundRel/tests.txt
- $roundRel/worker_report.json
- $roundRel/worker_log.md

Next action:
- Ask the reviewer to review the latest round evidence.
"@
Write-Utf8File $statePath $state

if ($exitCode -ne 0) {
  Write-Warning "Worker exited with code $exitCode. See $roundDir/worker_stderr.txt"
} else {
  Write-Host "Worker round completed: $roundDir"
}



