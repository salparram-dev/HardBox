# scripts/powershell/apply/local_security.ps1
# Establece configuraciones seguras de contraseña según CCN-STIC-599

param(
    [switch]$ForceBackup
)

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "sec_backup.inf" -ForceBackup:$ForceBackup

$backupPath = Get-BackupPath
$infFile    = Join-Path (Split-Path $backupPath -Parent) "ccn_hardening.inf"

# Guardar backup si procede
Create-SeceditBackup

# Configuración endurecida
$lines = @(
    "[Unicode]",
    "Unicode=yes",
    "",
    "[System Access]",
    "MinimumPasswordLength = 10",
    "PasswordComplexity = 1",
    "MaximumPasswordAge = 60",
    "MinimumPasswordAge = 1",
    "PasswordHistorySize = 10",
    "LockoutBadCount = 5",
    "ResetLockoutCount = 15",
    "LockoutDuration = 15",
    "",
    "[Version]",
    'signature="$CHICAGO$"',
    "Revision=1"
)

Set-Content -Path $infFile -Value $lines -Encoding Unicode -Force

# Aplicar configuración
secedit /configure /db (Join-Path (Split-Path $backupPath -Parent) "secedit.sdb") /cfg $infFile /areas SECURITYPOLICY
