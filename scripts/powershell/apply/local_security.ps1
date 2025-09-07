# scripts/powershell/apply/local_security.ps1
# Establece configuraciones seguras de contraseña según CCN-STIC-599

param(
    [switch]$ForceBackup
)

$backupDir  = "$env:ProgramData\HardBoxBackup"
$backupFile = Join-Path $backupDir "sec_backup.inf"
$infFile    = Join-Path $backupDir "ccn_hardening.inf"

# Crear carpeta segura si no existe
if (-not (Test-Path $backupDir)) {
    New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
    icacls $backupDir /inheritance:r /grant:r "Administrators:F" | Out-Null
}

# Exportar configuración actual solo si no hay backup o si se fuerza
if ($ForceBackup -or -not (Test-Path $backupFile)) {
    secedit /export /cfg $backupFile
}

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
secedit /configure /db "$backupDir\secedit.sdb" /cfg $infFile /areas SECURITYPOLICY

