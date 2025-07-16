# main.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
import os
#from utils.powershell_runner import run_powershell

SECTIONS = [
    ("Seguridad Local", "local_security"),
    ("Servicios", "services"),
    ("Windows Defender", "defender"),
    ("Acceso Remoto", "rdp"),
    ("Auditoría", "auditing"),
    ("Control USB", "usb"),
    ("Cortafuegos", "firewall"),
    ("IDS / EDR", "ids_edr")
]

SCRIPT_PATH = "scripts/powershell"

class HardBoxApp:
    def __init__(self, root):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = root
        self.root.title("HardBox - Bastionado Seguro Windows 11")
        self.root.geometry("900x650")

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill='both', expand=True, padx=10, pady=10)

        for section_name, script_name in SECTIONS:
            self.add_section(section_name, script_name)

    def add_section(self, section_title, script_base):
        tab = self.tabview.add(section_title)

        title_label = ctk.CTkLabel(tab, text=section_title, font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=15)

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
        if result["success"]:
            messagebox.showinfo("Éxito", result["output"])
        else:
            messagebox.showerror("Error", result["output"])

if __name__ == "__main__":
    root = ctk.CTk()
    app = HardBoxApp(root)
    root.mainloop()