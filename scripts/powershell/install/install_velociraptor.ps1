# scripts/powershell/install/install_velociraptor.ps1
# Instalador automatizado de Velociraptor EDR en modo standalone

$ErrorActionPreference = "Stop"

Write-Host "=== Instalación de Velociraptor EDR (Standalone) ===" -ForegroundColor Cyan

# Ruta de instalación por defecto
$installDir = "C:\Program Files\Velociraptor"
$exePath    = Join-Path $installDir "Velociraptor.exe"

# Ruta del instalador MSI (lo dejas en scripts/msi/)
$scriptDir     = Split-Path -Parent $MyInvocation.MyCommand.Definition
$basePath      = Split-Path -Parent (Split-Path -Parent $scriptDir)
$installerDir  = Join-Path $basePath "msi"
$msiInstaller  = Join-Path $installerDir "install\velociraptor-v0.74.5-windows-amd64.msi"

# Comprobar si ya está instalado
if (Test-Path $exePath) {
    Write-Host "Velociraptor ya está instalado en $installDir" -ForegroundColor Yellow
    exit 0
}

if (!(Test-Path $msiInstaller)) {
    Write-Error "No se encontró el instalador en: $msiInstaller"
    exit 1
}

Write-Host "Instalando Velociraptor desde $msiInstaller..." -ForegroundColor Green

# Instalar en modo silencioso
Start-Process "msiexec.exe" -ArgumentList "/i `"$msiInstaller`" /quiet /norestart" -Wait -NoNewWindow

# Verificar instalación
if (!(Test-Path $exePath)) {
    Write-Error "Error: No se encontró Velociraptor tras la instalación."
    exit 1
}

Write-Host "Velociraptor instalado correctamente en $installDir" -ForegroundColor Green

# (Opcional) Copiar config personalizada si existe
$customConfig = Join-Path $basePath "resources\client.config.yaml"
if (Test-Path $customConfig) {
    Copy-Item $customConfig (Join-Path $installDir "client.config.yaml") -Force
    Write-Host "Se aplicó configuración personalizada desde resources/client.config.yaml" -ForegroundColor Cyan
}

# === Añadir al PATH del sistema ===
$envPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
if ($envPath -notlike "*$installDir*") {
    [System.Environment]::SetEnvironmentVariable(
        "Path",
        "$envPath;$installDir",
        "Machine"
    )
    Write-Host "Se añadió $installDir al PATH del sistema. (Reinicia la terminal para usar 'velociraptor' directamente)" -ForegroundColor Cyan
}

exit 0
