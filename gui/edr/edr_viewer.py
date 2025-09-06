# gui/edr/edr_viewer.py
import customtkinter as ctk
import os
import tkinter.messagebox as messagebox
import threading
from PIL import Image
from utils.powershell_runner import run_powershell, run_command
from gui.edr.edr_service_viewer import VelociraptorServiceWindow
from utils.logger import log_action
from utils.window_utils import top_focus

SCRIPT_PATH = "scripts/powershell"

class EDRWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("EDR - Velociraptor")
        self.geometry("800x600")

        ctk.CTkLabel(
            self,
            text="Velociraptor - Endpoint Detection & Response",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        image_path = os.path.join("assets", "images" ,"velociraptor.png")
        if os.path.exists(image_path):
            edr_img = ctk.CTkImage(Image.open(image_path), size=(205, 166))
            ctk.CTkLabel(self, image=edr_img, text="").pack(pady=10)
        

        if self.is_installed():
            ctk.CTkLabel(self, text="Velociraptor está instalado y listo para usar.").pack(pady=10)

            ctk.CTkButton(
                self,
                text="Gestionar servicio",
                command=self.manage_service
            ).pack(pady=5)

            self.show_info()
        else:
            ctk.CTkLabel(self, text="Velociraptor no está instalado.").pack(pady=10)
            install_btn = ctk.CTkButton(
                self,
                text="Instalar Velociraptor",
                fg_color="#4CAF50",
                hover_color="#45A049",
                command=self.install
            )
            install_btn.pack(pady=15)

    def is_installed(self) -> bool:
        """Comprueba si Velociraptor está disponible en el sistema."""
        result = run_command("velociraptor version")
        return result["success"]

    def install(self):
        """Ejecuta el script PowerShell para instalar Velociraptor y reemplaza client.config.yaml por el personalizado."""
        def worker():
            ps1_path = os.path.join(SCRIPT_PATH, "install", "install_velociraptor.ps1")
            result = run_powershell(ps1_path)
            log_action("Velociraptor-Instalar", ps1_path, result)

            if result["success"]:
                self.after(0, lambda: messagebox.showinfo(
                    "Instalación",
                    f"Velociraptor instalado correctamente.\n"
                ))
                # Recargar ventana
                self.after(0, lambda: (self.destroy(), EDRWindow(self.master)))
            else:
                self.after(0, lambda: messagebox.showerror("Error", result["output"]))

        # Lanzar en segundo plano para no congelar la UI
        threading.Thread(target=worker, daemon=True).start()

    def manage_service(self):
        """Abre la ventana independiente de gestión de servicio Velociraptor"""
        win = VelociraptorServiceWindow.open() 
        top_focus(win)

    def show_info(self):
        """Muestra información de la versión de Velociraptor."""
        result = run_command("velociraptor version")
        info_text = result["output"]
        text_widget = ctk.CTkTextbox(self, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", info_text)
        text_widget.configure(state="disabled")
