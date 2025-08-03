# scripts/powershell/revert/firewall.ps1
# Restaura la configuración del cortafuegos de Windows desde el backup (CCN-STIC-599) 
try {
    $backupPath = "C:\Windows\Temp\firewall_backup.json"
    
    if (Test-Path $backupPath) {
        $config = Get-Content $backupPath | ConvertFrom-Json
        foreach ($item in $config) {
            Set-NetFirewallProfile -Profile $item.Name -Enabled $item.Enabled -DefaultInboundAction $item.Inbound -DefaultOutboundAction $item.Outbound
        }
        Write-Output "Configuración de firewall restaurada correctamente."
    } else {
        Write-Output "Archivo de backup no encontrado."
    }
} catch {
    Write-Output "Error al revertir configuración de firewall: $_"
}
