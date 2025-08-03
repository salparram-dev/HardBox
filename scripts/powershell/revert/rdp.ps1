# scripts/powershell/revert/rdp.ps1
# Activa RDP y permite reglas de firewall relacionadas
try {
    $key = "HKLM:\System\CurrentControlSet\Control\Terminal Server"
    Set-ItemProperty -Path $key -Name "fDenyTSConnections" -Value 0

    Set-Service -Name TermService -StartupType Automatic
    Start-Service -Name TermService

    $rdpRules = Get-NetFirewallRule | Where-Object {
        $_.DisplayGroup -match "Remote Desktop|Escritorio remoto"
    }
    $rdpRules | ForEach-Object {
        Enable-NetFirewallRule -Name $_.Name
    }

    Write-Output "RDP activado correctamente."
} catch {
    Write-Output "Error activando RDP: $_"
}
