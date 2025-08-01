# scripts/powershell/revert/defender.ps1
# Restaura valores originales de Microsoft Defender desde backup

$backupPath = "C:\\windows\\temp\\defender_state_backup.json"

try {
    if (Test-Path $backupPath) {
        $original = Get-Content $backupPath | ConvertFrom-Json

        Set-MpPreference -DisableRealtimeMonitoring $original.DisableRealtimeMonitoring
        Set-MpPreference -MAPSReporting $original.MAPSReporting
        Set-MpPreference -SubmitSamplesConsent $original.SubmitSamplesConsent
        Set-MpPreference -PUAProtection $original.PUAProtection

        Write-Output "Configuración de Microsoft Defender restaurada desde backup."
    } else {
        Write-Output "No se encontró el backup de configuración previa."
    }
} catch {
    Write-Output "Error al revertir la configuración de Defender: $_"
}
