# scripts/powershell/revert/local_security.ps1
# Restaura configuraciones anteriores de contraseña si se exportó backup previamente

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "sec_backup.inf"

$backupPath = Get-BackupPath

if (Test-Path $backupPath) {
    secedit /configure /db (Join-Path (Split-Path $backupPath -Parent) "secedit.sdb") /cfg $backupPath /areas SECURITYPOLICY
    Write-Output "Cambios de seguridad revertidos desde backup."
} else {
    Write-Output "No se ha encontrado respaldo previo en $backupPath. No se realizaron cambios."
}
