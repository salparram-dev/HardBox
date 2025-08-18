# gui/snort_alerts_viewer.py
import customtkinter as ctk
from tkinter import messagebox
import os
import subprocess
import threading
import re
from PIL import Image, ImageDraw
import pystray

class SnortAlertsWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Snort - Alertas y Reglas")
        self.geometry("950x800")

         # Guarda referencia en el master si existe ese atributo
        if master is not None and hasattr(master, "alerts_window"):
            master.alerts_window = self

        self.alert_file = self.detect_alert_file()
        self.rules_file = self.ensure_rules_file()

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
        self.after(3000, self.auto_refresh)

    # =========================
    # NUEVO: Manejo de cierre
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
        # Se va a destruir: limpiar la referencia del master
        try:
            if self.master is not None and hasattr(self.master, "alerts_window") and self.master.alerts_window is self:
                self.master.alerts_window = None
        except Exception:
            pass
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

    def detect_alert_file(self):
        possible_paths = [
            r"C:\Snort\log\alert.ids",
            r"C:\Program Files\Snort\log\alert.ids",
            r"C:\Program Files (x86)\Snort\log\alert.ids"
        ]
        for path in possible_paths:
            folder = os.path.dirname(path)
            if os.path.exists(folder):
                return path
        return None

    def ensure_rules_file(self):
        possible_paths = [
            r"C:\Snort\rules\local.rules",
            r"C:\Program Files\Snort\rules\local.rules",
            r"C:\Program Files (x86)\Snort\rules\local.rules"
        ]
        for path in possible_paths:
            folder = os.path.dirname(path)
            if os.path.exists(folder):
                if not os.path.exists(path):
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("# Reglas locales de Snort\n")
                return path
        return None

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
        if self.alert_file:
            open(self.alert_file, "w").close()
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
            messagebox.showinfo("Éxito", "Regla añadida correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_rules(self):
        if self.rules_file:
            with open(self.rules_file, "w", encoding="utf-8") as f:
                f.write(self.rules_text.get("1.0", "end").strip())
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
            snort_conf = r"C:\Snort\etc\snort.conf"
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
            messagebox.showinfo("IDS", f"Snort iniciado en interfaz {iface}.")

            threading.Thread(target=self._log_snort_output, daemon=True).start()
        except Exception as e:
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
        messagebox.showinfo("IDS", "Snort detenido.")

    def auto_refresh(self):
        if self.running:
            self.load_alerts()
        self.after(3000, self.auto_refresh)
