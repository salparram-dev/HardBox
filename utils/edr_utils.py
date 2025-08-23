# utils/snort_utils.py
import os

def detect_config_file():
    """Detecta la ruta de server.config.yaml automáticamente"""
    possible_paths = [
        r"C:\Program Files\Velociraptor\server.config.yaml",
        r"C:\Archivos de programa\Velociraptor\server.config.yaml",
        r"C:\Velociraptor\server.config.yaml"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None