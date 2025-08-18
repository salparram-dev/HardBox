# utils/powershell_runner.py

import subprocess
import os

def run_powershell(script_path: str) -> dict:
    if not os.path.exists(script_path):
        return {"success": False, "output": f"Script no encontrado: {script_path}"}

    try:
        completed = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
            capture_output=True,
            text=True,
            timeout=120,
            check=True
        )
        return {
            "success": True,
            "output": completed.stdout.strip() or "Script ejecutado correctamente."
        }
    except subprocess.CalledProcessError as e:
        return {"success": False, "output": e.stderr.strip() or "Error al ejecutar el script."}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Timeout: El script tardó demasiado en completarse."}

def run_command(command: str) -> dict:
    """Ejecuta un comando de PowerShell directamente."""
    try:
        completed = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            timeout=120,
            check=True
        )
        output = (completed.stderr + completed.stdout).strip()
        return {
            "success": True,
            "output": output
        }
    except subprocess.CalledProcessError as e:
        return {"success": False, "output": e.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Timeout: El comando tardó demasiado en completarse."}
