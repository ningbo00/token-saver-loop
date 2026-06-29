param(
  [string]$Round = ''
)

$KitDir = Split-Path -Parent $PSScriptRoot

$ErrorActionPreference = 'Stop'

$active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
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
Write-Host '--- worker_report.json'
if (Test-Path (Join-Path $roundDir 'worker_report.json')) { Get-Content (Join-Path $roundDir 'worker_report.json') } else { Write-Host '(missing)' }
Write-Host '--- tests / stdout summary'
if (Test-Path (Join-Path $roundDir 'tests.txt')) { Get-Content (Join-Path $roundDir 'tests.txt') -TotalCount 120 }
elseif (Test-Path (Join-Path $roundDir 'worker_stdout.txt')) { Get-Content (Join-Path $roundDir 'worker_stdout.txt') -TotalCount 120 }
else { Write-Host '(missing)' }
Write-Host '--- files for reviewer review'
Get-ChildItem $roundDir | Select-Object Name,Length | Format-Table -AutoSize

