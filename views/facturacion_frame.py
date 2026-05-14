# ============================================================
#  views/facturacion_frame.py
# ============================================================
import customtkinter as ctk
from tkinter import ttk, messagebox
from database.conexion import get_session
from servicios.productos_services import ProductosService
from servicios.ventas_services import VentasService


class FacturacionFrame(ctk.CTkFrame):
    def __init__(self, parent, fuentes, estilos, colores, id_usuario=1, **kwargs):
        super().__init__(parent, **kwargs)
        self.F          = fuentes
        self.E          = estilos
        self.C          = colores
        self.id_usuario = id_usuario
        self.contador   = 0

        self.configure(fg_color=self.C["fondo_principal"])
        self._construir_ui()
        self._nueva_factura()

    # ==========================================================
    #  UI CONTENEDOR DE PESTAÑAS
    # ==========================================================
    def _construir_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        barra = ctk.CTkFrame(self, fg_color=self.C["fondo_secundario"], height=48, corner_radius=0)
        barra.grid(row=0, column=0, sticky="ew")
        barra.grid_propagate(False)

        self.barra_tabs = ctk.CTkFrame(barra, fg_color="transparent")
        self.barra_tabs.pack(side="left", fill="y")

        ctk.CTkButton(
            barra, text="＋  Nueva factura",
            command=self._nueva_factura,
            fg_color=self.C["acento"],
            hover_color=self.C["acento_hover"],
            text_color="#fff",
            font=self.F["boton"],
            corner_radius=6,
            width=150, height=34,
        ).pack(side="left", padx=8, pady=7)

        self.contenedor_tabs = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_tabs.grid(row=1, column=0, sticky="nsew")
        self.contenedor_tabs.grid_rowconfigure(0, weight=1)
        self.contenedor_tabs.grid_columnconfigure(0, weight=1)

        self.tabs       = {}
        self.tab_activa = None

    def _nueva_factura(self):
        self.contador += 1
        tab_id = self.contador
        label  = f"Factura #{tab_id}"

        btn_frame = ctk.CTkFrame(self.barra_tabs, fg_color="transparent")
        btn_frame.pack(side="left", padx=(8, 0), pady=6)

        ctk.CTkButton(
            btn_frame, text=label,
            command=lambda tid=tab_id: self._activar_tab(tid),
            fg_color=self.C["fondo_tarjeta"],
            hover_color=self.C["acento_hover"],
            text_color=self.C["texto_primario"],
            font=self.F["cuerpo_md"],
            corner_radius=6,
            width=110, height=34,
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame, text="×",
            command=lambda tid=tab_id: self._cerrar_tab(tid),
            fg_color=self.C["fondo_tarjeta"],
            hover_color=self.C["error"],
            text_color=self.C["texto_secundario"],
            font=self.F["boton"],
            corner_radius=6,
            width=24, height=34,
        ).pack(side="left", padx=(2, 0))

        frame = _FacturaTab(
            self.contenedor_tabs,
            fuentes=self.F,
            estilos=self.E,
            colores=self.C,
            id_usuario=self.id_usuario,
            label=label,
        )
        frame.grid(row=0, column=0, sticky="nsew")

        self.tabs[tab_id] = {"btn": btn_frame, "frame": frame}
        self._activar_tab(tab_id)

    def _activar_tab(self, tab_id: int):
        for tid, data in self.tabs.items():
            data["frame"].grid_remove()
            data["btn"].winfo_children()[0].configure(
                fg_color=self.C["fondo_tarjeta"],
                text_color=self.C["texto_primario"],
            )
        self.tabs[tab_id]["frame"].grid()
        self.tabs[tab_id]["btn"].winfo_children()[0].configure(
            fg_color=self.C["acento"],
            text_color="#ffffff",
        )
        self.tab_activa = tab_id

    def _cerrar_tab(self, tab_id: int):
        data  = self.tabs[tab_id]
        frame = data["frame"]

        if frame.items_factura:
            if not messagebox.askyesno(
                "Cerrar factura",
                f"La Factura #{tab_id} tiene items sin cobrar. ¿Cerrar de todas formas?",
                parent=self
            ):
                return

        data["btn"].destroy()
        frame.destroy()
        del self.tabs[tab_id]

        if self.tabs:
            self._activar_tab(max(self.tabs.keys()))
        else:
            self._nueva_factura()


