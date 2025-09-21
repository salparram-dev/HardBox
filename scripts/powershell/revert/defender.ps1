# scripts/powershell/revert/defender.ps1
# Restaura valores originales de Microsoft Defender desde backup

# Importar utilidades de backup (subir desde revert hasta TFM\utils)
. (Join-Path $PSScriptRoot '..\..\..\utils\backup_utils.ps1') -BackupName "defender_state_backup.json"

$backupPath = Get-BackupPath

try {
    if (Test-Path $backupPath) {
        $original = Get-Content $backupPath | ConvertFrom-Json

        Set-MpPreference -DisableRealtimeMonitoring $original.DisableRealtimeMonitoring # Si estaba a True saldrá en False por motivos de seguridad de Microsoft
        Set-MpPreference -MAPSReporting $original.MAPSReporting
        Set-MpPreference -SubmitSamplesConsent $original.SubmitSamplesConsent
        Set-MpPreference -PUAProtection $original.PUAProtection

    } else {
        Write-Output  "No se ha encontrado backup en $backupPath"
    }
} catch {
    Write-Output "Error al revertir: $_"
}

