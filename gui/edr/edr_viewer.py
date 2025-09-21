# gui/edr/edr_viewer.py
import customtkinter as ctk
import os
import tkinter.messagebox as messagebox
import threading
from PIL import Image
from utils.powershell_runner import run_powershell, run_command
from gui.edr.edr_service_viewer import VelociraptorServiceWindow
from utils.logger import log_action
from utils.window_utils import top_focus, ensure_icon

SCRIPT_PATH = "scripts/powershell"

class EDRWindow(ctk.CTkToplevel):
    def __init__(self, master=None, nav_owner=None):
        super().__init__(master)
        self._master = master
        self._nav_owner = nav_owner

        self.protocol("WM_DELETE_WINDOW", self.close_window)

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
            ctk.CTkLabel(
                self,
                text="Velociraptor no está instalado.",
                font=("Arial", 14)
            ).pack(pady=(10, 5))

            install_btn = ctk.CTkButton(
                self,
                text="Instalar Velociraptor",
                fg_color="#4CAF50",
                hover_color="#45A049",
                command=self.install
            )
            install_btn.pack(pady=15)     

    def close_window(self):
        """Cierra la ventana y limpia la selección en la barra de navegación"""
        if self._nav_owner and hasattr(self._nav_owner, "top_nav"):
            self._nav_owner.top_nav.set("")
        self.destroy()


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
                def reload():
                    self.destroy()
                    new_win = EDRWindow(self._master, self._nav_owner)
                     # aplicar icono tras un pequeño retardo para asegurar que el handle existe
                    new_win.after(50, lambda: ensure_icon(new_win))
                    new_win.after(100, lambda: ensure_icon(new_win))  # segundo intento por seguridad

                    top_focus(new_win)
                    new_win.after(200, lambda: new_win.attributes('-topmost', False))

                    if hasattr(self._master, "top_nav"):
                        new_win.protocol("WM_DELETE_WINDOW", lambda: (self._master.top_nav.set(""), new_win.destroy()))

                self.after(250, reload)
            else:
                self.after(0, lambda: messagebox.showerror("Error", result["output"]))

        # Lanzar en segundo plano para no congelar la UI
        threading.Thread(target=worker, daemon=True).start()

    def manage_service(self):
        """Abre la ventana independiente de gestión de servicio Velociraptor"""
        win = VelociraptorServiceWindow.open() 
        ensure_icon(win)
        top_focus(win)

    def show_info(self):
        """Muestra información de la versión de Velociraptor."""
        result = run_command("velociraptor version")
        info_text = result["output"]
        text_widget = ctk.CTkTextbox(self, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", info_text)
        text_widget.configure(state="disabled")
