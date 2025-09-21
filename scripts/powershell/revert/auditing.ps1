# scripts/powershell/revert/auditing.ps1
# Restaura las políticas de auditoría desde el backup

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "audit_backup.csv"

$backupPath = Get-BackupPath

try {
    if (Test-Path $backupPath) {
        auditpol /restore /file:$backupPath
        Write-Output "Cambios revertidos desde backup."
    } else {
        Write-Output "No se ha encontrado el archivo de backup."
    }
} catch {
    Write-Output "Error al restaurar: $_"
}

