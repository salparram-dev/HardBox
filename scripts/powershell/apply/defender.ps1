# scripts/powershell/apply/defender.ps1
# Refuerza la configuración de Windows Defender según el perfil CCN-STIC-599 (perfil estándar)

param(
    [switch]$ForceBackup,
    [int]$MAPSReporting = 2,           # 0=Deshabilitado, 1=Básico, 2=Avanzado
    [int]$SubmitSamplesConsent = 1,    # 0=Nunca, 1=Solo seguras, 2=Preguntar, 3=Siempre
    [int]$PUAProtection = 1             # 0=Deshabilitado, 1=Habilitado, 2=Auditoría
)

# Importar utilidades de backup
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') `
    -BackupName "defender_state_backup.json" `
    -ForceBackup:$ForceBackup

# Guardar estado actual
$currentState = @{
    DisableRealtimeMonitoring = (Get-MpPreference).DisableRealtimeMonitoring
    MAPSReporting              = (Get-MpPreference).MAPSReporting
    SubmitSamplesConsent       = (Get-MpPreference).SubmitSamplesConsent
    PUAProtection              = (Get-MpPreference).PUAProtection
}

Create-JsonBackup $currentState

# Aplicar configuración
# Protección en tiempo real siempre habilitada por seguridad
Set-MpPreference -DisableRealtimeMonitoring $false

# Aplicar valores seleccionados por el usuario
Set-MpPreference -MAPSReporting $MAPSReporting
Set-MpPreference -SubmitSamplesConsent $SubmitSamplesConsent
Set-MpPreference -PUAProtection $PUAProtection
