# scripts/powershell/apply/rdp.ps1
# Desactiva RDP y bloquea reglas de firewall relacionadas

try {
    # Desactivar RDP (conexiones remotas)
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value 1

    $rdpRules = Get-NetFirewallRule | Where-Object {
        $_.DisplayGroup -match "Remote Desktop|Escritorio remoto"
    }
    $rdpRules | ForEach-Object {
        Disable-NetFirewallRule -Name $_.Name
    }

    Write-Output "RDP deshabilitado y reglas de firewall bloqueadas."
} catch {
    Write-Output "Error deshabilitando RDP: $_"
}
