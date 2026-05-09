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
        self.title("Ventana Principal")
        self.geometry("1200x840")
        self.configure(fg_color=self.C["fondo_principal"])
        # self.resizable(False, False)

        self.menuVisible = True

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Barra superior (siempre visible) ──────────────────
        self.barra_top = ctk.CTkFrame(self, fg_color=self.C["fondo_secundario"], height=48, corner_radius=0)
        self.barra_top.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.barra_top.grid_propagate(False)

        icono_menu = ctk.CTkImage(Image.open("icon/menu.png"), size=(16, 16))
        self.btn_menuVisible = ctk.CTkButton(
            self.barra_top,
            text="", width=40, height=36,
            fg_color=self.C["fondo_secundario"],
            hover_color=self.C["acento_hover"],
            image=icono_menu,
            command=self.toggle_menu
        )
        self.btn_menuVisible.pack(side="left", padx=8, pady=6)

        # ── Botones de navegación en la barra top ─────────────
        icono_inventario  = ctk.CTkImage(Image.open("icon/inventario.png"),  size=(16, 16))
        icono_facturacion = ctk.CTkImage(Image.open("icon/facturacion.png"), size=(16, 16))
        icono_personal    = ctk.CTkImage(Image.open("icon/personal.png"),    size=(16, 16))
        icono_ajustes     = ctk.CTkImage(Image.open("icon/ajustes.png"),     size=(16, 16))

        navegacion = [
            ("Inventario",  icono_inventario,  self._abrir_inventario),
            ("Facturación", icono_facturacion, self._abrir_facturacion),
            ("Personal",    icono_personal,    self._abrir_personal),
            ("Ajustes",     icono_ajustes,     self._abrir_ajustes),
        ]
        for texto, icono, comando in navegacion:
            ctk.CTkButton(
                self.barra_top,
                text=texto,
                image=icono,
                anchor="w",
                width=140, height=36,
                fg_color=self.C["fondo_secundario"],
                hover_color=self.C["acento_hover"],
                text_color=self.C["texto_primario"],
                font=self.F["boton"],
                corner_radius=6,
                command=comando,
            ).pack(side="left", padx=4, pady=6)

        # ── Menú lateral ──────────────────────────────────────
        self.menu = Ml.MenuLateral(
            self,
            fuentes=self.F,
            estilos=self.E,
            colores=self.C
        )
        self.menu.grid(row=1, column=0, sticky="nsew")

        # ── Frame de contenido ────────────────────────────────
        self.frame_contenido = ctk.CTkFrame(self, fg_color=self.C["fondo_principal"])
        self.frame_contenido.grid(row=1, column=1, sticky="nsew")
        self.frame_contenido.grid_rowconfigure(0, weight=1)
        self.frame_contenido.grid_columnconfigure(0, weight=1)

    # ----------------------------------------------------------
    # NAVEGACIÓN
    # ----------------------------------------------------------
    def _cambiar_vista(self, vista_clase, **kwargs):
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()
        vista = vista_clase(
            self.frame_contenido,
            fuentes=self.F,
            estilos=self.E,
            colores=self.C,
            **kwargs
        )
        vista.pack(fill="both", expand=True)

    def _abrir_inventario(self):
        from views.inventario_frame import InventarioFrame
        self._cambiar_vista(InventarioFrame)

    def _abrir_facturacion(self):
        from views.facturacion_frame import FacturacionFrame
        self._cambiar_vista(FacturacionFrame, id_usuario=1)

    def _abrir_personal(self):
        pass

    def _abrir_ajustes(self):
        pass

    def toggle_menu(self):
        if self.menuVisible:
            self.menu.grid_forget()
            self.menuVisible = False
        else:
            self.menu.grid(row=1, column=0, sticky="nsew")
            self.menuVisible = True


ventana = VentanaPrincipal()
ventana.mainloop()