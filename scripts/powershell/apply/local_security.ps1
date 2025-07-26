# scripts/powershell/apply/local_security.ps1
# Establece configuraciones seguras de contraseña según CCN-STIC-599

try {
    $backup = "C:\\windows\\temp\\sec_backup.inf"
    if (!(Test-Path $backup)) {
        secedit /export /cfg $backup # Exportar la configuración actual
    }

    $lines = @(
        "[Unicode]",
        "Unicode=yes",
        "",
        "[System Access]",
        "MinimumPasswordLength = 10",
        "PasswordComplexity = 1",
        "MaximumPasswordAge = 60",
        "MinimumPasswordAge = 1",
        "PasswordHistorySize = 10",
        "LockoutBadCount = 5",
        "ResetLockoutCount = 15",
        "LockoutDuration = 15",
        "",
        "[Version]",
        'signature="$CHICAGO$"',
        "Revision=1"

    )

    $path = "C:\\windows\\temp\\ccn_hardening.inf"
    Set-Content -Path $path -Value $lines -Encoding Unicode

    secedit /configure /db secedit.sdb /cfg $path /areas SECURITYPOLICY

    Write-Output "Configuración de seguridad local aplicada con éxito."
} catch {
    Write-Output "Error aplicando configuración: $_"
}
