# scripts/powershell/apply/defender.ps1
# Refuerza la configuración de Windows Defender según el perfil CCN-STIC-599 (perfil estándar)

param(
    [switch]$ForceBackup
)

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "defender_state_backup.json" -ForceBackup:$ForceBackup

$currentState = @{
    DisableRealtimeMonitoring = (Get-MpPreference).DisableRealtimeMonitoring
    MAPSReporting              = (Get-MpPreference).MAPSReporting
    SubmitSamplesConsent       = (Get-MpPreference).SubmitSamplesConsent
    PUAProtection              = (Get-MpPreference).PUAProtection
}

# Guardar backup si procede (la función ya decide si sobrescribir o no)
Create-JsonBackup $currentState

# Aplicar configuración endurecida
Set-MpPreference -DisableRealtimeMonitoring $false
Set-MpPreference -MAPSReporting Advanced
Set-MpPreference -SubmitSamplesConsent SendSafeSamples
Set-MpPreference -PUAProtection 1
