# ============================================================
#  views/personal_frame.py
# ============================================================
import customtkinter as ctk
from tkinter import ttk, messagebox
from database.conexion import get_session
from servicios.personal_service import PersonalService
from servicios.usuarios_services import UsuariosService

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


class PersonalFrame(ctk.CTkFrame):
    def __init__(self, parent, fuentes, estilos, colores, **kwargs):
        super().__init__(parent, **kwargs)
        self.F = fuentes
        self.E = estilos
        self.C = colores

        self.session  = get_session()
        self.svc      = PersonalService(self.session)
        self.usr_svc  = UsuariosService(self.session)

        self._construir_ui()
        self._cargar_tabla()

    # ==========================================================
    #  UI
    # ==========================================================
    def _construir_ui(self):
        self.configure(fg_color=self.C["fondo_principal"])
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_encabezado()
        self._construir_tabla()
        self._construir_barra_estado()

    def _construir_encabezado(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Gestión de Personal",
                     **self.E["label_titulo"]).grid(row=0, column=0, sticky="w")

        # Buscador
        self.entrada_busqueda = ctk.CTkEntry(
            frame, placeholder_text="🔍  Buscar por nombre o usuario...",
            **self.E["entry"]
        )
        self.entrada_busqueda.grid(row=0, column=1, sticky="ew", padx=16)
        self.entrada_busqueda.bind("<KeyRelease>", self._buscar)

        # Botones
        botones = ctk.CTkFrame(frame, fg_color="transparent")
        botones.grid(row=0, column=2)

        ctk.CTkButton(botones, text="＋  Nuevo",
                      command=self._dialogo_nuevo,
                      **self.E["boton_primario"]).pack(side="left", padx=(0, 8))

        for texto, cmd, color, hover in [
            ("✎  Editar",    self._editar,   self.C["acento_secundario"], "#3d2760"),
            ("📅  Turnos",   self._turnos,   self.C["info"],              "#1565c0"),
            ("💰  Nómina",   self._nomina,   self.C["exito"],             "#388e3c"),
            ("📋  Accesos",  self._accesos,  self.C["fondo_tarjeta"],     self.C["borde"]),
            ("🗑  Eliminar", self._eliminar, self.C["error"],             "#c0392b"),
        ]:
            ctk.CTkButton(
                botones, text=texto, command=cmd,
                fg_color=color, hover_color=hover,
                text_color=self.C["texto_primario"],
                font=self.F["boton"], corner_radius=8, height=40,
            ).pack(side="left", padx=(0, 6))

    def _construir_tabla(self):
        contenedor = ctk.CTkFrame(self, **self.E["frame_tarjeta"])
        contenedor.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Per.Treeview",
            background=self.C["fondo_secundario"],
            foreground=self.C["texto_primario"],
            fieldbackground=self.C["fondo_secundario"],
            rowheight=34, font=("Roboto", 12), borderwidth=0,
        )
        style.configure("Per.Treeview.Heading",
            background=self.C["fondo_tarjeta"],
            foreground=self.C["texto_primario"],
            font=("Roboto", 12, "bold"), relief="flat",
        )
        style.map("Per.Treeview",
            background=[("selected", self.C["acento"])],
            foreground=[("selected", "#ffffff")],
        )

        cols = ("id", "nombre", "apellido", "username", "rol", "email", "ultimo_acceso", "estado")
        self.tabla = ttk.Treeview(contenedor, columns=cols,
                                  show="headings", style="Per.Treeview", selectmode="browse")
        config = {
            "id":            ("ID",            50,  "center"),
            "nombre":        ("Nombre",        130, "w"),
            "apellido":      ("Apellido",      130, "w"),
            "username":      ("Usuario",       110, "center"),
            "rol":           ("Rol",           120, "center"),
            "email":         ("Email",         180, "w"),
            "ultimo_acceso": ("Último acceso", 150, "center"),
            "estado":        ("Estado",         80, "center"),
        }
        for col, (titulo, ancho, anchor) in config.items():
            self.tabla.heading(col, text=titulo, anchor="center")
            self.tabla.column(col, width=ancho, anchor=anchor, minwidth=40)

        self.tabla.tag_configure("activo",   foreground=self.C["texto_primario"])
        self.tabla.tag_configure("inactivo", foreground=self.C["texto_desactivado"])

        scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        self.tabla.bind("<Double-1>", lambda e: self._editar())

    def _construir_barra_estado(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
        self.lbl_estado = ctk.CTkLabel(frame, text="", **self.E["label_subtitulo"])
        self.lbl_estado.pack(side="left")

    # ==========================================================
    #  CARGA
    # ==========================================================
    def _cargar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        usuarios = self.svc.obtener_todos(solo_activos=False)
        for u in usuarios:
            acceso = u.ultimo_acceso.strftime("%Y-%m-%d %H:%M") if u.ultimo_acceso else "—"
            tag    = "activo" if u.activo else "inactivo"
            self.tabla.insert("", "end", tags=(tag,), values=(
                u.id_usuario,
                u.nombre,
                u.apellido,
                u.username,
                u.rol.nombre if u.rol else "—",
                u.email or "—",
                acceso,
                "Activo" if u.activo else "Inactivo",
            ))
        self.lbl_estado.configure(text=f"{len(usuarios)} empleados registrados")

    def _buscar(self, *_):
        texto = self.entrada_busqueda.get().strip()
        self.tabla.delete(*self.tabla.get_children())
        resultados = self.svc.buscar(texto) if texto else self.svc.obtener_todos(solo_activos=False)
        for u in resultados:
            acceso = u.ultimo_acceso.strftime("%Y-%m-%d %H:%M") if u.ultimo_acceso else "—"
            self.tabla.insert("", "end", values=(
                u.id_usuario, u.nombre, u.apellido, u.username,
                u.rol.nombre if u.rol else "—", u.email or "—", acceso,
                "Activo" if u.activo else "Inactivo",
            ))

    # ==========================================================
    #  HELPERS
    # ==========================================================
    def _usuario_seleccionado(self) -> "Usuario | None":
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un empleado.")
            return None
        id_u = self.tabla.item(sel[0])["values"][0]
        return self.svc.obtener_por_id(id_u)

    # ==========================================================
    #  DIÁLOGO CREAR / EDITAR
    # ==========================================================
    def _dialogo_nuevo(self):
        self._abrir_dialogo()

    def _editar(self):
        u = self._usuario_seleccionado()
        if u:
            self._abrir_dialogo(u)

    def _abrir_dialogo(self, usuario=None):
        d = ctk.CTkToplevel(self)
        d.title("Nuevo empleado" if not usuario else f"Editar — {usuario.nombre}")
        d.geometry("440x500")
        d.resizable(False, False)
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text="Nuevo empleado" if not usuario else "Editar empleado",
                     **self.E["label_titulo"]).pack(pady=(20, 12))

        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24)

        def campo(label, valor="", show=""):
            ctk.CTkLabel(scroll, text=label, **self.E["label_cuerpo"]).pack(anchor="w")
            e = ctk.CTkEntry(scroll, show=show, **self.E["entry"])
            e.pack(fill="x", pady=(2, 10))
            if valor:
                e.insert(0, str(valor))
            return e

        e_nombre   = campo("Nombre *",   usuario.nombre   if usuario else "")
        e_apellido = campo("Apellido *", usuario.apellido if usuario else "")
        e_email    = campo("Email",      usuario.email    if usuario else "")
        e_username = campo("Usuario *",  usuario.username if usuario else "")
        e_password = campo("Contraseña" + (" (dejar vacío = no cambiar)" if usuario else " *"), show="*")

        ctk.CTkLabel(scroll, text="Rol *", **self.E["label_cuerpo"]).pack(anchor="w")
        roles     = self.usr_svc.obtener_roles()
        nombres_r = [r.nombre for r in roles]
        var_rol   = ctk.StringVar(value=usuario.rol.nombre if usuario and usuario.rol else (nombres_r[0] if nombres_r else ""))
        ctk.CTkComboBox(scroll, values=nombres_r, variable=var_rol,
                        font=self.F["cuerpo_md"]).pack(fill="x", pady=(2, 10))

        if usuario:
            var_activo = ctk.BooleanVar(value=usuario.activo)
            ctk.CTkCheckBox(scroll, text="Empleado activo", variable=var_activo,
                            font=self.F["cuerpo_md"], text_color=self.C["texto_primario"],
                            fg_color=self.C["acento"]).pack(anchor="w", pady=(0, 10))

        def guardar():
            nombre   = e_nombre.get().strip()
            apellido = e_apellido.get().strip()
            username = e_username.get().strip()
            password = e_password.get().strip()
            if not nombre or not apellido or not username:
                messagebox.showerror("Error", "Completa los campos obligatorios (*).", parent=d)
                return
            rol_obj = next((r for r in roles if r.nombre == var_rol.get()), None)

            if usuario:
                datos = {"nombre": nombre, "apellido": apellido,
                         "email": e_email.get().strip(), "id_rol": rol_obj.id_rol if rol_obj else None,
                         "activo": var_activo.get()}
                self.usr_svc.actualizar(usuario.id_usuario, datos)
                if password:
                    self.usr_svc.cambiar_password(usuario.id_usuario, password)
            else:
                if not password:
                    messagebox.showerror("Error", "La contraseña es obligatoria.", parent=d)
                    return
                self.usr_svc.crear({
                    "nombre": nombre, "apellido": apellido,
                    "email": e_email.get().strip(), "username": username,
                    "password": password, "id_rol": rol_obj.id_rol if rol_obj else None,
                })
            self._cargar_tabla()
            d.destroy()

        ctk.CTkButton(d, text="Guardar", command=guardar,
                      **self.E["boton_primario"]).pack(fill="x", padx=24, pady=(0, 20))

    # ==========================================================
    #  TURNOS
    # ==========================================================
    def _turnos(self):
        u = self._usuario_seleccionado()
        if not u:
            return

        d = ctk.CTkToplevel(self)
        d.title(f"Turnos — {u.nombre} {u.apellido}")
        d.geometry("500x520")
        d.resizable(False, False)
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text="Horario semanal", **self.E["label_titulo"]).pack(pady=(20, 4))
        ctk.CTkLabel(d, text=f"{u.nombre} {u.apellido}", **self.E["label_subtitulo"]).pack(pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24)

        turnos_actuales = {t.dia_semana: t for t in self.svc.obtener_turnos(u.id_usuario)}
        entradas = {}

        for dia in DIAS:
            fila = ctk.CTkFrame(scroll, fg_color="transparent")
            fila.pack(fill="x", pady=4)
            fila.grid_columnconfigure(1, weight=1)
            fila.grid_columnconfigure(2, weight=1)

            t = turnos_actuales.get(dia)
            var_activo = ctk.BooleanVar(value=bool(t))

            ctk.CTkCheckBox(fila, text=dia, variable=var_activo,
                            font=self.F["cuerpo_md"], text_color=self.C["texto_primario"],
                            fg_color=self.C["acento"], width=110).grid(row=0, column=0, sticky="w")

            e_ini = ctk.CTkEntry(fila, placeholder_text="08:00", width=90, **self.E["entry"])
            e_fin = ctk.CTkEntry(fila, placeholder_text="17:00", width=90, **self.E["entry"])
            e_ini.grid(row=0, column=1, padx=8)
            e_fin.grid(row=0, column=2)

            if t:
                e_ini.insert(0, t.hora_inicio)
                e_fin.insert(0, t.hora_fin)

            entradas[dia] = (var_activo, e_ini, e_fin)

        def guardar():
            turnos = []
            for dia, (var, e_ini, e_fin) in entradas.items():
                if var.get():
                    hi = e_ini.get().strip()
                    hf = e_fin.get().strip()
                    if not hi or not hf:
                        messagebox.showerror("Error", f"Completa las horas del {dia}.", parent=d)
                        return
                    turnos.append({"dia_semana": dia, "hora_inicio": hi, "hora_fin": hf})
            self.svc.guardar_turnos(u.id_usuario, turnos)
            messagebox.showinfo("✔", "Turnos guardados.", parent=d)
            d.destroy()

        ctk.CTkButton(d, text="Guardar turnos", command=guardar,
                      **self.E["boton_primario"]).pack(fill="x", padx=24, pady=16)

    # ==========================================================
    #  NÓMINA
    # ==========================================================
    def _nomina(self):
        u = self._usuario_seleccionado()
        if not u:
            return

        d = ctk.CTkToplevel(self)
        d.title(f"Nómina — {u.nombre} {u.apellido}")
        d.geometry("840x720")
        #d.resizable(False, False)
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text="Registro de nómina", **self.E["label_titulo"]).pack(pady=(20, 4))
        ctk.CTkLabel(d, text=f"{u.nombre} {u.apellido}", **self.E["label_subtitulo"]).pack(pady=(0, 10))

        # Historial
        hist_frame = ctk.CTkFrame(d, **self.E["frame_tarjeta"])
        hist_frame.pack(fill="x", padx=24, pady=(0, 12))

        cols = ("periodo", "salario", "bono", "deduc", "total", "fecha")
        tabla_n = ttk.Treeview(hist_frame, columns=cols, show="headings",
                               style="Per.Treeview", height=5)
        for col, titulo, ancho in [
            ("periodo", "Período",  90), ("salario", "Salario",  100),
            ("bono",    "Bono",     80), ("deduc",   "Deduc.",    80),
            ("total",   "Total",   100), ("fecha",   "Fecha pago",120),
        ]:
            tabla_n.heading(col, text=titulo, anchor="center")
            tabla_n.column(col, width=ancho, anchor="center")
        tabla_n.pack(fill="x", padx=8, pady=8)

        for n in self.svc.obtener_nomina(u.id_usuario):
            tabla_n.insert("", "end", values=(
                n.periodo, f"${n.salario_base:,.0f}", f"${n.bonificacion:,.0f}",
                f"${n.deducciones:,.0f}", f"${n.total_pago:,.0f}",
                n.fecha_pago.strftime("%Y-%m-%d"),
            ))

        # Formulario nuevo pago
        form = ctk.CTkFrame(d, fg_color="transparent")
        form.pack(fill="x", padx=24)
        form.grid_columnconfigure((0, 1), weight=1)

        def campo_form(fila, col, label, placeholder=""):
            ctk.CTkLabel(form, text=label, **self.E["label_cuerpo"]).grid(
                row=fila*2, column=col, sticky="w", pady=(6, 0))
            e = ctk.CTkEntry(form, placeholder_text=placeholder, **self.E["entry"])
            e.grid(row=fila*2+1, column=col, sticky="ew", padx=(0, 8) if col == 0 else 0)
            return e

        from datetime import datetime
        e_periodo = campo_form(0, 0, "Período *", f"{datetime.now().strftime('%Y-%m')}")
        e_salario = campo_form(0, 1, "Salario base *", "0")
        e_bono    = campo_form(1, 0, "Bonificación",   "0")
        e_deduc   = campo_form(1, 1, "Deducciones",    "0")

        ctk.CTkLabel(form, text="Observaciones", **self.E["label_cuerpo"]).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(6, 0))
        e_obs = ctk.CTkEntry(form, **self.E["entry"])
        e_obs.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(2, 12))

        def registrar():
            try:
                datos = {
                    "id_usuario":   u.id_usuario,
                    "salario_base": float(e_salario.get()),
                    "bonificacion": float(e_bono.get() or 0),
                    "deducciones":  float(e_deduc.get() or 0),
                    "periodo":      e_periodo.get().strip(),
                    "observaciones": e_obs.get().strip(),
                }
                if not datos["periodo"]:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Verifica los campos.", parent=d)
                return
            self.svc.registrar_pago_nomina(datos)
            messagebox.showinfo("✔", "Pago registrado.", parent=d)
            d.destroy()

        ctk.CTkButton(d, text="Registrar pago", command=registrar,
                      **self.E["boton_primario"]).pack(fill="x", padx=24, pady=(0, 20))

    # ==========================================================
    #  HISTORIAL DE ACCESOS
    # ==========================================================
    def _accesos(self):
        u = self._usuario_seleccionado()
        if not u:
            return
        acceso = u.ultimo_acceso.strftime("%Y-%m-%d %H:%M:%S") if u.ultimo_acceso else "Sin accesos registrados"
        messagebox.showinfo(
            f"Último acceso — {u.nombre}",
            f"Usuario: {u.username}\nRol: {u.rol.nombre if u.rol else '—'}\nÚltimo acceso: {acceso}"
        )

    # ==========================================================
    #  ELIMINAR
    # ==========================================================
    def _eliminar(self):
        u = self._usuario_seleccionado()
        if not u:
            return
        if messagebox.askyesno("Confirmar", f"¿Desactivar a '{u.nombre} {u.apellido}'?"):
            self.usr_svc.desactivar(u.id_usuario)
            self._cargar_tabla()