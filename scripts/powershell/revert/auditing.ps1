# scripts/powershell/revert/auditing.ps1
# Restaura las políticas de auditoría desde el backup

try {
    $backupPath = "C:\Windows\Temp\audit_backup.csv"
    if (Test-Path $backupPath) {
        auditpol /restore /file:$backupPath
        Write-Output "Configuración de auditoría restaurada desde backup."
    } else {
        Write-Output "No se encontró el archivo de backup de auditoría."
    }
} catch {
    Write-Output "Error al restaurar configuración de auditoría: $_"
}
