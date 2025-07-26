# scripts/powershell/revert/local_security.ps1
# Restaura configuraciones anteriores de contraseña si se exportó backup previamente

try {
    $backupPath = "C:\\windows\\temp\\sec_backup.inf"
    if (Test-Path $backupPath) {
        secedit /configure /db secedit.sdb /cfg $backupPath /areas SECURITYPOLICY
        Write-Output "Configuración de seguridad restaurada desde backup."
    } else {
        Write-Output "No se encontró respaldo previo en $backupPath. No se realizaron cambios."
    }
} catch {
    Write-Output "Error revirtiendo configuración: $_"
}
