# scripts/powershell/apply/auditing.ps1
# Configura políticas de auditoría recomendadas (CCN-STIC-599) usando GUIDs

try {
    $backupPath = "C:\\Windows\\Temp\\audit_backup.csv"
    if (!(Test-Path $backupPath)) {
        auditpol /backup /file:$backupPath
    }

    $auditSettings = @{
        "{0CCE9215-69AE-11D9-BED3-505054503030}" = "enable"  # Inicio de sesión
        "{0CCE9216-69AE-11D9-BED3-505054503030}" = "enable"  # Cerrar sesión
        "{0CCE9217-69AE-11D9-BED3-505054503030}" = "enable"  # Bloqueo de cuenta
        "{0CCE9210-69AE-11D9-BED3-505054503030}" = "enable"  # Cambio de estado de seguridad
        "{0CCE922F-69AE-11D9-BED3-505054503030}" = "enable"  # Cambio en la directiva de auditoría
        "{0CCE9230-69AE-11D9-BED3-505054503030}" = "enable"  # Cambio de la directiva de autenticación
        "{0CCE9235-69AE-11D9-BED3-505054503030}" = "enable"  # Administración de cuentas de usuario
        "{0CCE9237-69AE-11D9-BED3-505054503030}" = "enable"  # Administración de grupos de seguridad
        "{0CCE9212-69AE-11D9-BED3-505054503030}" = "enable"  # Integridad del sistema
    }

    $auditSettings.Keys | ForEach-Object {
        auditpol /set /subcategory:$_ /success:enable /failure:enable | Out-Null
    }

    Write-Output "Auditoría endurecida aplicada correctamente."
} catch {
    Write-Output "Error aplicando configuración de auditoría: $_"
}
