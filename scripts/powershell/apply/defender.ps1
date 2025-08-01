# scripts/powershell/apply/defender.ps1
# Refuerza la configuración de Windows Defender según el perfil CCN-STIC-599 (perfil estándar)

$backupPath = "C:\\windows\\temp\\defender_state_backup.json"

try {
    $currentState = @{
        DisableRealtimeMonitoring = (Get-MpPreference).DisableRealtimeMonitoring
        MAPSReporting = (Get-MpPreference).MAPSReporting
        SubmitSamplesConsent = (Get-MpPreference).SubmitSamplesConsent
        PUAProtection = (Get-MpPreference).PUAProtection
    }

    $currentState | ConvertTo-Json | Set-Content -Path $backupPath -Encoding UTF8

    # Aplicar configuración endurecida
    Set-MpPreference -DisableRealtimeMonitoring $false
    Set-MpPreference -MAPSReporting Advanced
    Set-MpPreference -SubmitSamplesConsent SendSafeSamples
    Set-MpPreference -PUAProtection 1

    Write-Output "Configuración de Microsoft Defender aplicada con éxito."
} catch {
    Write-Output "Error al aplicar la configuración de Defender: $_"
}
