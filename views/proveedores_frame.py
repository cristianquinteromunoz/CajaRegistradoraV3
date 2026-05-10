# ============================================================
#  views/proveedores_frame.py
# ============================================================
import customtkinter as ctk
from tkinter import ttk, messagebox
from database.conexion import get_session
from servicios.proveedores_services import ProveedoresService


class ProveedoresFrame(ctk.CTkFrame):
    def __init__(self, parent, fuentes, estilos, colores, id_usuario=1, **kwargs):
        super().__init__(parent, **kwargs)
        self.F = fuentes
        self.E = estilos
        self.C = colores
        self.id_usuario = id_usuario

        self.session = get_session()
        self.svc     = ProveedoresService(self.session)

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

        ctk.CTkLabel(frame, text="Proveedores",
                     **self.E["label_titulo"]).grid(row=0, column=0, sticky="w")

        self.entrada_busqueda = ctk.CTkEntry(
            frame, placeholder_text="🔍  Buscar proveedor...", **self.E["entry"]
        )
        self.entrada_busqueda.grid(row=0, column=1, sticky="ew", padx=16)
        self.entrada_busqueda.bind("<KeyRelease>", self._buscar)

        botones = ctk.CTkFrame(frame, fg_color="transparent")
        botones.grid(row=0, column=2)

        ctk.CTkButton(botones, text="＋  Nuevo",
                      command=self._dialogo_nuevo,
                      **self.E["boton_primario"]).pack(side="left", padx=(0, 6))

        for texto, cmd, color, hover in [
            ("✎  Editar",    self._editar,    self.C["acento_secundario"], "#3d2760"),
            ("📦  Productos", self._productos, self.C["info"],              "#1565c0"),
            ("🛒  Órdenes",   self._ordenes,   self.C["exito"],             "#388e3c"),
            ("💳  Cuenta",    self._cuenta,    self.C["advertencia"],       "#e65100"),
            ("🗑  Eliminar",  self._eliminar,  self.C["error"],             "#c0392b"),
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
        style.configure("Prov.Treeview",
            background=self.C["fondo_secundario"], foreground=self.C["texto_primario"],
            fieldbackground=self.C["fondo_secundario"], rowheight=34,
            font=("Roboto", 12), borderwidth=0,
        )
        style.configure("Prov.Treeview.Heading",
            background=self.C["fondo_tarjeta"], foreground=self.C["texto_primario"],
            font=("Roboto", 12, "bold"), relief="flat",
        )
        style.map("Prov.Treeview",
            background=[("selected", self.C["acento"])],
            foreground=[("selected", "#ffffff")],
        )

        cols = ("id", "nombre", "telefono", "email", "direccion", "productos", "saldo")
        self.tabla = ttk.Treeview(contenedor, columns=cols,
                                  show="headings", style="Prov.Treeview", selectmode="browse")
        config = {
            "id":        ("ID",          50,  "center"),
            "nombre":    ("Nombre",      180, "w"),
            "telefono":  ("Teléfono",    110, "center"),
            "email":     ("Email",       180, "w"),
            "direccion": ("Dirección",   180, "w"),
            "productos": ("# Productos",  90, "center"),
            "saldo":     ("Saldo",       100, "center"),
        }
        for col, (titulo, ancho, anchor) in config.items():
            self.tabla.heading(col, text=titulo, anchor="center")
            self.tabla.column(col, width=ancho, anchor=anchor, minwidth=40)

        self.tabla.tag_configure("deuda",    foreground=self.C["error"])
        self.tabla.tag_configure("normal",   foreground=self.C["texto_primario"])

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
        proveedores = self.svc.obtener_todos()
        for p in proveedores:
            saldo     = self.svc.saldo_proveedor(p.id_proveedor)
            n_prods   = len(self.svc.productos_del_proveedor(p.id_proveedor))
            tag       = "deuda" if saldo > 0 else "normal"
            saldo_txt = f"${saldo:,.0f}" if saldo == 0 else (f"+${saldo:,.0f}" if saldo > 0 else f"-${abs(saldo):,.0f}")
            self.tabla.insert("", "end", tags=(tag,), values=(
                p.id_proveedor, p.nombre, p.telefono or "—",
                p.email or "—", p.direccion or "—", n_prods, saldo_txt,
            ))
        self.lbl_estado.configure(text=f"{len(proveedores)} proveedores")

    def _buscar(self, *_):
        texto = self.entrada_busqueda.get().strip()
        self.tabla.delete(*self.tabla.get_children())
        resultados = self.svc.buscar(texto) if texto else self.svc.obtener_todos()
        for p in resultados:
            saldo = self.svc.saldo_proveedor(p.id_proveedor)
            self.tabla.insert("", "end", values=(
                p.id_proveedor, p.nombre, p.telefono or "—",
                p.email or "—", p.direccion or "—",
                len(self.svc.productos_del_proveedor(p.id_proveedor)),
                f"${saldo:,.0f}",
            ))

    def _proveedor_seleccionado(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un proveedor.")
            return None
        return self.svc.obtener_por_id(self.tabla.item(sel[0])["values"][0])

    # ==========================================================
    #  DIÁLOGO CREAR / EDITAR
    # ==========================================================
    def _dialogo_nuevo(self):
        self._abrir_dialogo()

    def _editar(self):
        p = self._proveedor_seleccionado()
        if p:
            self._abrir_dialogo(p)

    def _abrir_dialogo(self, proveedor=None):
        d = ctk.CTkToplevel(self)
        d.title("Nuevo proveedor" if not proveedor else f"Editar — {proveedor.nombre}")
        d.geometry("420x380")
        d.resizable(False, False)
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text="Nuevo proveedor" if not proveedor else "Editar proveedor",
                     **self.E["label_titulo"]).pack(pady=(20, 12))

        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24)

        def campo(label, valor=""):
            ctk.CTkLabel(scroll, text=label, **self.E["label_cuerpo"]).pack(anchor="w")
            e = ctk.CTkEntry(scroll, **self.E["entry"])
            e.pack(fill="x", pady=(2, 10))
            if valor:
                e.insert(0, str(valor))
            return e

        e_nombre    = campo("Nombre *",    proveedor.nombre    if proveedor else "")
        e_telefono  = campo("Teléfono",    proveedor.telefono  if proveedor else "")
        e_email     = campo("Email",       proveedor.email     if proveedor else "")
        e_direccion = campo("Dirección",   proveedor.direccion if proveedor else "")

        def guardar():
            nombre = e_nombre.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio.", parent=d)
                return
            datos = {
                "nombre":    nombre,
                "telefono":  e_telefono.get().strip() or None,
                "email":     e_email.get().strip() or None,
                "direccion": e_direccion.get().strip() or None,
            }
            if proveedor:
                self.svc.actualizar(proveedor.id_proveedor, datos)
            else:
                self.svc.crear(datos)
            self._cargar_tabla()
            d.destroy()

        ctk.CTkButton(d, text="Guardar", command=guardar,
                      **self.E["boton_primario"]).pack(fill="x", padx=24, pady=(0, 20))

    # ==========================================================
    #  PRODUCTOS DEL PROVEEDOR
    # ==========================================================
    def _productos(self):
        p = self._proveedor_seleccionado()
        if not p:
            return

        d = ctk.CTkToplevel(self)
        d.title(f"Productos — {p.nombre}")
        d.geometry("500x380")
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text=f"Productos de {p.nombre}",
                     **self.E["label_titulo"]).pack(pady=(20, 12))

        cols = ("nombre", "categoria", "stock", "precio_compra")
        tabla = ttk.Treeview(d, columns=cols, show="headings",
                             style="Prov.Treeview", height=10)
        for col, titulo, ancho in [
            ("nombre",       "Nombre",       200),
            ("categoria",    "Categoría",    130),
            ("stock",        "Stock",         80),
            ("precio_compra","Precio compra", 110),
        ]:
            tabla.heading(col, text=titulo, anchor="center")
            tabla.column(col, width=ancho, anchor="center")
        tabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for prod in self.svc.productos_del_proveedor(p.id_proveedor):
            tabla.insert("", "end", values=(
                prod.nombre,
                prod.categoria.nombre if prod.categoria else "—",
                prod.stock_actual,
                f"${prod.precio_compra:,.0f}",
            ))

    # ==========================================================
    #  ÓRDENES DE COMPRA
    # ==========================================================
    def _ordenes(self):
        p = self._proveedor_seleccionado()
        if not p:
            return

        d = ctk.CTkToplevel(self)
        d.title(f"Órdenes — {p.nombre}")
        d.geometry("620x520")
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text="Historial de órdenes",
                     **self.E["label_titulo"]).pack(pady=(20, 4))
        ctk.CTkLabel(d, text=p.nombre, **self.E["label_subtitulo"]).pack(pady=(0, 10))

        # Tabla de órdenes
        cols = ("id", "fecha", "total", "estado")
        tabla_o = ttk.Treeview(d, columns=cols, show="headings",
                               style="Prov.Treeview", height=6)
        for col, titulo, ancho in [
            ("id",     "ID",      60), ("fecha",  "Fecha",   140),
            ("total",  "Total",  110), ("estado", "Estado",  100),
        ]:
            tabla_o.heading(col, text=titulo, anchor="center")
            tabla_o.column(col, width=ancho, anchor="center")
        tabla_o.pack(fill="x", padx=20, pady=(0, 8))

        tabla_o.tag_configure("pendiente", foreground=self.C["advertencia"])
        tabla_o.tag_configure("recibida",  foreground=self.C["exito"])
        tabla_o.tag_configure("cancelada", foreground=self.C["error"])

        def refrescar_ordenes():
            tabla_o.delete(*tabla_o.get_children())
            for o in self.svc.obtener_ordenes(p.id_proveedor):
                tabla_o.insert("", "end", iid=o.id_orden, tags=(o.estado,), values=(
                    o.id_orden,
                    o.fecha_orden.strftime("%Y-%m-%d %H:%M"),
                    f"${o.total:,.0f}",
                    o.estado.capitalize(),
                ))

        refrescar_ordenes()

        # Cambiar estado
        def cambiar_estado(estado):
            sel = tabla_o.selection()
            if not sel:
                messagebox.showwarning("Atención", "Selecciona una orden.", parent=d)
                return
            self.svc.cambiar_estado_orden(int(sel[0]), estado)
            refrescar_ordenes()

        btn_frame = ctk.CTkFrame(d, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkButton(btn_frame, text="✔ Marcar recibida",
                      command=lambda: cambiar_estado("recibida"),
                      fg_color=self.C["exito"], hover_color="#388e3c",
                      text_color="#fff", font=self.F["boton"],
                      corner_radius=8, height=36).pack(side="left", padx=(0, 8))

        ctk.CTkButton(btn_frame, text="✖ Cancelar orden",
                      command=lambda: cambiar_estado("cancelada"),
                      fg_color=self.C["error"], hover_color="#c0392b",
                      text_color="#fff", font=self.F["boton"],
                      corner_radius=8, height=36).pack(side="left")

        # Nueva orden
        ctk.CTkLabel(d, text="Nueva orden", **self.E["label_subtitulo"]).pack(
            anchor="w", padx=20, pady=(8, 4))

        form = ctk.CTkFrame(d, fg_color="transparent")
        form.pack(fill="x", padx=20)
        form.grid_columnconfigure((0, 1, 2), weight=1)

        productos = self.svc.productos_del_proveedor(p.id_proveedor)
        nombres_p = [pr.nombre for pr in productos]
        var_prod  = ctk.StringVar(value=nombres_p[0] if nombres_p else "")

        ctk.CTkLabel(form, text="Producto", **self.E["label_cuerpo"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(form, text="Cantidad", **self.E["label_cuerpo"]).grid(row=0, column=1, sticky="w", padx=8)
        ctk.CTkLabel(form, text="Precio unit.", **self.E["label_cuerpo"]).grid(row=0, column=2, sticky="w")

        ctk.CTkComboBox(form, values=nombres_p or ["(sin productos)"],
                        variable=var_prod, font=self.F["cuerpo_md"]).grid(
            row=1, column=0, sticky="ew", pady=4)
        e_cant  = ctk.CTkEntry(form, **self.E["entry"]); e_cant.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        e_prec  = ctk.CTkEntry(form, **self.E["entry"]); e_prec.grid(row=1, column=2, sticky="ew", pady=4)

        def crear_orden():
            try:
                prod_obj = next(pr for pr in productos if pr.nombre == var_prod.get())
                cant     = float(e_cant.get())
                precio   = float(e_prec.get())
            except (ValueError, StopIteration):
                messagebox.showerror("Error", "Completa los campos correctamente.", parent=d)
                return
            self.svc.crear_orden(
                id_proveedor = p.id_proveedor,
                id_usuario   = self.id_usuario,
                items        = [{"id_producto": prod_obj.id_producto,
                                 "cantidad": cant, "precio_unit": precio}],
            )
            refrescar_ordenes()
            e_cant.delete(0, "end")
            e_prec.delete(0, "end")

        ctk.CTkButton(d, text="＋ Crear orden", command=crear_orden,
                      **self.E["boton_primario"]).pack(fill="x", padx=20, pady=12)

    # ==========================================================
    #  CUENTA / SALDO
    # ==========================================================
    def _cuenta(self):
        p = self._proveedor_seleccionado()
        if not p:
            return

        d = ctk.CTkToplevel(self)
        d.title(f"Cuenta — {p.nombre}")
        d.geometry("560x500")
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        saldo = self.svc.saldo_proveedor(p.id_proveedor)
        ctk.CTkLabel(d, text="Estado de cuenta", **self.E["label_titulo"]).pack(pady=(20, 4))
        ctk.CTkLabel(d, text=p.nombre, **self.E["label_subtitulo"]).pack()
        ctk.CTkLabel(d, text=f"Saldo actual: ${saldo:,.0f}",
                     font=self.F["titulo_md"],
                     text_color=self.C["error"] if saldo > 0 else self.C["exito"]).pack(pady=(4, 12))

        # Historial
        cols = ("fecha", "concepto", "tipo", "monto", "saldo")
        tabla_c = ttk.Treeview(d, columns=cols, show="headings",
                               style="Prov.Treeview", height=7)
        for col, titulo, ancho in [
            ("fecha",    "Fecha",    120), ("concepto", "Concepto", 180),
            ("tipo",     "Tipo",      80), ("monto",    "Monto",     90),
            ("saldo",    "Saldo",     90),
        ]:
            tabla_c.heading(col, text=titulo, anchor="center")
            tabla_c.column(col, width=ancho, anchor="center")
        tabla_c.pack(fill="x", padx=20, pady=(0, 10))
        tabla_c.tag_configure("debito",  foreground=self.C["error"])
        tabla_c.tag_configure("credito", foreground=self.C["exito"])

        for m in self.svc.historial_cuenta(p.id_proveedor):
            tabla_c.insert("", "end", tags=(m.tipo,), values=(
                m.fecha.strftime("%Y-%m-%d"), m.concepto,
                m.tipo.capitalize(), f"${m.monto:,.0f}", f"${m.saldo:,.0f}",
            ))

        # Nuevo movimiento
        form = ctk.CTkFrame(d, fg_color="transparent")
        form.pack(fill="x", padx=20)
        form.grid_columnconfigure((0, 1, 2), weight=1)

        var_tipo = ctk.StringVar(value="debito")
        ctk.CTkLabel(form, text="Concepto", **self.E["label_cuerpo"]).grid(row=0, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(form, text="Monto",    **self.E["label_cuerpo"]).grid(row=0, column=2, sticky="w", padx=8)

        e_concepto = ctk.CTkEntry(form, **self.E["entry"])
        e_concepto.grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)
        e_monto = ctk.CTkEntry(form, **self.E["entry"])
        e_monto.grid(row=1, column=2, sticky="ew", padx=(8, 0), pady=4)

        tipo_frame = ctk.CTkFrame(d, fg_color="transparent")
        tipo_frame.pack(fill="x", padx=20, pady=(4, 0))
        ctk.CTkRadioButton(tipo_frame, text="Débito (deuda)",
                           value="debito", variable=var_tipo,
                           fg_color=self.C["error"], font=self.F["cuerpo_md"],
                           text_color=self.C["texto_primario"]).pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(tipo_frame, text="Crédito (pago)",
                           value="credito", variable=var_tipo,
                           fg_color=self.C["exito"], font=self.F["cuerpo_md"],
                           text_color=self.C["texto_primario"]).pack(side="left")

        def registrar():
            try:
                monto    = float(e_monto.get())
                concepto = e_concepto.get().strip()
                if not concepto:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Completa los campos.", parent=d)
                return
            self.svc.registrar_movimiento(p.id_proveedor, concepto, monto, var_tipo.get())
            self._cargar_tabla()
            d.destroy()

        ctk.CTkButton(d, text="Registrar movimiento", command=registrar,
                      **self.E["boton_primario"]).pack(fill="x", padx=20, pady=12)

    # ==========================================================
    #  ELIMINAR
    # ==========================================================
    def _eliminar(self):
        p = self._proveedor_seleccionado()
        if not p:
            return
        if messagebox.askyesno("Confirmar", f"¿Desactivar a '{p.nombre}'?"):
            self.svc.desactivar(p.id_proveedor)
            self._cargar_tabla()