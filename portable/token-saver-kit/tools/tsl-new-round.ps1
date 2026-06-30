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
$visibleTaskPath = Join-Path $KitDir 'WORKER_NEXT_TASK.md'
$latestPromptPath = Join-Path $KitDir 'LATEST_WORKER_PROMPT.md'
$contextPath = Join-Path $Active 'context_pack.md'
$planPath = Join-Path $Active 'reviewer_plan.md'
$progressPath = Join-Path $Active 'progress.md'
$workerCopyPrompt = 'Read token-saver-kit/LATEST_WORKER_PROMPT.md and execute it.'

if (-not $Tier) {
  $stateText = if (Test-Path $statePath) { Get-Content $statePath -Raw } else { '' }
  if ($stateText -match 'Current tier:\s*(T[0-3])') { $Tier = $Matches[1] } else { $Tier = 'T2' }
}

if ($Task) {
  Write-Utf8File $taskPath "# Task`n`n$Task`n"
  Write-Utf8File $visibleTaskPath @"
# Worker: Do This Task Now

## Current task

$Task

## Source of truth

Use `token-saver-kit/LATEST_WORKER_PROMPT.md` as the stable worker prompt path.
"@
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
- Commit/tag/push only when explicitly requested in the current prompt; report hashes and validation if used.
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
$roundStatusPath = Join-Path $roundDir 'round_status.json'

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
- At the start of execution, write `${roundRel}/round_status.json` with status `in_progress`; at the very end, rewrite it with status `done`.
- Write final reports to temporary files first when possible, then rename/copy them into place so the reviewer does not read half-written JSON.
- Change parent-project files only inside the stated task scope.
- Run git commit/tag/push only when this prompt or the user explicitly asks for that exact action; report commit hashes if used.
- Do not run destructive git operations such as reset --hard, clean -fdx, forced push, or checkout/restore that discards user work.
- Do not modify lock files, generated files, binary files, archives, executables, dist/, build/, .git/, node_modules/, or __pycache__/ unless explicitly allowed.
- Do not claim success without command evidence.
- $workflowLimit

## Stop Conditions

Stop and report instead of guessing if requirements conflict, validation fails after one focused attempt, or you need to expand beyond scope.

Missing-file rule: if a target implementation file is absent and the task allows creating it, continue and record that fact. If required context/config/input files are absent, stop. If optional docs are absent, record a deviation but do not stop by default.

Git evidence rule: run `git rev-parse --is-inside-work-tree` before git status/diff. If it fails, do not keep retrying git; record changed files, file sizes, and concise manual diff notes instead.

## Required Validation

$TestCommands

If a Python validation command would create `__pycache__/`, prefer `python -B` or set `PYTHONDONTWRITEBYTECODE=1` when that still validates the task.

## Required Reports

Write:
- $roundRel/round_status.json
- $roundRel/worker_log.md
- $roundRel/worker_report.json
- $progressRel

worker_report.json must include status, tier, summary, files_read, files_changed, commands_run, acceptance, risks, deviations, open_questions, and next_action.

Keep `acceptance` compact and evidence-shaped. For each important acceptance item, prefer:
`{"implemented": true|false, "validated": true|false, "evidence": "command|test|static|manual|not_run", "note": "short reason when useful"}`

Set report status to `done` only after reports and validation evidence are complete. Use `blocked` or `failed` when stopping early.
"@

@{
  status = 'prompt_ready'
  round = $roundRel
  updated_by = 'tsl-new-round.ps1'
} | ConvertTo-Json -Depth 3 | Set-Content -Path $roundStatusPath -Encoding utf8
Write-Utf8File (Join-Path $roundDir 'tier.md') "# Tier`n`n$Tier`n"
Write-Utf8File (Join-Path $roundDir 'worker_prompt.md') $prompt
Copy-Item -Path (Join-Path $roundDir 'worker_prompt.md') -Destination (Join-Path $Active 'worker_prompt.md') -Force
Copy-Item -Path (Join-Path $roundDir 'worker_prompt.md') -Destination $latestPromptPath -Force

$phase = if ($Tier -eq 'T0') { 'worker_inspection' } else { 'worker_execution' }
Write-Utf8File $statePath @"
# State

Status: worker_prompt_ready
Current phase: $phase
Current tier: $Tier
Source/config/doc file limit: $MaxFiles
Latest round: $roundRel

Latest artifacts:
- $roundRel/worker_prompt.md
- token-saver-kit/LATEST_WORKER_PROMPT.md

Next action:
- Copy this to the worker:
  $workerCopyPrompt
"@

if (-not (Test-Path $progressPath)) {
  Write-Utf8File $progressPath "# Progress`n`n- Status: worker prompt ready.`n- Next worker prompt: $workerCopyPrompt`n"
} else {
  Add-Content -Path $progressPath -Encoding utf8 -Value "`n- Status: worker prompt ready.`n- Next worker prompt: $workerCopyPrompt"
}

Write-Host "Prepared worker prompt: $(Join-Path $roundDir 'worker_prompt.md')"
Write-Host ''
Write-Host 'Next worker prompt:'
Write-Host $workerCopyPrompt
