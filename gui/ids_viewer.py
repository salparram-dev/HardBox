# gui/ids_view.py
import customtkinter as ctk
import os
import subprocess

class IDSWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("IDS - Snort")
        self.geometry("800x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        title = ctk.CTkLabel(self, text="IDS - Snort", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=10)

        if not self.snort_installed():
            msg = ctk.CTkLabel(self, text="Snort no está instalado en el sistema.\n¿Quieres instalarlo ahora?", justify="center")
            msg.pack(pady=15)

            install_btn = ctk.CTkButton(self, text="Instalar Snort", fg_color="#4CAF50", command=self.install_snort)
            install_btn.pack(pady=5)
        else:
            info_label = ctk.CTkLabel(self, text="Snort está instalado.\nAquí se mostrará información y herramientas del IDS.", justify="center")
            info_label.pack(pady=15)

    def snort_installed(self):
        """Comprueba si Snort está instalado en el sistema"""
        try:
            result = subprocess.run(["snort", "-V"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def install_snort(self):
        # Aquí pondríamos el script o comando para instalar Snort
        ctk.CTkLabel(self, text="Instalación de Snort iniciada...").pack(pady=10)
        # Ejemplo: subprocess.run(["powershell", "-Command", "Install-Snort.ps1"])
