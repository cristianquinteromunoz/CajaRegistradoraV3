# ============================================================
#  theme.py  —  Estilos globales de la aplicación
# ============================================================
import customtkinter as ctk
import pyglet

# ------------------------------------------------------------

pyglet.font.add_file("assets/fonts/StackSansNotch-Bold.ttf")
pyglet.font.add_file("assets/fonts/StackSansNotch-ExtraLight.ttf")
pyglet.font.add_file("assets/fonts/StackSansNotch-Light.ttf")
pyglet.font.add_file("assets/fonts/StackSansNotch-Medium.ttf")
pyglet.font.add_file("assets/fonts/StackSansNotch-Regular.ttf")
pyglet.font.add_file("assets/fonts/StackSansNotch-SemiBold.ttf")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ------------------------------------------------------------
# PALETA DE COLORES
# ------------------------------------------------------------
COLORES = {
    # Fondos
    "fondo_principal":  "#000000",
    "fondo_secundario": "#273745",
    "fondo_tarjeta":    "#095b8b",

    # Acento / botones
    "acento":           "#095b8b",
    "acento_hover":     "#098b7a",
    "acento_secundario":"#098b7a",

    # Texto
    "texto_primario":   "#ffffff",
    "texto_secundario": "#a0a0b0",
    "texto_desactivado":"#555566",

    # Estados
    "exito":            "#4caf50",
    "advertencia":      "#ff9800",
    "error":            "#f44336",
    "info":             "#2196f3",

    # Bordes
    "borde":            "#2a2a4a",
}


def cargar_fuentes() -> dict:

    return {
        # Títulos
        "titulo_xl":  ctk.CTkFont(family="StackSansNotch-Bold", size=40),
        "titulo_lg":  ctk.CTkFont(family="StackSansNotch-Bold", size=28),
        "titulo_md":  ctk.CTkFont(family="StackSansNotch-SemiBold", size=20),
        "titulo_sm":  ctk.CTkFont(family="StackSansNotch-SemiBold", size=16),

        # Cuerpo
        "cuerpo_lg":  ctk.CTkFont(family="StackSansNotch-Light", size=16),
        "cuerpo_md":  ctk.CTkFont(family="StackSansNotch-Light", size=14),
        "cuerpo_sm":  ctk.CTkFont(family="StackSansNotch-Light", size=12),

        # Especiales
        "boton":      ctk.CTkFont(family="StackSansNotch-Regular", size=14, weight="bold"),
        "caption":    ctk.CTkFont(family="StackSansNotch-Regular", size=11, slant="italic"),
        "codigo":     ctk.CTkFont(family="StackSansNotch-Regular", size=13),
    }


def estilos(fuentes: dict) -> dict:

    C = COLORES
    F = fuentes
    return {
        "label_titulo": {
            "font": F["titulo_lg"],
            "text_color": C["texto_primario"],
        },
        "label_subtitulo": {
            "font": F["titulo_sm"],
            "text_color": C["texto_secundario"],
        },
        "label_cuerpo": {
            "font": F["cuerpo_md"],
            "text_color": C["texto_primario"],
        },
        "boton_primario": {
            "font": F["boton"],
            "fg_color": C["acento"],
            "hover_color": C["acento_hover"],
            "text_color": C["texto_primario"],
            "corner_radius": 8,
            "height": 40,
        },
        "boton_secundario": {
            "font": F["boton"],
            "fg_color": "transparent",
            "hover_color": C["fondo_tarjeta"],
            "text_color": C["acento"],
            "border_color": C["acento"],
            "border_width": 2,
            "corner_radius": 8,
            "height": 40,
        },
        "entry": {
            "font": F["cuerpo_md"],
            "fg_color": C["fondo_secundario"],
            "border_color": C["borde"],
            "text_color": C["texto_primario"],
            "corner_radius": 8,
            "height": 40,
        },
        "frame_tarjeta": {
            "fg_color": C["fondo_tarjeta"],
            "corner_radius": 12,
            "border_width": 1,
            "border_color": C["borde"],
        },
    }