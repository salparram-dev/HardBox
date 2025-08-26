# gui/ids_viewer.py
import customtkinter as ctk
import os, threading
from utils.powershell_runner import run_powershell, run_command
from gui.ids.ids_config_viewer import SnortConfigWindow
from gui.ids.ids_alerts_viewer import SnortAlertsWindow
import tkinter.messagebox as messagebox
import shutil
from PIL import Image
from utils.ids_utils import detect_snort_conf
from utils.logger import log_action
from utils.window_utils import top_focus

SCRIPT_PATH = "scripts/powershell"

class IDSWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("IDS - Snort")
        self.geometry("800x600")

        ctk.CTkLabel(
            self,
            text="Snort - Sistema de Detección de Intrusos",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        image_path = os.path.join("assets", "images" ,"snort.png")
        if os.path.exists(image_path):
            snort_img = ctk.CTkImage(Image.open(image_path), size=(150, 150))
            ctk.CTkLabel(self, image=snort_img, text="").pack(pady=10)


        if self.is_installed():
            ctk.CTkLabel(self, text="Snort está instalado y listo para usar.").pack(pady=10)

            # Botón para abrir configuración
            ctk.CTkButton(
                self,
                text="Configurar Snort",
                command=self.open_config
            ).pack(pady=5)

            # Botón para abrir gestión de alertas (singleton)
            ctk.CTkButton(
                self,
                text="Gestionar alertas",
                command=self.open_alerts
            ).pack(pady=5)

            self.show_info()
        else:
            ctk.CTkLabel(self, text="Snort no está instalado.").pack(pady=10)
            install_btn = ctk.CTkButton(
                self,
                text="Instalar Snort",
                fg_color="#4CAF50",
                hover_color="#45A049",
                command=self.install
            )
            install_btn.pack(pady=15)

    def open_config(self):
        """Abre la ventana de configuración"""
        win = SnortConfigWindow(self)
        top_focus(win)

    def open_alerts(self):
        """Abre o restaura la ventana singleton de alertas"""
        win = SnortAlertsWindow.open()
        top_focus(win)

    def is_installed(self) -> bool:
        """Comprueba si Snort está disponible en el sistema."""
        result = run_command("snort -V")
        return result["success"]

    def install(self):
        """Ejecuta el script PowerShell para instalar Snort y reemplaza snort.conf por el personalizado."""
        def worker():
            ps1_path = os.path.join(SCRIPT_PATH, "install", "install_snort.ps1")
            result = run_powershell(ps1_path)
            log_action("Snort-Instalar", ps1_path, result)

            if result["success"]:
                conf_path = detect_snort_conf()
                if conf_path:
                    try:
                        custom_conf = os.path.join("resources", "snort.conf")
                        shutil.copyfile(custom_conf, conf_path)
                        self.after(0, lambda: messagebox.showinfo(
                            "Instalación",
                            "Snort instalado correctamente.\nSe ha reemplazado el snort.conf con el personalizado.",
                            parent=self
                        ))
                    except Exception as e:
                        self.after(0, lambda: messagebox.showwarning(
                            "Aviso",
                            f"Snort instalado, pero no se pudo reemplazar snort.conf:\n{e}",
                            parent=self
                        ))
                else:
                    self.after(0, lambda: messagebox.showwarning(
                        "Aviso",
                        "Snort instalado, pero no se encontró snort.conf para reemplazar.",
                        parent=self
                    ))

                # Recargar la ventana al terminar
                self.after(0, lambda: (self.destroy(), IDSWindow(self.master)))
            else:
                self.after(0, lambda: messagebox.showerror("Error", result["output"], parent=self))

        # Lanzar en segundo plano para no congelar la UI
        threading.Thread(target=worker, daemon=True).start()

    def show_info(self):
        """Muestra la información de versión de Snort."""
        result = run_command("snort -V")
        info_text = result["output"]
        text_widget = ctk.CTkTextbox(self, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", info_text)
        text_widget.configure(state="disabled")
