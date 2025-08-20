# gui/snort_alerts_viewer.py
import customtkinter as ctk
from tkinter import messagebox
import os
import subprocess
import threading
import re
from PIL import Image, ImageDraw
import pystray
from plyer import notification
from utils.snort_utils import *
from utils.logger import log_action

class SnortAlertsWindow(ctk.CTkToplevel):
    _instance = None   # Singleton global

    @classmethod
    def open(cls, master=None):
        """Crea o restaura la ventana singleton de alertas"""
        if cls._instance is None or not cls._instance.winfo_exists():
            cls._instance = cls(master=None)  # <--- importante: siempre None
        else:
            cls._instance.deiconify()
            cls._instance.lift()
            cls._instance.focus_force()
        return cls._instance

    def __init__(self, master=None):
        super().__init__(master or None)
        self.title("Snort - Alertas y Reglas")
        self.geometry("950x800")

        SnortAlertsWindow._instance = self  # registrar singleton

        self.alert_file = detect_alert_file()
        self.rules_file = detect_local_rules()

        self.snort_process = None
        self.running = False
        self.tray_icon = None

        # Interceptar cierre
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # === PESTAÑA ALERTAS ===
        tab_alerts = tabview.add("Alertas")
        self.alert_text = ctk.CTkTextbox(tab_alerts, wrap="word")
        self.alert_text.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame_alert = ctk.CTkFrame(tab_alerts)
        btn_frame_alert.pack(pady=5)

        ctk.CTkButton(btn_frame_alert, text="Limpiar", command=self.clear_alerts).pack(side="left", padx=5)

        self.start_btn = ctk.CTkButton(btn_frame_alert, text="Iniciar IDS", fg_color="#4CAF50",
                                       hover_color="#45A049", command=self.start_ids)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ctk.CTkButton(btn_frame_alert, text="Detener IDS", fg_color="#f44336",
                                      hover_color="#e53935", command=self.stop_ids, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # === Selector de interfaz ===
        self.interfaces = self.get_snort_interfaces()
        interface_names = [i[1] for i in self.interfaces]
        self.interface_var = ctk.StringVar(value=interface_names[0] if interface_names else "")
        ctk.CTkLabel(btn_frame_alert, text="Interfaz:").pack(side="left", padx=5)
        self.interface_menu = ctk.CTkOptionMenu(btn_frame_alert, variable=self.interface_var, values=interface_names)
        self.interface_menu.pack(side="left", padx=5)

        # === PESTAÑA REGLAS ===
        tab_rules = tabview.add("Reglas")

        # --- Formulario de creación rápida ---
        form = ctk.CTkFrame(tab_rules)
        form.pack(fill="x", padx=20, pady=10)

        self.proto_var = ctk.StringVar(value="tcp")
        self.src_ip_var = ctk.StringVar(value="$HOME_NET")
        self.src_port_var = ctk.StringVar(value="any")
        self.dst_ip_var = ctk.StringVar(value="$EXTERNAL_NET")
        self.dst_port_var = ctk.StringVar(value="any")
        self.msg_var = ctk.StringVar()
        self.sid_var = ctk.StringVar()

        fields = [
            ("Protocolo", self.proto_var, ["tcp", "udp", "icmp", "ip"]),
            ("IP Origen", self.src_ip_var, None),
            ("Puerto Origen", self.src_port_var, None),
            ("IP Destino", self.dst_ip_var, None),
            ("Puerto Destino", self.dst_port_var, None),
            ("Mensaje", self.msg_var, None),
            ("SID", self.sid_var, None),
        ]

        for label, var, options in fields:
            row = ctk.CTkFrame(form)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label+":", width=120, anchor="w").pack(side="left", padx=5)
            if options:
                ctk.CTkOptionMenu(row, variable=var, values=options).pack(side="left", fill="x", expand=True, padx=5)
            else:
                ctk.CTkEntry(row, textvariable=var).pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(form, text="Añadir regla",
                      fg_color="#4CAF50", hover_color="#45A049",
                      command=self.add_rule_from_form).pack(pady=10)

        # --- Editor de reglas completo ---
        self.rules_text = ctk.CTkTextbox(tab_rules, wrap="word", height=300)
        self.rules_text.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame_rules = ctk.CTkFrame(tab_rules)
        btn_frame_rules.pack(pady=5)
        ctk.CTkButton(btn_frame_rules, text="Guardar reglas",
                      fg_color="#2196F3", hover_color="#1976D2",
                      command=self.save_rules).pack(side="left", padx=5)

        self.load_alerts()
        self.load_rules()
        self.last_alerts_count = 0  # para contar alertas previas
        self.after(3000, self.auto_refresh)

    # =========================
    # Manejo de cierre / systray
    # =========================
    def on_close(self):
        if self.running:
            if not messagebox.askyesno("IDS en ejecución",
                                       "Snort está corriendo.\n¿Quieres detenerlo al cerrar la ventana?"):
                self.withdraw()
                self.show_in_tray()
                return
            else:
                self.stop_ids()
        # destruir instancia singleton
        SnortAlertsWindow._instance = None
        self.destroy()

    def show_in_tray(self):
        if self.tray_icon:
            return

        # Crear icono simple
        icon_img = Image.new("RGB", (64, 64), "blue")
        draw = ImageDraw.Draw(icon_img)
        draw.rectangle((16, 16, 48, 48), fill="white")

        def restore_window(icon, item):
            self.deiconify()
            self.tray_icon.stop()
            self.tray_icon = None

        def quit_app(icon, item):
            if self.running:
                self.stop_ids()
            self.tray_icon.stop()
            self.tray_icon = None
            SnortAlertsWindow._instance = None
            self.destroy()

        menu = pystray.Menu(
            pystray.MenuItem("Restaurar ventana", restore_window),
            pystray.MenuItem("Salir", quit_app)
        )

        self.tray_icon = pystray.Icon("Snort IDS", icon_img, "Snort IDS", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    # =========================
    # FUNCIONES DE ALERTAS
    # =========================
    def get_snort_interfaces(self):
        try:
            result = subprocess.run(["snort", "-W"], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.splitlines():
                match = re.match(r"\s*(\d+)\s+([0-9A-F:]{17}|[0:]{17})\s+(.*?)\s+\\Device.*?\s+(.*)", line, re.IGNORECASE)
                if match:
                    idx = match.group(1)
                    ip_addr = match.group(3).strip()
                    desc = match.group(4).strip()
                    display = f"{idx} - {ip_addr} - {desc}"
                    interfaces.append((idx, display))
            return interfaces
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron obtener interfaces: {e}")
            return []


    def load_alerts(self):
        self.alert_text.delete("1.0", "end")
        if self.alert_file and os.path.exists(self.alert_file):
            with open(self.alert_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if content.strip():
                self.alert_text.insert("1.0", content)
            else:
                self.alert_text.insert("1.0", "No se encontró ninguna alerta.")
        else:
            self.alert_text.insert("1.0", "No se encontró archivo de alertas.\n"
                                          "Inicie Snort para generar alertas aquí.")

    def clear_alerts(self):
        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de borrar todos las alertas registradas?")
        if self.alert_file and confirm:
            open(self.alert_file, "w").close()
            log_action("Snort-Limpiar alertas", self.alert_file, {"success": True, "output": "Alertas borradas"})
            self.last_alerts_count = 0
            self.load_alerts()

    # =========================
    # FUNCIONES DE REGLAS
    # =========================
    def load_rules(self):
        self.rules_text.delete("1.0", "end")
        if self.rules_file and os.path.exists(self.rules_file):
            with open(self.rules_file, "r", encoding="utf-8") as f:
                self.rules_text.insert("1.0", f.read())
        else:
            self.rules_text.insert("1.0", "# No se encontró local.rules")

    def add_rule_from_form(self):
        try:
            sid_value = self.sid_var.get().strip()
            if not sid_value.isdigit():
                messagebox.showerror("Error", "El SID debe ser numérico")
                return

            rule = (
                f"alert {self.proto_var.get()} "
                f"{self.src_ip_var.get()} {self.src_port_var.get()} -> "
                f"{self.dst_ip_var.get()} {self.dst_port_var.get()} "
                f'(msg:"{self.msg_var.get()}"; sid:{sid_value}; rev:1;)'
            )

            with open(self.rules_file, "a", encoding="utf-8") as f:
                f.write(rule + "\n")

            self.load_rules()
            log_action("Snort-Añadir regla", self.rules_file, {"success": True, "output": rule})
            messagebox.showinfo("Éxito", "Regla añadida correctamente.")
        except Exception as e:
            log_action("Snort-Añadir regla", self.rules_file, {"success": False, "output": "No se ha podido añadir la regla"})
            messagebox.showerror("Error", str(e))

    def save_rules(self):
        if self.rules_file:
            with open(self.rules_file, "w", encoding="utf-8") as f:
                f.write(self.rules_text.get("1.0", "end").strip())

            log_action("Snort-Guardar reglas", self.rules_file, {"success": True, "output": "Reglas actualizadas"})
            messagebox.showinfo("Éxito", "Reglas guardadas correctamente.")

    # =========================
    # IDS
    # =========================
    def start_ids(self):
        if not self.rules_file:
            messagebox.showerror("Error", "No se encontró local.rules")
            return
        if not self.alert_file:
            messagebox.showerror("Error", "No se encontró carpeta de logs para alertas")
            return

        try:
            snort_conf = detect_snort_conf()
            if not snort_conf:
                messagebox.showerror("Error", "No se encontró snort.conf")
                return

            log_dir = os.path.dirname(self.alert_file)
            selected_desc = self.interface_var.get()
            iface = next((idx for idx, desc in self.interfaces if desc == selected_desc), None)
            if not iface:
                messagebox.showerror("Error", "No se pudo determinar el índice de la interfaz seleccionada")
                return

            cmd = [
                r"snort",
                "-A", "fast",
                "-c", snort_conf,
                "-l", log_dir,
                "-i", iface,
                "-k", "none"
            ]

            self.snort_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            log_action("Snort-Iniciar IDS", "snort", {"success": True, "output": f"Interfaz {iface}"})
            messagebox.showinfo("IDS", f"Snort iniciado en interfaz {iface}.")

            threading.Thread(target=self._log_snort_output, daemon=True).start()
        except Exception as e:
            log_action("Snort-Iniciar IDS", "snort", {"success": False, "output": "No se ha podido iniciar la ejecución"})
            messagebox.showerror("Error", str(e))

    def _log_snort_output(self):
        if self.snort_process:
            for line in self.snort_process.stderr:
                print("[Snort]", line.strip())

    def stop_ids(self):
        if self.snort_process:
            self.snort_process.terminate()
            self.snort_process = None
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        log_action("Snort-Detener IDS", "snort", {"success": True, "output": "Proceso terminado"})
        messagebox.showinfo("IDS", "Snort detenido.")

    def auto_refresh(self):
        if self.running and self.alert_file and os.path.exists(self.alert_file):
            with open(self.alert_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = [line.strip() for line in f if line.strip()]

            current_count = len(lines)

            if current_count > self.last_alerts_count:
                new_alerts = lines[self.last_alerts_count:]
                latest_alert = new_alerts[-1] if new_alerts else "Nueva alerta de Snort"
                notification.notify(
                    title="🚨 Snort IDS",
                    message=f"{len(new_alerts)} nueva(s) alerta(s)\n{latest_alert[:150]}",
                    timeout=5
                )
                self.last_alerts_count = current_count

            # Actualizar área de texto
            self.alert_text.delete("1.0", "end")
            self.alert_text.insert("1.0", "\n".join(lines))

        elif self.running:
            self.alert_text.delete("1.0", "end")
            self.alert_text.insert("1.0", "Esperando alertas...")

        self.after(3000, self.auto_refresh)
