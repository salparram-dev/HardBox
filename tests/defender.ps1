# Comprobar si la protección en tiempo real está activa
(Get-MpPreference).DisableRealtimeMonitoring # Debe ser false

# Ver el nivel de participación en MAPS (cloud reporting)
(Get-MpPreference).MAPSReporting # Deber ser 2

# Ver el consentimiento para el envío de muestras
(Get-MpPreference).SubmitSamplesConsent # Debe ser 1

# Ver si la protección contra apps potencialmente no deseadas (PUA) está activa
(Get-MpPreference).PUAProtection # Debe ser 1
