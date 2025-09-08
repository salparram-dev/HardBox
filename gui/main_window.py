# main_window.py
import ctypes, sys

# Si no somos admin, reiniciamos el script Python con privilegios elevados
def elevate_privileges():
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

elevate_privileges()

import customtkinter as ctk
import tkinter.messagebox as messagebox
import os
from PIL import Image
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.powershell_runner import run_powershell
from gui.parameter_form import ParameterForm
from utils.logger import log_action
from gui.log_viewer import LogViewerWindow
from gui.edr.edr_viewer import EDRWindow
from gui.ids.ids_viewer import IDSWindow
from gui.sections import SECTIONS, BACKUPS, DESCRIPTIONS, PARAMETERS, IMAGES
from utils.window_utils import top_focus, ensure_icon

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
            values=["🛡️ EDR", "🔍 IDS", "📜 Acciones"],
            command=self.handle_top_nav,
            width=500
        )
        self.top_nav.place(relx=1.0, rely=0.0, x=-20, y=10, anchor="ne")

        for section_name, script_name in SECTIONS:
            self.add_section(section_name, script_name)
    
    def handle_top_nav(self, choice):
        if choice == "📜 Acciones":
            self.open_logs()
        elif choice == "🔍 IDS":
             if messagebox.askyesno("Opciones avanzadas", "Esta sección es para usuarios avanzados. ¿Quieres continuar?"):
                self.open_ids()
        elif choice == "🛡️ EDR":
            if messagebox.askyesno("Opciones avanzadas", "Esta sección es para usuarios avanzados. ¿Quieres continuar?"):
                self.open_edr()

    def open_logs(self):
        win = LogViewerWindow(self.root)
        ensure_icon(win)
        top_focus(win)
        win.after(200, lambda: win.attributes('-topmost', False))  # quita el "siempre encima"
        win.protocol("WM_DELETE_WINDOW", lambda: (self.top_nav.set(""), win.destroy()))
    
    def open_edr(self):
        win = EDRWindow(self.root)
        ensure_icon(win)
        top_focus(win)
        win.after(200, lambda: win.attributes('-topmost', False))  # quita el "siempre encima"
        win.protocol("WM_DELETE_WINDOW", lambda: (self.top_nav.set(""), win.destroy()))

    def open_ids(self):
        win = IDSWindow(self.root)
        ensure_icon(win)
        top_focus(win)
        win.after(200, lambda: win.attributes('-topmost', False))  # quita el "siempre encima"
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
        result = None

        def execute_with_params(params_dict):
            # Construir lista de parámetros para PowerShell
            ps_params = []
            for k, v in params_dict.items():
                ps_params.extend([f"-{k}", str(v)])

            # Comprobar backup
            backup_path = BACKUPS.get(base_name, "")
            if os.path.exists(backup_path):
                overwrite = messagebox.askyesno(
                    "Backup existente",
                    f"Ya existe un backup en:\n{backup_path}\n\n¿Quieres sobrescribirlo con uno nuevo?"
                )
                if overwrite:
                    ps_params.append("-ForceBackup")

            # Ejecutar script con parámetros
            result_local = run_powershell(ps1_path, ps_params)
            log_action("Aplicar", ps1_path, result_local)

            # Mostrar resultado
            if result_local.get("success"):
                messagebox.showinfo("Éxito", "Los cambios se aplicaron con éxito.")
            else:
                messagebox.showerror("Error", "Error al aplicar los cambios.")

        if mode == "apply":
            # Si la sección tiene parámetros configurables, abrir formulario
            if base_name in PARAMETERS:
                win = ParameterForm(self.root, base_name, PARAMETERS[base_name], execute_with_params, sections_list=SECTIONS)
                ensure_icon(win)
            else:
                # Comportamiento actual sin formulario
                backup_path = BACKUPS.get(base_name, "")
                if os.path.exists(backup_path):
                    overwrite = messagebox.askyesno(
                        "Backup existente",
                        f"Ya existe un backup en:\n{backup_path}\n\n¿Quieres sobrescribirlo con uno nuevo?"
                    )
                    params = ["-ForceBackup"] if overwrite else None
                    result = run_powershell(ps1_path, params)
                else:
                    result = run_powershell(ps1_path)

                log_action("Aplicar", ps1_path, result)

                if result.get("success"):
                    messagebox.showinfo("Éxito", "Los cambios se aplicaron con éxito.")
                else:
                    messagebox.showerror("Error", "Error al aplicar los cambios.")

        elif mode == "revert":
            result = run_powershell(ps1_path)
            log_action("Revertir", ps1_path, result)

            if result.get("success"):
                messagebox.showinfo("Éxito", "Los cambios se aplicaron con éxito.")
            else:
                messagebox.showerror("Error", "Error al aplicar los cambios.")


if __name__ == "__main__":
    root = ctk.CTk()
    ensure_icon(root)
    app = HardBoxApp(root)
    root.mainloop()
