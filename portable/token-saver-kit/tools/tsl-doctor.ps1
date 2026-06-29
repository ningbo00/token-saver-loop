param(
  [switch]$Json
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
$checks = New-Object System.Collections.Generic.List[object]

function Add-Check($Name, $Path) {
  $ok = Test-Path $Path
  $checks.Add([ordered]@{ name = $Name; status = if ($ok) { 'ok' } else { 'missing' }; path = $Path.Replace('\','/') }) | Out-Null
}

Add-Check 'START_HERE' (Join-Path $KitDir 'START_HERE.md')
Add-Check 'reviewer_skill' (Join-Path $KitDir 'skills/reviewer.md')
Add-Check 'worker_skill' (Join-Path $KitDir 'skills/worker.md')
Add-Check 'active_task' $Active
Add-Check 'rounds' (Join-Path $Active 'rounds')
Add-Check 'new_round_tool' (Join-Path $PSScriptRoot 'tsl-new-round.ps1')
Add-Check 'latest_tool' (Join-Path $PSScriptRoot 'tsl-latest.ps1')
Add-Check 'review_tool' (Join-Path $PSScriptRoot 'tsl-review.ps1')
Add-Check 'redflags_tool' (Join-Path $PSScriptRoot 'tsl-redflags.ps1')
Add-Check 'doctor_tool' (Join-Path $PSScriptRoot 'tsl-doctor.ps1')
Add-Check 'archive_tool' (Join-Path $PSScriptRoot 'tsl-archive.ps1')

$redflagsJson = & (Join-Path $PSScriptRoot 'tsl-redflags.ps1') -Json
$redflags = $redflagsJson | ConvertFrom-Json

$checkArray = @($checks.ToArray())
$result = [ordered]@{
  kit = $KitDir.Replace('\','/')
  checks = $checkArray
  redflags = $redflags.flags
  next_action = if (-not (Test-Path $Active)) { 'ask_reviewer_to_create_task' } else { 'use_tsl-latest_or_reviewer_review' }
}

if ($Json) {
  $result | ConvertTo-Json -Depth 6
} else {
  $checks | ForEach-Object { Write-Host "[$($_.status)] $($_.name): $($_.path)" }
  if ($redflags.count -gt 0) {
    Write-Host 'Red flags:'
    $redflags.flags | ForEach-Object { Write-Host "- [$($_.level)] $($_.message)" }
  }
  Write-Host "Next action: $($result.next_action)"
}
