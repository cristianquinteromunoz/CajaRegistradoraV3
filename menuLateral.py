import customtkinter as ctk
from database.conexion import get_session
from servicios.productos_services import ProductosService


class MenuLateral(ctk.CTkFrame):
    def __init__(self, master, fuentes, estilos, colores, on_logout, **kwargs):
        super().__init__(master, width=250, corner_radius=0, **kwargs)
        self.F         = fuentes
        self.E         = estilos
        self.C         = colores
        self.on_logout = on_logout
        self.usuario   = None

        self.session  = get_session()
        self.prod_svc = ProductosService(self.session)

        self.configure(fg_color=self.C["fondo_tarjeta"])
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Logo ──────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Kuro Systems", **self.E["label_titulo"]
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # ── Panel de alertas ──────────────────────────────────
        self.panel_alertas = ctk.CTkScrollableFrame(
            self, fg_color="transparent", label_text=""
        )
        self.panel_alertas.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.panel_alertas.grid_columnconfigure(0, weight=1)

        # ── Espacio flexible ──────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent").grid(row=2, column=0, sticky="nsew")

        # ── Panel inferior usuario ────────────────────────────
        self.panel_usuario = ctk.CTkFrame(
            self, fg_color=self.C["fondo_secundario"], corner_radius=10
        )
        self.panel_usuario.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 16))
        self.panel_usuario.grid_columnconfigure(0, weight=1)

        self.lbl_nombre = ctk.CTkLabel(
            self.panel_usuario, text="—",
            font=self.F["cuerpo_md"], text_color=self.C["texto_primario"], anchor="w"
        )
        self.lbl_nombre.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))

        self.lbl_rol = ctk.CTkLabel(
            self.panel_usuario, text="",
            font=self.F["cuerpo_sm"], text_color=self.C["texto_secundario"], anchor="w"
        )
        self.lbl_rol.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        ctk.CTkButton(
            self.panel_usuario, text="⏻  Cerrar sesión",
            command=self._cerrar_sesion,
            fg_color=self.C["error"], hover_color="#c0392b",
            text_color="#ffffff", font=self.F["boton"],
            corner_radius=8, height=36,
        ).grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

    # ----------------------------------------------------------
    def set_usuario(self, usuario):
        self.usuario = usuario
        self.lbl_nombre.configure(text=f"👤  {usuario.nombre} {usuario.apellido}")
        self.lbl_rol.configure(text=usuario.rol.nombre if usuario.rol else "")
        self.actualizar_alertas()

    def actualizar_alertas(self):
        """Refresca el panel de alertas."""
        for w in self.panel_alertas.winfo_children():
            w.destroy()

        stock_bajo  = self.prod_svc.productos_bajo_stock()
        por_vencer  = self.prod_svc.productos_proximos_vencer(dias=30)

        if not stock_bajo and not por_vencer:
            ctk.CTkLabel(
                self.panel_alertas, text="✅ Sin alertas",
                font=self.F["cuerpo_sm"], text_color=self.C["exito"]
            ).grid(row=0, column=0, sticky="w", padx=8, pady=4)
            return

        fila = 0

        if stock_bajo:
            self._alerta_titulo(fila, f"⚠ Stock bajo ({len(stock_bajo)})",
                                self.C["advertencia"])
            fila += 1
            for p in stock_bajo:
                self._alerta_fila(fila, f"  {p.nombre}",
                                  f"{p.stock_actual}/{p.stock_minimo}",
                                  self.C["advertencia"])
                fila += 1

        if por_vencer:
            self._alerta_titulo(fila, f"🗓 Por vencer ({len(por_vencer)})",
                                self.C["error"])
            fila += 1
            for p in por_vencer:
                dias_rest = (p.fecha_vencimiento - __import__("datetime").datetime.now()).days
                self._alerta_fila(fila, f"  {p.nombre}",
                                  f"{dias_rest}d",
                                  self.C["error"] if dias_rest <= 7 else self.C["advertencia"])
                fila += 1

    def _alerta_titulo(self, fila, texto, color):
        ctk.CTkLabel(
            self.panel_alertas, text=texto,
            font=self.F["cuerpo_sm"], text_color=color,
            anchor="w"
        ).grid(row=fila, column=0, sticky="ew", padx=6, pady=(8, 2))

    def _alerta_fila(self, fila, nombre, valor, color):
        f = ctk.CTkFrame(self.panel_alertas,
                         fg_color=self.C["fondo_secundario"], corner_radius=6)
        f.grid(row=fila, column=0, sticky="ew", padx=6, pady=1)
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f, text=nombre, font=self.F["cuerpo_sm"],
                     text_color=self.C["texto_primario"],
                     anchor="w").grid(row=0, column=0, sticky="w", padx=6, pady=3)
        ctk.CTkLabel(f, text=valor, font=self.F["cuerpo_sm"],
                     text_color=color).grid(row=0, column=1, padx=6)

    def _cerrar_sesion(self):
        from tkinter import messagebox
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?"):
            self.on_logout()