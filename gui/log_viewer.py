# gui/log_viewer.py

import customtkinter as ctk
import json
import csv
import os
from tkinter import messagebox
from utils.window_utils import set_icon

LOG_FILE = "logs/hardbox_actions.log"

class LogViewerWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Historial de Acciones")
        self.geometry("800x500")

        self.logs = []
        self.filtered_logs = []

        self.filter_var = ctk.StringVar(value="Todos")

        # Filtros (se actualizarán dinámicamente en load_logs)
        self.filter_box = ctk.CTkOptionMenu(
            self,
            variable=self.filter_var,
            values=["Todos"],  # inicial, luego se actualizará
            command=self.apply_filter
        )
        self.filter_box.pack(pady=10)

        # Área de texto scrollable
        self.textbox = ctk.CTkTextbox(self, wrap="none")
        self.textbox.pack(expand=True, fill="both", padx=10, pady=10)

        # Botones
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        refresh_btn = ctk.CTkButton(btn_frame, text="Refrescar", command=self.refresh_logs)
        refresh_btn.pack(side="left", padx=10)

        export_btn = ctk.CTkButton(btn_frame, text="Exportar CSV", command=self.export_csv)
        export_btn.pack(side="left", padx=10)

        clear_btn = ctk.CTkButton(btn_frame, text="Limpiar Logs", fg_color="#f44336", hover_color="#e53935", command=self.clear_logs)
        clear_btn.pack(side="left", padx=10)

        self.load_logs()
        self.display_logs()

    def load_logs(self):
        self.logs.clear()
        if not os.path.exists(LOG_FILE):
            return
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    self.logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        self.filtered_logs = self.logs.copy()

        # Actualizar opciones del filtro dinámicamente
        self.update_filter_options()

    def update_filter_options(self):
        """Reconstruye el menú de filtros con las acciones detectadas en los logs"""
        base_filters = ["Todos", "Aplicar", "Revertir", "✔️ Éxito", "❌ Error"]

        # Obtener todas las acciones únicas en los logs
        acciones = sorted(set(l["action"] for l in self.logs if "action" in l))

        # Unir base + dinámicas
        all_filters = base_filters + [a for a in acciones if a not in base_filters]

        # Actualizar OptionMenu
        self.filter_box.configure(values=all_filters)

        # Si el valor actual ya no existe, resetear a "Todos"
        if self.filter_var.get() not in all_filters:
            self.filter_var.set("Todos")

    def display_logs(self):
        self.textbox.configure(state="normal")  # Habilitar edición temporal
        self.textbox.delete("1.0", "end")
        for log in self.filtered_logs[-100:]:
            status = "✔️" if log["success"] else "❌"
            line = f"[{log['timestamp']}] {status} {log['action']} {log['script']} → {log['message']}\n"
            self.textbox.insert("end", line)
        self.textbox.configure(state="disabled")  # Bloquear edición tras insertar

    def apply_filter(self, choice):
        # Diccionario de filtros predefinidos
        filters = {
            "Todos": lambda l: True,
            "Aplicar": lambda l: l["action"] == "Aplicar",
            "Verificar": lambda l: l["action"] == "Verificar",
            "Revertir": lambda l: l["action"] == "Revertir",
            "✔️ Éxito": lambda l: l["success"],
            "❌ Error": lambda l: not l["success"],
        }

        # Si el filtro es uno de los predefinidos, lo usamos
        if choice in filters:
            filtro = filters[choice]
        else:
            # Si no, filtramos directamente por el nombre de la acción (ej: "Snort-Iniciar IDS")
            filtro = lambda l: l["action"] == choice

        # Aplicar filtro
        self.filtered_logs = [l for l in self.logs if filtro(l)]
        self.display_logs()

    def export_csv(self):
        if not self.filtered_logs:
            messagebox.showwarning("Aviso", "No hay logs para exportar.", parent=self)
            return
        out_path = "logs/export.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.logs[0].keys())
            writer.writeheader()
            writer.writerows(self.filtered_logs)
        messagebox.showinfo("Exportado", f"Logs exportados en {out_path}", parent=self)

    def clear_logs(self):
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de borrar todos los logs?", parent=self)
        if confirm:
            open(LOG_FILE, "w").close()
            self.logs.clear()
            self.filtered_logs.clear()
            self.update_filter_options()
            self.display_logs()
            messagebox.showinfo("Limpiado", "Logs eliminados con éxito.", parent=self)
            
    def refresh_logs(self):
        self.load_logs()
        self.apply_filter(self.filter_var.get())
