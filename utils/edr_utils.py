# utils/edr_utils.py
import requests
from resources.api_key import VT_API_KEY

def get_reputation(sha256_hash):
    """
    Consulta la reputación de un hash en VirusTotal.
    Devuelve un string con el resumen.
    """
    url = f"https://www.virustotal.com/api/v3/files/{sha256_hash}"
    headers = {
        "x-apikey": VT_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            stats = data["data"]["attributes"]["last_analysis_stats"]
            total_detections = stats["malicious"]
            total_engines = sum(stats.values())

            reputation = f"Reputación en VirusTotal:\n" \
                         f" - Motores que lo detectan como malicioso: {total_detections}/{total_engines}\n"

            vt_link = f"https://www.virustotal.com/gui/file/{sha256_hash}"
            reputation += f" - Ver en VT: {vt_link}"

            return reputation
        elif response.status_code == 404:
            return "No hay información en VirusTotal para este hash."
        else:
            return f"Error consultando VirusTotal: {response.status_code}"
    except Exception as e:
        return f"Error inesperado en la consulta a VirusTotal. Pruebe de nuevo"