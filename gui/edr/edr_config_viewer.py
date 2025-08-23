# gui/edr/edr_config_viewer.py
import customtkinter as ctk
import os
import tkinter.messagebox as messagebox
from tkinter import filedialog
from utils.edr_utils import detect_config_file
from utils.logger import log_action

class VelociraptorConfigWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Configuración de Velociraptor")
        self.geometry("1000x750")

        # Detectar archivo automáticamente
        self.config_path = detect_config_file()

        # Variable para mostrar la ruta
        self.path_var = ctk.StringVar(value=self.config_path or "")

        path_frame = ctk.CTkFrame(self)
        path_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(path_frame, text="Archivo de configuración:",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5)

        self.path_entry = ctk.CTkEntry(path_frame, textvariable=self.path_var, width=600)
        self.path_entry.pack(side="left", padx=5)

        ctk.CTkButton(path_frame, text="Seleccionar archivo", command=self.select_config_file).pack(side="left", padx=5)

        # Editor de texto
        self.text = ctk.CTkTextbox(self, wrap="word")
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

        if self.config_path:
            self.load_config(self.config_path)
        else:
            self.text.insert("1.0", "# No se encontró server.config.yaml\n")

        # Botones
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Guardar cambios", fg_color="#4CAF50",
                      hover_color="#45A049", command=self.save_config).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Cerrar",
                      fg_color="#f44336", hover_color="#e53935",
                      command=self.destroy).pack(side="left", padx=10)


    def select_config_file(self):
        """Permite seleccionar manualmente un archivo de configuración"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar server.config.yaml",
            filetypes=[("YAML files", "*.yaml"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.path_var.set(file_path)
            self.config_path = file_path
            self.load_config(file_path)

    def load_config(self, path):
        """Carga el contenido del archivo en el editor"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.text.delete("1.0", "end")
                self.text.insert("1.0", f.read())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def save_config(self):
        """Guarda los cambios en server.config.yaml"""
        try:
            config_path = self.path_var.get().strip()
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end").strip())

            log_action("Velociraptor-Config-Editar", config_path,
                       {"success": True, "output": "Configuración guardada"})
            messagebox.showinfo("Éxito", "Configuración de Velociraptor guardada correctamente.")
        except Exception as e:
            log_action("Velociraptor-Config-Editar", config_path,
                       {"success": False, "output": str(e)})
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
