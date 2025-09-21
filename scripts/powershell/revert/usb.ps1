# scripts/powershell/revert/usb.ps1
# Restaura la configuración uso de USBSTOR desde el backup
# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "usb_backup.json"

$regPath = "HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR"
$backupPath = Get-BackupPath

try {
    if (Test-Path $backupPath) {
        $originalVal = Get-Content -Path $backupPath | ConvertFrom-Json
        Set-ItemProperty -Path "Registry::$regPath" -Name "Start" -Value $originalVal
        Write-Output "Control USB revertido: valor original restaurado."
    } else {
        Write-Output "No se encontró backup para revertir la configuración."
    }
} catch {
    Write-Output "Error revirtiendo control USB: $_"
}

