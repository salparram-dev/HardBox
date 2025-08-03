# scripts/powershell/apply/firewall.ps1
# Configuración recomendada para los tres perfiles del cortafuegos de Windows (CCN-STIC-599) 
try {
    $backupPath = "C:\Windows\Temp\firewall_backup.json"
    
    $profiles = @("Domain", "Private", "Public")
    if (!(Test-Path $backupPath)) {
        $currentConfig = @()
        foreach ($prof in $profiles) {
            $state = Get-NetFirewallProfile -Profile $prof
            $currentConfig += [PSCustomObject]@{
                Name    = $prof
                Enabled = $state.Enabled
                Inbound = $state.DefaultInboundAction
                Outbound = $state.DefaultOutboundAction
            }}   

        $currentConfig | ConvertTo-Json | Set-Content -Path $backupPath -Encoding UTF8
    }

    foreach ($prof in $profiles) {
        Set-NetFirewallProfile -Profile $prof -Enabled True -DefaultInboundAction Block -DefaultOutboundAction Allow
    }

    Write-Output "Configuración de firewall aplicada correctamente."
} catch {
    Write-Output "Error aplicando configuración de firewall: $_"
}
