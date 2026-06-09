param(
  [Parameter(Mandatory=$true)]
  [string]$Task,

  [ValidateSet('T3','T2','T1','T0')]
  [string]$Tier = 'T2',

  [int]$MaxFiles = 8,

  [string]$TestCommands = 'No explicit test command provided. Inspect project scripts and run the narrowest relevant validation if safe.',

  [switch]$ArchiveExisting
)

$KitDir = Split-Path -Parent $PSScriptRoot

$ErrorActionPreference = 'Stop'

function Write-Utf8File($Path, $Content) {
  $dir = Split-Path -Parent $Path
  if ($dir) { New-Item -ItemType Directory -Force $dir | Out-Null }
  $Content | Set-Content -Path $Path -Encoding utf8
}

$active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
if ((Test-Path $active) -and $ArchiveExisting) {
  $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $archiveRoot = Join-Path (Join-Path $KitDir '.ai') 'archive'
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
