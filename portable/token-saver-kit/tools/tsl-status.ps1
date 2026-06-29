param(
  [switch]$Json
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
$Rounds = Join-Path $Active 'rounds'
$statePath = Join-Path $Active 'state.md'
$latestPromptPath = Join-Path $KitDir 'LATEST_WORKER_PROMPT.md'

function Rel($Path) {
  if (-not $Path) { return $null }
  return $Path.Replace('\','/')
}

function Read-StateValue($Text, $Name) {
  if ($Text -match "(?m)^$([regex]::Escape($Name)):\s*(.+)$") { return $Matches[1].Trim() }
  return $null
}

$latest = $null
if (Test-Path $Rounds) {
  $latest = Get-ChildItem -Path $Rounds -Directory -Filter 'round_*' |
    Where-Object { $_.Name -match '^round_\d+$' } |
    Sort-Object Name |
    Select-Object -Last 1
}

$stateText = if (Test-Path $statePath) { Get-Content $statePath -Raw } else { '' }
$status = Read-StateValue $stateText 'Status'
$phase = Read-StateValue $stateText 'Current phase'
$latestReport = if ($latest) { Join-Path $latest.FullName 'worker_report.json' } else { $null }
$latestPrompt = if (Test-Path $latestPromptPath) { $latestPromptPath } else { $null }

$nextRole = 'reviewer'
$nextPrompt = 'Read token-saver-kit/START_HERE.md and act as reviewer only.'
if ($latest -and (Test-Path $latestReport)) {
  $nextRole = 'reviewer'
  $nextPrompt = "Review the latest $((Rel $latest.FullName)) evidence."
} elseif ($latest -and $latestPrompt) {
  $nextRole = 'worker'
  $nextPrompt = 'Read token-saver-kit/LATEST_WORKER_PROMPT.md and execute it.'
}

$result = [ordered]@{
  status = if ($status) { $status } else { 'not_started' }
  phase = $phase
  latest_round = if ($latest) { Rel $latest.FullName } else { $null }
  latest_worker_prompt = if ($latestPrompt) { Rel $latestPrompt } else { $null }
  worker_report = if ($latestReport -and (Test-Path $latestReport)) { Rel $latestReport } else { $null }
  next_role = $nextRole
  next_prompt = $nextPrompt
}

if ($Json) {
  $result | ConvertTo-Json -Depth 4
} else {
  Write-Host "Status: $($result.status)"
  if ($result.phase) { Write-Host "Phase: $($result.phase)" }
  if ($result.latest_round) { Write-Host "Latest round: $($result.latest_round)" }
  Write-Host "Next role: $($result.next_role)"
  Write-Host 'Next prompt:'
  Write-Host $result.next_prompt
}
