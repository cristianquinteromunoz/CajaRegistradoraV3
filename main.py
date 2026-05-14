# ============================================================
#  main.py
# ============================================================
from database.init_db import inicializar
import customtkinter as ctk
import menuLateral as Ml
from PIL import Image
import theme

inicializar()


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.F = theme.cargar_fuentes()
        self.E = theme.estilos(self.F)
        self.C = theme.COLORES
        self.title("Kuro Systems")
        self.geometry("1200x840")
        self.configure(fg_color=self.C["fondo_principal"])

        self.usuario_actual = None
        self.menuVisible    = True

        self._mostrar_login()

    # ==========================================================
    #  LOGIN / LOGOUT
    # ==========================================================
    def _mostrar_login(self):
        """Limpia la ventana y muestra la pantalla de login."""
        for w in self.winfo_children():
            w.destroy()

        from views.loggin_frame import LoginFrame
        login = LoginFrame(
            self,
            fuentes=self.F,
            estilos=self.E,
            colores=self.C,
            on_login=self._on_login,
        )
        login.pack(fill="both", expand=True)

    def _on_login(self, usuario):
        """Callback que recibe el usuario logueado y construye la app."""
        self.usuario_actual = usuario
        self._construir_app()

    def _logout(self):
        """Limpia la app y vuelve al login."""
        self.usuario_actual = None
        self.menuVisible    = True
        self._mostrar_login()

    # ==========================================================
    #  CONSTRUCCIÓN DE LA APP
    # ==========================================================
    def _construir_app(self):
        for w in self.winfo_children():
            w.destroy()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Barra superior ────────────────────────────────────
        self.barra_top = ctk.CTkFrame(
            self, fg_color=self.C["fondo_secundario"], height=48, corner_radius=0
        )
        self.barra_top.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.barra_top.grid_propagate(False)

        icono_menu = ctk.CTkImage(Image.open("icon/menu.png"), size=(16, 16))
        ctk.CTkButton(
            self.barra_top, text="", width=40, height=36,
            fg_color=self.C["fondo_secundario"],
            hover_color=self.C["acento_hover"],
            image=icono_menu,
            command=self.toggle_menu,
        ).pack(side="left", padx=8, pady=6)

        # Botones de navegación
        icono_inventario  = ctk.CTkImage(Image.open("icon/inventario.png"),  size=(16, 16))
        icono_facturacion = ctk.CTkImage(Image.open("icon/facturacion.png"), size=(16, 16))
        icono_personal    = ctk.CTkImage(Image.open("icon/personal.png"),    size=(16, 16))
        icono_proveedores = ctk.CTkImage(Image.open("icon/ajustes.png"),     size=(16, 16))
        icono_caja = ctk.CTkImage(Image.open("icon/caja.png"), size=(16, 16))
        icono_dashboard = ctk.CTkImage(Image.open("icon/dashboard.png"), size=(16, 16))

        # Agrega al inicio de la lista de navegación
        for texto, icono, comando in [
            ("Inventario", icono_inventario, self._abrir_inventario),
            ("Facturación", icono_facturacion, self._abrir_facturacion),
            ("Personal", icono_personal, self._abrir_personal),
            ("Proveedores", icono_proveedores, self._abrir_proveedores),
            ("Cierre de caja", icono_caja, self._abrir_cierre),
            ("Dashboard", icono_dashboard, self._abrir_dashboard),
        ]:
            ctk.CTkButton(
                self.barra_top, text=texto, image=icono,
                anchor="w", width=140, height=36,
                fg_color=self.C["fondo_secundario"],
                hover_color=self.C["acento_hover"],
                text_color=self.C["texto_primario"],
                font=self.F["boton"], corner_radius=6,
                command=comando,
            ).pack(side="left", padx=4, pady=6)

        # ── Menú lateral ──────────────────────────────────────
        self.menu = Ml.MenuLateral(
            self,
            fuentes=self.F,
            estilos=self.E,
            colores=self.C,
            on_logout=self._logout,
        )
        self.menu.grid(row=1, column=0, sticky="nsew")
        self.menu.set_usuario(self.usuario_actual)

        # ── Frame de contenido ────────────────────────────────
        self.frame_contenido = ctk.CTkFrame(self, fg_color=self.C["fondo_principal"])
        self.frame_contenido.grid(row=1, column=1, sticky="nsew")
        self.frame_contenido.grid_rowconfigure(0, weight=1)
        self.frame_contenido.grid_columnconfigure(0, weight=1)

    # ==========================================================
    #  TOGGLE MENÚ
    # ==========================================================
    def toggle_menu(self):
        if self.menuVisible:
            self.menu.grid_forget()
            self.menuVisible = False
        else:
            self.menu.grid(row=1, column=0, sticky="nsew")
            self.menuVisible = True

    # ==========================================================
    #  NAVEGACIÓN
    # ==========================================================
    def _cambiar_vista(self, vista_clase, **kwargs):
        # Ocultar todas las vistas actuales
        for w in self.frame_contenido.winfo_children():
            w.grid_remove()

        # Buscar si ya existe una instancia de esta vista
        for w in self.frame_contenido.winfo_children():
            if isinstance(w, vista_clase):
                w.grid()
                return

        # Si no existe, crearla
        vista = vista_clase(
            self.frame_contenido,
            fuentes=self.F,
            estilos=self.E,
            colores=self.C,
            **kwargs
        )
        vista.grid(row=0, column=0, sticky="nsew")

    def _abrir_inventario(self):
        from views.inventario_frame import InventarioFrame
        self._cambiar_vista(InventarioFrame)

    def _abrir_facturacion(self):
        from views.facturacion_frame import FacturacionFrame
        self._cambiar_vista(FacturacionFrame, id_usuario=self.usuario_actual.id_usuario)

    def _abrir_personal(self):
        from views.personal_frame import PersonalFrame
        self._cambiar_vista(PersonalFrame)

    def _abrir_proveedores(self):
        from views.proveedores_frame import ProveedoresFrame
        self._cambiar_vista(ProveedoresFrame, id_usuario=self.usuario_actual.id_usuario)

    def _abrir_dashboard(self):
        from views.dashboard_frame import DashboardFrame
        self._cambiar_vista(DashboardFrame)

    def _abrir_cierre(self):
        from views.cierre_caja_frame import CierreCajaFrame
        self._cambiar_vista(CierreCajaFrame, id_usuario=self.usuario_actual.id_usuario)


ventana = VentanaPrincipal()
ventana.mainloop()