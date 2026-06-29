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
$verdictPath = Join-Path $latest.FullName 'verdict.json'

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
$commandCount = ($commands | Measure-Object).Count
$passedCommandCount = ($passedCommands | Measure-Object).Count
$failedCommandCount = ($failedCommands | Measure-Object).Count
$redflagsJson = & (Join-Path $PSScriptRoot 'tsl-redflags.ps1') -Json
$redflags = $redflagsJson | ConvertFrom-Json
$errorFlags = @($redflags.flags | Where-Object { $_.level -eq 'error' })
$warnFlags = @($redflags.flags | Where-Object { $_.level -eq 'warn' })

function Get-ReportValue($Name) {
  if (-not $report) { return $null }
  $property = $report.PSObject.Properties[$Name]
  if ($property) { return $property.Value }
  return $null
}

function Has-ReportProperty($Name) {
  if (-not $report) { return $false }
  return $null -ne $report.PSObject.Properties[$Name]
}

function Downgrade-Tier($Tier) {
  switch ($Tier) {
    'T3' { return 'T2' }
    'T2' { return 'T1' }
    'T1' { return 'T0' }
    default { return 'T0' }
  }
}

$tier = [string](Get-ReportValue 'tier')
if (-not $tier) {
  $tierPath = Join-Path $latest.FullName 'tier.md'
  if (Test-Path $tierPath) {
    $tierText = Get-Content $tierPath -Raw
    if ($tierText -match 'T[0-3]') { $tier = $Matches[0] }
  }
}
if (-not $tier) { $tier = 'T2' }

$reasons = New-Object System.Collections.Generic.List[string]
$evidenceGapCount = 0
function Add-Reason($Text) {
  if ($Text) { $reasons.Add([string]$Text) | Out-Null }
}

if (-not $report) { Add-Reason 'worker_report.json is missing or invalid.' }
foreach ($flag in $errorFlags) { Add-Reason "error red flag: $($flag.area) - $($flag.message)" }
foreach ($flag in $warnFlags) { Add-Reason "warning red flag: $($flag.area) - $($flag.message)" }
if ($report -and $report.status -ne 'done') { Add-Reason "worker status is '$($report.status)', not 'done'." }
if ($report -and $commandCount -eq 0) { Add-Reason 'commands_run is empty.' }
if ($failedCommandCount -gt 0) { Add-Reason "$failedCommandCount validation command(s) failed." }
if ($report -and $passedCommandCount -eq 0) { Add-Reason 'no passed validation command is recorded.' }
if ($report -and -not (Test-Path $testsPath)) { Add-Reason 'tests.txt is missing.'; $evidenceGapCount += 1 }
foreach ($name in @('summary','files_changed','commands_run','acceptance','risks','deviations','open_questions','next_action')) {
  if (-not (Has-ReportProperty $name)) {
    Add-Reason "worker_report.json is missing '$name'."
    $evidenceGapCount += 1
  }
}
foreach ($name in @('summary','next_action')) {
  $value = Get-ReportValue $name
  if ($null -eq $value -or ([string]$value).Trim() -eq '') {
    Add-Reason "worker_report.json has empty '$name'."
    $evidenceGapCount += 1
  }
}

$hasDangerousGit = @($redflags.flags | Where-Object { $_.area -eq 'dangerous_git' }).Count -gt 0
$hasKitBoundary = @($redflags.flags | Where-Object { $_.area -eq 'kit_boundary' }).Count -gt 0
$hasInvalidEvidence = @($redflags.flags | Where-Object { $_.area -eq 'evidence' -and $_.level -eq 'error' }).Count -gt 0
$hasScopeError = @($redflags.flags | Where-Object { $_.area -eq 'scope' -and $_.level -eq 'error' }).Count -gt 0

$verdict = 'FIX_SAME_TIER'
$confidence = 'medium'
$nextTier = $tier
$nextAction = 'Ask the worker to fix the evidence gaps or failed validation in the same tier.'

