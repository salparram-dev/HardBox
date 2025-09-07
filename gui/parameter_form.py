# gui/parameter_form.py
import customtkinter as ctk
from tkinter import BOTH, RIGHT, LEFT, Y

class ParameterForm(ctk.CTkToplevel):
    def __init__(self, parent, section_name, params, on_submit, sections_list=None):
        super().__init__(parent)

        # Buscar nombre bonito en SECTIONS
        display_name = section_name
        if sections_list:
            for nice_name, base in sections_list:
                if base == section_name:
                    display_name = nice_name
                    break

        self.title(f"Configurar parámetros: {display_name}")
        self.geometry("500x600")
        self.minsize(400, 400)
        self.resizable(True, True)

        self.entries = {}
        self.on_submit = on_submit

        # Frame con scroll
        container = ctk.CTkFrame(self)
        container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        canvas = ctk.CTkCanvas(container, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
        scroll_frame = ctk.CTkFrame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Título
        title_label = ctk.CTkLabel(
            scroll_frame,
            text=f"Parámetros para {display_name}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=15)

        # Nota explicativa
        note_label = ctk.CTkLabel(
            scroll_frame,
            text="⭐ Los valores que aparecen al iniciar son los recomendados",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        )
        note_label.pack(pady=(0, 10))

        # Campos dinámicos
        for p in params:
            # Si es checkbox (services, auditing, etc.)
            if p.get("type") == "checkbox" or "type" not in p:
                var = ctk.BooleanVar(value=True)  # por defecto marcados
                chk = ctk.CTkCheckBox(scroll_frame, text=p["label"], variable=var)
                chk.pack(anchor="w", padx=10, pady=5)
                self.entries[p["name"]] = (var, "checkbox")
                continue

            frame = ctk.CTkFrame(scroll_frame)
            frame.pack(fill="x", padx=5, pady=5)

            # Label limpio, sin (Recomendado) ni color
            label = ctk.CTkLabel(frame, text=p["label"])
            label.pack(anchor="w", pady=(0, 2))

            if p.get("type") == "bool":
                var = ctk.StringVar()
                values_list = []
                default_bool = bool(p["default"])
                for opt in ["Habilitado", "Deshabilitado"]:
                    if (opt == "Habilitado" and default_bool) or (opt == "Deshabilitado" and not default_bool):
                        values_list.append(f"{opt} (Recomendado)")
                        var.set(f"{opt} (Recomendado)")
                    else:
                        values_list.append(opt)

                option = ctk.CTkOptionMenu(frame, values=values_list, variable=var)
                if p.get("readonly"):
                    option.configure(state="disabled")
                    self.entries[p["name"]] = (p["default"], "readonly")
                else:
                    self.entries[p["name"]] = (option, "bool")
                option.pack(fill="x")

            elif p.get("type") == "choice":
                var = ctk.StringVar()
                display_choices = []
                for k, v in p["choices"].items():
                    if v == p["default"]:
                        display_choices.append(f"{k} (Recomendado)")
                        var.set(f"{k} (Recomendado)")
                    else:
                        display_choices.append(k)
                option = ctk.CTkOptionMenu(frame, values=display_choices, variable=var)
                option.pack(fill="x")
                self.entries[p["name"]] = (option, "choice", p["choices"])

            else:
                entry = ctk.CTkEntry(frame)
                entry.insert(0, str(p["default"]))
                entry.pack(fill="x")
                self.entries[p["name"]] = (entry, "text")

            if p.get("note"):
                note_label = ctk.CTkLabel(frame, text=p["note"],
                                          font=ctk.CTkFont(size=10, slant="italic"),
                                          text_color="gray")
                note_label.pack(anchor="w", pady=(2, 0))

        # Botones
        btn_frame = ctk.CTkFrame(scroll_frame)
        btn_frame.pack(pady=20)

        apply_btn = ctk.CTkButton(
            btn_frame,
            text="Aplicar",
            fg_color="#4CAF50",
            hover_color="#45A049",
            command=self.submit
        )
        apply_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            fg_color="#f44336",
            hover_color="#e53935",
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=10)

        # Modal
        self.transient(parent)
        self.grab_set()
        self.focus_force()

    def submit(self):
        values = {}
        for name, widget_info in self.entries.items():
            wtype = widget_info[1]

            if wtype == "checkbox":
                if widget_info[0].get():
                    values[name] = True

            elif wtype == "bool":
                sel = widget_info[0].get().replace(" (Recomendado)", "")
                values[name] = 1 if sel == "Habilitado" else 0

            elif wtype == "choice":
                selected_label = widget_info[0].get().replace(" (Recomendado)", "")
                choices_map = widget_info[2]
                values[name] = choices_map[selected_label]

            elif wtype == "text":
                val = widget_info[0].get().strip()
                if val.isdigit():
                    val = int(val)
                values[name] = val

            elif wtype == "readonly":
                values[name] = widget_info[0]

        self.on_submit(values)
        self.destroy()
