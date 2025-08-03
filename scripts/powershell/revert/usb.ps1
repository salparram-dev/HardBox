# scripts/powershell/revert/usb.ps1
# Restaura la configuración uso de USBSTOR desde el backup
try {
    $regPath = "HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR"
    $backupPath = "C:\Windows\Temp\usb_backup.json"

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
