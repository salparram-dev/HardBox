param(
    [string]$BackupName,
    [switch]$ForceBackup
)

$backupDir = "$env:ProgramData\HardBoxBackup"

function Ensure-BackupDir {
    if (-not (Test-Path $backupDir)) {
        New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
        icacls $backupDir /inheritance:r /grant:r "Administrators:F" | Out-Null
    }
}

function Get-BackupPath {
    return Join-Path $backupDir $BackupName
}

function Create-JsonBackup($data) {
    $path = Get-BackupPath
    if ($ForceBackup -or -not (Test-Path $path)) {
        $data | ConvertTo-Json | Set-Content -Path $path -Encoding UTF8
    }
}
function Create-FileBackup($command) {
    $path = Get-BackupPath
    if ($ForceBackup -or -not (Test-Path $path)) {
        if ($ForceBackup -and -not (Test-Path $path)) {
            Remove-Item $path -Force
        }
        & $command
    }
}


Ensure-BackupDir
