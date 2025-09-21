$key = 'HKLM:\System\CurrentControlSet\Control\Terminal Server'
Get-ItemProperty -Path $key -Name 'fDenyTSConnections'
Get-Service -Name "TermService" | Select-Object Status, StartType
Get-NetFirewallRule | Where-Object {
    $_.DisplayGroup -in @("Remote Desktop", "Escritorio remoto")
} | Select-Object DisplayName, Enabled
