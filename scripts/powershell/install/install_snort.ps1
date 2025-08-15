# scripts/powershell/install/install_snort.ps1
# Instala Npcap y Snort mostrando asistentes, y añade Snort al PATH

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$basePath  = Split-Path -Parent (Split-Path -Parent $scriptDir)

# Ruta a la carpeta exe
$exePath = Join-Path $basePath "exe"

Write-Host "Ruta exePath detectada: $exePath"

function Snort-Installed {
    try {
        snort -V | Out-Null
        return $true
    } catch {
        return $false
    }
}

Write-Host "Instalando Npcap..."
$npcapInstaller = Join-Path $exePath "install/npcap-1.83.exe"
if (-Not (Test-Path $npcapInstaller)) {
    Write-Error "No se encontró el instalador de Npcap en: $npcapInstaller"
    exit 1
}
# Ejecuta instalación con ventana interactiva
Start-Process -FilePath $npcapInstaller -Wait

Write-Host "Instalando Snort..."
$snortInstaller = Join-Path $exePath "install/Snort_2_9_20_Installer.x64.exe"
if (-Not (Test-Path $snortInstaller)) {
    Write-Error "No se encontró el instalador de Snort en: $snortInstaller"
    exit 1
}
# Ejecuta instalación de forma silenciosa
Start-Process -FilePath $snortInstaller -ArgumentList "/S" -Wait

# Añadir Snort al PATH si está instalado
$possiblePaths = @(
    "C:\Snort\bin",
    "C:\Program Files\Snort\bin",
    "C:\Program Files (x86)\Snort\bin"
)

$snortPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $snortPath = $path
        break
    }
}

if ($snortPath) {
    Write-Host "Añadiendo Snort al PATH del sistema: $snortPath"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$snortPath*") {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentPath;$snortPath",
            "Machine"
        )
        Write-Host "PATH actualizado. Es posible que necesite reiniciar la sesión para que los cambios surtan efecto."
    }
}

if (Snort-Installed) {
    Write-Host "Snort instalado y disponible."
} else {
    Write-Error "No se pudo instalar o detectar Snort."
}
