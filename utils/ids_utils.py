# utils/snort_utils.py
import os

def detect_snort_conf():
    possible_paths = [
        r"C:\Snort\etc\snort.conf",
        r"C:\Program Files\Snort\etc\snort.conf",
        r"C:\Program Files (x86)\Snort\etc\snort.conf"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def detect_local_rules():
    possible_paths = [
        r"C:\Snort\rules\local.rules",
        r"C:\Program Files\Snort\rules\local.rules",
        r"C:\Program Files (x86)\Snort\rules\local.rules"
    ]
    for path in possible_paths:
        folder = os.path.dirname(path)
        if os.path.exists(folder):
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write("# Reglas locales de Snort\n")
            return path
    return None

def detect_alert_file():
    possible_paths = [
        r"C:\Snort\log\alert.ids",
        r"C:\Program Files\Snort\log\alert.ids",
        r"C:\Program Files (x86)\Snort\log\alert.ids"
    ]
    for path in possible_paths:
        folder = os.path.dirname(path)
        if os.path.exists(folder):
            return path
    return None
