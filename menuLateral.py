import customtkinter as ctk


class MenuLateral(ctk.CTkFrame):
    def __init__(self, master, fuentes, estilos, colores, **kwargs):
        super().__init__(master, width=250, corner_radius=0, **kwargs)
        self.F = fuentes
        self.E = estilos
        self.C = colores
        self.configure(fg_color=self.C["fondo_tarjeta"])

        # Por ahora vacío — aquí puedes agregar contenido más adelante
        ctk.CTkLabel(
            self, text="Kuro Systems",
            **self.E["label_titulo"]
        ).pack(padx=20, pady=20)