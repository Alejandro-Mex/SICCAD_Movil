import os
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    COLOR_TEXTO_NEGRO, COLOR_ROJO_ELIMINAR, FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient


class LoginMobileView(ft.Container):
    """ Interfaz 1 Móvil: Inicio de sesión (Versión Empleado) """
    def __init__(self, page: ft.Page, al_iniciar_sesion_exitoso):
        super().__init__()
        self.page = page
        self.al_iniciar_sesion_exitoso = al_iniciar_sesion_exitoso
        self.firebase = FirebaseMobileClient()

        # Configuración del contenedor de pantalla completa
        self.expand = True
        self.bgcolor = COLOR_MORADO_FONDO
        self.padding = ft.padding.symmetric(horizontal=28, vertical=20)
        self.alignment = ft.alignment.center

        self.content = self._construir_interfaz()

    def _construir_interfaz(self):
        # 1. ESCUDO DEL AYUNTAMIENTO (Si existe en assets/logos/escudo_merida.png lo muestra)
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))

        widget_escudo = (
            ft.Image(
                src=ruta_escudo,
                width=115,
                height=130,
                fit=ft.ImageFit.CONTAIN
            )
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=95)
        )

        # 2. TÍTULOS INSTITUCIONALES
        lbl_cad = ft.Text(
            "Centro de Alfabetización Digital",
            font_family=FAMILIA_FUENTE,
            size=19,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BLANCO,
            text_align=ft.TextAlign.CENTER
        )

        lbl_merida = ft.Text(
            "Ayuntamiento de Mérida",
            font_family=FAMILIA_FUENTE,
            size=15,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BLANCO,
            text_align=ft.TextAlign.CENTER
        )

        # 3. CAMPOS DE ENTRADA (Usuario y Contraseña)
        self.txt_usuario = ft.TextField(
            bgcolor=COLOR_BLANCO,
            color=COLOR_TEXTO_NEGRO,
            border_radius=25,
            border_width=0,
            height=46,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=10),
            text_style=ft.TextStyle(font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD),
            on_submit=self.intentar_login  # Permite iniciar sesión al dar Enter / "Ir" en el teclado del celular
        )

        self.txt_password = ft.TextField(
            bgcolor=COLOR_BLANCO,
            color=COLOR_TEXTO_NEGRO,
            password=True,
            can_reveal_password=False,
            border_radius=25,
            border_width=0,
            height=46,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=10),
            text_style=ft.TextStyle(font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD),
            on_submit=self.intentar_login
        )

        # 4. BOTÓN "Entrar"
        self.btn_entrar = ft.ElevatedButton(
            content=ft.Text(
                "Entrar",
                font_family=FAMILIA_FUENTE,
                size=18,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BLANCO
            ),
            bgcolor=COLOR_MORADO_FONDO,
            width=210,
            height=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=25),
                elevation=2
            ),
            on_click=self.intentar_login
        )

        # 5. TARJETA AMARILLA (#FCCb2d) CON BORDE BLANCO Y SOMBRA
        tarjeta_amarilla = ft.Container(
            bgcolor=COLOR_AMARILLO_TARJETA,
            border_radius=28,
            border=ft.border.all(2.5, COLOR_BLANCO),
            padding=ft.padding.symmetric(horizontal=24, vertical=30),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.with_opacity(0.35, ft.colors.BLACK),
                offset=ft.Offset(0, 5)
            ),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=8,
                controls=[
                    ft.Text(
                        "Usuario:",
                        font_family=FAMILIA_FUENTE,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO_NEGRO
                    ),
                    self.txt_usuario,
                    ft.Container(height=6),
                    ft.Text(
                        "Contraseña:",
                        font_family=FAMILIA_FUENTE,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXTO_NEGRO
                    ),
                    self.txt_password,
                    ft.Container(height=16),
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=self.btn_entrar
                    )
                ]
            )
        )

        # COLUMNA PRINCIPAL CENTRADA
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
            controls=[
                widget_escudo,
                ft.Container(height=6),
                lbl_cad,
                lbl_merida,
                ft.Container(height=28),
                tarjeta_amarilla
            ]
        )

    def mostrar_alerta(self, titulo: str, mensaje: str):
        """ Muestra un modal emergente con el estilo institucional en el celular """
        def cerrar_dlg(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=COLOR_BLANCO,
            shape=ft.RoundedRectangleBorder(radius=20),
            title=ft.Text(
                titulo,
                font_family=FAMILIA_FUENTE,
                size=18,
                weight=ft.FontWeight.BOLD,
                color=COLOR_MORADO_FONDO,
                text_align=ft.TextAlign.CENTER
            ),
            content=ft.Text(
                mensaje,
                font_family=FAMILIA_FUENTE,
                size=14,
                weight=ft.FontWeight.W_500,
                color=COLOR_TEXTO_NEGRO,
                text_align=ft.TextAlign.CENTER
            ),
            actions=[
                ft.ElevatedButton(
                    text="Aceptar",
                    bgcolor=COLOR_MORADO_FONDO,
                    color=COLOR_BLANCO,
                    on_click=cerrar_dlg
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def intentar_login(self, e=None):
        usuario = (self.txt_usuario.value or "").strip()
        password = (self.txt_password.value or "").strip()

        if not usuario or not password:
            self.mostrar_alerta("Campos vacíos", "Por favor, ingresa tu Usuario y Contraseña.")
            return

        self.btn_entrar.disabled = True
        self.page.update()

        exito, resultado = self.firebase.validar_login_movil_empleado(usuario, password)

        self.btn_entrar.disabled = False
        self.page.update()

        if exito:
            # Pasa los datos y permisos del empleado al Menú Principal Móvil
            self.al_iniciar_sesion_exitoso(resultado)
        else:
            self.mostrar_alerta("Acceso denegado", resultado)