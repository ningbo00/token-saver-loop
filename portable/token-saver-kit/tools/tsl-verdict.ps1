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

$KitDir = Split-Path -Parent $PSScriptRoot

$ErrorActionPreference = 'Stop'

function Write-Utf8File($Path, $Content) {
  $dir = Split-Path -Parent $Path
  if ($dir) { New-Item -ItemType Directory -Force $dir | Out-Null }
  $Content | Set-Content -Path $Path -Encoding utf8
}

$active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
$rounds = Join-Path $active 'rounds'
$roundDir = Get-ChildItem -Path $rounds -Directory -Filter 'round_*' | Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty FullName
if (!$roundDir) { throw 'No round found.' }

if (-not $ReviewMarkdown) {
  $ReviewMarkdown = @"
# Reviewer Review

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
Write-Utf8File (Join-Path $roundDir 'reviewer_review.md') $ReviewMarkdown

$obj = [ordered]@{
  verdict = $Verdict
  current_tier = $CurrentTier
  next_tier = $NextTier
  reasons = $Reasons
  findings = @()
  worker_reliability = [ordered]@{
    followed_scope = $null
    tests_verified = $null
    report_matches_diff = $null
    needs_downgrade = ($Verdict -eq 'downgrade' -or $Verdict -eq 'stop')
  }
}
$obj | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $roundDir 'verdict.json') -Encoding utf8

$nextAction = switch ($Verdict) {
  'pass' { 'Commit or archive this task.' }
  'same-tier-fix' { 'Prepare another worker round at the same tier.' }
  'downgrade' { 'Prepare another worker round with lower freedom.' }
  'stop' { 'Stop the worker and let the reviewer or user decide.' }
}
$phase = if ($Verdict -eq 'pass') { 'done' } elseif ($Verdict -eq 'stop') { 'stopped' } else { 'worker_execution' }
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

