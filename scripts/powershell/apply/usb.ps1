# scripts/powershell/apply/usb.ps1
# Desactiva el uso de USBSTOR (CCN-STIC-599)
try {
    $regPath = "HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR"
    $backupPath = "C:\Windows\Temp\usb_backup.json"

    if (-not (Test-Path $backupPath)) {
        $startVal = Get-ItemProperty -Path "Registry::$regPath" -Name "Start" | Select-Object -ExpandProperty Start
        $startVal | ConvertTo-Json | Set-Content -Path $backupPath -Encoding UTF8
    }

    Set-ItemProperty -Path "Registry::$regPath" -Name "Start" -Value 4 # Valor 4 = Bloqueo

    Write-Output "Control USB aplicado: almacenamiento USB deshabilitado."
} catch {
    Write-Output "Error aplicando control USB: $_"
}
