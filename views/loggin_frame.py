# ============================================================
#  views/login_frame.py
# ============================================================
import customtkinter as ctk
from tkinter import messagebox
from servicios.usuarios_services import UsuariosService
from database.conexion import get_session


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, fuentes, estilos, colores, on_login, **kwargs):
        super().__init__(parent, **kwargs)
        self.F        = fuentes
        self.E        = estilos
        self.C        = colores
        self.on_login = on_login   # callback(usuario) que llama la ventana principal

        self.session = get_session()
        self.svc     = UsuariosService(self.session)

        self.configure(fg_color=self.C["fondo_principal"])
        self._construir_ui()

    # ==========================================================
    #  UI
    # ==========================================================
    def _construir_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tarjeta centrada
        tarjeta = ctk.CTkFrame(self, **self.E["frame_tarjeta"], width=400)
        tarjeta.grid(row=0, column=0)
        tarjeta.grid_propagate(False)
        tarjeta.configure(width=400, height=440)

        # Logo / nombre del sistema
        ctk.CTkLabel(
            tarjeta, text="🐾",
            font=ctk.CTkFont(size=52),
            text_color=self.C["acento"],
        ).pack(pady=(40, 4))

        ctk.CTkLabel(
            tarjeta, text="Kuro Systems",
            **self.E["label_titulo"],
        ).pack()

        ctk.CTkLabel(
            tarjeta, text="Inicia sesión para continuar",
            **self.E["label_subtitulo"],
        ).pack(pady=(4, 28))

        # Campos
        self.e_usuario = ctk.CTkEntry(
            tarjeta, placeholder_text="Usuario",
            **self.E["entry"]
        )
        self.e_usuario.pack(fill="x", padx=40, pady=(0, 12))

        self.e_password = ctk.CTkEntry(
            tarjeta, placeholder_text="Contraseña",
            show="*", **self.E["entry"]
        )
        self.e_password.pack(fill="x", padx=40, pady=(0, 6))

        # Mensaje de error (oculto por defecto)
        self.lbl_error = ctk.CTkLabel(
            tarjeta, text="",
            font=self.F["cuerpo_sm"],
            text_color=self.C["error"],
        )
        self.lbl_error.pack(pady=(0, 16))

        # Botón
        ctk.CTkButton(
            tarjeta, text="Iniciar sesión",
            command=self._login,
            **self.E["boton_primario"],
        ).pack(fill="x", padx=40, pady=(0, 40))

        # Enter para hacer login
        self.e_usuario.bind("<Return>",  lambda e: self.e_password.focus())
        self.e_password.bind("<Return>", lambda e: self._login())
        self.e_usuario.focus()

    # ==========================================================
    #  LOGIN
    # ==========================================================
    def _login(self):
        username = self.e_usuario.get().strip()
        password = self.e_password.get().strip()

        if not username or not password:
            self._mostrar_error("Completa todos los campos.")
            return

        usuario = self.svc.login(username, password)

        if usuario:
            self.lbl_error.configure(text="")
            self.on_login(usuario)
        else:
            self._mostrar_error("Usuario o contraseña incorrectos.")
            self.e_password.delete(0, "end")
            self.e_password.focus()

    def _mostrar_error(self, mensaje: str):
        self.lbl_error.configure(text=f"⚠  {mensaje}")