# scripts/powershell/revert/services.ps1
# Restaura el estado exacto de los servicios modificados

# Sube tres niveles desde la carpeta actual del script y entra en utils
$utilsPath = Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1' | Resolve-Path

# Importa el script de utilidades
. $utilsPath -BackupName "services_state_backup.json" -ForceBackup:$ForceBackup


$backupPath = Get-BackupPath

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
    Write-Output "No se ha encontrado backup en $backupPath"
}

