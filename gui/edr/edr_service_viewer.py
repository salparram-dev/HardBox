# gui/edr/edr_service_window.py
import customtkinter as ctk
from tkinter import messagebox, ttk
import subprocess
import threading
import time
import yaml
import json
from collections import Counter
from PIL import Image, ImageDraw
import pystray
from utils.logger import log_action
from utils.edr_utils import detect_config_file

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class VelociraptorServiceWindow(ctk.CTkToplevel):
    _instance = None  # Singleton global

    @classmethod
    def open(cls, master=None):
        """Crea o restaura la ventana singleton de servicio Velociraptor"""
        if cls._instance is None or not cls._instance.winfo_exists():
            cls._instance = cls(master=None)  # siempre None
        else:
            cls._instance.deiconify()
            cls._instance.lift()
            cls._instance.focus_force()
        return cls._instance

    def __init__(self, master=None):
        super().__init__(master or None)
        self.title("Velociraptor - Gestión de servicio")
        self.geometry("1600x800")

        VelociraptorServiceWindow._instance = self

        self.server_process = None
        self.client_process = None
        self.running = False
        self.tray_icon = None

        # interceptar cierre
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # === pestaña servicio ===
        self.tab_service = self.tabview.add("Servicio")

        self.start_btn = ctk.CTkButton(self.tab_service, text="Iniciar Velociraptor",
                                       fg_color="#4CAF50", hover_color="#45A049",
                                       command=self.start_velociraptor)
        self.start_btn.pack(pady=10)

        self.stop_btn = ctk.CTkButton(self.tab_service, text="Detener Velociraptor",
                                      fg_color="#f44336", hover_color="#e53935",
                                      command=self.stop_velociraptor, state="disabled")
        self.stop_btn.pack(pady=10)

        # URL del panel
        self.url_label = ctk.CTkLabel(self.tab_service, text="Panel no disponible")
        self.url_label.pack(pady=10)

        # === pestañas consultas ===
        self.tab_procs = self.tabview.add("Procesos")
        self.tab_conns = self.tabview.add("Conexiones")
        self.tab_services = self.tabview.add("Servicios")
        self.tab_files = self.tabview.add("Archivos recientes")

        # inicializar cada tabla + refresco automático
        process_query = "SELECT Name,Pid,Username FROM pslist()"
        conn_query = "SELECT Laddr.IP,Laddr.Port,Raddr.IP,Raddr.Port,Status,TypeString FROM netstat()"
        serv_query = "SELECT Name,DisplayName,State,StartMode FROM wmi(query='SELECT Name, DisplayName, State, StartMode " \
        "FROM Win32_Service', namespace='root/CIMV2')"
        files_query = (
            "SELECT Name, Mtime, OSPath "
            "FROM glob(globs='C:\\\\Users\\\\**', accessor='file') "
            "WHERE NOT IsDir "
            "AND Size > 0 "
            "AND Mtime > now() - 30*24*60*60 "
            "AND Name =~ '(?i)\\.(py|exe|dll|bat|ps1|vbs|js|jar|cmd|msi|scr|com|doc|docx|xls|xlsx|ppt|pptx|pdf|rtf|txt|csv|zip|rar|7z|gz|tar|iso|img|bin|dat|cfg|ini|conf|xml|json|png|jpg|jpeg|gif|bmp|tiff|svg|mp3|wav|mp4|avi|mkv)$' "
            "ORDER BY Mtime DESC "
            "LIMIT 200"
        )

        self._init_query_tab(self.tab_procs, "Procesos", process_query, self.show_process_charts)
        self._init_query_tab(self.tab_conns, "Conexiones", conn_query, self.show_conn_chart)
        self._init_query_tab(self.tab_services, "Servicios", serv_query, self.show_service_charts)
        self._init_query_tab(self.tab_files, "Archivos", files_query, self.show_files_chart)

        # Estilo de tablas moderno
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white",
                        fieldbackground="#2b2b2b", rowheight=25, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background="#444", foreground="white",
                        font=("Segoe UI", 12, "bold"))
        style.map("Treeview", background=[("selected", "#1f6aa5")])

        # Ejecutar las consultas iniciales automáticamente
        self.after(500, lambda: self.run_query(process_query, self.tab_procs, self.show_process_charts))
        self.after(1000, lambda: self.run_query(conn_query, self.tab_conns, self.show_conn_chart))
        self.after(1500,lambda: self.run_query(serv_query, self.tab_services, self.show_service_charts))
        self.after(2000, lambda: self.run_query(files_query, self.tab_files, self.show_files_chart))

    def _init_query_tab(self, parent, label, query, chart_callback):
        """Inicializa una pestaña con tabla y botón de refresco"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # botón de refrescar
        btn = ctk.CTkButton(frame, text=f"Refrescar {label}",
                            fg_color="#2196F3", hover_color="#1976D2",
                            command=lambda: self.run_query(query, parent, chart_callback))
        btn.pack(pady=5)

        # tabla
        tree = ttk.Treeview(frame, show="headings", height=10)
        tree.pack(fill="both", expand=True, pady=10)
        setattr(parent, "tree", tree)

        # espacio gráfico
        chart_frame = ctk.CTkFrame(frame)
        chart_frame.pack(fill="both", expand=True, pady=5)
        setattr(parent, "chart_frame", chart_frame)

    def on_close(self):
        if self.running:
            if not messagebox.askyesno("Velociraptor en ejecución",
                                       "Velociraptor sigue corriendo.\n¿Quieres detenerlo al cerrar la ventana?", parent=self):
                self.withdraw()
                self.show_in_tray()
                return
            else:
                self.stop_velociraptor()
        VelociraptorServiceWindow._instance = None
        self.destroy()

    def show_in_tray(self):
        if self.tray_icon:
            return
        icon_img = Image.new("RGB", (64, 64), "green")
        draw = ImageDraw.Draw(icon_img)
        draw.ellipse((16, 16, 48, 48), fill="white")

        def restore(icon, item):
            self.deiconify()
            self.tray_icon.stop()
            self.tray_icon = None

        def quit_app(icon, item):
            if self.running:
                self.stop_velociraptor()
            self.tray_icon.stop()
            self.tray_icon = None
            VelociraptorServiceWindow._instance = None
            self.destroy()

        menu = pystray.Menu(
            pystray.MenuItem("Restaurar ventana", restore),
            pystray.MenuItem("Salir", quit_app)
        )
        self.tray_icon = pystray.Icon("Velociraptor", icon_img, "Velociraptor", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def start_velociraptor(self):
        try:
            config_file = detect_config_file()
            if not config_file:
                messagebox.showerror("Error", "No se encontró archivo de configuración de Velociraptor.", parent=self)
                return

            # leer URL desde el config
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                host = cfg.get("GUI", {}).get("bind_address", "127.0.0.1")
                port = cfg.get("GUI", {}).get("bind_port", 8889)
                url = f"http://{host}:{port}/"
                self.url_label.configure(text=f"Panel web: {url}")
            except Exception:
                self.url_label.configure(text="No se pudo leer la URL del panel")

            server_cmd = ["velociraptor", "frontend", "-c", config_file]
            client_cmd = ["velociraptor", "client", "-c", config_file]

            self.server_process = subprocess.Popen(
                server_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            self.client_process = subprocess.Popen(
                client_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )

            self.running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")

            log_action("Velociraptor-Iniciar servicio", "velociraptor",
                       {"success": True, "output": "Servidor y cliente iniciados"})
            messagebox.showinfo("Velociraptor", "Servidor y cliente iniciados correctamente.", parent=self)

            threading.Thread(target=self._log_output, daemon=True).start()

        except Exception as e:
            log_action("Velociraptor-Iniciar servicio", "velociraptor",
                       {"success": False, "output": str(e)})
            messagebox.showerror("Error", f"No se pudo iniciar Velociraptor:\n{e}", parent=self)

    def _log_output(self):
        for proc, name in [(self.server_process, "server"), (self.client_process, "client")]:
            if proc:
                for line in proc.stderr:
                    print(f"[Velociraptor-{name}] {line.strip()}")

    def stop_velociraptor(self):
        try:
            if self.server_process:
                subprocess.run(["taskkill", "/PID", str(self.server_process.pid), "/T", "/F"])
                self.server_process = None
            if self.client_process:
                subprocess.run(["taskkill", "/PID", str(self.client_process.pid), "/T", "/F"])
                self.client_process = None

            self.running = False
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.url_label.configure(text="Panel no disponible")

            log_action("Velociraptor-Detener servicio", "velociraptor",
                       {"success": True, "output": "Procesos terminados"})
            messagebox.showinfo("Velociraptor", "Servidor y cliente detenidos.", parent=self)
        except Exception as e:
            log_action("Velociraptor-Detener servicio", "velociraptor",
                       {"success": False, "output": str(e)})
            messagebox.showerror("Error", f"No se pudo detener Velociraptor:\n{e}", parent=self)

    def run_query(self, query: str, tab, chart_callback):
        """Ejecuta consultas VQL y muestra resultados en tabla y gráfica"""
        try:
            cmd = f'velociraptor query "{query}" --format jsonl'

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )

            raw_output = result.stdout if result.stdout.strip() else result.stderr

            if not raw_output:
                messagebox.showinfo("Consulta", "No se encontraron resultados.", parent=self)
                return

            output = raw_output.strip().splitlines()
            rows = []
            for line in output:
                try:
                    row = json.loads(line)
                    # limpieza de textos
                    for k, v in row.items():
                        if isinstance(v, str):
                            row[k] = v.encode("utf-8", "ignore").decode("utf-8", "ignore").strip()
                    rows.append(row)
                except json.JSONDecodeError:
                    continue

            if not rows:
                return

            # limpiar tabla
            tree = getattr(tab, "tree")
            for col in tree.get_children():
                tree.delete(col)

            headers = {
                "Name": "Nombre",
                "DisplayName": "Nombre visible",
                "State": "Estado",
                "StartMode": "Modo de arranque",
                "Pid": "PID",
                "Username": "Usuario",
                "Mtime": "Última modificación",
                "Laddr.IP": "IP local",
                "Laddr.Port": "Puerto local",
                "Raddr.IP": "IP remota",
                "Raddr.Port": "Puerto remoto",
                "Status": "Estado",
                "TypeString": "Protocolo",
                "OSPath": "Protocolo",
            }

            tree["columns"] = list(rows[0].keys())
            for col in tree["columns"]:
                col_title = headers.get(col, col)
                tree.heading(col, text=col_title)
                tree.column(col, width=200, anchor="center")

            for row in rows:
                tree.insert("", "end", values=[row.get(col, "") for col in tree["columns"]])

            chart_callback(rows, getattr(tab, "chart_frame"))

        except Exception as e:
            messagebox.showerror("Error", f"Error ejecutando consulta: {e}", parent=self)

    # === GRÁFICAS ===
    def _render_chart(self, data, chart_frame, title, xlabel, ylabel):
        # Limpiar el frame antes de dibujar
        for widget in chart_frame.winfo_children():
            widget.destroy()

        # Figura con layout automático para evitar cortes
        fig = Figure(figsize=(8, 5), dpi=100, constrained_layout=True)
        ax = fig.add_subplot(111)

        # Barras con estilo moderno
        bars = ax.bar(data.keys(), data.values(),
                    color="#4CAF50", edgecolor="black", linewidth=0.7)

        # Títulos y etiquetas
        ax.set_title(title, fontsize=16, fontweight="bold", color="#333333")
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.tick_params(axis="x", rotation=30, labelsize=10)
        ax.tick_params(axis="y", labelsize=10)

        # Mostrar valores encima de las barras
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

        # Fondo claro para contraste
        ax.set_facecolor("#f9f9f9")
        fig.patch.set_facecolor("#f0f0f0")

        # Canvas responsivo
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


    def show_process_charts(self, rows, chart_frame):
        for widget in chart_frame.winfo_children():
            widget.destroy()

        counts_name = Counter([r.get("Name", "Desconocido") for r in rows])
        top10 = dict(counts_name.most_common(10))
        counts_user = Counter([r.get("Username", "Desconocido") for r in rows])

        fig = Figure(figsize=(12, 5), dpi=100, constrained_layout=True)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        # Gráfico 1
        bars1 = ax1.bar(top10.keys(), top10.values(),
                        color="#1f77b4", edgecolor="black")
        ax1.set_title("Top 10 procesos por nombre", fontsize=12, fontweight="bold")
        ax1.tick_params(axis="x", rotation=30)
        for bar in bars1:
            ax1.annotate(f'{bar.get_height()}',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

        # Gráfico 2
        bars2 = ax2.bar(counts_user.keys(), counts_user.values(),
                        color="#2ca02c", edgecolor="black")
        ax2.set_title("Procesos por usuario", fontsize=12, fontweight="bold")
        ax2.tick_params(axis="x", rotation=30)
        for bar in bars2:
            ax2.annotate(f'{bar.get_height()}',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


    def show_conn_chart(self, rows, chart_frame):
        # Contar por estado, usando "Desconocido" si está vacío o None
        counts = Counter([str(r.get("Status") or "Desconocido") for r in rows])
        self._render_chart(counts, chart_frame,
                        "Conexiones por estado", "Estado", "Cantidad")


    def show_service_charts(self, rows, chart_frame):
        # Limpiar el frame de gráficas
        for widget in chart_frame.winfo_children():
            widget.destroy()

        # Contar servicios por estado
        counts_state = Counter([str(r.get("State") or "Desconocido") for r in rows])
        # Contar servicios por modo de arranque
        counts_startmode = Counter([str(r.get("StartMode") or "Desconocido") for r in rows])

        # Crear figura con dos subplots
        fig = Figure(figsize=(12, 5), dpi=100, constrained_layout=True)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        # --- Gráfico 1: Servicios por estado ---
        bars1 = ax1.bar(counts_state.keys(), counts_state.values(),
                        color="#1f77b4", edgecolor="black")
        ax1.set_title("Servicios por estado", fontsize=12, fontweight="bold")
        ax1.tick_params(axis="x", rotation=30)
        for bar in bars1:
            ax1.annotate(f'{bar.get_height()}',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

        # --- Gráfico 2: Servicios por modo de arranque ---
        bars2 = ax2.bar(counts_startmode.keys(), counts_startmode.values(),
                        color="#2ca02c", edgecolor="black")
        ax2.set_title("Servicios por modo de arranque", fontsize=12, fontweight="bold")
        ax2.tick_params(axis="x", rotation=30)
        for bar in bars2:
            ax2.annotate(f'{bar.get_height()}',
                        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

        # Mostrar en el frame
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def show_files_chart(self, rows, chart_frame):
        counts = Counter([r.get("Mtime", "Sin fecha")[:10]
                        for r in rows if r.get("Mtime")])
        self._render_chart(counts, chart_frame,
                        "Archivos recientes por fecha", "Fecha", "Cantidad")
