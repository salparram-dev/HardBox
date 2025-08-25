# gui/edr/edr_config_viewer.py
import customtkinter as ctk
import re
import tkinter.messagebox as messagebox
from tkinter import filedialog
from utils.edr_utils import detect_config_file
from utils.logger import log_action
import yaml


class VelociraptorConfigWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Configuración de Velociraptor")
        self.geometry("1000x750")

        # Detectar archivo automáticamente
        self.config_path = detect_config_file()

        # -------------------------
        # Sección: ruta del archivo
        # -------------------------
        self.path_var = ctk.StringVar(value=self.config_path or "")
        path_frame = ctk.CTkFrame(self)
        path_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(path_frame, text="Archivo de configuración:",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5)

        ctk.CTkEntry(path_frame, textvariable=self.path_var, width=600).pack(side="left", padx=5)
        ctk.CTkButton(path_frame, text="Seleccionar archivo", command=self.select_config_file).pack(side="left", padx=5)

        # -------------------------
        # Sección: configuración básica
        # -------------------------
        basic_frame = ctk.CTkFrame(self)
        basic_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(basic_frame, text="Configuración básica",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.gui_port_var = ctk.StringVar()
        self.frontend_port_var = ctk.StringVar()
        self.server_url_var = ctk.StringVar()

        form_items = [
            ("GUI Port", self.gui_port_var),
            ("Frontend Port", self.frontend_port_var),
            ("Servidor URL", self.server_url_var),
        ]

        for label_text, var in form_items:
            row = ctk.CTkFrame(basic_frame)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label_text + ":", width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkEntry(row, textvariable=var).pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(
            basic_frame,
            text="Guardar configuración básica",
            fg_color="#4CAF50",
            hover_color="#45A049",
            command=self.save_basic_config
        ).pack(pady=10)

        # -------------------------
        # Sección avanzada
        # -------------------------
        advanced_frame = ctk.CTkFrame(self)
        advanced_frame.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkLabel(advanced_frame, text="Edición avanzada",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.text_area = ctk.CTkTextbox(advanced_frame, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)

        if self.config_path:
            self.load_config(self.config_path)
        else:
            self.text_area.insert("1.0", "# No se encontró server.config.yaml\n")

        btn_frame = ctk.CTkFrame(advanced_frame)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Guardar archivo completo", fg_color="#4CAF50",
                      hover_color="#45A049", command=self.save_config).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cerrar", fg_color="#f44336", hover_color="#e53935",
                      command=self.destroy).pack(side="left", padx=10)

    # -------------------------
    # Métodos auxiliares
    # -------------------------
    def select_config_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar server.config.yaml",
            filetypes=[("YAML files", "*.yaml"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.path_var.set(file_path)
            self.config_path = file_path
            self.load_config(file_path)

    def extract_value(self, cfg, keys, default=""):
        """Extrae un valor de un diccionario anidado como en Snort pero para YAML"""
        current = cfg
        try:
            for k in keys:
                current = current[k]
            return str(current)
        except Exception:
            return default

    def load_config(self, path):
        """Carga el YAML completo y extrae SIEMPRE los valores actuales"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
                self.text_area.delete("1.0", "end")
                self.text_area.insert("1.0", raw)

            # Extraer valores reales del YAML
            cfg = yaml.safe_load(raw) or {}
            self.gui_port_var.set(self.extract_value(cfg, ["GUI", "bind_port"]))
            self.frontend_port_var.set(self.extract_value(cfg, ["Frontend", "bind_port"]))
            urls = cfg.get("Client", {}).get("server_urls", [])
            self.server_url_var.set(urls[0] if urls else "")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}", parent=self)
    

    def save_basic_config(self):
        """Actualiza solo los campos básicos en el YAML sin alterar el resto del formato"""
        try:
            if not self.config_path:
                raise Exception("Ruta de configuración no definida")

            # Leer YAML original como texto
            with open(self.config_path, "r", encoding="utf-8") as f:
                original_lines = f.readlines()

            # Cargar YAML como dict para obtener estructura
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}

            # Actualizar en memoria
            if self.gui_port_var.get():
                cfg.setdefault("GUI", {})["bind_port"] = int(self.gui_port_var.get())
            if self.frontend_port_var.get():
                cfg.setdefault("Frontend", {})["bind_port"] = int(self.frontend_port_var.get())
            if self.server_url_var.get():
                cfg.setdefault("Client", {})["server_urls"] = [self.server_url_var.get()]

            # Reemplazar solo las líneas necesarias en el texto original
            def replace_line(lines, key, new_value):
                for i, line in enumerate(lines):
                    if line.strip().startswith(f"{key}:"):
                        indent = line[:len(line) - len(line.lstrip())]
                        lines[i] = f"{indent}{key}: {new_value}\n"
                        break

            # GUI bind_port
            if self.gui_port_var.get():
                for i, line in enumerate(original_lines):
                    if line.strip().startswith("GUI:"):
                        # buscar bind_port dentro de GUI
                        j = i + 1
                        while j < len(original_lines) and not original_lines[j].strip().endswith(":"):
                            if "bind_port:" in original_lines[j]:
                                indent = original_lines[j][:len(original_lines[j]) - len(original_lines[j].lstrip())]
                                original_lines[j] = f"{indent}bind_port: {int(self.gui_port_var.get())}\n"
                                break
                            j += 1

            # Frontend bind_port
            if self.frontend_port_var.get():
                for i, line in enumerate(original_lines):
                    if line.strip().startswith("Frontend:"):
                        j = i + 1
                        while j < len(original_lines) and not original_lines[j].strip().endswith(":"):
                            if "bind_port:" in original_lines[j]:
                                indent = original_lines[j][:len(original_lines[j]) - len(original_lines[j].lstrip())]
                                original_lines[j] = f"{indent}bind_port: {int(self.frontend_port_var.get())}\n"
                                break
                            j += 1

            # Client server_urls (solo primera URL)
            if self.server_url_var.get():
                for i, line in enumerate(original_lines):
                    if line.strip().startswith("server_urls:"):
                        # siguiente línea es la URL
                        if i + 1 < len(original_lines) and original_lines[i+1].strip().startswith("- "):
                            indent = original_lines[i+1][:len(original_lines[i+1]) - len(original_lines[i+1].lstrip())]
                            original_lines[i+1] = f"{indent}- {self.server_url_var.get()}\n"
                        break

            # Guardar el archivo modificado
            with open(self.config_path, "w", encoding="utf-8") as f:
                f.writelines(original_lines)

            # Recargar para refrescar editor avanzado e inputs
            self.load_config(self.config_path)

            log_action("Velociraptor-Guardar configuración", self.config_path,
                    {"success": True, "output": "Configuración básica guardada"})
            messagebox.showinfo("Éxito", "Configuración básica guardada correctamente.", parent=self)

        except Exception as e:
            log_action("Velociraptor-Guardar configuración", self.config_path,
                    {"success": False, "output": str(e)})
            messagebox.showerror("Error", f"No se pudo guardar la configuración básica:\n{e}", parent=self)


    def save_config(self):
        """Guarda el YAML completo desde el editor avanzado"""
        try:
            config_path = self.path_var.get().strip()
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(self.text_area.get("1.0", "end").strip())

            log_action("Velociraptor-Guardar Configuración", config_path,
                       {"success": True, "output": "Configuración guardada"})
            messagebox.showinfo("Éxito", "Configuración avanzada guardada correctamente.", parent=self)
        except Exception as e:
            log_action("Velociraptor-Guardar Configuración", self.config_path,
                       {"success": False, "output": str(e)})
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}", parent=self)
