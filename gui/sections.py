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
    "auditing" : "C:/ProgramData/HardBoxBackup/audit_backup.csv",
    "usb": "C:/ProgramData/HardBoxBackup/usb_backup.json",
    "firewall": "C:/ProgramData/HardBoxBackup/firewall_backup.json", 
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

PARAMETERS = {
    "local_security": [
        {"name": "MinimumPasswordLength", "label": "Longitud mínima de contraseña", "default": 10, "type": "text"},
        {"name": "PasswordComplexity", "label": "Complejidad", "default": True, "type": "bool"},
        {"name": "MaximumPasswordAge", "label": "Máx. días de validez", "default": 60, "type": "text"},
        {"name": "MinimumPasswordAge", "label": "Mín. días antes de cambiar", "default": 1, "type": "text"},
        {"name": "PasswordHistorySize", "label": "Historial de contraseñas", "default": 10, "type": "text"},
        {"name": "LockoutBadCount", "label": "Intentos fallidos antes de bloqueo", "default": 5, "type": "text"},
        {"name": "ResetLockoutCount", "label": "Minutos para reiniciar contador", "default": 15, "type": "text"},
        {"name": "LockoutDuration", "label": "Duración del bloqueo (min)", "default": 15, "type": "text"}
    ],

    "services": [
        {"name": "Fax", "label": "Fax"},
        {"name": "RemoteRegistry", "label": "Registro remoto"},
        {"name": "XblGameSave", "label": "Xbox Live Game Save"},
        {"name": "WSearch", "label": "Búsqueda de Windows"},
        {"name": "DiagTrack", "label": "Experiencias de usuario y telemetría"},
        {"name": "MapsBroker", "label": "Servicio de descarga de mapas"},
        {"name": "SharedAccess", "label": "Conexión compartida a Internet"},
        {"name": "BluetoothSupportService", "label": "Soporte de Bluetooth"},
        {"name": "RetailDemo", "label": "Modo demostración de venta"}
    ],
    "defender": [
        {
            "name": "DisableRealtimeMonitoring",
            "label": "Deshabilitar Protección en tiempo real",
            "default": False,
            "type": "bool",
            "readonly": True,  # <- no editable
            "note": "Por motivos de seguridad según Microsoft, no se puede desactivar."
        },
        {
            "name": "MAPSReporting",
            "label": "Nivel de MAPS",
            "default": 2,
            "type": "choice",
            "choices": {
                "Deshabilitado": 0,
                "Básico": 1,
                "Avanzado": 2
            }
        },
        {
            "name": "SubmitSamplesConsent",
            "label": "Envío de muestras",
            "default": 1,
            "type": "choice",
            "choices": {
                "Nunca": 0,
                "Solo seguras": 1,
                "Preguntar": 2,
                "Siempre": 3
            }
        },
        {
            "name": "PUAProtection",
            "label": "Protección contra aplicaciones potencialmente no deseadas",
            "default": 1,
            "type": "choice",
            "choices": {
                "Deshabilitado": 0,
                "Habilitado (bloqueo)": 1,
                "Solo auditoría": 2
            }
        }
    ],
    "auditing": [
        {
            "name": "Logon",
            "label": "Inicio de sesión",
            "default": "both",
            "type": "choice",
            "choices": {
                "Sin auditoría": "none",
                "Aciertos": "success",
                "Errores": "failure",
                "Aciertos y errores": "both"
            }
        },
        {
            "name": "Logoff",
            "label": "Cerrar sesión",
            "default": "both",
            "type": "choice",
            "choices": {
                "Sin auditoría": "none",
                "Aciertos": "success",
                "Errores": "failure",
                "Aciertos y errores": "both"
            }
        },
        {
            "name": "AccountLockout",
            "label": "Bloqueo de cuenta",
            "default": "both",
            "type": "choice",
            "choices": {
                "Sin auditoría": "none",
                "Aciertos": "success",
                "Errores": "failure",
                "Aciertos y errores": "both"
            }
        },
        {
            "name": "SecurityStateChange",
            "label": "Cambio de estado de seguridad",
            "default": "both",
            "type": "choice",
            "choices": {
                "Sin auditoría": "none",
                "Aciertos": "success",
                "Errores": "failure",
                "Aciertos y errores": "both"
            }
        },
        {
            "name": "AuditPolicyChange",
            "label": "Cambio en la directiva de auditoría",
            "default": "both",
            "type": "choice",
            "choices": {
                "Sin auditoría": "none",
                "Aciertos": "success",
                "Errores": "failure",
                "Aciertos y errores": "both"
            }
        },
        {
            "name": "AuthenticationPolicyChange",
            "label": "Cambio de la directiva de autenticación",
            "default": "both",
            "type": "choice",
            "choices": {
                "Sin auditoría": "none",
                "Aciertos": "success",
                "Errores": "failure",
                "Aciertos y errores": "both"
            }
        },
        {
            "name": "UserAccountManagement",
            "label": "Administración de cuentas de usuario",
            "default": "both",
            "type": "choice",
            "choices": {
                "Sin auditoría": "none",
                "Aciertos": "success",
                "Errores": "failure",
                "Aciertos y errores": "both"
            }
        },
        {
            "name": "SecurityGroupManagement",
            "label": "Administración de grupos de seguridad",
            "default": "both",
            "type": "choice",
            "choices": {
                "Sin auditoría": "none",
                "Aciertos": "success",
                "Errores": "failure",
                "Aciertos y errores": "both"
            }
        },
        {
            "name": "SystemIntegrity",
            "label": "Integridad del sistema",
            "default": "both",
            "type": "choice",
            "choices": {
                "Sin auditoría": "none",
                "Aciertos": "success",
                "Errores": "failure",
                "Aciertos y errores": "both"
            }
        }
    ],
    "usb": [
        {
            "name": "UsbMode",
            "label": "Modo de almacenamiento USB",
            "default": "disabled",
            "type": "choice",
            "choices": {
                "Deshabilitado": "disabled",
                "Manual (habilitado bajo demanda)": "manual",
                "Automático (siempre habilitado)": "automatic"
            }
        }
    ],
    "firewall": [
        # Perfil de dominio
        {
            "name": "DomainEnabled",
            "label": "Firewall de dominio",
            "default": True,
            "type": "bool"
        },
        {
            "name": "DomainInbound",
            "label": "Acción de entrada (Dominio)",
            "default": "Block",
            "type": "choice",
            "choices": {
                "Bloquear": "Block",
                "Permitir": "Allow"
            }
        },
        {
            "name": "DomainOutbound",
            "label": "Acción de salida (Dominio)",
            "default": "Allow",
            "type": "choice",
            "choices": {
                "Permitir": "Allow",
                "Bloquear": "Block"
            }
        },

        # Perfil privado
        {
            "name": "PrivateEnabled",
            "label": "Firewall privado",
            "default": True,
            "type": "bool"
        },
        {
            "name": "PrivateInbound",
            "label": "Acción de entrada (Privado)",
            "default": "Block",
            "type": "choice",
            "choices": {
                "Bloquear": "Block",
                "Permitir": "Allow"
            }
        },
        {
            "name": "PrivateOutbound",
            "label": "Acción de salida (Privado)",
            "default": "Allow",
            "type": "choice",
            "choices": {
                "Permitir": "Allow",
                "Bloquear": "Block"
            }
        },

        # Perfil público
        {
            "name": "PublicEnabled",
            "label": "Firewall público",
            "default": True,
            "type": "bool"
        },
        {
            "name": "PublicInbound",
            "label": "Acción de entrada (Público)",
            "default": "Block",
            "type": "choice",
            "choices": {
                "Bloquear": "Block",
                "Permitir": "Allow"
            }
        },
        {
            "name": "PublicOutbound",
            "label": "Acción de salida (Público)",
            "default": "Allow",
            "type": "choice",
            "choices": {
                "Permitir": "Allow",
                "Bloquear": "Block"
            }
        }
    ]
    
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
