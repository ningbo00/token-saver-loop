param(
  [switch]$Json
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Parent = Split-Path -Parent $KitDir
$Active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
$Rounds = Join-Path $Active 'rounds'
$flags = New-Object System.Collections.Generic.List[object]

function Add-Flag($Level, $Area, $Message) {
  $flags.Add([ordered]@{ level = $Level; area = $Area; message = $Message }) | Out-Null
}

foreach ($name in @('.token-saver-loop', '__pycache__', 'build', 'dist', 'node_modules')) {
  $p = Join-Path $Parent $name
  if (Test-Path $p) { Add-Flag 'warn' 'generated_or_temp' "Found $name in parent project root." }
}

$allowedTools = @(
  'tsl-new-round.ps1',
  'tsl-latest.ps1',
  'tsl-review.ps1',
  'tsl-redflags.ps1',
  'tsl-doctor.ps1',
  'tsl-archive.ps1'
)
Get-ChildItem -Path $PSScriptRoot -File -Filter '*.ps1' | ForEach-Object {
  if ($allowedTools -notcontains $_.Name) {
    Add-Flag 'error' 'unknown_tool' "Found unexpected tool script $($_.Name)."
  }
}

if (-not (Test-Path (Join-Path $KitDir 'START_HERE.md'))) { Add-Flag 'error' 'kit' 'Missing START_HERE.md.' }
if (-not (Test-Path (Join-Path $KitDir 'skills/reviewer.md'))) { Add-Flag 'error' 'kit' 'Missing skills/reviewer.md.' }
if (-not (Test-Path (Join-Path $KitDir 'skills/worker.md'))) { Add-Flag 'error' 'kit' 'Missing skills/worker.md.' }

$latest = $null
if (Test-Path $Rounds) {
  $latest = Get-ChildItem -Path $Rounds -Directory -Filter 'round_*' |
    Where-Object { $_.Name -match '^round_\d+$' } |
    Sort-Object Name |
    Select-Object -Last 1
}

if ($latest) {
  foreach ($file in @('worker_prompt.md', 'worker_report.json', 'worker_log.md')) {
    if (-not (Test-Path (Join-Path $latest.FullName $file))) {
      Add-Flag 'warn' 'round' "Latest round is missing $file."
    }
  }
  $reportPath = Join-Path $latest.FullName 'worker_report.json'
  if (Test-Path $reportPath) {
    try {
      $report = Get-Content $reportPath -Raw | ConvertFrom-Json
      if ($report.status -eq 'done' -and -not (Test-Path (Join-Path $latest.FullName 'tests.txt'))) {
        Add-Flag 'warn' 'evidence' 'Worker reports done but tests.txt is missing.'
      }
    } catch {
      Add-Flag 'error' 'evidence' 'worker_report.json is not valid JSON.'
    }
  }
} else {
  Add-Flag 'info' 'round' 'No round_NNN directory found yet.'
}

$flagArray = @($flags.ToArray())
$result = [ordered]@{ flags = $flagArray; count = $flagArray.Count }
if ($Json) {
  $result | ConvertTo-Json -Depth 5
} else {
  if ($flags.Count -eq 0) {
    Write-Host 'No red flags found.'
  } else {
    $flags | ForEach-Object { Write-Host "[$($_.level)] $($_.area): $($_.message)" }
  }
}
