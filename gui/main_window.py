# main_window.py
import ctypes, sys

# Si no somos admin, reiniciamos el script Python con privilegios elevados
def elevar_privilegios():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join([f'"{arg}"' for arg in sys.argv]),
            None,
            1
        )
        sys.exit(0)

elevar_privilegios()

import customtkinter as ctk
import tkinter.messagebox as messagebox
import os
from PIL import Image
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.powershell_runner import run_powershell
from utils.logger import log_action
from gui.log_viewer import LogViewerWindow
from gui.ids.ids_viewer import IDSWindow
from gui.sections import SECTIONS, DESCRIPTIONS, IMAGES

SCRIPT_PATH = "scripts/powershell"

class HardBoxApp:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = root
        self.root.title("HardBox - Bastionado Seguro Windows 11")
        self.root.geometry("1500x750")

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill='both', expand=True, padx=10, pady=10)

        log_btn = ctk.CTkButton(self.root, text="⚙ Logs", width=90, command=self.abrir_logs)
        log_btn.place(relx=1.0, rely=0.0, x=-110, y=10, anchor="ne")

        ids_btn = ctk.CTkButton(self.root, text="🔍 IDS (Snort)", width=120, command=self.abrir_ids)
        ids_btn.place(relx=1.0, rely=0.0, x=-240, y=10, anchor="ne")

        for section_name, script_name in SECTIONS:
            self.add_section(section_name, script_name)

    def abrir_logs(self):
        LogViewerWindow(self.root)
    
    def abrir_ids(self):
        IDSWindow(self.root)

    def add_section(self, section_title, script_base):
        tab = self.tabview.add(section_title)

        title_label = ctk.CTkLabel(tab, text=section_title, font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=15)

        image_path = IMAGES.get(script_base)
        if image_path and os.path.exists(image_path):
            img = ctk.CTkImage(light_image=Image.open(image_path), size=(70, 70))
            img_label = ctk.CTkLabel(tab, image=img, text="")
            img_label.pack(pady=(0, 10))

        desc_label = ctk.CTkLabel(tab, text=DESCRIPTIONS.get(script_base, ""), wraplength=600, justify="left")
        desc_label.pack(pady=(0, 15))

        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(pady=10)

        apply_btn = ctk.CTkButton(
            button_frame,
            text="Aplicar",
            command=lambda: self.run_script("apply", script_base),
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        apply_btn.pack(side="left", padx=20)

        revert_btn = ctk.CTkButton(
            button_frame,
            text="Revertir",
            command=lambda: self.run_script("revert", script_base),
            fg_color="#f44336",
            hover_color="#e53935"
        )
        revert_btn.pack(side="left", padx=20)

    def run_script(self, mode, base_name):
        ps1_path = os.path.join(SCRIPT_PATH, mode, f"{base_name}.ps1")
        result = run_powershell(ps1_path)
        log_action(mode.capitalize(), ps1_path, result)
        if result["success"]:
            messagebox.showinfo("Éxito", result["output"])
        else:
            messagebox.showerror("Error", result["output"])

if __name__ == "__main__":
    root = ctk.CTk()
    app = HardBoxApp(root)
    root.mainloop()
