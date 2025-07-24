# gui/sections.py

SECTIONS = [
    ("Seguridad Local", "local_security"),
    ("Servicios", "services"),
    ("Windows Defender", "defender"),
    ("Acceso Remoto", "rdp"),
    ("Auditoría", "auditing"),
    ("Control USB", "usb"),
    ("Cortafuegos", "firewall"),
    ("IDS / EDR", "ids_edr")
]

DESCRIPTIONS = {
    "local_security": "Aplica medidas como contraseñas seguras, bloqueo de sesión y configuración de cuentas.",
    "services": "Desactiva servicios innecesarios para reducir la superficie de exposición del sistema.",
    "defender": "Configura Windows Defender con ajustes recomendados por el CCN para proteger contra malware.",
    "rdp": "Desactiva el acceso remoto al sistema mediante Escritorio Remoto para evitar conexiones no autorizadas.",
    "auditing": "Activa auditoría de seguridad para registrar eventos críticos y cambios en el sistema.",
    "usb": "Restringe el uso de dispositivos USB para prevenir la extracción de datos o infecciones.",
    "firewall": "Aplica una plantilla segura al cortafuegos de Windows para controlar el tráfico entrante y saliente.",
    "ids_edr": "Permite activar Snort (IDS) y Velociraptor (EDR) para detección de amenazas y respuesta."
}

IMAGES = {
    "local_security": "assets/images/local_security.png",
    "services": "assets/images/services.png",
    "defender": "assets/images/defender.png",
    "rdp": "assets/images/rdp.png",
    "auditing": "assets/images/auditing.png",
    "usb": "assets/images/usb.png",
    "firewall": "assets/images/firewall.png",
    "ids_edr": "assets/images/ids_edr.png"
}