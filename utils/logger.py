# utils/logger.py

import json
from datetime import datetime
import os

LOG_PATH = "logs/hardbox_actions.log"

def log_action(action_type: str, script_path: str, result: dict) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action_type,  # "Aplicar" o "Revertir"
        "script": script_path,
        "success": result.get("success", False),
        "message": result.get("output", "")
    }

    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry, ensure_ascii=False) + "\n")