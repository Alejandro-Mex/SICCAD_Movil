import os
from datetime import datetime
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient


class JustificacionEstudianteView(ft.Container):
    """
    Formulario de Justificación del Estudiante:
    - Campo 'Fecha:' (precargado con la fecha actual y editable).
    - Campo 'Justificacion:' (multilínea).
    - Botón 'Enviar' amarillo que guarda en 'usuarios/{id}/control_justificaciones'.
    """
    def __init__(self, page: ft.Page, datos_estudiante: dict, al_regresar):
        super().__init__()
        self.page = page
        self.datos_estudiante = datos_estudiante or {}
        self.al_regresar = al_regresar
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_BLANCO
        self.padding = 0

        self.content = self._construir_interfaz()

    def _construir_interfaz(self):
        # 1. Barra superior morada
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))

        widget_escudo = (
            ft.Image(src=ruta_escudo, width=55, height=65, fit=ft.ImageFit.CONTAIN)
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=48)
        )

        header_morado = ft.Container(
            bgcolor=COLOR_MORADO_FONDO,
            height=95,
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

        # 2. Campo Fecha (Precargado con la fecha de hoy DD/MM/YYYY pero editable)
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        self.txt_fecha = ft.TextField(
            value=fecha_hoy,
            width=330,
            height=54,
            bgcolor=COLOR_BLANCO,
            color=COLOR_MORADO_FONDO,
            border_color=COLOR_MORADO_FONDO,
            border_width=2.5,
            border_radius=16,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=12),
            text_style=ft.TextStyle(
                font_family=FAMILIA_FUENTE,
                size=16,
                weight=ft.FontWeight.W_500,
                color=COLOR_MORADO_FONDO
            )
        )

        # 3. Campo Justificacion (Caja grande multilínea)
        self.txt_justificacion = ft.TextField(
            width=330,
            min_lines=9,
            max_lines=11,
            multiline=True,
            bgcolor=COLOR_BLANCO,
            color=COLOR_MORADO_FONDO,
            border_color=COLOR_MORADO_FONDO,
            border_width=2.5,
            border_radius=18,
            content_padding=ft.padding.all(16),
            text_style=ft.TextStyle(
                font_family=FAMILIA_FUENTE,
                size=15,
                weight=ft.FontWeight.W_500,
                color=COLOR_MORADO_FONDO
            )
        )

        # 4. Botón "Enviar" (Amarillo con letras blancas grandes)
        self.btn_enviar = ft.ElevatedButton(
            content=ft.Text(
                "Enviar",
                font_family=FAMILIA_FUENTE,
                size=24,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BLANCO
            ),
            bgcolor=COLOR_AMARILLO_TARJETA,
            width=245,
            height=54,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=28),
                elevation=3
            ),
            on_click=self.clic_enviar
        )

        cuerpo = ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=26, vertical=22),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True,
                controls=[
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=8,
                        controls=[
                            ft.Text(
                                "Fecha:",
                                font_family=FAMILIA_FUENTE,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_MORADO_FONDO
                            ),
                            self.txt_fecha,
                            ft.Container(height=14),
                            ft.Text(
                                "Justificacion:",
                                font_family=FAMILIA_FUENTE,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_MORADO_FONDO
                            ),
                            self.txt_justificacion,
                        ]
                    ),
                    ft.Container(
                        padding=ft.padding.only(bottom=20),
                        content=self.btn_enviar
                    )
                ]
            )
        )

        return ft.Column(
            spacing=0,
            expand=True,
            controls=[
                header_morado,
                cuerpo
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
                color="#000000",
                text_align=ft.TextAlign.CENTER
            ),
            actions=[
                ft.ElevatedButton(
                    text="Aceptar",
                    bgcolor=COLOR_MORADO_FONDO,
                    color=COLOR_BLANCO,
                    on_click=cerrar
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def clic_enviar(self, e):
        fecha = (self.txt_fecha.value or "").strip()
        justificacion = (self.txt_justificacion.value or "").strip()

        if not fecha or not justificacion:
            self.mostrar_alerta("Campos vacíos", "Por favor ingresa la Fecha y la Justificación antes de enviar.")
            return

        self.btn_enviar.disabled = True
        self.page.update()

        exito, msg = self.firebase.enviar_justificacion_estudiante(
            self.datos_estudiante, fecha, justificacion
        )

        self.btn_enviar.disabled = False
        self.page.update()

        if exito:
            self.mostrar_alerta("Justificación enviada", msg, regresar_al_cerrar=True)
        else:
            self.mostrar_alerta("Error", msg, regresar_al_cerrar=False)