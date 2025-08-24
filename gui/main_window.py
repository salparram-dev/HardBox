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
from gui.edr.edr_viewer import EDRWindow
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

        # --- Navegación superior con SegmentedButton ---
        self.top_nav = ctk.CTkSegmentedButton(
            self.root,
            values=["🛡️ EDR", "🔍 IDS", "⚙ Acciones"],
            command=self.handle_top_nav,
            width=500
        )
        self.top_nav.place(relx=1.0, rely=0.0, x=-20, y=10, anchor="ne")
        #self.top_nav.set("⚙ Acciones")  # por defecto


        for section_name, script_name in SECTIONS:
            self.add_section(section_name, script_name)
    
    def handle_top_nav(self, choice):
        if choice == "⚙ Acciones":
            self.abrir_logs()
        elif choice == "🔍 IDS":
            self.abrir_ids()
        elif choice == "🛡️ EDR":
            self.abrir_edr()

    def abrir_logs(self):
        win = LogViewerWindow(self.root)
        win.protocol("WM_DELETE_WINDOW", lambda: (self.top_nav.set(""), win.destroy()))
    
    def abrir_edr(self):
        win = EDRWindow(self.root)
        win.protocol("WM_DELETE_WINDOW", lambda: (self.top_nav.set(""), win.destroy()))

    def abrir_ids(self):
        win = IDSWindow(self.root)
        win.protocol("WM_DELETE_WINDOW", lambda: (self.top_nav.set(""), win.destroy()))

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
        if mode == "apply":
            log_action("Aplicar", ps1_path, result)
        elif mode == "revert":
            log_action("Revertir", ps1_path, result)

        if result["success"]:
            messagebox.showinfo("Éxito", result["output"])
        else:
            messagebox.showerror("Error", result["output"])

if __name__ == "__main__":
    root = ctk.CTk()
    app = HardBoxApp(root)
    root.mainloop()
