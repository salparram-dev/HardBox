# scripts/powershell/apply/services.ps1
# Desactiva servicios innecesarios según recomendaciones del perfil estándar CCN-STIC-599

param(
    [switch]$ForceBackup,
    [switch]$Fax,
    [switch]$RemoteRegistry,
    [switch]$XblGameSave,
    [switch]$WSearch,
    [switch]$DiagTrack,
    [switch]$MapsBroker,
    [switch]$SharedAccess,
    [switch]$BluetoothSupportService,
    [switch]$RetailDemo
)

# Importar utilidades de backup
$utilsPath = Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1' | Resolve-Path
. $utilsPath -BackupName "services_state_backup.json" -ForceBackup:$ForceBackup

$serviceStates = @()

# Lista de todos los servicios recomendados
$allServices = @(
    "Fax",
    "RemoteRegistry",
    "XblGameSave",
    "WSearch",
    "DiagTrack",
    "MapsBroker",
    "SharedAccess",
    "BluetoothSupportService",
    "RetailDemo"
)

# Guardar estado actual de todos (para revertir)
foreach ($svc in $allServices) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        $cim = Get-CimInstance -ClassName Win32_Service -Filter "Name='$svc'"
        $serviceStates += [pscustomobject]@{
            Name      = $svc
            Status    = $s.Status.ToString()
            StartMode = $cim.StartMode
        }
    }
}

Create-JsonBackup $serviceStates

# Desactivar solo los que el usuario haya marcado
foreach ($svc in $allServices) {
    if ((Get-Variable $svc -ValueOnly) -eq $true) {
        try {
            Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue
            Set-Service -Name $svc -StartupType Disabled
            Write-Output "Servicio '$svc' detenido y deshabilitado."
        } catch {
            Write-Output "Error al modificar el servicio '$svc': $_"
        }
    }
}
