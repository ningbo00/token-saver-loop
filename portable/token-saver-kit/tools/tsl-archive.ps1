param(
  [string]$Name = ''
)

$ErrorActionPreference = 'Stop'
$KitDir = Split-Path -Parent $PSScriptRoot
$Ai = Join-Path $KitDir '.ai'
$Active = Join-Path $Ai 'active_task'
if (-not (Test-Path $Active)) { throw 'No active_task directory to archive.' }

$stamp = if ($Name) { $Name } else { Get-Date -Format 'yyyyMMdd_HHmmss' }
$ArchiveRoot = Join-Path $Ai 'archive'
$Dest = Join-Path $ArchiveRoot $stamp
New-Item -ItemType Directory -Force $ArchiveRoot | Out-Null
if (Test-Path $Dest) { throw "Archive destination already exists: $Dest" }
Move-Item -LiteralPath $Active -Destination $Dest
Write-Host "Archived active_task to: $($Dest.Replace('\','/'))"
