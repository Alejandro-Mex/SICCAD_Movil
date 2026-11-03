import os
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    COLOR_ROJO_ELIMINAR, FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient


class ConsultaHorasEstudianteView(ft.Container):
    """
    Pantalla de Consulta de Horas del Estudiante:
    - Tabla de 2 columnas (Fecha | Horas).
    - Letras MORADAS si validado == True | Letras ROJAS si validado == False.
    - Muestra 'Horas restantes:' precargadas desde Firebase.
    - Botón 'Justificacion' abajo.
    """
    def __init__(self, page: ft.Page, datos_estudiante: dict, al_regresar, ir_a_justificacion=None):
        super().__init__()
        self.page = page
        self.datos_estudiante = datos_estudiante or {}
        self.al_regresar = al_regresar
        self.ir_a_justificacion = ir_a_justificacion
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_MORADO_FONDO
        self.padding = ft.padding.symmetric(horizontal=22, vertical=12)

        self.registros_horas = self.firebase.obtener_horas_hechas_alumno(self.datos_estudiante)
        self.columna_filas = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

        self.content = self._construir_interfaz()
        self._renderizar_filas()

    def _construir_interfaz(self):
        # 1. Escudo superior (Tocarlo regresa al Menú del Estudiante)
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))

        widget_escudo = (
            ft.Image(src=ruta_escudo, width=80, height=90, fit=ft.ImageFit.CONTAIN)
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=70)
        )

        # 2. Título superior
        lbl_titulo = ft.Text(
            "Lista de alumnos",
            font_family=FAMILIA_FUENTE,
            size=23,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BLANCO,
            text_align=ft.TextAlign.CENTER
        )

        # 3. Cabecera de 2 Columnas: Fecha (50%) | Horas (50%)
        header_tabla = ft.Row(
            spacing=3,
            controls=[
                ft.Container(
                    expand=5,
                    height=54,
                    bgcolor=COLOR_AMARILLO_TARJETA,
                    border=ft.border.all(2, COLOR_BLANCO),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        "Fecha",
                        font_family=FAMILIA_FUENTE,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_MORADO_FONDO
                    )
                ),
                ft.Container(
                    expand=5,
                    height=54,
                    bgcolor=COLOR_AMARILLO_TARJETA,
                    border=ft.border.all(2, COLOR_BLANCO),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        "Horas",
                        font_family=FAMILIA_FUENTE,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_MORADO_FONDO
                    )
                )
            ]
        )

        contenedor_tabla = ft.Container(
            bgcolor=COLOR_AMARILLO_TARJETA,
            padding=3,
            width=340,
            height=330,
            content=ft.Column(
                spacing=3,
                controls=[
                    header_tabla,
                    ft.Container(
                        expand=True,
                        content=self.columna_filas
                    )
                ]
            )
        )

        # 4. Campo "Horas restantes:"
        horas_restantes_val = str(self.datos_estudiante.get("cantidad_horas", 480))

        caja_horas_restantes = ft.Container(
            width=335,
            height=52,
            bgcolor=COLOR_BLANCO,
            border_radius=16,
            border=ft.border.all(2.5, COLOR_AMARILLO_TARJETA),
            padding=ft.padding.symmetric(horizontal=20),
            alignment=ft.alignment.center_left,
            content=ft.Text(
                horas_restantes_val,
                font_family=FAMILIA_FUENTE,
                size=19,
                weight=ft.FontWeight.BOLD,
                color=COLOR_MORADO_FONDO
            )
        )

        # 5. Botón "Justificacion"
        ruta_ico_just = "icons/justificacion.png"
        existe_ico_just = os.path.exists(os.path.join("assets", ruta_ico_just))

        widget_ico_just = (
            ft.Image(src=ruta_ico_just, width=50, height=50, fit=ft.ImageFit.CONTAIN)
            if existe_ico_just
            else ft.Icon(name=ft.icons.FIND_IN_PAGE_OUTLINED, color=COLOR_MORADO_FONDO, size=44)
        )

        btn_justificacion = ft.Container(
            width=315,
            height=74,
            bgcolor=COLOR_BLANCO,
            border_radius=22,
            border=ft.border.all(2.5, COLOR_AMARILLO_TARJETA),
            padding=ft.padding.symmetric(horizontal=18, vertical=6),
            ink=True,
            on_click=lambda e: self.ir_a_justificacion(self.datos_estudiante) if self.ir_a_justificacion else None,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.colors.with_opacity(0.25, ft.colors.BLACK),
                offset=ft.Offset(0, 3)
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    widget_ico_just,
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            "Justificacion",
                            font_family=FAMILIA_FUENTE,
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_AMARILLO_TARJETA
                        )
                    )
                ]
            )
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            controls=[
                ft.Container(
                    padding=ft.padding.only(top=8),
                    content=ft.GestureDetector(
                        on_tap=lambda e: self.al_regresar(),
                        content=widget_escudo
                    )
                ),
                lbl_titulo,
                contenedor_tabla,
                ft.Container(
                    width=335,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=6,
                        controls=[
                            ft.Text(
                                "Horas restantes:",
                                font_family=FAMILIA_FUENTE,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_AMARILLO_TARJETA
                            ),
                            caja_horas_restantes
                        ]
                    )
                ),
                ft.Container(
                    padding=ft.padding.only(bottom=10),
                    content=btn_justificacion
                )
            ]
        )

    def _renderizar_filas(self):
        self.columna_filas.controls.clear()

        for reg in self.registros_horas:
            # Color dinámico según si ya fue validado en la App de Escritorio:
            # validado == True  -> Letras MORADAS (#553a8f)
            # validado == False -> Letras ROJAS (#FF0015)
            esta_validado = bool(reg.get("validado", False))
            color_texto = COLOR_MORADO_FONDO if esta_validado else COLOR_ROJO_ELIMINAR

            fila = ft.Row(
                spacing=3,
                controls=[
                    ft.Container(
                        expand=5,
                        height=62,
                        bgcolor=COLOR_BLANCO,
                        border=ft.border.all(2, COLOR_AMARILLO_TARJETA),
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            str(reg.get("fecha", "")),
                            font_family=FAMILIA_FUENTE,
                            size=16,
                            weight=ft.FontWeight.BOLD if not esta_validado else ft.FontWeight.W_500,
                            color=color_texto
                        )
                    ),
                    ft.Container(
                        expand=5,
                        height=62,
                        bgcolor=COLOR_BLANCO,
                        border=ft.border.all(2, COLOR_AMARILLO_TARJETA),
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            str(reg.get("horas", "")),
                            font_family=FAMILIA_FUENTE,
                            size=17,
                            weight=ft.FontWeight.BOLD if not esta_validado else ft.FontWeight.W_500,
                            color=color_texto
                        )
                    )
                ]
            )
            self.columna_filas.controls.append(fila)

        self.page.update()