# ============================================================
#  views/dashboard_frame.py
# ============================================================
import customtkinter as ctk
from tkinter import ttk
from database.conexion import get_session
from servicios.reportes_service import ReportesService
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


# Paleta para matplotlib (se actualiza al construir)
_COLORES = {}


def _estilo_figura(fig, ax, color_fondo, color_texto):
    fig.patch.set_facecolor(color_fondo)
    ax.set_facecolor(color_fondo)
    ax.tick_params(colors=color_texto, labelsize=8)
    ax.xaxis.label.set_color(color_texto)
    ax.yaxis.label.set_color(color_texto)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a2a4a")


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, fuentes, estilos, colores, **kwargs):
        super().__init__(parent, **kwargs)
        self.F = fuentes
        self.E = estilos
        self.C = colores
        global _COLORES
        _COLORES = colores

        self.session = get_session()
        self.svc     = ReportesService(self.session)

        self.configure(fg_color=self.C["fondo_principal"])
        self._construir_ui()
        self.actualizar()

    # ==========================================================
    #  LAYOUT PRINCIPAL
    # ==========================================================
    def _construir_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Encabezado ────────────────────────────────────────
        enc = ctk.CTkFrame(self, fg_color="transparent")
        enc.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 0))
        enc.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(enc, text="Dashboard", **self.E["label_titulo"]).grid(
            row=0, column=0, sticky="w")
        self.lbl_fecha = ctk.CTkLabel(enc, text="", **self.E["label_subtitulo"])
        self.lbl_fecha.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(enc, text="🔄  Actualizar", command=self.actualizar,
                      **self.E["boton_primario"], width=130).grid(
            row=0, column=2, padx=(12, 0))

        # ── Área scrollable ───────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        self.scroll.grid_columnconfigure((0, 1, 2, 3), weight=1)

    # ==========================================================
    #  ACTUALIZAR TODO
    # ==========================================================
    def actualizar(self):
        self.lbl_fecha.configure(
            text=f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # Limpiar contenido anterior
        for w in self.scroll.winfo_children():
            w.destroy()

        self._construir_kpis()
        self._construir_comparativo()
        self._grafica_ventas_diarias()
        self._grafica_horas_pico()
        self._grafica_gastos_ingresos()
        self._tabla_productos_vendidos()
        self._tabla_stock_bajo()
        self._tabla_empleados()
        self._tabla_proveedores()

    # ==========================================================
    #  HELPERS
    # ==========================================================
    def _tarjeta(self, fila, col, colspan=1, rowspan=1) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self.scroll, **self.E["frame_tarjeta"])
        f.grid(row=fila, column=col, columnspan=colspan, rowspan=rowspan,
               sticky="nsew", padx=6, pady=6)
        return f

    def _kpi_card(self, parent, titulo, valor, subtitulo="", color=None):
        card = ctk.CTkFrame(parent, fg_color=self.C["fondo_secundario"], corner_radius=10)
        card.pack(side="left", expand=True, fill="both", padx=6, pady=6)
        ctk.CTkLabel(card, text=titulo, font=self.F["cuerpo_sm"],
                     text_color=self.C["texto_secundario"]).pack(pady=(12, 2))
        ctk.CTkLabel(card, text=valor, font=self.F["titulo_lg"],
                     text_color=color or self.C["texto_primario"]).pack()
        if subtitulo:
            ctk.CTkLabel(card, text=subtitulo, font=self.F["cuerpo_sm"],
                         text_color=self.C["texto_secundario"]).pack(pady=(2, 12))
        else:
            card.pack_configure(pady=(0, 6))

    def _seccion_titulo(self, parent, texto):
        ctk.CTkLabel(parent, text=texto, **self.E["label_titulo"]).pack(
            anchor="w", padx=16, pady=(14, 6))

    def _canvas_grafica(self, parent, fig) -> FigureCanvasTkAgg:
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 10))
        return canvas

    def _mini_tabla(self, parent, cols: list, filas: list):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dash.Treeview",
            background=self.C["fondo_secundario"],
            foreground=self.C["texto_primario"],
            fieldbackground=self.C["fondo_secundario"],
            rowheight=28, font=("Roboto", 11), borderwidth=0)
        style.configure("Dash.Treeview.Heading",
            background=self.C["fondo_tarjeta"],
            foreground=self.C["texto_primario"],
            font=("Roboto", 11, "bold"), relief="flat")
        style.map("Dash.Treeview",
            background=[("selected", self.C["acento"])],
            foreground=[("selected", "#fff")])

        ids   = [c[0] for c in cols]
        tabla = ttk.Treeview(parent, columns=ids, show="headings",
                             style="Dash.Treeview", height=min(len(filas), 7))
        for cid, titulo, ancho in cols:
            tabla.heading(cid, text=titulo, anchor="center")
            tabla.column(cid, width=ancho, anchor="center", minwidth=40)
        for fila in filas:
            tabla.insert("", "end", values=fila)

        scroll = ttk.Scrollbar(parent, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", padx=(0, 8), pady=(0, 8))
        tabla.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    # ==========================================================
    #  SECCIÓN 1 — KPIs
    # ==========================================================
    def _construir_kpis(self):
        t = self._tarjeta(0, 0, colspan=4)
        self._seccion_titulo(t, "📊  Resumen del día y mes")

        kpi_hoy = self.svc.kpis_hoy()
        kpi_mes = self.svc.kpis_mes()
        comp    = self.svc.comparativo_semanas()

        fila_hoy = ctk.CTkFrame(t, fg_color="transparent")
        fila_hoy.pack(fill="x", padx=6)

        self._kpi_card(fila_hoy, "Ventas hoy",
                       f"${kpi_hoy['total_hoy']:,.0f}",
                       f"{kpi_hoy['num_ventas_hoy']} transacciones",
                       self.C["acento"])
        self._kpi_card(fila_hoy, "Ticket promedio",
                       f"${kpi_hoy['ticket_promedio']:,.0f}",
                       "Por venta hoy")
        self._kpi_card(fila_hoy, "Descuentos hoy",
                       f"${kpi_hoy['descuentos_hoy']:,.0f}",
                       color=self.C["advertencia"])
        self._kpi_card(fila_hoy, "Ventas del mes",
                       f"${kpi_mes['total_mes']:,.0f}",
                       f"{kpi_mes['num_ventas_mes']} transacciones",
                       self.C["info"])
        self._kpi_card(fila_hoy, "Gastos del mes",
                       f"${kpi_mes['gastos_mes']:,.0f}",
                       color=self.C["error"])
        self._kpi_card(fila_hoy, "Utilidad del mes",
                       f"${kpi_mes['utilidad_mes']:,.0f}",
                       color=self.C["exito"])

        # Comparativo semanas
        signo = "▲" if comp["cambio_pct"] >= 0 else "▼"
        color = self.C["exito"] if comp["cambio_pct"] >= 0 else self.C["error"]
        self._kpi_card(fila_hoy, "vs Semana anterior",
                       f"{signo} {abs(comp['cambio_pct']):.1f}%",
                       f"Esta: ${comp['esta_semana']:,.0f}  |  Ant: ${comp['semana_anterior']:,.0f}",
                       color)

    # ==========================================================
    #  SECCIÓN 2 — Comparativo períodos
    # ==========================================================
    def _construir_comparativo(self):
        t = self._tarjeta(1, 0, colspan=4)
        self._seccion_titulo(t, "📅  Ventas por mes (últimos 6 meses)")

        datos = self.svc.ventas_por_mes(6)
        if not datos:
            ctk.CTkLabel(t, text="Sin datos aún", **self.E["label_subtitulo"]).pack(pady=20)
            return

        periodos = [d["periodo"]  for d in datos]
        totales  = [d["total"]    for d in datos]
        cantidades = [d["cantidad"] for d in datos]

        fig, ax1 = plt.subplots(figsize=(10, 2.8))
        ax2 = ax1.twinx()
        _estilo_figura(fig, ax1, self.C["fondo_tarjeta"], self.C["texto_primario"])
        ax2.set_facecolor(self.C["fondo_tarjeta"])
        ax2.tick_params(colors=self.C["texto_secundario"], labelsize=8)

        x = range(len(periodos))
        ax1.bar(x, totales, color=self.C["acento"], alpha=0.8, label="Total $")
        ax2.plot(x, cantidades, color=self.C["exito"], marker="o", linewidth=2, label="# Ventas")
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(periodos, rotation=0, fontsize=8)
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
        fig.tight_layout(pad=1.2)
        self._canvas_grafica(t, fig)
        plt.close(fig)

    # ==========================================================
    #  SECCIÓN 3 — Ventas diarias
    # ==========================================================
    def _grafica_ventas_diarias(self):
        t = self._tarjeta(2, 0, colspan=2)
        self._seccion_titulo(t, "📈  Ventas últimos 30 días")

        datos = self.svc.ventas_por_dia(30)
        if not datos:
            ctk.CTkLabel(t, text="Sin datos aún", **self.E["label_subtitulo"]).pack(pady=20)
            return

        dias    = [d["dia"][-5:]  for d in datos]   # MM-DD
        totales = [d["total"]     for d in datos]

        fig, ax = plt.subplots(figsize=(5.5, 2.6))
        _estilo_figura(fig, ax, self.C["fondo_tarjeta"], self.C["texto_primario"])
        ax.fill_between(range(len(dias)), totales, alpha=0.3, color=self.C["acento"])
        ax.plot(range(len(dias)), totales, color=self.C["acento"], linewidth=2)
        step = max(1, len(dias) // 6)
        ax.set_xticks(range(0, len(dias), step))
        ax.set_xticklabels(dias[::step], rotation=30, fontsize=7)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1000:.0f}k"))
        fig.tight_layout(pad=1.2)
        self._canvas_grafica(t, fig)
        plt.close(fig)

    # ==========================================================
    #  SECCIÓN 4 — Horas pico
    # ==========================================================
    def _grafica_horas_pico(self):
        t = self._tarjeta(2, 2, colspan=2)
        self._seccion_titulo(t, "⏰  Horas pico de ventas")

        datos = self.svc.horas_pico()
        if not datos:
            ctk.CTkLabel(t, text="Sin datos aún", **self.E["label_subtitulo"]).pack(pady=20)
            return

        horas     = [d["hora"]     for d in datos]
        cantidades = [d["cantidad"] for d in datos]

        fig, ax = plt.subplots(figsize=(5.5, 2.6))
        _estilo_figura(fig, ax, self.C["fondo_tarjeta"], self.C["texto_primario"])
        bars = ax.bar(horas, cantidades, color=self.C["acento_secundario"], alpha=0.85)
        max_val = max(cantidades) if cantidades else 1
        for bar, val in zip(bars, cantidades):
            if val == max_val:
                bar.set_color(self.C["acento"])
        ax.set_xticks(range(len(horas)))
        ax.set_xticklabels(horas, rotation=45, fontsize=7)
        ax.set_ylabel("# ventas", fontsize=8)
        fig.tight_layout(pad=1.2)
        self._canvas_grafica(t, fig)
        plt.close(fig)

    # ==========================================================
    #  SECCIÓN 5 — Gastos vs Ingresos
    # ==========================================================
    def _grafica_gastos_ingresos(self):
        t = self._tarjeta(3, 0, colspan=4)
        self._seccion_titulo(t, "💰  Gastos vs Ingresos (últimos 6 meses)")

        datos = self.svc.gastos_vs_ingresos(6)
        if not datos:
            ctk.CTkLabel(t, text="Sin datos aún", **self.E["label_subtitulo"]).pack(pady=20)
            return

        periodos  = [d["periodo"]  for d in datos]
        ingresos  = [d["ingresos"] for d in datos]
        gastos    = [d["gastos"]   for d in datos]
        utilidades = [d["utilidad"] for d in datos]

        fig, ax = plt.subplots(figsize=(10, 2.8))
        _estilo_figura(fig, ax, self.C["fondo_tarjeta"], self.C["texto_primario"])
        x  = range(len(periodos))
        w  = 0.3
        ax.bar([i - w for i in x], ingresos,  width=w, label="Ingresos",  color=self.C["exito"],   alpha=0.85)
        ax.bar(list(x),             gastos,    width=w, label="Gastos",    color=self.C["error"],   alpha=0.85)
        ax.bar([i + w for i in x], utilidades, width=w, label="Utilidad", color=self.C["info"],    alpha=0.85)
        ax.set_xticks(list(x))
        ax.set_xticklabels(periodos, fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
        ax.legend(fontsize=8, facecolor=self.C["fondo_secundario"],
                  labelcolor=self.C["texto_primario"], framealpha=0.8)
        fig.tight_layout(pad=1.2)
        self._canvas_grafica(t, fig)
        plt.close(fig)

    # ==========================================================
    #  SECCIÓN 6 — Productos más vendidos
    # ==========================================================
    def _tabla_productos_vendidos(self):
        t = self._tarjeta(4, 0, colspan=2)
        self._seccion_titulo(t, "🏆  Productos más vendidos")

        datos = self.svc.productos_mas_vendidos(10)
        if not datos:
            ctk.CTkLabel(t, text="Sin ventas registradas", **self.E["label_subtitulo"]).pack(pady=20)
            return

        cols = [
            ("nombre",   "Producto",   180),
            ("cantidad", "Unidades",    80),
            ("ingresos", "Ingresos",   100),
        ]
        filas = [(d["nombre"], f"{d['cantidad']:.0f}", f"${d['ingresos']:,.0f}") for d in datos]
        self._mini_tabla(t, cols, filas)

    # ==========================================================
    #  SECCIÓN 7 — Stock bajo
    # ==========================================================
    def _tabla_stock_bajo(self):
        t = self._tarjeta(4, 2, colspan=2)
        self._seccion_titulo(t, "⚠️  Productos con stock bajo")

        datos = self.svc.productos_stock_bajo()
        if not datos:
            ctk.CTkLabel(t, text="✅ Todos los productos tienen stock suficiente",
                         font=self.F["cuerpo_md"], text_color=self.C["exito"]).pack(pady=20)
            return

        cols = [
            ("nombre",   "Producto",  180),
            ("actual",   "Stock",      70),
            ("minimo",   "Mínimo",     70),
            ("unidad",   "Unidad",     80),
        ]
        filas = [(p.nombre, p.stock_actual, p.stock_minimo, p.unidad_medida or "—") for p in datos]
        self._mini_tabla(t, cols, filas)

    # ==========================================================
    #  SECCIÓN 8 — Rendimiento empleados
    # ==========================================================
    def _tabla_empleados(self):
        t = self._tarjeta(5, 0, colspan=2)
        self._seccion_titulo(t, "👤  Rendimiento por empleado")

        datos = self.svc.rendimiento_empleados()
        if not datos:
            ctk.CTkLabel(t, text="Sin datos aún", **self.E["label_subtitulo"]).pack(pady=20)
            return

        cols = [
            ("nombre",    "Empleado",       160),
            ("ventas",    "# Ventas",        70),
            ("total",     "Total vendido",  110),
            ("ticket",    "Ticket prom.",   100),
            ("descuentos","Descuentos",      90),
        ]
        filas = [(d["nombre"], d["num_ventas"], f"${d['total']:,.0f}",
                  f"${d['ticket_prom']:,.0f}", f"${d['descuentos']:,.0f}") for d in datos]
        self._mini_tabla(t, cols, filas)

    # ==========================================================
    #  SECCIÓN 9 — Estado proveedores
    # ==========================================================
    def _tabla_proveedores(self):
        t = self._tarjeta(5, 2, colspan=2)
        self._seccion_titulo(t, "🏭  Estado de cuenta proveedores")

        datos = self.svc.estado_proveedores()
        if not datos:
            ctk.CTkLabel(t, text="✅ Sin deudas con proveedores",
                         font=self.F["cuerpo_md"], text_color=self.C["exito"]).pack(pady=20)
            return

        cols = [
            ("proveedor", "Proveedor", 200),
            ("saldo",     "Saldo",     110),
        ]
        filas = [(d["proveedor"],
                  f"${d['saldo']:,.0f}" if d["saldo"] >= 0 else f"-${abs(d['saldo']):,.0f}")
                 for d in datos]
        self._mini_tabla(t, cols, filas)