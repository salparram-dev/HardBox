# scripts/powershell/apply/auditing.ps1
# Configura políticas de auditoría (CCN-STIC-599) con niveles: none, success, failure, both

param(
    [switch]$ForceBackup,
    [string]$Logon = "both",
    [string]$Logoff = "both",
    [string]$AccountLockout = "both",
    [string]$SecurityStateChange = "both",
    [string]$AuditPolicyChange = "both",
    [string]$AuthenticationPolicyChange = "both",
    [string]$UserAccountManagement = "both",
    [string]$SecurityGroupManagement = "both",
    [string]$SystemIntegrity = "both"
)

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') `
    -BackupName "audit_backup.csv" `
    -ForceBackup:$ForceBackup

# Guardar backup si procede
$backupPath = Get-BackupPath
Create-FileBackup $backupPath {
    param($dest)
    auditpol /backup /file:"$dest"
}

# Mapa GUID -> valor de parámetro
$auditSettings = @{
    "{0CCE9215-69AE-11D9-BED3-505054503030}" = $Logon                  # Inicio de sesión
    "{0CCE9216-69AE-11D9-BED3-505054503030}" = $Logoff                 # Cerrar sesión
    "{0CCE9217-69AE-11D9-BED3-505054503030}" = $AccountLockout         # Bloqueo de cuenta
    "{0CCE9210-69AE-11D9-BED3-505054503030}" = $SecurityStateChange    # Cambio de estado de seguridad
    "{0CCE922F-69AE-11D9-BED3-505054503030}" = $AuditPolicyChange      # Cambio en la directiva de auditoría
    "{0CCE9230-69AE-11D9-BED3-505054503030}" = $AuthenticationPolicyChange # Cambio de la directiva de autenticación
    "{0CCE9235-69AE-11D9-BED3-505054503030}" = $UserAccountManagement  # Administración de cuentas de usuario
    "{0CCE9237-69AE-11D9-BED3-505054503030}" = $SecurityGroupManagement # Administración de grupos de seguridad
    "{0CCE9212-69AE-11D9-BED3-505054503030}" = $SystemIntegrity        # Integridad del sistema
}

# Aplicar configuración según el valor elegido
foreach ($guid in $auditSettings.Keys) {
    $mode = $auditSettings[$guid].ToLower()

    switch ($mode) {
        "none" {
            auditpol /set /subcategory:$guid /success:disable /failure:disable | Out-Null
        }
        "success" {
            auditpol /set /subcategory:$guid /success:enable /failure:disable | Out-Null
        }
        "failure" {
            auditpol /set /subcategory:$guid /success:disable /failure:enable | Out-Null
        }
        "both" {
            auditpol /set /subcategory:$guid /success:enable /failure:enable | Out-Null
        }
        default {
            Write-Output "Valor no reconocido para ${guid}: $mode"
        }
    }
}
