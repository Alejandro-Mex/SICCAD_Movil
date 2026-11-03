import os
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_BLANCO, FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient


class AgregarHorasEstudianteView(ft.Container):
    """
    Pantalla de Agregar Horas del Estudiante:
    - Campo 'Hora de entrada:'
    - Campo 'Hora de salida:'
    - Botón 'Guardar' verde (#148000) que guarda en 'usuarios/{id}/control_horas' con validado=False.
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

        # 2. Campos: Hora de entrada y Hora de salida
        self.txt_hora_entrada = ft.TextField(
            hint_text="Ej. 8:00 am",
            width=330,
            height=58,
            bgcolor=COLOR_BLANCO,
            color=COLOR_MORADO_FONDO,
            border_color=COLOR_MORADO_FONDO,
            border_width=2.8,
            border_radius=16,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=14),
            text_style=ft.TextStyle(
                font_family=FAMILIA_FUENTE,
                size=16,
                weight=ft.FontWeight.BOLD,
                color=COLOR_MORADO_FONDO
            )
        )

        self.txt_hora_salida = ft.TextField(
            hint_text="Ej. 17:00 pm",
            width=330,
            height=58,
            bgcolor=COLOR_BLANCO,
            color=COLOR_MORADO_FONDO,
            border_color=COLOR_MORADO_FONDO,
            border_width=2.8,
            border_radius=16,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=14),
            text_style=ft.TextStyle(
                font_family=FAMILIA_FUENTE,
                size=16,
                weight=ft.FontWeight.BOLD,
                color=COLOR_MORADO_FONDO
            )
        )

        # 3. Botón "Guardar" (Verde #148000 idéntico a tu captura)
        self.btn_guardar = ft.ElevatedButton(
            content=ft.Text(
                "Guardar",
                font_family=FAMILIA_FUENTE,
                size=24,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BLANCO
            ),
            bgcolor="#148000",
            width=250,
            height=56,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=28),
                elevation=3
            ),
            on_click=self.clic_guardar
        )

        cuerpo = ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=26, vertical=28),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True,
                controls=[
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=10,
                        controls=[
                            ft.Text(
                                "Hora de entrada:",
                                font_family=FAMILIA_FUENTE,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_MORADO_FONDO
                            ),
                            self.txt_hora_entrada,
                            ft.Container(height=18),
                            ft.Text(
                                "Hora de salida:",
                                font_family=FAMILIA_FUENTE,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_MORADO_FONDO
                            ),
                            self.txt_hora_salida,
                        ]
                    ),
                    ft.Container(
                        padding=ft.padding.only(bottom=65),
                        content=self.btn_guardar
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

    def clic_guardar(self, e):
        h_entrada = (self.txt_hora_entrada.value or "").strip()
        h_salida = (self.txt_hora_salida.value or "").strip()

        if not h_entrada or not h_salida:
            self.mostrar_alerta("Campos vacíos", "Por favor ingresa la Hora de entrada y la Hora de salida.")
            return

        self.btn_guardar.disabled = True
        self.page.update()

        exito, msg = self.firebase.agregar_horas_estudiante(
            self.datos_estudiante, h_entrada, h_salida
        )

        self.btn_guardar.disabled = False
        self.page.update()

        if exito:
            self.mostrar_alerta("Horas registradas", msg, regresar_al_cerrar=True)
        else:
            self.mostrar_alerta("Error", msg, regresar_al_cerrar=False)