# ============================================================
#  views/cierre_caja_frame.py
# ============================================================
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from database.conexion import get_session
from servicios.reportes_service import ReportesService
from servicios.ventas_services import VentasService
from datetime import datetime


class CierreCajaFrame(ctk.CTkFrame):
    def __init__(self, parent, fuentes, estilos, colores, id_usuario=1, **kwargs):
        super().__init__(parent, **kwargs)
        self.F          = fuentes
        self.E          = estilos
        self.C          = colores
        self.id_usuario = id_usuario

        self.session    = get_session()
        self.rep_svc    = ReportesService(self.session)
        self.ven_svc    = VentasService(self.session)

        self.configure(fg_color=self.C["fondo_principal"])
        self._construir_ui()
        self._cargar_datos()

    # ==========================================================
    #  UI
    # ==========================================================
    def _construir_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Encabezado ────────────────────────────────────────
        enc = ctk.CTkFrame(self, fg_color="transparent")
        enc.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        enc.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(enc, text="Cierre de Caja",
                     **self.E["label_titulo"]).grid(row=0, column=0, sticky="w")

        self.lbl_fecha = ctk.CTkLabel(
            enc, text=datetime.now().strftime("%A %d de %B de %Y"),
            **self.E["label_subtitulo"]
        )
        self.lbl_fecha.grid(row=1, column=0, sticky="w")

        btns = ctk.CTkFrame(enc, fg_color="transparent")
        btns.grid(row=0, column=1, rowspan=2, sticky="e")

        ctk.CTkButton(btns, text="🔄  Actualizar",
                      command=self._cargar_datos,
                      **self.E["boton_secundario"], width=130).pack(side="left", padx=(0, 8))

        ctk.CTkButton(btns, text="📄  Exportar PDF",
                      command=self._exportar_pdf,
                      **self.E["boton_primario"], width=140).pack(side="left")

        # ── Contenido scrollable ──────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        self.scroll.grid_columnconfigure(0, weight=3)
        self.scroll.grid_columnconfigure(1, weight=2)

    # ==========================================================
    #  CARGA DE DATOS
    # ==========================================================
    def _cargar_datos(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        ventas_hoy = self.ven_svc.ventas_de_hoy()
        kpis       = self.rep_svc.kpis_hoy()
        productos  = self.rep_svc.productos_mas_vendidos(10)

        self._seccion_resumen(kpis, ventas_hoy)
        self._seccion_metodos_pago(ventas_hoy)
        self._seccion_detalle_ventas(ventas_hoy)
        self._seccion_productos(productos)

    # ==========================================================
    #  SECCIONES
    # ==========================================================
    def _tarjeta(self, fila, col, colspan=1, titulo="") -> ctk.CTkFrame:
        f = ctk.CTkFrame(self.scroll, **self.E["frame_tarjeta"])
        f.grid(row=fila, column=col, columnspan=colspan,
               sticky="nsew", padx=6, pady=6)
        if titulo:
            ctk.CTkLabel(f, text=titulo, **self.E["label_titulo"]).pack(
                anchor="w", padx=16, pady=(14, 8))
        return f

    def _kpi(self, parent, titulo, valor, color=None):
        card = ctk.CTkFrame(parent, fg_color=self.C["fondo_secundario"], corner_radius=10)
        card.pack(side="left", expand=True, fill="both", padx=6, pady=(0, 12))
        ctk.CTkLabel(card, text=titulo, font=self.F["cuerpo_sm"],
                     text_color=self.C["texto_secundario"]).pack(pady=(10, 2))
        ctk.CTkLabel(card, text=valor, font=self.F["titulo_md"],
                     text_color=color or self.C["texto_primario"]).pack(pady=(0, 10))

    def _seccion_resumen(self, kpis, ventas):
        t = self._tarjeta(0, 0, colspan=2, titulo="📊  Resumen del día")

        fila = ctk.CTkFrame(t, fg_color="transparent")
        fila.pack(fill="x", padx=6)

        completadas = [v for v in ventas if v.estado.value == "completada"]
        anuladas    = [v for v in ventas if v.estado.value == "anulada"]

        self._kpi(fila, "Total vendido",
                  f"${kpis['total_hoy']:,.0f}", self.C["acento"])
        self._kpi(fila, "# Ventas",
                  str(kpis["num_ventas_hoy"]))
        self._kpi(fila, "Ticket promedio",
                  f"${kpis['ticket_promedio']:,.0f}", self.C["info"])
        self._kpi(fila, "Descuentos aplicados",
                  f"${kpis['descuentos_hoy']:,.0f}", self.C["advertencia"])
        self._kpi(fila, "Ventas anuladas",
                  str(len(anuladas)), self.C["error"] if anuladas else None)

    def _seccion_metodos_pago(self, ventas):
        t = self._tarjeta(1, 0, colspan=2, titulo="💳  Ingresos por método de pago")

        completadas = [v for v in ventas if v.estado.value == "completada"]

        totales = {}
        for v in completadas:
            m = v.metodo_pago.value if hasattr(v.metodo_pago, "value") else str(v.metodo_pago)
            totales[m] = totales.get(m, 0) + v.total

        fila = ctk.CTkFrame(t, fg_color="transparent")
        fila.pack(fill="x", padx=6)

        iconos = {"efectivo": "💵", "tarjeta": "💳", "transferencia": "🏦", "mixto": "🔀"}
        for metodo, total in totales.items():
            self._kpi(fila, f"{iconos.get(metodo, '')} {metodo.capitalize()}",
                      f"${total:,.0f}", self.C["exito"])

        if not totales:
            ctk.CTkLabel(t, text="Sin ventas registradas hoy",
                         **self.E["label_subtitulo"]).pack(pady=12)

    def _seccion_detalle_ventas(self, ventas):
        t = self._tarjeta(2, 0, colspan=2, titulo="🧾  Detalle de ventas del día")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Cierre.Treeview",
            background=self.C["fondo_secundario"],
            foreground=self.C["texto_primario"],
            fieldbackground=self.C["fondo_secundario"],
            rowheight=30, font=("Roboto", 11), borderwidth=0)
        style.configure("Cierre.Treeview.Heading",
            background=self.C["fondo_tarjeta"],
            foreground=self.C["texto_primario"],
            font=("Roboto", 11, "bold"), relief="flat")
        style.map("Cierre.Treeview",
            background=[("selected", self.C["acento"])],
            foreground=[("selected", "#fff")])

        cols = ("id", "hora", "items", "subtotal", "descuento", "total", "metodo", "estado")
        tabla = ttk.Treeview(t, columns=cols, show="headings",
                             style="Cierre.Treeview", height=min(len(ventas), 10))

        for col, titulo, ancho in [
            ("id",       "#",          50),
            ("hora",     "Hora",       80),
            ("items",    "Items",      60),
            ("subtotal", "Subtotal",  100),
            ("descuento","Descuento",  90),
            ("total",    "Total",     100),
            ("metodo",   "Método",     100),
            ("estado",   "Estado",     90),
        ]:
            tabla.heading(col, text=titulo, anchor="center")
            tabla.column(col, width=ancho, anchor="center")

        tabla.tag_configure("anulada",    foreground=self.C["error"])
        tabla.tag_configure("completada", foreground=self.C["texto_primario"])

        for v in sorted(ventas, key=lambda x: x.fecha_venta):
            estado = v.estado.value if hasattr(v.estado, "value") else str(v.estado)
            metodo = v.metodo_pago.value if hasattr(v.metodo_pago, "value") else str(v.metodo_pago)
            tabla.insert("", "end", tags=(estado,), values=(
                v.id_venta,
                v.fecha_venta.strftime("%H:%M"),
                len(v.detalles),
                f"${v.subtotal:,.0f}",
                f"${v.total_descuento:,.0f}",
                f"${v.total:,.0f}",
                metodo.capitalize(),
                estado.capitalize(),
            ))

        scroll_y = ttk.Scrollbar(t, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y", padx=(0, 8), pady=(0, 8))
        tabla.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _seccion_productos(self, productos):
        t = self._tarjeta(3, 0, colspan=2, titulo="🏆  Productos más vendidos hoy")

        if not productos:
            ctk.CTkLabel(t, text="Sin ventas de productos hoy",
                         **self.E["label_subtitulo"]).pack(pady=12)
            return

        cols = ("nombre", "cantidad", "ingresos")
        tabla = ttk.Treeview(t, columns=cols, show="headings",
                             style="Cierre.Treeview", height=min(len(productos), 8))
        for col, titulo, ancho in [
            ("nombre",   "Producto",   250),
            ("cantidad", "Unidades",    90),
            ("ingresos", "Ingresos",   110),
        ]:
            tabla.heading(col, text=titulo, anchor="center")
            tabla.column(col, width=ancho, anchor="center")

        for p in productos:
            tabla.insert("", "end", values=(
                p["nombre"], f"{p['cantidad']:.0f}", f"${p['ingresos']:,.0f}"
            ))

        tabla.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    # ==========================================================
    #  EXPORTAR PDF
    # ==========================================================
    def _exportar_pdf(self):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                            Paragraph, Spacer)
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
        except ImportError:
            messagebox.showerror("Error",
                "Instala reportlab para exportar PDF:\npip install reportlab")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"cierre_caja_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        if not ruta:
            return

        ventas_hoy = self.ven_svc.ventas_de_hoy()
        kpis       = self.rep_svc.kpis_hoy()
        productos  = self.rep_svc.productos_mas_vendidos(10)

        doc    = SimpleDocTemplate(ruta, pagesize=letter,
                                   leftMargin=2*cm, rightMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []

        # Estilo título
        estilo_titulo = ParagraphStyle("titulo", parent=styles["Title"],
                                       fontSize=18, spaceAfter=4)
        estilo_sub    = ParagraphStyle("sub", parent=styles["Normal"],
                                       fontSize=11, textColor=colors.grey, spaceAfter=16)
        estilo_sec    = ParagraphStyle("sec", parent=styles["Heading2"],
                                       fontSize=13, spaceBefore=14, spaceAfter=6)

        # Encabezado
        story.append(Paragraph("Cierre de Caja", estilo_titulo))
        story.append(Paragraph(datetime.now().strftime("%A %d de %B de %Y — %H:%M"), estilo_sub))

        # KPIs
        story.append(Paragraph("Resumen del día", estilo_sec))
        data_kpi = [
            ["Total vendido", "# Ventas", "Ticket promedio", "Descuentos"],
            [
                f"${kpis['total_hoy']:,.0f}",
                str(kpis["num_ventas_hoy"]),
                f"${kpis['ticket_promedio']:,.0f}",
                f"${kpis['descuentos_hoy']:,.0f}",
            ]
        ]
        t_kpi = Table(data_kpi, colWidths=[4.5*cm]*4)
        t_kpi.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN",       (0,0), (-1,-1), "CENTER"),
            ("FONTSIZE",    (0,0), (-1,-1), 11),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f5f5f5"), colors.white]),
            ("GRID",        (0,0), (-1,-1), 0.5, colors.grey),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("TOPPADDING",  (0,0),(-1,-1), 8),
        ]))
        story.append(t_kpi)
        story.append(Spacer(1, 0.4*cm))

        # Detalle ventas
        story.append(Paragraph("Detalle de ventas", estilo_sec))
        completadas = [v for v in ventas_hoy if v.estado.value == "completada"]
        data_v = [["#", "Hora", "Items", "Subtotal", "Descuento", "Total", "Método"]]
        for v in sorted(completadas, key=lambda x: x.fecha_venta):
            metodo = v.metodo_pago.value if hasattr(v.metodo_pago, "value") else str(v.metodo_pago)
            data_v.append([
                str(v.id_venta),
                v.fecha_venta.strftime("%H:%M"),
                str(len(v.detalles)),
                f"${v.subtotal:,.0f}",
                f"${v.total_descuento:,.0f}",
                f"${v.total:,.0f}",
                metodo.capitalize(),
            ])
        # Fila totales
        data_v.append([
            "", "", "TOTAL",
            f"${sum(v.subtotal for v in completadas):,.0f}",
            f"${sum(v.total_descuento for v in completadas):,.0f}",
            f"${sum(v.total for v in completadas):,.0f}",
            "",
        ])

        t_v = Table(data_v, colWidths=[1.2*cm, 1.5*cm, 1.2*cm, 2.8*cm, 2.5*cm, 2.8*cm, 2.5*cm])
        t_v.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME",    (0,-1),(-1,-1),"Helvetica-Bold"),
            ("BACKGROUND",  (0,-1),(-1,-1), colors.HexColor("#e8f5e9")),
            ("ALIGN",       (0,0), (-1,-1), "CENTER"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-2),[colors.HexColor("#f5f5f5"), colors.white]),
            ("GRID",        (0,0), (-1,-1), 0.5, colors.grey),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
            ("TOPPADDING",  (0,0),(-1,-1), 6),
        ]))
        story.append(t_v)
        story.append(Spacer(1, 0.4*cm))

        # Productos más vendidos
        if productos:
            story.append(Paragraph("Productos más vendidos", estilo_sec))
            data_p = [["Producto", "Unidades", "Ingresos"]]
            for p in productos:
                data_p.append([p["nombre"], f"{p['cantidad']:.0f}", f"${p['ingresos']:,.0f}"])
            t_p = Table(data_p, colWidths=[9*cm, 3*cm, 3.5*cm])
            t_p.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#0f3460")),
                ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
                ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
                ("ALIGN",       (0,0), (-1,-1), "CENTER"),
                ("ALIGN",       (0,1), (0,-1),  "LEFT"),
                ("FONTSIZE",    (0,0), (-1,-1), 9),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f5f5f5"), colors.white]),
                ("GRID",        (0,0), (-1,-1), 0.5, colors.grey),
                ("BOTTOMPADDING",(0,0),(-1,-1), 6),
                ("TOPPADDING",  (0,0),(-1,-1), 6),
            ]))
            story.append(t_p)

        # Pie de página
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Kuro Systems",
            ParagraphStyle("pie", parent=styles["Normal"],
                           fontSize=8, textColor=colors.grey, alignment=1)
        ))

        doc.build(story)
        messagebox.showinfo("✔ PDF generado",
                            f"Informe guardado en:\n{ruta}")