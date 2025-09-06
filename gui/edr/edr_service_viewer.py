# gui/edr/edr_service_window.py
import customtkinter as ctk
from tkinter import messagebox, ttk
import subprocess
import json
from collections import Counter
from utils.logger import log_action
from utils.window_utils import top_focus

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class VelociraptorServiceWindow(ctk.CTkToplevel):
    _instance = None  # Singleton global

    @classmethod
    def open(cls, master=None):
        """Crea o restaura la ventana singleton de servicio Velociraptor"""
        if cls._instance is None or not cls._instance.winfo_exists():
            cls._instance = cls(master=None)
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

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # === Tabview ===
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Pestañas consultas  ---
        self.tab_users = self.tabview.add("Usuarios")
        self.tab_procs = self.tabview.add("Procesos")
        self.tab_conns = self.tabview.add("Conexiones")
        self.tab_services = self.tabview.add("Servicios")
        self.tab_files = self.tabview.add("Archivos recientes")

        # Queries
        users_query = "SELECT SID, Name, Disabled, Lockout, LocalAccount FROM wmi(query='SELECT * FROM Win32_UserAccount')"
        process_query = "SELECT Name,Pid,Username FROM pslist()"
        conn_query = "SELECT Laddr.IP,Laddr.Port,Raddr.IP,Raddr.Port,Status,TypeString FROM netstat()"
        serv_query = ("SELECT Name,DisplayName,State,StartMode "
                      "FROM wmi(query='SELECT Name, DisplayName, State, StartMode FROM Win32_Service', namespace='root/CIMV2')")
        files_query = (
            "SELECT Name, Mtime, OSPath FROM glob(globs='C:\\\\Users\\\\**', accessor='file') "
            "WHERE NOT IsDir AND Size > 0 AND Mtime > now() - 30*24*60*60 "
            "AND Name =~ '(?i)\\.(py|exe|dll|bat|ps1|vbs|js|jar|cmd|msi|scr|com|doc|docx|xls|xlsx|ppt|pptx|pdf|rtf|txt|csv|zip|rar|7z|gz"
            "|tar|iso|img|bin|dat|cfg|ini|conf|xml|json|png|jpg|jpeg|gif|bmp|tiff|svg|mp3|wav|mp4|avi|mkv)$' "
            "ORDER BY Mtime DESC LIMIT 500"
        )

        # Inicializar pestañas
        self._init_query_tab(self.tab_users, "Usuarios", users_query, self.show_users_charts)
        self._init_query_tab(self.tab_procs, "Procesos", process_query, self.show_process_charts)
        self._init_query_tab(self.tab_conns, "Conexiones", conn_query, self.show_conn_chart)
        self._init_query_tab(self.tab_services, "Servicios", serv_query, self.show_service_charts)
        self._init_query_tab(self.tab_files, "Archivos", files_query, self.show_files_chart)

        # Estilo moderno
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white",
                        fieldbackground="#2b2b2b", rowheight=25, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background="#444", foreground="white",
                        font=("Segoe UI", 12, "bold"))
        style.map("Treeview", background=[("selected", "#1f6aa5")])

        # Consultas iniciales
        self.after(500, lambda: self.run_query(users_query, self.tab_users, self.show_users_charts))
        self.after(1000, lambda: self.run_query(process_query, self.tab_procs, self.show_process_charts))
        self.after(1500, lambda: self.run_query(conn_query, self.tab_conns, self.show_conn_chart))
        self.after(2000, lambda: self.run_query(serv_query, self.tab_services, self.show_service_charts))
        self.after(2500, lambda: self.run_query(files_query, self.tab_files, self.show_files_chart))

    # ---------------- MÉTODOS AUXILIARES ----------------
    def _init_query_tab(self, parent, label, query, chart_callback):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn = ctk.CTkButton(
            frame,
            text=f"Refrescar {label}",
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=lambda: self.run_query(query, parent, chart_callback)
        )
        btn.pack(pady=5)
        if label == "Archivos":
            hash_btn = ctk.CTkButton(
                frame,
                text="Calcular hash del archivo seleccionado",
                fg_color="#4CAF50",
                hover_color="#45A049",
                command=lambda: self.calculate_file_hash(parent)
            )
            hash_btn.pack(pady=5)


        # --- Frame para Treeview + Scrollbars ---
        tree_frame = ctk.CTkFrame(frame)
        tree_frame.pack(fill="both", expand=True, pady=10)

        # Scroll vertical
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Scroll horizontal
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        # Treeview
        tree = ttk.Treeview(
            tree_frame,
            show="headings",
            height=10,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        tree.pack(side="left", fill="both", expand=True)

        # Vincular scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        setattr(parent, "tree", tree)

        chart_frame = ctk.CTkFrame(frame)
        chart_frame.pack(fill="both", expand=True, pady=5)
        setattr(parent, "chart_frame", chart_frame)



    def on_close(self):
        VelociraptorServiceWindow._instance = None
        self.destroy()
    
    def run_query(self, query: str, tab, chart_callback):
        """Ejecuta consultas VQL y muestra resultados en tabla y gráfica"""
        try:
            cmd = f'velociraptor query "{query}" --format jsonl'

            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
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
                            row[k] = v.strip()
                    rows.append(row)
                except json.JSONDecodeError:
                    continue

            if not rows:
                return

            tree = getattr(tab, "tree")

            # Guardar anchos actuales antes de tocar columnas
            current_widths = {}
            if tree["columns"]:
                current_widths = {col: tree.column(col, "width") for col in tree["columns"]}

            headers = {
                "SID": "Identificador",
                "Name": "Nombre",
                "Disabled": "Deshabilitado",
                "Lockout": "Bloqueado",
                "LocalAccount": "Cuenta local",
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
                "OSPath": "Ruta",
            }

            # Determinar nuevas columnas
            new_cols = list(rows[0].keys())

            # Solo redefinir columnas si han cambiado
            if list(tree["columns"]) != new_cols:
                tree["columns"] = new_cols
                for col in tree["columns"]:
                    col_title = headers.get(col, col)
                    tree.heading(col, text=col_title)
                    tree.column(
                        col,
                        width=current_widths.get(col, 650),
                        anchor="center"
                    )

            # Limpiar filas
            for item in tree.get_children():
                tree.delete(item)

            # Insertar nuevas filas
            for row in rows:
                if "Disabled" in row:
                    row["Disabled"] = "Sí" if row["Disabled"] else "No"
                if "Lockout" in row:
                    row["Lockout"] = "Sí" if row["Lockout"] else "No"
                if "LocalAccount" in row:
                    row["LocalAccount"] = "Sí" if row["LocalAccount"] else "No"

                tree.insert("", "end", values=[row.get(col, "") for col in tree["columns"]])

            chart_callback(rows, getattr(tab, "chart_frame"))

        except Exception as e:
            messagebox.showerror("Error", f"Error ejecutando consulta: {e}", parent=self)

    def calculate_file_hash(self, tab):
        tree = getattr(tab, "tree")
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Hash", "Selecciona un archivo primero.", parent=self)
            return

        # Obtener valores de la fila seleccionada
        values = tree.item(selected[0], "values")
        cols = tree["columns"]
        row = dict(zip(cols, values))
        filepath = row.get("OSPath")
        filepath = filepath.replace("\\", "/")


        if not filepath:
            messagebox.showerror("Hash", "No se pudo obtener la ruta del archivo.", parent=self)
            return

        try:
            # Query de Velociraptor para calcular hashes
            query = f"SELECT hash(path=OSPath) AS Hashes FROM glob(globs='{filepath}')"
            cmd = f'velociraptor query "{query}" --format jsonl'

            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
                text=True,
                shell=True
            )

            output = result.stdout.strip().splitlines()
            if not output:
                messagebox.showinfo("Hash", "No se pudo calcular el hash.", parent=self)
                return
            hash_data = json.loads(output[0])['Hashes']

            # Crear ventana emergente para mostrar y copiar hashes
            hash_window = ctk.CTkToplevel(self)
            top_focus(hash_window)
            hash_window.title("Hashes del archivo")
            hash_window.geometry("700x300")

            msg = (
                f"Archivo: {filepath}\n\n"
                f"MD5: {hash_data.get('MD5')}\n"
                f"SHA1: {hash_data.get('SHA1')}\n"
                f"SHA256: {hash_data.get('SHA256')}"
            )

            # Campo de texto donde se puede seleccionar y copiar
            text_box = ctk.CTkTextbox(hash_window, wrap="word", width=650, height=200)
            text_box.insert("1.0", msg)
            text_box.configure(state="disabled")
            text_box.pack(padx=10, pady=10, fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"Error calculando hash: {e}", parent=self)


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

    def show_users_charts(self, rows, chart_frame):
        for widget in chart_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(12, 5), dpi=100, constrained_layout=True)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        # Gráfico 1 → Local vs Dominio
        counts_local = Counter(
            ["Local" if r.get("LocalAccount") == "Sí" else "Dominio" for r in rows]
        )
        ax1.bar(counts_local.keys(), counts_local.values(),
                color=["#4CAF50", "#2196F3"], edgecolor="black")
        ax1.set_title("Usuarios locales vs dominio", fontsize=12, fontweight="bold")

        # Gráfico 2 → Habilitados vs Deshabilitados
        enabled = sum(1 for r in rows if r.get("Disabled") == "No")
        disabled = sum(1 for r in rows if r.get("Disabled") == "Sí")
        ax2.pie([enabled, disabled],
                labels=["Habilitados", "Deshabilitados"],
                colors=["#4CAF50", "#f44336"],
                autopct='%1.1f%%',
                startangle=90)
        ax2.set_title("Usuarios habilitados vs deshabilitados", fontsize=12, fontweight="bold")

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
                        color="#4CAF50", edgecolor="black")
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
