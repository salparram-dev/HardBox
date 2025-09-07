# scripts/powershell/revert/local_security.ps1
# Restaura configuraciones anteriores de contraseña si se exportó backup previamente

$backupDir = "$env:ProgramData\HardBoxBackup"
$backupFile = Join-Path $backupDir "sec_backup.inf"

if (Test-Path $backupFile) {
    secedit /configure /db "$backupDir\secedit.sdb" /cfg $backupFile /areas SECURITYPOLICY
    Write-Output "Configuración de seguridad restaurada desde backup."
} else {
    Write-Output "No se ha encontrado respaldo previo en $backupFile. No se realizaron cambios."
}
