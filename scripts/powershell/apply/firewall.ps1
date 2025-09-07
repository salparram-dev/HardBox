# scripts/powershell/apply/firewall.ps1
# Configuración recomendada para los tres perfiles del cortafuegos de Windows (CCN-STIC-599) 
param(
    [switch]$ForceBackup
)

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "firewall_backup.json" -ForceBackup:$ForceBackup

$profiles = @("Domain", "Private", "Public")

# Obtener configuración actual
$currentConfig = @()
foreach ($prof in $profiles) {
    $state = Get-NetFirewallProfile -Profile $prof
    $currentConfig += [PSCustomObject]@{
        Name     = $prof
        Enabled  = $state.Enabled
        Inbound  = $state.DefaultInboundAction
        Outbound = $state.DefaultOutboundAction
    }
}

# Guardar backup si procede
Create-JsonBackup $currentConfig

# Aplicar configuración endurecida
foreach ($prof in $profiles) {
    Set-NetFirewallProfile -Profile $prof -Enabled True -DefaultInboundAction Block -DefaultOutboundAction Allow
}