# ==============================================================
#  PESTAÑA INDIVIDUAL
# ==============================================================
class _FacturaTab(ctk.CTkFrame):
    def __init__(self, parent, fuentes, estilos, colores, id_usuario=1, label="Factura"):
        super().__init__(parent)   # sin **kwargs
        self.F          = fuentes
        self.E          = estilos
        self.C          = colores
        self.id_usuario = id_usuario
        self.label      = label

        self.session     = get_session()
        self.prod_svc    = ProductosService(self.session)
        self.ventas_svc  = VentasService(self.session)
        self.items_factura = []

        self._construir_ui()

    # ==========================================================
    #  UI PRINCIPAL
    # ==========================================================
    def _construir_ui(self):
        self.configure(fg_color=self.C["fondo_principal"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

    def _construir_panel_izquierdo(self):
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text=self.label,
                     **self.E["label_titulo"]).grid(row=0, column=0, sticky="w", pady=(0, 12))

        busq = ctk.CTkFrame(panel, **self.E["frame_tarjeta"])
        busq.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        busq.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(busq, text="Agregar producto / servicio",
                     **self.E["label_subtitulo"]).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(10, 6))

        ctk.CTkLabel(busq, text="Buscar:", **self.E["label_cuerpo"]).grid(
            row=1, column=0, padx=(14, 6), pady=(0, 10))

        self.entrada_busqueda = ctk.CTkEntry(
            busq, placeholder_text="Nombre o código de barras...", **self.E["entry"])
        self.entrada_busqueda.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(0, 10))
        self.entrada_busqueda.bind("<Return>",     self._buscar)
        self.entrada_busqueda.bind("<KeyRelease>", self._buscar)

        self.var_tipo = ctk.StringVar(value="Producto")
        ctk.CTkSegmentedButton(
            busq, values=["Producto", "Servicio"],
            variable=self.var_tipo, command=self._buscar,
            font=self.F["cuerpo_md"],
        ).grid(row=1, column=2, padx=(0, 14), pady=(0, 10))

        self.lista_resultados = ctk.CTkScrollableFrame(
            busq, height=130, fg_color=self.C["fondo_secundario"])
        self.lista_resultados.grid(row=2, column=0, columnspan=3, sticky="ew", padx=14, pady=(0, 14))

        self._construir_tabla_items(panel)

        acciones = ctk.CTkFrame(panel, fg_color="transparent")
        acciones.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        ctk.CTkButton(acciones, text="🗑  Quitar item", command=self._quitar_item,
                      fg_color=self.C["error"], hover_color="#c0392b",
                      text_color=self.C["texto_primario"], font=self.F["boton"],
                      corner_radius=8, height=38).pack(side="left", padx=(0, 8))

        ctk.CTkButton(acciones, text="🧹  Limpiar todo", command=self._limpiar_factura,
                      fg_color=self.C["fondo_tarjeta"], hover_color=self.C["borde"],
                      text_color=self.C["texto_primario"], font=self.F["boton"],
                      corner_radius=8, height=38).pack(side="left")

    def _construir_tabla_items(self, parent):
        contenedor = ctk.CTkFrame(parent, **self.E["frame_tarjeta"])
        contenedor.grid(row=2, column=0, sticky="nsew")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Fact.Treeview",
            background=self.C["fondo_secundario"], foreground=self.C["texto_primario"],
            fieldbackground=self.C["fondo_secundario"], rowheight=32,
            font=("Roboto", 12), borderwidth=0)
        style.configure("Fact.Treeview.Heading",
            background=self.C["fondo_tarjeta"], foreground=self.C["texto_primario"],
            font=("Roboto", 12, "bold"), relief="flat")
        style.map("Fact.Treeview",
            background=[("selected", self.C["acento"])],
            foreground=[("selected", "#ffffff")])

        cols = ("tipo", "nombre", "presentacion", "cantidad", "precio", "descuento", "subtotal")
        self.tabla_items = ttk.Treeview(contenedor, columns=cols,
                                        show="headings", style="Fact.Treeview", selectmode="browse")
        for col, titulo, ancho, anchor in [
            ("tipo",         "Tipo",          70,  "center"),
            ("nombre",       "Nombre",        200, "w"),
            ("presentacion", "Presentación",  100, "center"),
            ("cantidad",     "Cant.",          60, "center"),
            ("precio",       "Precio",         90, "center"),
            ("descuento",    "Descuento",      90, "center"),
            ("subtotal",     "Subtotal",       90, "center"),
        ]:
            self.tabla_items.heading(col, text=titulo, anchor="center")
            self.tabla_items.column(col, width=ancho, anchor=anchor, minwidth=40)

        scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=self.tabla_items.yview)
        self.tabla_items.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.tabla_items.grid(row=0, column=0, sticky="nsew")
        self.tabla_items.bind("<Double-1>", self._editar_cantidad)

    def _construir_panel_derecho(self):
        panel = ctk.CTkFrame(self, **self.E["frame_tarjeta"])
        panel.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        panel.grid_rowconfigure(3, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Resumen de pago",
                     **self.E["label_titulo"]).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 16))

        totales = ctk.CTkFrame(panel, fg_color=self.C["fondo_secundario"], corner_radius=10)
        totales.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))
        totales.grid_columnconfigure(1, weight=1)

        self.var_subtotal  = ctk.StringVar(value="$0")
        self.var_descuento = ctk.StringVar(value="$0")
        self.var_total     = ctk.StringVar(value="$0")

        for fila, label, var, color in [
            (0, "Subtotal:",  self.var_subtotal,  None),
            (1, "Descuento:", self.var_descuento, self.C["exito"]),
            (3, "TOTAL:",     self.var_total,     self.C["acento"]),
        ]:
            ctk.CTkLabel(totales, text=label, font=self.F["cuerpo_md"],
                         text_color=self.C["texto_secundario"]).grid(
                row=fila, column=0, sticky="w", padx=16, pady=4)
            ctk.CTkLabel(totales, textvariable=var,
                         font=self.F["titulo_sm"] if color else self.F["cuerpo_md"],
                         text_color=color or self.C["texto_primario"]).grid(
                row=fila, column=1, sticky="e", padx=16, pady=4)

        ttk.Separator(totales, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=4)

        ctk.CTkLabel(panel, text="Método de pago",
                     **self.E["label_subtitulo"]).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 8))

        pago_frame = ctk.CTkFrame(panel, fg_color="transparent")
        pago_frame.grid(row=3, column=0, sticky="new", padx=20)
        pago_frame.grid_columnconfigure((0, 1), weight=1)

        self.var_metodo = ctk.StringVar(value="efectivo")
        for i, (texto, valor) in enumerate([
            ("💵 Efectivo",      "efectivo"),
            ("💳 Tarjeta",       "tarjeta"),
            ("🏦 Transferencia", "transferencia"),
            ("🔀 Mixto",         "mixto"),
        ]):
            ctk.CTkRadioButton(pago_frame, text=texto, value=valor,
                               variable=self.var_metodo, command=self._toggle_mixto,
                               font=self.F["cuerpo_md"], text_color=self.C["texto_primario"],
                               fg_color=self.C["acento"]).grid(
                row=i // 2, column=i % 2, sticky="w", pady=4)

        self.frame_mixto = ctk.CTkFrame(panel, fg_color="transparent")
        self.frame_mixto.grid(row=4, column=0, sticky="ew", padx=20, pady=(10, 0))
        self.frame_mixto.grid_columnconfigure((0, 1), weight=1)
        self.frame_mixto.grid_remove()

        for i, (lbl, attr) in enumerate([
            ("Efectivo $", "e_mixto_efectivo"),
            ("Tarjeta $",  "e_mixto_tarjeta"),
            ("Transfer $", "e_mixto_transfer"),
        ]):
            ctk.CTkLabel(self.frame_mixto, text=lbl, **self.E["label_cuerpo"]).grid(
                row=i, column=0, sticky="w", pady=2)
            e = ctk.CTkEntry(self.frame_mixto, **self.E["entry"])
            e.grid(row=i, column=1, sticky="ew", padx=(8, 0), pady=2)
            e.insert(0, "0")
            setattr(self, attr, e)

        ctk.CTkLabel(panel, text="Observaciones",
                     **self.E["label_subtitulo"]).grid(row=5, column=0, sticky="w", padx=20, pady=(16, 4))
        self.txt_obs = ctk.CTkTextbox(panel, height=60,
                                      fg_color=self.C["fondo_secundario"],
                                      text_color=self.C["texto_primario"],
                                      font=self.F["cuerpo_md"], corner_radius=8)
        self.txt_obs.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 16))

        ctk.CTkButton(panel, text="✔  Cobrar", command=self._cobrar,
                      height=50, font=self.F["titulo_sm"],
                      fg_color=self.C["exito"], hover_color="#388e3c",
                      text_color="#ffffff", corner_radius=10).grid(
            row=7, column=0, sticky="ew", padx=20, pady=(0, 20))

    # ==========================================================
    #  BÚSQUEDA
    # ==========================================================
    def _buscar(self, *_):
        texto = self.entrada_busqueda.get().strip()
        for w in self.lista_resultados.winfo_children():
            w.destroy()
        if not texto:
            return

        if self.var_tipo.get() == "Producto":
            for p in self.prod_svc.buscar(texto)[:8]:
                self._fila_resultado_producto(p)
        else:
            from database.modelos import Servicio
            servicios = (self.session.query(Servicio)
                         .filter(Servicio.nombre.ilike(f"%{texto}%"), Servicio.activo == True)
                         .limit(8).all())
            for s in servicios:
                self._fila_resultado_servicio(s)

    def _fila_resultado_producto(self, producto):
        frame = ctk.CTkFrame(self.lista_resultados, fg_color=self.C["fondo_tarjeta"], corner_radius=6)
        frame.pack(fill="x", pady=2, padx=2)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text=f"[{producto.codigo_barras or '—'}]",
                     font=self.F["cuerpo_sm"], text_color=self.C["texto_secundario"],
                     width=100).grid(row=0, column=0, padx=8, pady=4)
        ctk.CTkLabel(frame, text=producto.nombre, font=self.F["cuerpo_md"],
                     text_color=self.C["texto_primario"], anchor="w").grid(
            row=0, column=1, sticky="w", padx=4)
        ctk.CTkLabel(frame, text=f"Stock: {producto.stock_actual}",
                     font=self.F["cuerpo_sm"], text_color=self.C["texto_secundario"]).grid(
            row=0, column=2, padx=8)
        ctk.CTkButton(frame, text="＋", width=32, height=28,
                      fg_color=self.C["acento"], hover_color=self.C["acento_hover"],
                      font=self.F["boton"],
                      command=lambda p=producto: self._seleccionar_producto(p)).grid(
            row=0, column=3, padx=8, pady=4)

    def _fila_resultado_servicio(self, servicio):
        frame = ctk.CTkFrame(self.lista_resultados, fg_color=self.C["fondo_tarjeta"], corner_radius=6)
        frame.pack(fill="x", pady=2, padx=2)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text=servicio.nombre, font=self.F["cuerpo_md"],
                     text_color=self.C["texto_primario"], anchor="w").grid(
            row=0, column=0, sticky="w", padx=12, pady=4)
        ctk.CTkLabel(frame, text=f"${servicio.precio:,.0f}",
                     font=self.F["cuerpo_md"], text_color=self.C["acento"]).grid(
            row=0, column=1, padx=8)
        ctk.CTkButton(frame, text="＋", width=32, height=28,
                      fg_color=self.C["acento"], hover_color=self.C["acento_hover"],
                      font=self.F["boton"],
                      command=lambda s=servicio: self._agregar_servicio(s)).grid(
            row=0, column=2, padx=8, pady=4)

    # ==========================================================
    #  SELECCIÓN DE PRODUCTO
    # ==========================================================
    def _seleccionar_producto(self, producto):
        presentaciones = self.prod_svc.obtener_presentaciones(producto.id_producto)
        if not presentaciones:
            messagebox.showwarning("Sin presentaciones",
                f"'{producto.nombre}' no tiene presentaciones configuradas.", parent=self)
            return

        d = ctk.CTkToplevel(self)
        d.title(f"Agregar — {producto.nombre}")
        d.geometry("400x320")
        d.resizable(False, False)
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text=producto.nombre, **self.E["label_titulo"]).pack(pady=(16, 4))
        ctk.CTkLabel(d, text=f"Stock disponible: {producto.stock_actual}",
                     **self.E["label_subtitulo"]).pack()

        ctk.CTkLabel(d, text="Presentación", **self.E["label_cuerpo"]).pack(anchor="w", padx=24, pady=(12, 2))
        nombres_pres = [
            f"{p.tipo_venta.nombre if p.tipo_venta else '?'} — ${p.precio_venta:,.0f}"
            for p in presentaciones
        ]
        var_pres   = ctk.StringVar(value=nombres_pres[0])
        combo_pres = ctk.CTkComboBox(d, values=nombres_pres, variable=var_pres, font=self.F["cuerpo_md"])
        combo_pres.pack(fill="x", padx=24, pady=(0, 10))

        ctk.CTkLabel(d, text="Cantidad", **self.E["label_cuerpo"]).pack(anchor="w", padx=24)
        e_cant = ctk.CTkEntry(d, **self.E["entry"])
        e_cant.pack(fill="x", padx=24, pady=(2, 10))
        e_cant.insert(0, "1")

        var_dto = ctk.BooleanVar(value=False)
        lbl_dto = ctk.CTkLabel(d, text="", font=self.F["cuerpo_sm"], text_color=self.C["texto_secundario"])
        chk_dto = ctk.CTkCheckBox(d, textvariable=ctk.StringVar(), variable=var_dto,
                                  fg_color=self.C["exito"], font=self.F["cuerpo_md"],
                                  text_color=self.C["texto_primario"])

        def actualizar_label_dto(*_):
            idx = nombres_pres.index(var_pres.get())
            p   = presentaciones[idx]
            if p.precio_con_descuento:
                lbl_dto.configure(text=f"Aplicar descuento ({p.porcentaje_descuento:.1f}% → ${p.precio_con_descuento:,.0f})")
            else:
                lbl_dto.configure(text="Sin descuento configurado")
                var_dto.set(False)

        combo_pres.configure(command=actualizar_label_dto)
        lbl_dto.pack(anchor="w", padx=24)
        chk_dto.pack(anchor="w", padx=24, pady=(2, 12))
        actualizar_label_dto()

        def agregar():
            try:
                cantidad = float(e_cant.get())
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Ingresa una cantidad válida.", parent=d)
                return

            idx          = nombres_pres.index(var_pres.get())
            pres         = presentaciones[idx]
            aplicar_dto  = var_dto.get() and pres.precio_con_descuento is not None
            precio_final = pres.precio_con_descuento if aplicar_dto else pres.precio_venta

            self._agregar_item({
                "tipo":                 "Producto",
                "id_producto":          producto.id_producto,
                "id_tipo_venta":        pres.id_tipo_venta,
                "nombre":               producto.nombre,
                "presentacion":         pres.tipo_venta.nombre if pres.tipo_venta else "—",
                "cantidad":             cantidad,
                "precio_unitario":      pres.precio_venta,
                "descuento_aplicado":   aplicar_dto,
                "porcentaje_descuento": pres.porcentaje_descuento or 0,
                "precio_con_descuento": pres.precio_con_descuento,
                "precio_final":         precio_final,
                "subtotal_linea":       precio_final * cantidad,
            })
            d.destroy()

        ctk.CTkButton(d, text="Agregar a factura", command=agregar,
                      **self.E["boton_primario"]).pack(fill="x", padx=24, pady=(0, 16))

    def _agregar_servicio(self, servicio):
        self._agregar_item({
            "tipo":                 "Servicio",
            "id_producto":          None,
            "id_tipo_venta":        None,
            "id_servicio":          servicio.id_servicio,
            "nombre":               servicio.nombre,
            "presentacion":         "—",
            "cantidad":             1,
            "precio_unitario":      servicio.precio,
            "descuento_aplicado":   False,
            "porcentaje_descuento": 0,
            "precio_con_descuento": None,
            "precio_final":         servicio.precio,
            "subtotal_linea":       servicio.precio,
        })

    # ==========================================================
    #  ITEMS
    # ==========================================================
    def _agregar_item(self, item: dict):
        self.items_factura.append(item)
        self._refrescar_tabla()

    def _refrescar_tabla(self):
        self.tabla_items.delete(*self.tabla_items.get_children())
        for item in self.items_factura:
            dto_txt = f"-{item['porcentaje_descuento']:.1f}%" if item["descuento_aplicado"] else "—"
            self.tabla_items.insert("", "end", values=(
                item["tipo"], item["nombre"], item["presentacion"],
                item["cantidad"], f"${item['precio_unitario']:,.0f}",
                dto_txt, f"${item['subtotal_linea']:,.0f}",
            ))
        self._actualizar_totales()

    def _actualizar_totales(self):
        subtotal  = sum(i["precio_unitario"] * i["cantidad"] for i in self.items_factura)
        descuento = sum((i["precio_unitario"] - i["precio_final"]) * i["cantidad"]
                        for i in self.items_factura if i["descuento_aplicado"])
        total = subtotal - descuento
        self.var_subtotal.set(f"${subtotal:,.0f}")
        self.var_descuento.set(f"-${descuento:,.0f}")
        self.var_total.set(f"${total:,.0f}")

    def _quitar_item(self):
        sel = self.tabla_items.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un item.", parent=self)
            return
        self.items_factura.pop(self.tabla_items.index(sel[0]))
        self._refrescar_tabla()

    def _limpiar_factura(self):
        if not self.items_factura:
            return
        if messagebox.askyesno("Confirmar", "¿Limpiar todos los items?", parent=self):
            self.items_factura.clear()
            self._refrescar_tabla()

    def _editar_cantidad(self, event=None):
        sel = self.tabla_items.selection()
        if not sel:
            return
        item = self.items_factura[self.tabla_items.index(sel[0])]

        d = ctk.CTkToplevel(self)
        d.title("Editar cantidad")
        d.geometry("280x160")
        d.resizable(False, False)
        d.grab_set()
        d.configure(fg_color=self.C["fondo_principal"])

        ctk.CTkLabel(d, text=item["nombre"], **self.E["label_subtitulo"]).pack(pady=(16, 4))
        ctk.CTkLabel(d, text="Nueva cantidad", **self.E["label_cuerpo"]).pack(anchor="w", padx=24)
        e = ctk.CTkEntry(d, **self.E["entry"])
        e.pack(fill="x", padx=24, pady=(4, 12))
        e.insert(0, str(item["cantidad"]))

        def guardar():
            try:
                nueva = float(e.get())
                if nueva <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida.", parent=d)
                return
            item["cantidad"]       = nueva
            item["subtotal_linea"] = item["precio_final"] * nueva
            self._refrescar_tabla()
            d.destroy()

        ctk.CTkButton(d, text="Guardar", command=guardar,
                      **self.E["boton_primario"]).pack(fill="x", padx=24)

    # ==========================================================
    #  PAGO MIXTO
    # ==========================================================
    def _toggle_mixto(self):
        if self.var_metodo.get() == "mixto":
            self.frame_mixto.grid()
        else:
            self.frame_mixto.grid_remove()

    # ==========================================================
    #  COBRAR
    # ==========================================================
    def _cobrar(self):
        if not self.items_factura:
            messagebox.showwarning("Factura vacía", "Agrega al menos un producto o servicio.", parent=self)
            return

        items_productos = [i for i in self.items_factura if i["tipo"] == "Producto"]

        venta = self.ventas_svc.crear_venta(
            id_usuario  = self.id_usuario,
            metodo_pago = self.var_metodo.get(),
            items       = [{
                "id_producto":          i["id_producto"],
                "id_tipo_venta":        i["id_tipo_venta"],
                "cantidad":             i["cantidad"],
                "precio_unitario":      i["precio_unitario"],
                "descuento_aplicado":   i["descuento_aplicado"],
                "porcentaje_descuento": i["porcentaje_descuento"],
                "precio_con_descuento": i["precio_con_descuento"],
            } for i in items_productos],
        )

        if venta:
            total = sum(i["subtotal_linea"] for i in self.items_factura)
            messagebox.showinfo("✔ Venta registrada",
                f"Venta #{venta.id_venta} registrada.\nTotal: ${total:,.0f}", parent=self)
            self.items_factura.clear()
            self._refrescar_tabla()
            self.entrada_busqueda.delete(0, "end")
            for w in self.lista_resultados.winfo_children():
                w.destroy()
            self.txt_obs.delete("1.0", "end")
        else:
            messagebox.showerror("Error", "No se pudo registrar la venta. Verifica el stock.", parent=self)