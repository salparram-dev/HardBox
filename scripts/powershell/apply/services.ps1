# scripts/powershell/apply/services.ps1
# Desactiva servicios innecesarios según recomendaciones del perfil estándar CCN-STIC-599

$backupPath = "C:\\windows\\temp\\services_state_backup.json"
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
                Name = $svc
                Status = $s.Status.ToString()
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

$serviceStates | ConvertTo-Json | Set-Content -Path $backupPath -Encoding UTF8
