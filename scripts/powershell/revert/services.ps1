# scripts/powershell/revert/services.ps1
# Restaura el estado exacto de los servicios modificados

$backupPath = "C:\\windows\\temp\\services_state_backup.json"

if (Test-Path $backupPath) {
    $states = Get-Content $backupPath | ConvertFrom-Json

    foreach ($svc in $states) {
        try {
            if (Get-Service -Name $svc.Name -ErrorAction SilentlyContinue) {
                Set-Service -Name $svc.Name -StartupType $svc.StartMode
                if ($svc.Status -eq "Running") {
                    Start-Service -Name $svc.Name -ErrorAction SilentlyContinue
                }
                Write-Output "Servicio '$($svc.Name)' restaurado a $($svc.StartMode) y estado $($svc.Status)."
            }
        } catch {
            Write-Output "Error al restaurar '$($svc.Name)': $_"
        }
    }
} else {
    Write-Output "No se encontró backup en $backupPath"
}
