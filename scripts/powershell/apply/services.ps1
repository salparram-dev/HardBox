# scripts/powershell/apply/services.ps1
# Desactiva servicios innecesarios según recomendaciones del perfil estándar CCN-STIC-599

param(
    [switch]$ForceBackup
)

# Sube tres niveles desde la carpeta actual del script y entra en utils
$utilsPath = Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1' | Resolve-Path

# Importa el script de utilidades
. $utilsPath -BackupName "services_state_backup.json" -ForceBackup:$ForceBackup


$serviceStates = @()

$services = @(
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

foreach ($svc in $services) {
    try {
        $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
        if ($s) {
            $cim = Get-CimInstance -ClassName Win32_Service -Filter "Name='$svc'"
            $serviceStates += [pscustomobject]@{
                Name      = $svc
                Status    = $s.Status.ToString()
                StartMode = $cim.StartMode
            }

            Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue
            Set-Service -Name $svc -StartupType Disabled
            Write-Output "Servicio '$svc' detenido y deshabilitado."
        }
    } catch {
        Write-Output "Error al modificar el servicio '$svc': $_"
    }
}

# Guardar backup si procede
Create-JsonBackup $serviceStates
