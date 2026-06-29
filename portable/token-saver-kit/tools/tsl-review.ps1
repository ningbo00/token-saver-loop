param(
  [switch]$Json
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Rounds = Join-Path (Join-Path (Join-Path $KitDir '.ai') 'active_task') 'rounds'

function Get-ChangedPath($Item) {
  if ($null -eq $Item) { return '' }
  if ($Item -is [string]) { return $Item }
  $pathProperty = $Item.PSObject.Properties['path']
  if ($pathProperty) { return [string]$pathProperty.Value }
  return [string]$Item
}

function Get-CommandResult($Item) {
  if ($null -eq $Item) { return '' }
  $resultProperty = $Item.PSObject.Properties['result']
  if ($resultProperty) { return [string]$resultProperty.Value }
  return ''
}

$latest = $null
if (Test-Path $Rounds) {
  $latest = Get-ChildItem -Path $Rounds -Directory -Filter 'round_*' |
    Where-Object { $_.Name -match '^round_\d+$' } |
    Sort-Object Name |
    Select-Object -Last 1
}
if (-not $latest) { throw 'No round_NNN directory found.' }

$reportPath = Join-Path $latest.FullName 'worker_report.json'
$testsPath = Join-Path $latest.FullName 'tests.txt'
$diffstatPath = Join-Path $latest.FullName 'diffstat.txt'

$report = $null
if (Test-Path $reportPath) {
  try { $report = Get-Content $reportPath -Raw | ConvertFrom-Json } catch { $report = $null }
}

$changed = @()
if ($report -and $report.files_changed) {
  $changed = @($report.files_changed | ForEach-Object { Get-ChangedPath $_ } | Where-Object { $_ })
}

$commands = if ($report -and $report.commands_run) { @($report.commands_run) } else { @() }
$passedCommands = @($commands | Where-Object { (Get-CommandResult $_) -eq 'passed' })
$failedCommands = @($commands | Where-Object { (Get-CommandResult $_) -eq 'failed' })
$redflagsJson = & (Join-Path $PSScriptRoot 'tsl-redflags.ps1') -Json
$redflags = $redflagsJson | ConvertFrom-Json
$errorFlags = @($redflags.flags | Where-Object { $_.level -eq 'error' })
$warnFlags = @($redflags.flags | Where-Object { $_.level -eq 'warn' })
$verdictHint = if (-not $report) {
  'inspect_round'
} elseif ($errorFlags.Count -gt 0) {
  'fix_or_stop'
} elseif ($warnFlags.Count -gt 0) {
  'needs_review'
} elseif ($report.status -eq 'done') {
  'likely_pass_after_diff_check'
} else {
  'needs_review'
}

$result = [ordered]@{
  latest_round = $latest.FullName.Replace('\','/')
  status = if ($report) { $report.status } else { 'missing_report' }
  verdict_hint = $verdictHint
  summary = if ($report) { $report.summary } else { '' }
  changed_files = $changed
  changed_file_count = $changed.Count
  commands_total = $commands.Count
  commands_passed = $passedCommands.Count
  commands_failed = $failedCommands.Count
  redflags_total = $redflags.count
  redflags_errors = $errorFlags.Count
  redflags_warnings = $warnFlags.Count
  tests_file = if (Test-Path $testsPath) { $testsPath.Replace('\','/') } else { $null }
  diffstat_file = if (Test-Path $diffstatPath) { $diffstatPath.Replace('\','/') } else { $null }
  suggested_reviewer_action = if ($report) { $report.next_action } else { 'inspect_round' }
  next_prompt = "Review the latest $($latest.FullName.Replace('\','/')) evidence."
}

if ($Json) {
  $result | ConvertTo-Json -Depth 5
} else {
  Write-Host "Latest round: $($result.latest_round)"
  Write-Host "Status: $($result.status)"
  Write-Host "Verdict hint: $($result.verdict_hint)"
  if ($result.summary) { Write-Host "Summary: $($result.summary)" }
  Write-Host "Changed files: $($result.changed_file_count)"
  if ($changed.Count) { $changed | ForEach-Object { Write-Host "- $_" } } else { Write-Host "- none reported" }
  Write-Host "Commands: $($result.commands_passed) passed, $($result.commands_failed) failed, $($result.commands_total) total"
  Write-Host "Red flags: $($result.redflags_errors) errors, $($result.redflags_warnings) warnings"
  if ($redflags.count -gt 0) {
    $redflags.flags | ForEach-Object { Write-Host "- [$($_.level)] $($_.area): $($_.message)" }
  }
  Write-Host "Tests file: $($result.tests_file)"
  Write-Host "Diffstat: $($result.diffstat_file)"
  Write-Host "Suggested action: $($result.suggested_reviewer_action)"
  Write-Host "Next prompt: $($result.next_prompt)"
}
