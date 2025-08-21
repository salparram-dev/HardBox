# gui/ids_viewer.py
import customtkinter as ctk
import os, threading
from utils.powershell_runner import run_powershell, run_command
from gui.ids.snort_config_viewer import SnortConfigWindow
from gui.ids.snort_alerts_viewer import SnortAlertsWindow
import tkinter.messagebox as messagebox
import shutil
from PIL import Image
from utils.snort_utils import detect_snort_conf
from utils.logger import log_action


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


        if self.snort_instalado():
            ctk.CTkLabel(self, text="Snort está instalado y listo para usar.").pack(pady=10)

            # Botón para abrir configuración
            ctk.CTkButton(
                self,
                text="Configurar Snort",
                command=lambda: SnortConfigWindow(self)
            ).pack(pady=5)

            # Botón para abrir gestión de alertas (singleton)
            ctk.CTkButton(
                self,
                text="Gestionar alertas",
                command=self.abrir_alertas
            ).pack(pady=5)

            self.mostrar_info_snort()
        else:
            ctk.CTkLabel(self, text="Snort no está instalado.").pack(pady=10)
            instalar_btn = ctk.CTkButton(
                self,
                text="Instalar Snort",
                fg_color="#4CAF50",
                hover_color="#45A049",
                command=self.instalar_snort
            )
            instalar_btn.pack(pady=15)

    def abrir_alertas(self):
        """Abre o restaura la ventana singleton de alertas"""
        SnortAlertsWindow.open()

    def snort_instalado(self) -> bool:
        """Comprueba si Snort está disponible en el sistema."""
        result = run_command("snort -V")
        return result["success"]

    import threading

    def instalar_snort(self):
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
                            "Snort instalado correctamente.\nSe ha reemplazado el snort.conf con el personalizado."
                        ))
                    except Exception as e:
                        self.after(0, lambda: messagebox.showwarning(
                            "Aviso",
                            f"Snort instalado, pero no se pudo reemplazar snort.conf:\n{e}"
                        ))
                else:
                    self.after(0, lambda: messagebox.showwarning(
                        "Aviso",
                        "Snort instalado, pero no se encontró snort.conf para reemplazar."
                    ))

                # Recargar la ventana al terminar
                self.after(0, lambda: (self.destroy(), IDSWindow(self.master)))
            else:
                self.after(0, lambda: messagebox.showerror("Error", result["output"]))

        # Lanzar en segundo plano para no congelar la UI
        threading.Thread(target=worker, daemon=True).start()



    def mostrar_info_snort(self):
        """Muestra la información de versión de Snort."""
        result = run_command("snort -V")
        info_text = result["output"]
        text_widget = ctk.CTkTextbox(self, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", info_text)
        text_widget.configure(state="disabled")
