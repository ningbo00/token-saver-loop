param(
  [switch]$Json
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Rounds = Join-Path (Join-Path (Join-Path $KitDir '.ai') 'active_task') 'rounds'

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
  $changed = @($report.files_changed | ForEach-Object { $_.path })
}

$result = [ordered]@{
  latest_round = $latest.FullName.Replace('\','/')
  status = if ($report) { $report.status } else { 'missing_report' }
  summary = if ($report) { $report.summary } else { '' }
  changed_files = $changed
  tests_file = if (Test-Path $testsPath) { $testsPath.Replace('\','/') } else { $null }
  diffstat_file = if (Test-Path $diffstatPath) { $diffstatPath.Replace('\','/') } else { $null }
  suggested_reviewer_action = if ($report) { $report.next_action } else { 'inspect_round' }
}

if ($Json) {
  $result | ConvertTo-Json
} else {
  Write-Host "Latest round: $($result.latest_round)"
  Write-Host "Status: $($result.status)"
  if ($result.summary) { Write-Host "Summary: $($result.summary)" }
  Write-Host "Changed files:"
  if ($changed.Count) { $changed | ForEach-Object { Write-Host "- $_" } } else { Write-Host "- none reported" }
  Write-Host "Tests: $($result.tests_file)"
  Write-Host "Diffstat: $($result.diffstat_file)"
  Write-Host "Suggested action: $($result.suggested_reviewer_action)"
}
