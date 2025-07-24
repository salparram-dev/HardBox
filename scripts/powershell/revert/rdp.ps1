# scripts/powershell/revert/rdp.ps1

try {
    $key = 'HKLM:\System\CurrentControlSet\Control\Terminal Server'
    Set-ItemProperty -Path $key -Name 'fDenyTSConnections' -Value 0
    Write-Output "RDP activado correctamente."
} catch {
    Write-Output "Error al activar RDP: $_"
}