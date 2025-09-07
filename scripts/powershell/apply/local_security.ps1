# scripts/powershell/apply/local_security.ps1
# Establece configuraciones seguras de contraseña según CCN-STIC-599

param(
    [switch]$ForceBackup,
    [int]$MinimumPasswordLength = 10,
    [int]$PasswordComplexity = 1,
    [int]$MaximumPasswordAge = 60,
    [int]$MinimumPasswordAge = 1,
    [int]$PasswordHistorySize = 10,
    [int]$LockoutBadCount = 5,
    [int]$ResetLockoutCount = 15,
    [int]$LockoutDuration = 15
)

# Importar utils y hacer backup como ya lo tienes
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "sec_backup.inf" -ForceBackup:$ForceBackup
Create-SeceditBackup

# Usar las variables en el INF
$lines = @(
    "[Unicode]",
    "Unicode=yes",
    "",
    "[System Access]",
    "MinimumPasswordLength = $MinimumPasswordLength",
    "PasswordComplexity = $PasswordComplexity",
    "MaximumPasswordAge = $MaximumPasswordAge",
    "MinimumPasswordAge = $MinimumPasswordAge",
    "PasswordHistorySize = $PasswordHistorySize",
    "LockoutBadCount = $LockoutBadCount",
    "ResetLockoutCount = $ResetLockoutCount",
    "LockoutDuration = $LockoutDuration",
    "",
    "[Version]",
    'signature="$CHICAGO$"',
    "Revision=1"
)

# Guardar y aplicar
$infFile = Join-Path (Split-Path (Get-BackupPath) -Parent) "ccn_hardening.inf"
Set-Content -Path $infFile -Value $lines -Encoding Unicode -Force
secedit /configure /db (Join-Path (Split-Path (Get-BackupPath) -Parent) "secedit.sdb") /cfg $infFile /areas SECURITYPOLICY
