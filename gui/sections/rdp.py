# gui/sections/rdp.py

import customtkinter as ctk
import os
from utils.powershell_runner import run_powershell
from utils.logger import log_action

SCRIPT_PATH = "scripts/powershell"

DESCRIPTION = (
    "Esta sección permite desactivar o reactivar el acceso remoto mediante Escritorio Remoto (RDP). "
    "Se recomienda desactivar esta funcionalidad si no es estrictamente necesaria para reducir la superficie de ataque."
)

def build_section(frame: ctk.CTkFrame, script_base: str):
    title_label = ctk.CTkLabel(frame, text="Acceso Remoto (RDP)", font=ctk.CTkFont(size=20, weight="bold"))
    title_label.pack(pady=10)

    desc_label = ctk.CTkLabel(frame, text=DESCRIPTION, wraplength=600, justify="left")
    desc_label.pack(pady=(0, 15))

    button_frame = ctk.CTkFrame(frame)
    button_frame.pack(pady=10)

    def run_script(mode):
        ps1_path = os.path.join(SCRIPT_PATH, mode, f"{script_base}.ps1")
        result = run_powershell(ps1_path)
        log_action(mode.capitalize(), ps1_path, result)

        if result["success"]:
            ctk.CTkMessagebox(title="Éxito", message=result["output"], icon="check")
        else:
            ctk.CTkMessagebox(title="Error", message=result["output"], icon="cancel")

    apply_btn = ctk.CTkButton(
        button_frame,
        text="Aplicar",
        command=lambda: run_script("apply"),
        fg_color="#4CAF50",
        hover_color="#45A049"
    )
    apply_btn.pack(side="left", padx=20)

    revert_btn = ctk.CTkButton(
        button_frame,
        text="Revertir",
        command=lambda: run_script("revert"),
        fg_color="#f44336",
        hover_color="#e53935"
    )
    revert_btn.pack(side="left", padx=20)
