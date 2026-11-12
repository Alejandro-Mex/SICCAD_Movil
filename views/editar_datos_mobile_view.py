import os
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    COLOR_VERDE_GUARDAR, COLOR_ROJO_ELIMINAR, FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient


class EditarDatosMobileView(ft.Container):
    """ Vista Móvil de Editar Datos (Disponible tanto para Empleado como para Estudiante) """
    def __init__(self, page: ft.Page, datos_usuario: dict, al_regresar):
        super().__init__()
        self.page = page
        self.datos_usuario = datos_usuario or {}
        self.al_regresar = al_regresar
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_BLANCO
        self.padding = 0

        self.content = self._construir_interfaz()

    def _crear_input(self, valor_inicial: str, es_password=False):
        return ft.TextField(
            value=str(valor_inicial),
            width=330,
            height=48,
            password=es_password,
            can_reveal_password=es_password,
            bgcolor=COLOR_BLANCO,
            color=COLOR_MORADO_FONDO,
            border_color=COLOR_AMARILLO_TARJETA,
            border_width=2.5,
            border_radius=14,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
            text_style=ft.TextStyle(
                font_family=FAMILIA_FUENTE,
                size=15,
                weight=ft.FontWeight.BOLD,
                color=COLOR_MORADO_FONDO
            )
        )

    def _construir_interfaz(self):
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))

        widget_escudo = (
            ft.Image(src=ruta_escudo, width=55, height=65, fit=ft.ImageFit.CONTAIN)
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=48)
        )

        header_morado = ft.Container(
            bgcolor=COLOR_MORADO_FONDO,
            height=92,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border_radius=ft.border_radius.only(bottom_left=16, bottom_right=16),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.GestureDetector(
                        on_tap=lambda e: self.al_regresar(),
                        content=widget_escudo
                    ),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                        controls=[
                            ft.Text("Centro de", font_family=FAMILIA_FUENTE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
                            ft.Text("Alfabetización Digital", font_family=FAMILIA_FUENTE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
                        ]
                    )
                ]
            )
        )

        usuario_actual = (
            self.datos_usuario.get("usuario")
            or self.datos_usuario.get("numero_empleado")
            or self.datos_usuario.get("id_usuario")
            or ""
        )
        pass_actual = self.datos_usuario.get("password_visible", "")

        self.txt_nombres = self._crear_input(self.datos_usuario.get("nombres", ""))
        self.txt_apellidos = self._crear_input(self.datos_usuario.get("apellidos", ""))
        self.txt_correo = self._crear_input(self.datos_usuario.get("correo", ""))
        self.txt_usuario = self._crear_input(usuario_actual)
        self.txt_password = self._crear_input(pass_actual, es_password=True)

        self.btn_guardar = ft.ElevatedButton(
            content=ft.Text("Guardar", font_family=FAMILIA_FUENTE, size=20, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
            bgcolor=COLOR_VERDE_GUARDAR,
            width=235,
            height=48,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24), elevation=3),
            on_click=self.clic_guardar
        )

        btn_cancelar = ft.ElevatedButton(
            content=ft.Text("Cancelar", font_family=FAMILIA_FUENTE, size=20, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
            bgcolor=COLOR_ROJO_ELIMINAR,
            width=235,
            height=48,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24), elevation=3),
            on_click=lambda e: self.al_regresar()
        )

        cuerpo_scroll = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=8,
            controls=[
                ft.Container(
                    width=330,
                    padding=ft.padding.only(top=10),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=4,
                        controls=[
                            ft.Text("Ingresar nombres:", font_family=FAMILIA_FUENTE, size=16, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self.txt_nombres,
                            ft.Container(height=4),
                            ft.Text("Ingresar apellidos:", font_family=FAMILIA_FUENTE, size=16, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self.txt_apellidos,
                            ft.Container(height=4),
                            ft.Text("Ingresar correo:", font_family=FAMILIA_FUENTE, size=16, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self.txt_correo,
                            ft.Container(height=4),
                            ft.Text("Usuario:", font_family=FAMILIA_FUENTE, size=16, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self.txt_usuario,
                            ft.Container(height=4),
                            ft.Text("Contraseña:", font_family=FAMILIA_FUENTE, size=16, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self.txt_password,
                        ]
                    )
                ),
                ft.Container(height=12),
                self.btn_guardar,
                ft.Container(height=4),
                btn_cancelar,
                ft.Container(height=15)
            ]
        )

        return ft.Column(
            spacing=0,
            expand=True,
            controls=[
                header_morado,
                cuerpo_scroll
            ]
        )

    def mostrar_alerta(self, titulo: str, mensaje: str, regresar_al_cerrar=False):
        def cerrar(e):
            dlg.open = False
            self.page.update()
            if regresar_al_cerrar:
                self.al_regresar()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=COLOR_BLANCO,
            shape=ft.RoundedRectangleBorder(radius=20),
            title=ft.Text(titulo, font_family=FAMILIA_FUENTE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO, text_align=ft.TextAlign.CENTER),
            content=ft.Text(mensaje, font_family=FAMILIA_FUENTE, size=14, color="#000000", text_align=ft.TextAlign.CENTER),
            actions=[ft.ElevatedButton(text="Aceptar", bgcolor=COLOR_MORADO_FONDO, color=COLOR_BLANCO, on_click=cerrar)],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def clic_guardar(self, e):
        nombres = (self.txt_nombres.value or "").strip()
        apellidos = (self.txt_apellidos.value or "").strip()
        correo = (self.txt_correo.value or "").strip()
        usuario = (self.txt_usuario.value or "").strip()
        password = (self.txt_password.value or "").strip()

        if not nombres or not apellidos or not usuario:
            self.mostrar_alerta("Campos obligatorios", "Por favor ingresa Nombres, Apellidos y Usuario.")
            return

        self.btn_guardar.disabled = True
        self.page.update()

        exito, msg = self.firebase.actualizar_datos_perfil_movil({
            "nombres": nombres,
            "apellidos": apellidos,
            "correo": correo,
            "usuario": usuario,
            "contrasena": password
        })

        self.btn_guardar.disabled = False
        self.page.update()

        if exito:
            self.mostrar_alerta("Actualizado", msg, regresar_al_cerrar=True)
        else:
            self.mostrar_alerta("Error", msg, regresar_al_cerrar=False)