import os
import time
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient


class ListaAlumnosMobileView(ft.Container):
    """
    Pantalla 1 de Alumnos Móvil:
    - Tabla de 1 columna ('Nombres').
    - Doble clic sobre cualquier alumno abre la Pantalla 2 ('Horas hechas').
    """
    def __init__(self, page: ft.Page, al_regresar, ir_a_horas_hechas):
        super().__init__()
        self.page = page
        self.al_regresar = al_regresar
        self.ir_a_horas_hechas = ir_a_horas_hechas
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_MORADO_FONDO
        self.padding = ft.padding.symmetric(horizontal=22, vertical=15)

        self.alumnos = self.firebase.obtener_alumnos_movil()
        self.indice_seleccionado = None
        self.ultimo_clic_tiempo = 0
        self.ultimo_indice_clic = -1

        self.columna_filas = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
        self.content = self._construir_interfaz()
        self._renderizar_filas()

    def _construir_interfaz(self):
        # 1. Escudo superior
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))

        widget_escudo = (
            ft.Image(src=ruta_escudo, width=85, height=95, fit=ft.ImageFit.CONTAIN)
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=75)
        )

        # 2. Título "Lista de alumnos"
        lbl_titulo = ft.Text(
            "Lista de alumnos",
            font_family=FAMILIA_FUENTE,
            size=23,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BLANCO,
            text_align=ft.TextAlign.CENTER
        )

        # 3. Cabecera de la Tabla ("Nombres")
        header_tabla = ft.Container(
            bgcolor=COLOR_AMARILLO_TARJETA,
            height=58,
            border=ft.border.all(2, COLOR_BLANCO),
            alignment=ft.alignment.center,
            content=ft.Text(
                "Nombres",
                font_family=FAMILIA_FUENTE,
                size=21,
                weight=ft.FontWeight.BOLD,
                color=COLOR_MORADO_FONDO
            )
        )

        contenedor_tabla = ft.Container(
            bgcolor=COLOR_AMARILLO_TARJETA,
            padding=3,
            width=335,
            height=380,
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

        btn_volver_menu = ft.TextButton(
            content=ft.Text(
                "« Volver al menú",
                font_family=FAMILIA_FUENTE,
                size=14,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BLANCO
            ),
            on_click=lambda e: self.al_regresar()
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            controls=[
                ft.Container(
                    padding=ft.padding.only(top=15),
                    content=ft.GestureDetector(
                        on_tap=lambda e: self.al_regresar(),
                        content=widget_escudo
                    )
                ),
                lbl_titulo,
                contenedor_tabla,
                ft.Container(
                    padding=ft.padding.only(bottom=10),
                    content=btn_volver_menu
                )
            ]
        )

    def _renderizar_filas(self):
        self.columna_filas.controls.clear()

        for idx, alumno in enumerate(self.alumnos):
            esta_seleccionado = (idx == self.indice_seleccionado)
            color_fondo = "#EAE0F6" if esta_seleccionado else COLOR_BLANCO

            fila = ft.Container(
                bgcolor=color_fondo,
                height=64,
                border=ft.border.all(2.5, COLOR_AMARILLO_TARJETA),
                alignment=ft.alignment.center,
                ink=True,
                on_click=lambda e, i=idx: self._manejar_clic_fila(i),
                content=ft.Text(
                    str(alumno.get("nombre_mostrar", "")),
                    font_family=FAMILIA_FUENTE,
                    size=17,
                    weight=ft.FontWeight.W_500,
                    color=COLOR_MORADO_FONDO,
                    text_align=ft.TextAlign.CENTER
                )
            )
            self.columna_filas.controls.append(fila)

        self.page.update()

    def _manejar_clic_fila(self, idx: int):
        ahora = time.time()
        if idx == self.ultimo_indice_clic and (ahora - self.ultimo_clic_tiempo) < 0.45:
            # Doble clic -> Abre la tabla de 'Horas hechas' de este alumno
            self.ir_a_horas_hechas(self.alumnos[idx])
            return

        self.ultimo_indice_clic = idx
        self.ultimo_clic_tiempo = ahora
        self.indice_seleccionado = idx
        self._renderizar_filas()


class HorasHechasAlumnoMobileView(ft.Container):
    """
    Pantalla 2 de Alumnos Móvil ('Horas hechas'):
    - Tabla de 2 columnas (Fecha | Horas) con las asistencias del alumno seleccionado.
    """
    def __init__(self, page: ft.Page, datos_alumno: dict, al_regresar):
        super().__init__()
        self.page = page
        self.datos_alumno = datos_alumno or {}
        self.al_regresar = al_regresar
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_MORADO_FONDO
        self.padding = ft.padding.symmetric(horizontal=22, vertical=15)

        self.registros_horas = self.firebase.obtener_horas_hechas_alumno(self.datos_alumno)
        self.columna_filas = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

        self.content = self._construir_interfaz()
        self._renderizar_filas()

    def _construir_interfaz(self):
        # 1. Escudo superior
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))

        widget_escudo = (
            ft.Image(src=ruta_escudo, width=85, height=95, fit=ft.ImageFit.CONTAIN)
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=75)
        )

        # 2. Título "Horas hechas"
        lbl_titulo = ft.Text(
            "Horas hechas",
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
                    height=58,
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
                    height=58,
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
            height=380,
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

        btn_volver = ft.TextButton(
            content=ft.Text(
                "« Volver a lista de alumnos",
                font_family=FAMILIA_FUENTE,
                size=14,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BLANCO
            ),
            on_click=lambda e: self.al_regresar()
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            controls=[
                ft.Container(
                    padding=ft.padding.only(top=15),
                    content=ft.GestureDetector(
                        on_tap=lambda e: self.al_regresar(),
                        content=widget_escudo
                    )
                ),
                lbl_titulo,
                contenedor_tabla,
                ft.Container(
                    padding=ft.padding.only(bottom=10),
                    content=btn_volver
                )
            ]
        )

    def _renderizar_filas(self):
        self.columna_filas.controls.clear()

        for reg in self.registros_horas:
            fila = ft.Row(
                spacing=3,
                controls=[
                    ft.Container(
                        expand=5,
                        height=64,
                        bgcolor=COLOR_BLANCO,
                        border=ft.border.all(2, COLOR_AMARILLO_TARJETA),
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            str(reg.get("fecha", "")),
                            font_family=FAMILIA_FUENTE,
                            size=16,
                            weight=ft.FontWeight.W_500,
                            color=COLOR_MORADO_FONDO
                        )
                    ),
                    ft.Container(
                        expand=5,
                        height=64,
                        bgcolor=COLOR_BLANCO,
                        border=ft.border.all(2, COLOR_AMARILLO_TARJETA),
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            str(reg.get("horas", "")),
                            font_family=FAMILIA_FUENTE,
                            size=17,
                            weight=ft.FontWeight.W_500,
                            color=COLOR_MORADO_FONDO
                        )
                    )
                ]
            )
            self.columna_filas.controls.append(fila)

        self.page.update()