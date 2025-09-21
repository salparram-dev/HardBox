# scripts/powershell/revert/firewall.ps1
# Restaura la configuración del cortafuegos de Windows desde el backup (CCN-STIC-599) 
# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "firewall_backup.json"

$backupPath = Get-BackupPath

try {
    if (Test-Path $backupPath) {
        $config = Get-Content $backupPath | ConvertFrom-Json
        foreach ($item in $config) {
            Set-NetFirewallProfile -Profile $item.Name -Enabled $item.Enabled -DefaultInboundAction $item.Inbound -DefaultOutboundAction $item.Outbound
        }
        Write-Output "Cambios del firewall revertidos correctamente."
    } else {
        Write-Output "Archivo de backup no encontrado."
    }
} catch {
    Write-Output "Error al revertir: $_"
}
