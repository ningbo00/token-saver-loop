param(
  [switch]$Json
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Active = Join-Path (Join-Path $KitDir '.ai') 'active_task'
$Memory = Join-Path (Join-Path $KitDir '.ai') 'project_memory'
$Rounds = Join-Path $Active 'rounds'

function Write-Utf8File($Path, $Content) {
  $dir = Split-Path -Parent $Path
  if ($dir) { New-Item -ItemType Directory -Force $dir | Out-Null }
  $Content | Set-Content -Path $Path -Encoding utf8
}

function Rel($Path) {
  if (-not $Path) { return $null }
  return $Path.Replace('\','/')
}

function Ensure-MemoryFile($Name, $Title, $DefaultLine) {
  $path = Join-Path $Memory $Name
  if (-not (Test-Path $path)) {
    Write-Utf8File $path "# $Title`n`n- $DefaultLine`n"
  }
  return $path
}

New-Item -ItemType Directory -Force $Memory | Out-Null
$files = [ordered]@{
  current_goal = Ensure-MemoryFile 'current_goal.md' 'Current Goal' 'Not set yet.'
  architecture = Ensure-MemoryFile 'architecture.md' 'Architecture' 'Not summarized yet.'
  completed = Ensure-MemoryFile 'completed.md' 'Completed' 'Nothing accepted by reviewer yet.'
  risks = Ensure-MemoryFile 'risks.md' 'Risks' 'No known risks yet.'
  latest_evidence = Ensure-MemoryFile 'latest_evidence.md' 'Latest Evidence' 'No worker evidence reviewed yet.'
}

$latest = $null
if (Test-Path $Rounds) {
  $latest = Get-ChildItem -Path $Rounds -Directory -Filter 'round_*' |
    Where-Object { $_.Name -match '^round_\d+$' } |
    Sort-Object Name |
    Select-Object -Last 1
}

$report = $null
$verdict = $null
if ($latest) {
  $reportPath = Join-Path $latest.FullName 'worker_report.json'
  $verdictPath = Join-Path $latest.FullName 'verdict.json'
  if (Test-Path $reportPath) {
    try { $report = Get-Content $reportPath -Raw | ConvertFrom-Json } catch { $report = $null }
  }
  if (Test-Path $verdictPath) {
    try { $verdict = Get-Content $verdictPath -Raw | ConvertFrom-Json } catch { $verdict = $null }
  }
}

if ($latest -and ($report -or $verdict)) {
  $changed = if ($report -and $report.files_changed) {
    @($report.files_changed | ForEach-Object {
      if ($_ -is [string]) { $_ } elseif ($_.PSObject.Properties['path']) { [string]$_.path } else { [string]$_ }
    } | Where-Object { $_ })
  } else { @() }
  $commands = if ($report -and $report.commands_run) { @($report.commands_run) } else { @() }
  $passed = @($commands | Where-Object { $_.result -eq 'passed' })
  $failed = @($commands | Where-Object { $_.result -eq 'failed' })
  $lines = New-Object System.Collections.Generic.List[string]
  $lines.Add('# Latest Evidence') | Out-Null
  $lines.Add('') | Out-Null
  $lines.Add("- Round: $(Rel $latest.FullName)") | Out-Null
  $lines.Add("- Evidence verdict: $(if ($verdict) { $verdict.verdict } else { 'not generated' })") | Out-Null
  $lines.Add("- Reviewer final: false") | Out-Null
  $lines.Add("- Worker status: $(if ($report) { $report.status } else { 'missing_report' })") | Out-Null
  $lines.Add("- Summary: $(if ($report) { $report.summary } else { '' })") | Out-Null
  $lines.Add("- Changed files: $(($changed | Measure-Object).Count)") | Out-Null
  foreach ($path in $changed) { $lines.Add("  - $path") | Out-Null }
  $lines.Add("- Commands: $(($passed | Measure-Object).Count) passed, $(($failed | Measure-Object).Count) failed, $(($commands | Measure-Object).Count) total") | Out-Null
  $lines.Add("- Next action: $(if ($verdict) { $verdict.next_action } elseif ($report) { $report.next_action } else { 'review latest round' })") | Out-Null
  $lines.Add('') | Out-Null
  $lines.Add('This file is a compact navigation aid. Trust reports, tests, diffs, and reviewer decisions for acceptance.') | Out-Null
  Write-Utf8File $files.latest_evidence ($lines -join "`n")
}

$result = [ordered]@{
  memory_dir = Rel $Memory
  files = [ordered]@{
    current_goal = Rel $files.current_goal
    architecture = Rel $files.architecture
    completed = Rel $files.completed
    risks = Rel $files.risks
    latest_evidence = Rel $files.latest_evidence
  }
  latest_round = if ($latest) { Rel $latest.FullName } else { $null }
  next_read = @(
    Rel $files.current_goal,
    Rel $files.latest_evidence,
    Rel $files.risks
  )
}

if ($Json) {
  $result | ConvertTo-Json -Depth 5
} else {
  Write-Host "Memory dir: $($result.memory_dir)"
  Write-Host 'Next reviewer reads:'
  $result.next_read | ForEach-Object { Write-Host "- $_" }
}
