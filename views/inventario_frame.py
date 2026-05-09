# ============================================================
#  views/inventario_frame.py
# ============================================================
import customtkinter as ctk
from tkinter import ttk, messagebox
from database.conexion import get_session
from servicios.productos_services import ProductosService


class InventarioFrame(ctk.CTkFrame):
    def __init__(self, parent, fuentes, estilos, colores, **kwargs):
        super().__init__(parent, **kwargs)
        self.F = fuentes
        self.E = estilos
        self.C = colores

        self.session  = get_session()
        self.svc      = ProductosService(self.session)
        self.productos = []

        self._construir_ui()
        self._cargar_tabla()

    # ==========================================================
    #  UI PRINCIPAL
    # ==========================================================
    def _construir_ui(self):
        self.configure(fg_color=self.C["fondo_principal"])
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_encabezado()
        self._construir_filtros()
        self._construir_tabla()
        self._construir_barra_estado()

    # ----------------------------------------------------------
    def _construir_encabezado(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Inventario de Productos",
            **self.E["label_titulo"]
        ).grid(row=0, column=0, sticky="w")

        # Botones
        botones = ctk.CTkFrame(frame, fg_color="transparent")
        botones.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            botones, text="＋  Nuevo producto",
            command=self._dialogo_nuevo,
            **self.E["boton_primario"]
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botones, text="✎  Modificar",
            command=self._modificar,
            **self.E["boton_secundario"]
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botones, text="📦  Presentaciones",
            command=self._gestionar_presentaciones,
            font=self.F["boton"],
            fg_color=self.C["acento_secundario"],
            hover_color="#3d2760",
            text_color=self.C["texto_primario"],
            corner_radius=8,
            height=40,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botones, text="🗑  Eliminar",
            command=self._eliminar,
            font=self.F["boton"],
            fg_color=self.C["error"],
            hover_color="#c0392b",
            text_color=self.C["texto_primario"],
            corner_radius=8,
            height=40,
        ).pack(side="left")

    # ----------------------------------------------------------
    def _construir_filtros(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=12)
        frame.grid_columnconfigure(1, weight=1)

        # Buscador
        ctk.CTkLabel(frame, text="Buscar:", **self.E["label_cuerpo"]).grid(
            row=0, column=0, padx=(0, 8)
        )
        self.entrada_busqueda = ctk.CTkEntry(
            frame, placeholder_text="Nombre del producto...",
            **self.E["entry"]
        )
        self.entrada_busqueda.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.entrada_busqueda.bind("<KeyRelease>", self._buscar)

        # Filtro categoría
        ctk.CTkLabel(frame, text="Categoría:", **self.E["label_cuerpo"]).grid(
            row=0, column=2, padx=(0, 8)
        )
        categorias      = ["Todas"] + [c.nombre for c in self.svc.obtener_categorias()]
        self.var_cat    = ctk.StringVar(value="Todas")
        self.combo_cat  = ctk.CTkComboBox(
            frame,
            values=categorias,
            variable=self.var_cat,
            command=self._filtrar_categoria,
            font=self.F["cuerpo_md"],
            width=160,
        )
        self.combo_cat.grid(row=0, column=3, padx=(0, 12))

        # Filtro stock bajo
        self.var_stock_bajo = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            frame,
            text="Solo stock bajo",
            variable=self.var_stock_bajo,
            command=self._cargar_tabla,
            font=self.F["cuerpo_md"],
            text_color=self.C["texto_primario"],
            fg_color=self.C["acento"],
        ).grid(row=0, column=4)

    # ----------------------------------------------------------
    def _construir_tabla(self):
        contenedor = ctk.CTkFrame(self, **self.E["frame_tarjeta"])
        contenedor.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Inv.Treeview",
            background=self.C["fondo_secundario"],
            foreground=self.C["texto_primario"],
            fieldbackground=self.C["fondo_secundario"],
            rowheight=34,
            font=("Roboto", 12),
            borderwidth=0,
        )
        style.configure(
            "Inv.Treeview.Heading",
            background=self.C["fondo_tarjeta"],
            foreground=self.C["texto_primario"],
            font=("Roboto", 12, "bold"),
            relief="flat",
        )
        style.map(
            "Inv.Treeview",
            background=[("selected", self.C["acento"])],
            foreground=[("selected", "#ffffff")],
        )

        columnas = ("id", "codigo_barras", "nombre", "categoria", "proveedor",
                    "precio_compra", "stock", "stock_min", "unidad", "receta")
        self.tabla = ttk.Treeview(
            contenedor, columns=columnas,
            show="headings", style="Inv.Treeview", selectmode="browse"
        )

        config = {
            "id":            ("ID",            50,  "center"),
            "codigo_barras": ("Cód. barras",   130, "center"),
            "nombre":        ("Nombre",         200, "w"),
            "categoria":     ("Categoría",      130, "center"),
            "proveedor":     ("Proveedor",      150, "w"),
            "precio_compra": ("Precio compra",  120, "center"),
            "stock":         ("Stock",           80, "center"),
            "stock_min":     ("Stock mín.",      90, "center"),
            "unidad":        ("Unidad",          90, "center"),
            "receta":        ("Receta",          70, "center"),
        }
        for col, (titulo, ancho, anchor) in config.items():
            self.tabla.heading(col, text=titulo, anchor="center")
            self.tabla.column(col, width=ancho, anchor=anchor, minwidth=40)

        # Tags para filas con stock bajo
        self.tabla.tag_configure("stock_bajo", foreground=self.C["error"])
        self.tabla.tag_configure("normal",     foreground=self.C["texto_primario"])

        scroll_y = ttk.Scrollbar(contenedor, orient="vertical",   command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(contenedor, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        self.tabla.grid(row=0, column=0, sticky="nsew")

        self.tabla.bind("<Double-1>", lambda e: self._modificar())

    # ----------------------------------------------------------
    def _construir_barra_estado(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 16))

        self.lbl_estado = ctk.CTkLabel(
            frame, text="", **self.E["label_subtitulo"]
        )
        self.lbl_estado.pack(side="left")

        self.lbl_stock_alerta = ctk.CTkLabel(
            frame, text="",
            font=self.F["cuerpo_md"],
            text_color=self.C["error"],
        )
        self.lbl_stock_alerta.pack(side="right")

    # ==========================================================
    #  CARGA Y FILTROS
    # ==========================================================
    def _cargar_tabla(self, *_):
        if self.var_stock_bajo.get():
            self.productos = self.svc.productos_bajo_stock()
        else:
            self.productos = self.svc.obtener_todos()

        cat = self.var_cat.get()
        if cat != "Todas":
            self.productos = [p for p in self.productos if p.categoria and p.categoria.nombre == cat]

        self._refrescar_tabla(self.productos)

    def _refrescar_tabla(self, productos):
        self.tabla.delete(*self.tabla.get_children())
        for p in productos:
            tag  = "stock_bajo" if p.stock_actual <= p.stock_minimo else "normal"
            cat  = p.categoria.nombre  if p.categoria  else "—"
            prov = p.proveedor.nombre  if p.proveedor  else "—"
            self.tabla.insert("", "end", tags=(tag,), values=(
                p.id_producto,
                p.codigo_barras or "—",
                p.nombre,
                cat,
                prov,
                f"${p.precio_compra:,.0f}",
                p.stock_actual,
                p.stock_minimo,
                p.unidad_medida or "—",
                "Sí" if p.requiere_receta else "No",
            ))

        bajo_stock = sum(1 for p in productos if p.stock_actual <= p.stock_minimo)
        self.lbl_estado.configure(text=f"{len(productos)} productos")
        self.lbl_stock_alerta.configure(
            text=f"⚠ {bajo_stock} con stock bajo" if bajo_stock else ""
        )

    def _buscar(self, *_):
        texto = self.entrada_busqueda.get().strip()
        if texto:
            resultado = self.svc.buscar(texto)
        else:
            resultado = self.svc.obtener_todos()
        self._refrescar_tabla(resultado)

    def _filtrar_categoria(self, *_):
        self._cargar_tabla()

    # ==========================================================
    #  ACCIONES
    # ==========================================================
    def _fila_seleccionada(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla.")
            return None
        id_p = self.tabla.item(sel[0])["values"][0]
        return self.svc.obtener_por_id(id_p)

    def _dialogo_nuevo(self):
        self._abrir_dialogo("Nuevo producto")

    def _modificar(self):
        producto = self._fila_seleccionada()
        if producto:
            self._abrir_dialogo("Modificar producto", producto)

    def _eliminar(self):
        producto = self._fila_seleccionada()
        if not producto:
            return
        ok = messagebox.askyesno("Confirmar", f"¿Eliminar '{producto.nombre}'?")
        if ok:
            self.svc.eliminar(producto.id_producto)
            self._cargar_tabla()

    # ==========================================================
    #  DIÁLOGO CREAR / EDITAR
    # ==========================================================
    def _abrir_dialogo(self, titulo: str, producto=None):
        d = ctk.CTkToplevel(self)
        d.title(titulo)
        d.geometry("480x580")
        d.resizable(False, False)
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text=titulo, **self.E["label_titulo"]).pack(pady=(20, 14))

        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24)

        def campo(label, valor=""):
            ctk.CTkLabel(scroll, text=label, **self.E["label_cuerpo"]).pack(anchor="w")
            e = ctk.CTkEntry(scroll, **self.E["entry"])
            e.pack(fill="x", pady=(2, 10))
            if valor:
                e.insert(0, str(valor))
            return e

        e_nombre   = campo("Nombre *",          producto.nombre          if producto else "")
        e_barras   = campo("Código de barras",   producto.codigo_barras   if producto else "")
        e_desc     = campo("Descripción",        producto.descripcion     if producto else "")
        e_p_compra = campo("Precio compra *",   producto.precio_compra  if producto else "")
        e_stock    = campo("Stock actual *",    producto.stock_actual   if producto else "")
        e_stk_min  = campo("Stock mínimo",      producto.stock_minimo   if producto else "0")
        e_unidad   = campo("Unidad de medida",  producto.unidad_medida  if producto else "")

        # Categoría
        ctk.CTkLabel(scroll, text="Categoría", **self.E["label_cuerpo"]).pack(anchor="w")
        categorias     = self.svc.obtener_categorias()
        nombres_cat    = [c.nombre for c in categorias]
        val_cat_actual = producto.categoria.nombre if producto and producto.categoria else (nombres_cat[0] if nombres_cat else "")
        var_cat = ctk.StringVar(value=val_cat_actual)
        ctk.CTkComboBox(scroll, values=nombres_cat, variable=var_cat,
                        font=self.F["cuerpo_md"]).pack(fill="x", pady=(2, 10))

        # Proveedor
        ctk.CTkLabel(scroll, text="Proveedor", **self.E["label_cuerpo"]).pack(anchor="w")
        proveedores    = self.svc.obtener_proveedores()
        nombres_prov   = [p.nombre for p in proveedores]
        val_prov_actual = producto.proveedor.nombre if producto and producto.proveedor else (nombres_prov[0] if nombres_prov else "")
        var_prov = ctk.StringVar(value=val_prov_actual)
        ctk.CTkComboBox(scroll, values=nombres_prov or ["(sin proveedores)"],
                        variable=var_prov, font=self.F["cuerpo_md"]).pack(fill="x", pady=(2, 10))

        # Requiere receta
        var_receta = ctk.BooleanVar(value=producto.requiere_receta if producto else False)
        ctk.CTkCheckBox(scroll, text="Requiere receta médica",
                        variable=var_receta,
                        font=self.F["cuerpo_md"],
                        text_color=self.C["texto_primario"],
                        fg_color=self.C["acento"]).pack(anchor="w", pady=(0, 16))

        # Botón guardar
        def guardar():
            try:
                nombre    = e_nombre.get().strip()
                precio_c  = float(e_p_compra.get())
                stock     = float(e_stock.get())
                stk_min   = float(e_stk_min.get() or 0)
                if not nombre:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Verifica los campos obligatorios (*).", parent=d)
                return

            cat_obj  = next((c for c in categorias  if c.nombre == var_cat.get()),  None)
            prov_obj = next((p for p in proveedores if p.nombre == var_prov.get()), None)

            datos = {
                "nombre":          nombre,
                "codigo_barras":   e_barras.get().strip() or None,
                "descripcion":     e_desc.get().strip(),
                "precio_compra":   precio_c,
                "stock_actual":    stock,
                "stock_minimo":    stk_min,
                "unidad_medida":   e_unidad.get().strip(),
                "requiere_receta": var_receta.get(),
                "id_categoria":    cat_obj.id_categoria  if cat_obj  else None,
                "id_proveedor":    prov_obj.id_proveedor if prov_obj else None,
            }

            if producto:
                self.svc.actualizar(producto.id_producto, datos)
            else:
                self.svc.crear(datos)

            self._cargar_tabla()
            d.destroy()

        ctk.CTkButton(d, text="Guardar", command=guardar,
                      **self.E["boton_primario"]).pack(fill="x", padx=24, pady=(0, 20))

    # ==========================================================
    #  GESTIÓN DE PRESENTACIONES
    # ==========================================================
    def _gestionar_presentaciones(self):
        producto = self._fila_seleccionada()
        if not producto:
            return

        d = ctk.CTkToplevel(self)
        d.title(f"Presentaciones — {producto.nombre}")
        d.geometry("620x500")
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text=f"Presentaciones de {producto.nombre}",
                     **self.E["label_titulo"]).pack(pady=(20, 4))
        ctk.CTkLabel(d, text="Define cómo se puede vender este producto",
                     **self.E["label_subtitulo"]).pack(pady=(0, 12))

        # Tabla de presentaciones
        cols = ("tipo", "cantidad", "precio", "precio_desc", "descuento")
        tabla_p = ttk.Treeview(d, columns=cols, show="headings",
                               style="Inv.Treeview", height=6)
        for col, titulo, ancho in [
            ("tipo",       "Tipo",            120),
            ("cantidad",   "Unidades/present.",130),
            ("precio",     "Precio base",      110),
            ("precio_desc","Precio descuento", 120),
            ("descuento",  "% Descuento",      100),
        ]:
            tabla_p.heading(col, text=titulo, anchor="center")
            tabla_p.column(col, width=ancho, anchor="center")
        tabla_p.pack(fill="x", padx=20)

        def refrescar_presentaciones():
            tabla_p.delete(*tabla_p.get_children())
            for p in self.svc.obtener_presentaciones(producto.id_producto):
                tabla_p.insert("", "end", iid=p.id_presentacion, values=(
                    p.tipo_venta.nombre if p.tipo_venta else "—",
                    p.cantidad_por_presentacion,
                    f"${p.precio_venta:,.0f}",
                    f"${p.precio_con_descuento:,.0f}" if p.precio_con_descuento else "—",
                    f"{p.porcentaje_descuento:.1f}%" if p.porcentaje_descuento else "0%",
                ))

        refrescar_presentaciones()

        # Formulario nueva presentación
        form = ctk.CTkFrame(d, **self.E["frame_tarjeta"])
        form.pack(fill="x", padx=20, pady=12)
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        from database.modelos import TipoVenta as TipoVentaModel
        tipos      = self.session.query(TipoVentaModel).all()
        var_tipo   = ctk.StringVar(value=tipos[0].nombre if tipos else "")

        ctk.CTkLabel(form, text="Tipo", **self.E["label_cuerpo"]).grid(row=0, column=0, padx=8, sticky="w")
        ctk.CTkLabel(form, text="Unidades", **self.E["label_cuerpo"]).grid(row=0, column=1, padx=8, sticky="w")
        ctk.CTkLabel(form, text="Precio base", **self.E["label_cuerpo"]).grid(row=0, column=2, padx=8, sticky="w")
        ctk.CTkLabel(form, text="% Descuento", **self.E["label_cuerpo"]).grid(row=0, column=3, padx=8, sticky="w")

        ctk.CTkComboBox(form, values=[t.nombre for t in tipos],
                        variable=var_tipo, font=self.F["cuerpo_md"],
                        width=130).grid(row=1, column=0, padx=8, pady=6, sticky="ew")
        e_cant  = ctk.CTkEntry(form, **self.E["entry"]); e_cant.grid( row=1, column=1, padx=8, pady=6, sticky="ew")
        e_prec  = ctk.CTkEntry(form, **self.E["entry"]); e_prec.grid( row=1, column=2, padx=8, pady=6, sticky="ew")
        e_desc  = ctk.CTkEntry(form, **self.E["entry"]); e_desc.grid( row=1, column=3, padx=8, pady=6, sticky="ew")

        def agregar_presentacion():
            try:
                tipo_obj   = next(t for t in tipos if t.nombre == var_tipo.get())
                cantidad   = float(e_cant.get())
                precio     = float(e_prec.get())
                pct        = float(e_desc.get() or 0)
                precio_dto = round(precio * (1 - pct / 100), 2) if pct > 0 else None
            except (ValueError, StopIteration):
                messagebox.showerror("Error", "Completa los campos correctamente.", parent=d)
                return

            self.svc.crear_presentacion({
                "id_producto":               producto.id_producto,
                "id_tipo_venta":             tipo_obj.id_tipo_venta,
                "cantidad_por_presentacion": cantidad,
                "precio_venta":              precio,
                "precio_con_descuento":      precio_dto,
                "porcentaje_descuento":      pct,
            })
            refrescar_presentaciones()
            for e in (e_cant, e_prec, e_desc):
                e.delete(0, "end")

        ctk.CTkButton(d, text="＋ Agregar presentación",
                      command=agregar_presentacion,
                      **self.E["boton_primario"]).pack(padx=20, pady=(0, 16), fill="x")