if (-not $report -or $hasDangerousGit -or $hasKitBoundary -or $hasInvalidEvidence) {
  $verdict = 'STOP'
  $confidence = 'high'
  $nextTier = $tier
  $nextAction = 'Stop automatic continuation. Reviewer/user must inspect the round and decide the next task.'
} elseif ($hasScopeError) {
  $verdict = 'DOWNGRADE'
  $confidence = 'high'
  $nextTier = Downgrade-Tier $tier
  $nextAction = "Create a narrower $nextTier round with stricter file scope."
} elseif ($errorFlags.Count -gt 0) {
  $verdict = 'STOP'
  $confidence = 'medium'
  $nextTier = $tier
  $nextAction = 'Stop automatic continuation until the reviewer checks the error red flags.'
} elseif ($report.status -eq 'done' -and
          $warnFlags.Count -eq 0 -and
          $evidenceGapCount -eq 0 -and
          $commandCount -gt 0 -and
          $passedCommandCount -gt 0 -and
          $failedCommandCount -eq 0 -and
          (Test-Path $testsPath)) {
  $verdict = 'PASS'
  $confidence = 'medium'
  $nextTier = $tier
  $nextAction = 'Evidence is complete enough for reviewer fast diff/test spot-check. PASS is not final acceptance.'
  if ($reasons.Count -eq 0) { Add-Reason 'worker evidence exists, validation passed, and no red flags were found.' }
} elseif ($warnFlags.Count -gt 0 -or $failedCommandCount -gt 0 -or $passedCommandCount -eq 0) {
  $verdict = 'FIX_SAME_TIER'
  $confidence = 'medium'
  $nextTier = $tier
  $nextAction = 'Ask the worker to fix missing evidence, warnings, or validation failures without expanding scope.'
}

$verdictRecord = [ordered]@{
  verdict = $verdict
  confidence = $confidence
  reviewer_final = $false
  generated_by = 'tsl-review.ps1'
  latest_round = $latest.FullName.Replace('\','/')
  tier = $tier
  next_tier = $nextTier
  reasons = @($reasons.ToArray())
  next_action = $nextAction
  meaning = 'Evidence verdict only. Reviewer still owns final quality and business acceptance.'
}
$verdictRecord | ConvertTo-Json -Depth 6 | Set-Content -Path $verdictPath -Encoding utf8
$memoryJson = & (Join-Path $PSScriptRoot 'tsl-memory.ps1') -Json
$memory = $memoryJson | ConvertFrom-Json

$result = [ordered]@{
  latest_round = $latest.FullName.Replace('\','/')
  status = if ($report) { $report.status } else { 'missing_report' }
  verdict = $verdict
  confidence = $confidence
  reviewer_final = $false
  verdict_file = $verdictPath.Replace('\','/')
  latest_evidence_file = $memory.files.latest_evidence
  reasons = @($reasons.ToArray())
  next_tier = $nextTier
  summary = if ($report) { $report.summary } else { '' }
  changed_files = $changed
  changed_file_count = $changed.Count
  commands_total = $commandCount
  commands_passed = $passedCommandCount
  commands_failed = $failedCommandCount
  redflags_total = $redflags.count
  redflags_errors = $errorFlags.Count
  redflags_warnings = $warnFlags.Count
  tests_file = if (Test-Path $testsPath) { $testsPath.Replace('\','/') } else { $null }
  diffstat_file = if (Test-Path $diffstatPath) { $diffstatPath.Replace('\','/') } else { $null }
  suggested_reviewer_action = $nextAction
  next_prompt = "Review the latest $($latest.FullName.Replace('\','/')) evidence."
}

if ($Json) {
  $result | ConvertTo-Json -Depth 5
} else {
  Write-Host "Latest round: $($result.latest_round)"
  Write-Host "Status: $($result.status)"
  Write-Host "Evidence verdict: $($result.verdict)"
  Write-Host "Confidence: $($result.confidence)"
  Write-Host "Reviewer final: false"
  if ($result.summary) { Write-Host "Summary: $($result.summary)" }
  Write-Host "Changed files: $($result.changed_file_count)"
  if ($changed.Count) { $changed | ForEach-Object { Write-Host "- $_" } } else { Write-Host "- none reported" }
  Write-Host "Commands: $($result.commands_passed) passed, $($result.commands_failed) failed, $($result.commands_total) total"
  Write-Host "Red flags: $($result.redflags_errors) errors, $($result.redflags_warnings) warnings"
  if ($redflags.count -gt 0) {
    $redflags.flags | ForEach-Object { Write-Host "- [$($_.level)] $($_.area): $($_.message)" }
  }
  Write-Host "Reasons:"
  if ($reasons.Count) { $reasons | ForEach-Object { Write-Host "- $_" } } else { Write-Host "- none" }
  Write-Host "Next tier: $($result.next_tier)"
  Write-Host "Verdict file: $($result.verdict_file)"
  Write-Host "Latest evidence: $($result.latest_evidence_file)"
  Write-Host "Tests file: $($result.tests_file)"
  Write-Host "Diffstat: $($result.diffstat_file)"
  Write-Host "Suggested action: $($result.suggested_reviewer_action)"
  Write-Host "Next prompt: $($result.next_prompt)"
}
