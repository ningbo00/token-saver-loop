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

function Get-ChangedPath($Item) {
  if ($null -eq $Item) { return '' }
  if ($Item -is [string]) { return $Item }
  $pathProperty = $Item.PSObject.Properties['path']
  if ($pathProperty) { return [string]$pathProperty.Value }
  return [string]$Item
}

function Get-ConfiguredFileLimit {
  foreach ($path in @((Join-Path $Active 'state.md'), (Join-Path $Active 'reviewer_plan.md'))) {
    if (-not (Test-Path $path)) { continue }
    $text = Get-Content $path -Raw
    if ($text -match 'Source/config/doc file limit:\s*(\d+)') { return [int]$Matches[1] }
    if ($text -match 'Max parent-project source/config/doc files changed before stopping:\s*(\d+)') { return [int]$Matches[1] }
  }
  return $null
}

function Get-CommandText($Item) {
  if ($null -eq $Item) { return '' }
  if ($Item -is [string]) { return $Item }
  $commandProperty = $Item.PSObject.Properties['command']
  if ($commandProperty) { return [string]$commandProperty.Value }
  return [string]$Item
}

foreach ($name in @('.token-saver-loop', '__pycache__', 'build', 'dist', 'node_modules')) {
  $p = Join-Path $Parent $name
  if (Test-Path $p) { Add-Flag 'warn' 'generated_or_temp' "Found $name in parent project root." }
}

$allowedTools = @(
  'tsl-new-round.ps1',
  'tsl-latest.ps1',
  'tsl-review.ps1',
  'tsl-status.ps1',
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
if (-not (Test-Path (Join-Path $KitDir 'LATEST_WORKER_PROMPT.md'))) { Add-Flag 'warn' 'kit' 'Missing LATEST_WORKER_PROMPT.md.' }

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
      $changed = @($report.files_changed)
      $limit = Get-ConfiguredFileLimit
      if ($null -ne $limit) {
        $parentChanges = @($changed | Where-Object {
          $path = (Get-ChangedPath $_).Replace('\','/')
          $path -and ($path -notlike 'token-saver-kit/*')
        })
        if ($parentChanges.Count -gt $limit) {
          Add-Flag 'error' 'scope' "Worker changed $($parentChanges.Count) parent files, exceeding limit $limit."
        }
      }
      foreach ($file in $changed) {
        $path = Get-ChangedPath $file
        if (-not $path) { continue }
        $normalized = $path.Replace('\','/')
        if ($normalized -match '(^|/)(__pycache__|build|dist|node_modules)(/|$)') {
          Add-Flag 'warn' 'generated_or_temp' "Worker report includes generated/temp path: $normalized"
        }
        if ($normalized -match '^token-saver-kit/(tools|skills)/') {
          Add-Flag 'warn' 'kit_boundary' "Worker report includes kit tool/skill change: $normalized"
        }
      }
      if ($report.status -eq 'done') {
        $commands = @($report.commands_run)
        if ($commands.Count -eq 0) {
          Add-Flag 'warn' 'evidence' 'Worker reports done but commands_run is empty.'
        } elseif (-not ($commands | Where-Object { $_.result -eq 'passed' })) {
          Add-Flag 'warn' 'evidence' 'Worker reports done but no passed validation command is recorded.'
        }
      }
      foreach ($command in @($report.commands_run)) {
        $text = (Get-CommandText $command).Trim()
        if (-not $text) { continue }
        if ($text -match '(?i)\bgit\s+reset\s+--hard\b' -or
            $text -match '(?i)\bgit\s+clean\s+-[^\s]*[fdx][^\s]*\b' -or
            $text -match '(?i)\bgit\s+push\s+--force\b' -or
            $text -match '(?i)\bgit\s+checkout\s+--\b') {
          Add-Flag 'error' 'dangerous_git' "Worker report includes dangerous git command: $text"
        }
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
