param(
  [switch]$ValidatePreview,
  [switch]$PythonCache,
  [switch]$TempClone,
  [switch]$All
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Parent = Split-Path -Parent $KitDir
$removed = New-Object System.Collections.Generic.List[string]

function Remove-PathSafe($Path) {
  if (Test-Path $Path) {
    Remove-Item -LiteralPath $Path -Recurse -Force
    $removed.Add($Path.Replace('\','/')) | Out-Null
  }
}

if ($All -or $ValidatePreview) {
  Remove-PathSafe (Join-Path (Join-Path (Join-Path $KitDir '.ai') 'active_task') 'rounds/_validate')
}
if ($All -or $PythonCache) {
  Get-ChildItem -Path $Parent -Directory -Recurse -Filter '__pycache__' -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "$KitDir*" } |
    ForEach-Object { Remove-PathSafe $_.FullName }
}
if ($All -or $TempClone) {
  Remove-PathSafe (Join-Path $env:TEMP 'token-saver-loop-kit')
  Remove-PathSafe (Join-Path $Parent '.token-saver-loop')
}

if ($removed.Count -eq 0) {
  Write-Host 'Nothing cleaned.'
} else {
  Write-Host 'Removed:'
  $removed | ForEach-Object { Write-Host "- $_" }
}
