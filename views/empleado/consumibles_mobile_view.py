import os
import time
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient


class ListaConsumiblesMobileView(ft.Container):
    """
    Pantalla 1 de Consumibles Móvil:
    - Tabla de 2 columnas (Descripcion | Cantidad).
    - Doble clic sobre cualquier fila abre la Pantalla 2 para Agregar (+1) o Usar (-1).
    """
    def __init__(self, page: ft.Page, al_regresar, ir_a_detalle):
        super().__init__()
        self.page = page
        self.al_regresar = al_regresar
        self.ir_a_detalle = ir_a_detalle
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_MORADO_FONDO
        self.padding = ft.padding.symmetric(horizontal=22, vertical=15)

        self.items = self.firebase.obtener_consumibles_movil()
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

        # 2. Título "Lista de consumibles"
        lbl_titulo = ft.Text(
            "Lista de consumibles",
            font_family=FAMILIA_FUENTE,
            size=23,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BLANCO,
            text_align=ft.TextAlign.CENTER
        )

        # 3. Cabecera de 2 Columnas: Descripcion (60%) | Cantidad (40%)
        header_tabla = ft.Row(
            spacing=3,
            controls=[
                ft.Container(
                    expand=6,
                    height=58,
                    bgcolor=COLOR_AMARILLO_TARJETA,
                    border=ft.border.all(2, COLOR_BLANCO),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        "Descripcion",
                        font_family=FAMILIA_FUENTE,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_MORADO_FONDO
                    )
                ),
                ft.Container(
                    expand=4,
                    height=58,
                    bgcolor=COLOR_AMARILLO_TARJETA,
                    border=ft.border.all(2, COLOR_BLANCO),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        "Cantidad",
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

        for idx, item in enumerate(self.items):
            esta_seleccionado = (idx == self.indice_seleccionado)
            color_fondo = "#EAE0F6" if esta_seleccionado else COLOR_BLANCO

            fila = ft.GestureDetector(
                on_tap=lambda e, i=idx: self._manejar_clic_fila(i),
                content=ft.Row(
                    spacing=3,
                    controls=[
                        ft.Container(
                            expand=6,
                            height=64,
                            bgcolor=color_fondo,
                            border=ft.border.all(2, COLOR_AMARILLO_TARJETA),
                            alignment=ft.alignment.center,
                            padding=ft.padding.symmetric(horizontal=6),
                            content=ft.Text(
                                str(item.get("descripcion", "")),
                                font_family=FAMILIA_FUENTE,
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color=COLOR_MORADO_FONDO,
                                text_align=ft.TextAlign.CENTER
                            )
                        ),
                        ft.Container(
                            expand=4,
                            height=64,
                            bgcolor=color_fondo,
                            border=ft.border.all(2, COLOR_AMARILLO_TARJETA),
                            alignment=ft.alignment.center,
                            content=ft.Text(
                                str(item.get("cantidad", 0)),
                                font_family=FAMILIA_FUENTE,
                                size=17,
                                weight=ft.FontWeight.W_500,
                                color=COLOR_MORADO_FONDO
                            )
                        )
                    ]
                )
            )
            self.columna_filas.controls.append(fila)

        self.page.update()

    def _manejar_clic_fila(self, idx: int):
        ahora = time.time()
        if idx == self.ultimo_indice_clic and (ahora - self.ultimo_clic_tiempo) < 0.45:
            # Doble clic -> Abre la pantalla de Agregar (+1) / Usar (-1)
            self.ir_a_detalle(self.items[idx])
            return

        self.ultimo_indice_clic = idx
        self.ultimo_clic_tiempo = ahora
        self.indice_seleccionado = idx
        self._renderizar_filas()


class DetalleConsumibleMobileView(ft.Container):
    """
    Pantalla 2 de Consumibles Móvil:
    - Descripcion y Cantidad precargadas.
    - Botón 'Agregar' (Verde #148000): Suma +1 unidad.
    - Botón 'Usar' (Rojo oscuro #A80000): Resta -1 unidad.
    """
    def __init__(self, page: ft.Page, datos_item: dict, al_regresar):
        super().__init__()
        self.page = page
        self.datos_item = datos_item or {}
        self.al_regresar = al_regresar
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_BLANCO
        self.padding = 0

        self.lbl_cantidad = ft.Text(
            str(self.datos_item.get("cantidad", 0)),
            font_family=FAMILIA_FUENTE,
            size=18,
            weight=ft.FontWeight.BOLD,
            color=COLOR_MORADO_FONDO
        )

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

        # 2. Cajas de Descripción y Cantidad
        caja_descripcion = ft.Container(
            width=330,
            height=58,
            bgcolor=COLOR_BLANCO,
            border_radius=16,
            border=ft.border.all(2.8, COLOR_MORADO_FONDO),
            padding=ft.padding.symmetric(horizontal=18),
            alignment=ft.alignment.center_left,
            content=ft.Text(
                str(self.datos_item.get("descripcion", "")),
                font_family=FAMILIA_FUENTE,
                size=17,
                weight=ft.FontWeight.BOLD,
                color=COLOR_MORADO_FONDO
            )
        )

        caja_cantidad = ft.Container(
            width=330,
            height=58,
            bgcolor=COLOR_BLANCO,
            border_radius=16,
            border=ft.border.all(2.8, COLOR_MORADO_FONDO),
            padding=ft.padding.symmetric(horizontal=18),
            alignment=ft.alignment.center_left,
            content=self.lbl_cantidad
        )

        # 3. Botones "Agregar" (+1) y "Usar" (-1)
        btn_agregar = ft.ElevatedButton(
            content=ft.Text(
                "Agregar",
                font_family=FAMILIA_FUENTE,
                size=24,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BLANCO
            ),
            bgcolor="#148000",  # Verde intenso idéntico a tu captura
            width=250,
            height=56,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=28),
                elevation=3
            ),
            on_click=self.clic_agregar
        )

        btn_usar = ft.ElevatedButton(
            content=ft.Text(
                "Usar",
                font_family=FAMILIA_FUENTE,
                size=24,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BLANCO
            ),
            bgcolor="#A80000",  # Rojo oscuro idéntico a tu captura
            width=250,
            height=56,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=28),
                elevation=3
            ),
            on_click=self.clic_usar
        )

        cuerpo = ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=26, vertical=25),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=8,
                        controls=[
                            ft.Text(
                                "Descripcion:",
                                font_family=FAMILIA_FUENTE,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_MORADO_FONDO
                            ),
                            caja_descripcion,
                            ft.Container(height=15),
                            ft.Text(
                                "Cantidad:",
                                font_family=FAMILIA_FUENTE,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_MORADO_FONDO
                            ),
                            caja_cantidad,
                        ]
                    ),
                    ft.Container(height=35),
                    btn_agregar,
                    ft.Container(height=10),
                    btn_usar,
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

    def clic_agregar(self, e):
        """ Suma +1 unidad al producto consumible """
        _, nueva_cant = self.firebase.modificar_cantidad_consumible(self.datos_item, +1)
        self.lbl_cantidad.value = str(nueva_cant)
        self.page.update()

    def clic_usar(self, e):
        """ Resta -1 unidad al producto consumible """
        _, nueva_cant = self.firebase.modificar_cantidad_consumible(self.datos_item, -1)
        self.lbl_cantidad.value = str(nueva_cant)
        self.page.update()