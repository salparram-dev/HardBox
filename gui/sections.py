# gui/sections.py

SECTIONS = [
    ("Seguridad Local", "local_security"),
    ("Servicios", "services"),
    ("Windows Defender", "defender"),
    ("Acceso Remoto", "rdp"),
    ("Auditoría", "auditing"),
    ("Control USB", "usb"),
    ("Cortafuegos", "firewall"),
]

BACKUPS = {
    "local_security": "C:/ProgramData/HardBoxBackup/sec_backup.inf",
    "services": "C:/ProgramData/HardBoxBackup/services_state_backup.json",
    "defender": "C:/ProgramData/HardBoxBackup/defender_state_backup.json",
    "auditing" : "C:/ProgramData/HardBoxBackup/audit_backup.csv"
}

DESCRIPTIONS = {
    "local_security": "Refuerza las reglas de contraseñas: mínimo de caracteres, complejidad, historial y bloqueo tras intentos fallidos.",
    "services": "Desactiva servicios innecesarios para reducir riesgos de seguridad sin afectar el uso diario.",
    "defender": "Configura Windows Defender con opciones recomendadas para reforzar la detección de amenazas.",
    "rdp": "Desactiva el acceso por Escritorio Remoto para evitar conexiones no autorizadas desde otros equipos.",
    "auditing": "Activa registros de actividad clave como inicios de sesión, bloqueos y cambios de configuración.",
    "usb": "Restringe el uso de dispositivos USB para evitar robo de información o infecciones por malware.",
    "firewall": "Activa y configura correctamente el cortafuegos de Windows para bloquear conexiones no seguras."
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
