# scripts/powershell/apply/usb.ps1
# Desactiva el uso de USBSTOR (CCN-STIC-599)
param(
    [switch]$ForceBackup
)

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "usb_backup.json" -ForceBackup:$ForceBackup

$regPath = "HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR"

# Obtener valor actual
$startVal = Get-ItemProperty -Path "Registry::$regPath" -Name "Start" | Select-Object -ExpandProperty Start

# Guardar backup si procede
Create-JsonBackup $startVal

# Aplicar bloqueo (valor 4 = deshabilitado)
Set-ItemProperty -Path "Registry::$regPath" -Name "Start" -Value 4

Write-Output "Control USB aplicado: almacenamiento USB deshabilitado."

