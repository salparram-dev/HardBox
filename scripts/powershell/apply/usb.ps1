# scripts/powershell/apply/usb.ps1
# Configura el uso de USBSTOR (CCN-STIC-599) con varios modos

param(
    [switch]$ForceBackup,
    [string]$UsbMode = "disabled"  # Valores: disabled, manual, automatic
)

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') `
    -BackupName "usb_backup.json" `
    -ForceBackup:$ForceBackup

$regPath = "HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR"

# Obtener valor actual
$startVal = Get-ItemProperty -Path "Registry::$regPath" -Name "Start" | Select-Object -ExpandProperty Start

# Guardar backup
Create-JsonBackup $startVal

# Traducir modo a valor numérico
switch ($UsbMode.ToLower()) {
    "disabled" { $val = 4 }
    "manual"   { $val = 3 }
    "automatic"{ $val = 2 }
    default    { Write-Output "Modo USB no reconocido: $UsbMode. Usando 'disabled'."; $val = 4 }
}

# Aplicar configuración
Set-ItemProperty -Path "Registry::$regPath" -Name "Start" -Value $val
