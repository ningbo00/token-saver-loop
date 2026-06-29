param(
  [switch]$Json
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
$Rounds = Join-Path $Active 'rounds'

function Rel($Path) {
  if (-not $Path) { return $null }
  return $Path.Replace('\', '/')
}

$latest = $null
if (Test-Path $Rounds) {
  $latest = Get-ChildItem -Path $Rounds -Directory -Filter 'round_*' |
    Where-Object { $_.Name -match '^round_\d+$' } |
    Sort-Object Name |
    Select-Object -Last 1
}

$result = [ordered]@{
  kit = Rel $KitDir
  active_task = Rel $Active
  latest_round = if ($latest) { Rel $latest.FullName } else { $null }
  latest_worker_prompt = Rel (Join-Path $KitDir 'LATEST_WORKER_PROMPT.md')
  worker_prompt = if ($latest) { Rel (Join-Path $latest.FullName 'worker_prompt.md') } else { $null }
  worker_report = if ($latest) { Rel (Join-Path $latest.FullName 'worker_report.json') } else { $null }
  worker_log = if ($latest) { Rel (Join-Path $latest.FullName 'worker_log.md') } else { $null }
  tests = if ($latest) { Rel (Join-Path $latest.FullName 'tests.txt') } else { $null }
  diffstat = if ($latest) { Rel (Join-Path $latest.FullName 'diffstat.txt') } else { $null }
}

if ($Json) {
  $result | ConvertTo-Json
} else {
  if ($latest) {
    Write-Host "Latest round: $($result.latest_round)"
    Write-Host "Stable worker prompt: $($result.latest_worker_prompt)"
    Write-Host "Worker prompt: $($result.worker_prompt)"
    Write-Host "Worker report: $($result.worker_report)"
  } else {
    Write-Host "No round_NNN directory found."
  }
}
