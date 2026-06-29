param(
  [string]$Task = '',

  [ValidateSet('T3','T2','T1','T0')]
  [string]$Tier = '',

  [int]$MaxFiles = 8,

  [string]$TestCommands = '',

  [switch]$Preview
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
$Rounds = Join-Path $Active 'rounds'

function Write-Utf8File($Path, $Content) {
  $dir = Split-Path -Parent $Path
  if ($dir) { New-Item -ItemType Directory -Force $dir | Out-Null }
  $Content | Set-Content -Path $Path -Encoding utf8
}

function Next-RoundDir($RoundsRoot) {
  New-Item -ItemType Directory -Force $RoundsRoot | Out-Null
  $max = 0
  Get-ChildItem -Path $RoundsRoot -Directory -Filter 'round_*' | ForEach-Object {
    if ($_.Name -match '^round_(\d+)$') {
      $n = [int]$Matches[1]
      if ($n -gt $max) { $max = $n }
    }
  }
  Join-Path $RoundsRoot ('round_{0:D3}' -f ($max + 1))
}

New-Item -ItemType Directory -Force $Active, $Rounds | Out-Null

$statePath = Join-Path $Active 'state.md'
$taskPath = Join-Path $Active 'task.md'
$contextPath = Join-Path $Active 'context_pack.md'
$planPath = Join-Path $Active 'reviewer_plan.md'
$progressPath = Join-Path $Active 'progress.md'

if (-not $Tier) {
  $stateText = if (Test-Path $statePath) { Get-Content $statePath -Raw } else { '' }
  if ($stateText -match 'Current tier:\s*(T[0-3])') { $Tier = $Matches[1] } else { $Tier = 'T2' }
}

if ($Task) {
  Write-Utf8File $taskPath "# Task`n`n$Task`n"
}
if (-not (Test-Path $taskPath)) {
  throw 'Missing task. Pass -Task or write token-saver-kit/.ai/active_task/task.md first.'
}
if (-not $TestCommands) {
  $TestCommands = 'Run the narrowest relevant validation if safe; otherwise explain why validation was skipped.'
}

$taskText = Get-Content $taskPath -Raw

if (-not (Test-Path $contextPath)) {
  Write-Utf8File $contextPath @"
# Context Pack

## User Goal
$($taskText.Trim())

## Starting Tier
$Tier

## Constraints
- Use the worker model as a bounded executor, not as final reviewer.
- Trust files, diffs, tests, and reports over chat claims.
- Keep changes small. Default max changed files: $MaxFiles.
- Do not commit from the worker model.
"@
}

if (-not (Test-Path $planPath)) {
  Write-Utf8File $planPath @"
# Reviewer Plan

## Delegation Strategy
- Initial worker tier: $Tier
- Max parent-project source/config/doc files changed before stopping: $MaxFiles. Workflow reports plus progress.md are allowed reporting artifacts.
- The worker may execute according to the tier rules, then the reviewer checks objective artifacts.

## Test Commands
$TestCommands

## Review Inputs
The reviewer should inspect the latest round's worker_report.json, worker_log.md, tests.txt, diffstat.txt, and changed files when needed.
"@
}

$roundDir = if ($Preview) { Join-Path $Rounds '_validate' } else { Next-RoundDir $Rounds }
if ($Preview -and (Test-Path $roundDir)) {
  Get-ChildItem -Path $roundDir -File -ErrorAction SilentlyContinue | Remove-Item -Force
}
New-Item -ItemType Directory -Force $roundDir | Out-Null

$roundRel = $roundDir.Replace('\','/')
$progressRel = $progressPath.Replace('\','/')
$workflowLimit = if ($Tier -eq 'T0') {
  "T0: do not modify parent-project source/config/doc files. Write only required workflow report files and $progressRel."
} else {
  "Stop before changing more than $MaxFiles parent-project source/config/doc files. Required workflow report files and $progressRel do not count against this limit."
}

$prompt = @"
You are the worker model working as a bounded executor in the Token Saver Loop.

## Round

Round path: $roundRel
Tier: $Tier

## Task

$taskText

## Context Pack

$(Get-Content $contextPath -Raw)

## Reviewer Plan

$(Get-Content $planPath -Raw)

## Role Boundaries

- Execute only this worker prompt.
- Change parent-project files only inside the stated task scope.
- Do not commit.
- Do not modify lock files, generated files, binary files, archives, executables, dist/, build/, .git/, node_modules/, or __pycache__/ unless explicitly allowed.
- Do not claim success without command evidence.
- $workflowLimit

## Stop Conditions

Stop and report instead of guessing if requirements conflict, required files are missing, validation fails after one focused attempt, or you need to expand beyond scope.

## Required Validation

$TestCommands

## Required Reports

Write:
- $roundRel/worker_log.md
- $roundRel/worker_report.json
- $progressRel

worker_report.json must include status, tier, summary, files_read, files_changed, commands_run, acceptance, risks, deviations, open_questions, and next_action.
"@

Write-Utf8File (Join-Path $roundDir 'tier.md') "# Tier`n`n$Tier`n"
Write-Utf8File (Join-Path $roundDir 'worker_prompt.md') $prompt
Copy-Item -Path (Join-Path $roundDir 'worker_prompt.md') -Destination (Join-Path $Active 'worker_prompt.md') -Force

$phase = if ($Tier -eq 'T0') { 'worker_inspection' } else { 'worker_execution' }
Write-Utf8File $statePath @"
# State

Status: worker_prompt_ready
Current phase: $phase
Current tier: $Tier
Latest round: $roundRel

Latest artifacts:
- $roundRel/worker_prompt.md

Next action:
- Give the worker the latest worker_prompt.md.
"@

if (-not (Test-Path $progressPath)) {
  Write-Utf8File $progressPath "# Progress`n`n- Status: worker prompt ready.`n"
}

Write-Host "Prepared worker prompt: $(Join-Path $roundDir 'worker_prompt.md')"
