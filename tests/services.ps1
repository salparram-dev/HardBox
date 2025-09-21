$services = @(
    "Fax",
    "RemoteRegistry",
    "XblGameSave",
    "WSearch",
    "DiagTrack",
    "MapsBroker",
    "SharedAccess",
    "BluetoothSupportService",
    "RetailDemo"
)

foreach ($svc in $services) {
    if (Get-Service -Name $svc -ErrorAction SilentlyContinue) {
        $s = Get-Service -Name $svc
        Write-Output "$($s.Name): $($s.Status) | StartupType: $(Get-CimInstance -ClassName Win32_Service -Filter "Name='$svc'" | Select-Object -ExpandProperty StartMode)"
    } else {
        Write-Output "${svc}: No encontrado"
    }
}
