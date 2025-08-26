# gui/snort_config_viewer.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import re
from utils.ids_utils import detect_snort_conf
from utils.logger import log_action

class SnortConfigWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Configuración de Snort")
        self.geometry("950x750")

        self.config_path = detect_snort_conf()

        # Título
        ctk.CTkLabel(self, text="Configuración de Snort", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=15)

        # Ruta de snort.conf
        self.path_var = ctk.StringVar(value=self.config_path or "No detectado")
        path_frame = ctk.CTkFrame(self)
        path_frame.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(path_frame, text="Ruta de snort.conf:", anchor="w").pack(side="left", padx=5)
        ctk.CTkEntry(path_frame, textvariable=self.path_var, width=500).pack(side="left", padx=5)
        ctk.CTkButton(path_frame, text="Cambiar", command=self.change_config_path).pack(side="left", padx=5)

        # Cargar archivo
        self.config_content = ""
        if self.config_path and os.path.exists(self.config_path):
            self.load_config()

        # === SECCIÓN CONFIG BÁSICA ===
        basic_frame = ctk.CTkFrame(self)
        basic_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(basic_frame, text="Configuración básica", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.home_net_var = ctk.StringVar(value=self.extract_value("ipvar HOME_NET"))
        self.external_net_var = ctk.StringVar(value=self.extract_value("ipvar EXTERNAL_NET"))
        self.rule_path_var = ctk.StringVar(value=self.extract_value("var RULE_PATH"))

        form_items = [
            ("HOME_NET", self.home_net_var),
            ("EXTERNAL_NET", self.external_net_var),
            ("RULE_PATH", self.rule_path_var)
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

        # === SECCIÓN AVANZADA ===
        advanced_frame = ctk.CTkFrame(self)
        advanced_frame.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkLabel(advanced_frame, text="Edición avanzada", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.text_area = ctk.CTkTextbox(advanced_frame, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_area.insert("1.0", self.config_content or "# No se encontró snort.conf")

        btn_frame = ctk.CTkFrame(advanced_frame)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Guardar archivo completo", fg_color="#4CAF50", hover_color="#45A049",
                      command=self.save_config).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cerrar", fg_color="#f44336", hover_color="#d32f2f",
                      command=self.destroy).pack(side="left", padx=10)

    def change_config_path(self):
        new_path = filedialog.askopenfilename(title="Seleccionar snort.conf", filetypes=[("Conf Files", "*.conf")])
        if new_path:
            self.config_path = new_path
            self.path_var.set(new_path)
            self.load_config()

    def load_config(self):
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8", errors="ignore") as f:
                self.config_content = f.read()
        else:
            messagebox.showerror("Error", "No se puede cargar snort.conf", parent=self)

    def extract_value(self, key):
        match = re.search(rf"^{key}\s+(.+)$", self.config_content, re.MULTILINE)
        return match.group(1) if match else ""

    def save_basic_config(self):
        if not self.config_content:
            messagebox.showerror("Error", "No hay configuración cargada.", parent=self)
            return

        # Actualizamos las líneas en memoria
        updated_content = re.sub(r"^ipvar HOME_NET\s+.+$", f"ipvar HOME_NET {self.home_net_var.get()}", self.config_content, flags=re.MULTILINE)
        updated_content = re.sub(r"^ipvar EXTERNAL_NET\s+.+$", f"ipvar EXTERNAL_NET {self.external_net_var.get()}", updated_content, flags=re.MULTILINE)
        updated_content = re.sub(r"^var RULE_PATH\s+.+$", f"var RULE_PATH {self.rule_path_var.get()}", updated_content, flags=re.MULTILINE)

        self.config_content = updated_content

        # Actualizamos el editor avanzado para que refleje el cambio
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", self.config_content)

        # Guardamos directamente a disco
        if self.config_path:
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    f.write(self.config_content)

                log_action("Snort-Guardar configuración", "snort", {"success": True, "output": "Configuración básica guardada"})
                messagebox.showinfo("Éxito", "Configuración básica guardada correctamente.", parent=self)
            except Exception as e:
                log_action("Snort-Guardar configuración", "snort", {"success": False, "output": "No se pudo guardar la configuración básica"})
                messagebox.showerror("Error", str(e), parent=self)
        else:
            log_action("Snort-Guardar configuración", "snort", {"success": False, "output": "No se pudo guardar la configuración básica"})
            messagebox.showerror("Error", "Ruta de configuración no definida.", parent=self)


    def save_config(self):
        if self.config_path:
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get("1.0", "end").strip())

                log_action("Snort-Guardar configuración", "snort", {"success": True, "output": "Configuración guardada"})
                messagebox.showinfo("Éxito", "Configuración guardada correctamente.", parent=self)
            except Exception as e:
                log_action("Snort-Guardar configuración", "snort", {"success": False, "output": "No se pudo guardar la configuración"})
                messagebox.showerror("Error", str(e), parent=self)
        else:
            log_action("Snort-Guardar configuración", "snort", {"success": False, "output": "No se pudo guardar la configuración"})
            messagebox.showerror("Error", "Ruta de configuración no definida.", parent=self)
