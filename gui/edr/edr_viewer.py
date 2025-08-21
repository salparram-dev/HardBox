import customtkinter as ctk
import os
import shutil
import tkinter.messagebox as messagebox
from PIL import Image
from utils.powershell_runner import run_powershell, run_command
from utils.logger import log_action

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
        

        if self.velociraptor_instalado():
            ctk.CTkLabel(self, text="Velociraptor está instalado y listo para usar.").pack(pady=10)

            ctk.CTkButton(
                self,
                text="Configurar Velociraptor",
                command=self.configurar_velociraptor
            ).pack(pady=5)

            ctk.CTkButton(
                self,
                text="Gestionar servicio",
                fg_color="#FF9800",
                hover_color="#F57C00",
                command=self.gestionar_servicio
            ).pack(pady=5)

            self.mostrar_info_velociraptor()
        else:
            ctk.CTkLabel(self, text="Velociraptor no está instalado.").pack(pady=10)
            instalar_btn = ctk.CTkButton(
                self,
                text="Instalar Velociraptor",
                fg_color="#4CAF50",
                hover_color="#45A049",
                command=self.instalar_velociraptor
            )
            instalar_btn.pack(pady=15)

    def velociraptor_instalado(self) -> bool:
        """Comprueba si Velociraptor está disponible en el sistema."""
        result = run_command("velociraptor version")
        return result["success"]

    def instalar_velociraptor(self):
        """Ejecuta el script PowerShell para instalar Velociraptor."""
        ps1_path = os.path.join(SCRIPT_PATH, "install", "install_velociraptor.ps1")
        result = run_powershell(ps1_path)
        log_action("Velociraptor-Instalar", ps1_path, result)

        if result["success"]:
            messagebox.showinfo("Instalación", "Velociraptor instalado correctamente.")
            self.destroy()
            EDRWindow(self.master)  # Recargar ventana
        else:
            messagebox.showerror("Error", result["output"])

    def configurar_velociraptor(self):
        messagebox.showinfo("Configurar", "Aquí abriremos el configurador de Velociraptor (pendiente).")

    def gestionar_servicio(self):
        messagebox.showinfo("Servicio", "Aquí pondremos start/stop del servicio Velociraptor (pendiente).")

    def mostrar_info_velociraptor(self):
        """Muestra información de la versión de Velociraptor."""
        result = run_command("velociraptor version")
        info_text = result["output"]
        text_widget = ctk.CTkTextbox(self, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", info_text)
        text_widget.configure(state="disabled")
