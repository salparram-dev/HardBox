import customtkinter as ctk
import os
from utils.powershell_runner import run_powershell
from utils.logger import log_action
import tkinter.messagebox as messagebox

SCRIPT_PATH = "scripts/powershell"

DESCRIPTION = (
    "Aquí se describe claramente qué hace esta sección. "
    "Explica al usuario final qué se va a modificar en el sistema cuando aplique o revierta esta configuración."
)

def build_section(frame: ctk.CTkFrame, script_base: str):
    # Título
    title_label = ctk.CTkLabel(frame, text=script_base.replace("_", " ").title(), font=ctk.CTkFont(size=20, weight="bold"))
    title_label.pack(pady=10)

    # Descripción
    desc_label = ctk.CTkLabel(frame, text=DESCRIPTION, wraplength=600, justify="left")
    desc_label.pack(pady=(0, 15))

    # Botones
    button_frame = ctk.CTkFrame(frame)
    button_frame.pack(pady=10)

    def run_script(mode):
        ps1_path = os.path.join(SCRIPT_PATH, mode, f"{script_base}.ps1")
        result = run_powershell(ps1_path)
        log_action(mode.capitalize(), ps1_path, result)

        if result["success"]:
            messagebox.showinfo("Éxito", result["output"])
        else:
            messagebox.showerror("Error", result["output"])

    apply_btn = ctk.CTkButton(
        button_frame, text="Aplicar", command=lambda: run_script("apply"),
        fg_color="#4CAF50", hover_color="#45A049"
    )
    apply_btn.pack(side="left", padx=20)

    revert_btn = ctk.CTkButton(
        button_frame, text="Revertir", command=lambda: run_script("revert"),
        fg_color="#f44336", hover_color="#e53935"
    )
    revert_btn.pack(side="left", padx=20)
