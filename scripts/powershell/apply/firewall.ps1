# scripts/powershell/apply/firewall.ps1
# Configuración personalizada para los tres perfiles del cortafuegos de Windows (CCN-STIC-599)

param(
    [switch]$ForceBackup,

    [int]$DomainEnabled = 1,
    [string]$DomainInbound = "Block",
    [string]$DomainOutbound = "Allow",

    [int]$PrivateEnabled = 1,
    [string]$PrivateInbound = "Block",
    [string]$PrivateOutbound = "Allow",

    [int]$PublicEnabled = 1,
    [string]$PublicInbound = "Block",
    [string]$PublicOutbound = "Allow"
)

# Convertir enteros a booleanos
$DomainEnabled  = [bool]$DomainEnabled
$PrivateEnabled = [bool]$PrivateEnabled
$PublicEnabled  = [bool]$PublicEnabled

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') `
    -BackupName "firewall_backup.json" `
    -ForceBackup:$ForceBackup

# Guardar configuración actual
$currentConfig = @()
foreach ($prof in @("Domain", "Private", "Public")) {
    $state = Get-NetFirewallProfile -Profile $prof
    $currentConfig += [PSCustomObject]@{
        Name     = $prof
        Enabled  = $state.Enabled
        Inbound  = $state.DefaultInboundAction
        Outbound = $state.DefaultOutboundAction
    }
}
Create-JsonBackup $currentConfig

# Aplicar configuración
Set-NetFirewallProfile -Profile Domain  -Enabled:$DomainEnabled  -DefaultInboundAction $DomainInbound  -DefaultOutboundAction $DomainOutbound
Set-NetFirewallProfile -Profile Private -Enabled:$PrivateEnabled -DefaultInboundAction $PrivateInbound -DefaultOutboundAction $PrivateOutbound
Set-NetFirewallProfile -Profile Public  -Enabled:$PublicEnabled  -DefaultInboundAction $PublicInbound  -DefaultOutboundAction $PublicOutbound
