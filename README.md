# HardBox

HardBox es una aplicación de escritorio para Windows que integra tres componentes clave de ciberseguridad:  
- **Bastionado del sistema** mediante scripts de PowerShell.  
- **Sistema de detección de intrusos (IDS)** con Snort.  
- **Monitorización forense (EDR local)** con Velociraptor.  

El objetivo de HardBox es ofrecer una herramienta accesible para usuarios sin conocimientos técnicos avanzados, permitiendo aplicar medidas de seguridad recomendadas y monitorizar la actividad del sistema de manera sencilla, desde una interfaz gráfica en Python.

---

## ⚙️ Tecnologías utilizadas

- Python 3.11+  
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)  
- PowerShell (Windows 10/11 Pro)  
- [Snort IDS](https://www.snort.org/)  
- [Velociraptor](https://www.velocidex.com/velociraptor/)  
- [Matplotlib](https://matplotlib.org/)  
- [Oracle VirtualBox](https://www.virtualbox.org/) (entorno de pruebas)  

Opcional:  
- [VirusTotal API](https://www.virustotal.com/) para calcular la reputación de archivos a partir de su hash.  

---

## 📥 Instalación

1. **Clonar o descargar el repositorio**:  
    ```bash
    git clone https://github.com/salparram-dev/HardBox.git
    cd HardBox

2. **Instalar dependencias**:  
   ```bash
   pip install -r requirements.txt

3. **Ejecutar la aplicación en modo depuración:**: 
    ```bash
    pip install -r requirements.txt

## 🔑 Configuración opcional

Si deseas habilitar la integración con la API de VirusTotal, crea un archivo api_key.py en la carpeta resources con el siguiente contenido:
    ```bash
    VT_API_KEY = "TU_API_KEY"

## 🚀 Funcionalidades principales

- **Bastionado**: aplicación y reversión de medidas de seguridad (políticas de contraseña, RDP, servicios, cortafuegos, auditoría, etc.).
- **Snort IDS**: instalación guiada, gestión de reglas y visualización de alertas en tiempo real.
- **Velociraptor (EDR local)**: consultas VQL sobre usuarios, procesos, servicios, conexiones y archivos recientes, con gráficos y opción de cálculo de hashes + reputación en VirusTotal.
- **Logs centralizados**: todas las acciones quedan registradas para trazabilidad y auditoría.
- **Backups automáticos**: posibilidad de revertir cualquier cambio aplicado desde la interfaz.

## 📄 Licencia

Este proyecto se distribuye bajo licencia MIT.