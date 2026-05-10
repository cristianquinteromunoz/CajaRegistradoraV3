import customtkinter as ctk


class MenuLateral(ctk.CTkFrame):
    def __init__(self, master, fuentes, estilos, colores, on_logout, **kwargs):
        super().__init__(master, width=250, corner_radius=0, **kwargs)
        self.F          = fuentes
        self.E          = estilos
        self.C          = colores
        self.on_logout  = on_logout   # callback para cerrar sesión
        self.usuario    = None

        self.configure(fg_color=self.C["fondo_tarjeta"])
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Logo ──────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Kuro Systems",
            **self.E["label_titulo"]
        ).grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # ── Espacio central libre ──────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent").grid(row=1, column=0, sticky="nsew")

        # ── Panel inferior del usuario ─────────────────────────
        self.panel_usuario = ctk.CTkFrame(
            self, fg_color=self.C["fondo_secundario"], corner_radius=10
        )
        self.panel_usuario.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 16))
        self.panel_usuario.grid_columnconfigure(0, weight=1)

        self.lbl_nombre = ctk.CTkLabel(
            self.panel_usuario, text="—",
            font=self.F["cuerpo_md"],
            text_color=self.C["texto_primario"],
            anchor="w",
        )
        self.lbl_nombre.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))

        self.lbl_rol = ctk.CTkLabel(
            self.panel_usuario, text="",
            font=self.F["cuerpo_sm"],
            text_color=self.C["texto_secundario"],
            anchor="w",
        )
        self.lbl_rol.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        ctk.CTkButton(
            self.panel_usuario, text="⏻  Cerrar sesión",
            command=self._cerrar_sesion,
            fg_color=self.C["error"],
            hover_color="#c0392b",
            text_color="#ffffff",
            font=self.F["boton"],
            corner_radius=8,
            height=36,
        ).grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 10))

    def set_usuario(self, usuario):
        """Actualiza el panel inferior con los datos del usuario logueado."""
        self.usuario = usuario
        self.lbl_nombre.configure(text=f"👤  {usuario.nombre} {usuario.apellido}")
        self.lbl_rol.configure(text=usuario.rol.nombre if usuario.rol else "")

    def _cerrar_sesion(self):
        from tkinter import messagebox
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?"):
            self.on_logout()