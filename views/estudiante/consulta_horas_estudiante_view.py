import os
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    COLOR_ROJO_ELIMINAR, FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient
from utils.pdf_mobile_generator import generar_pdf_horas_alumno_movil


class ConsultaHorasEstudianteView(ft.Container):
    """
    Pantalla de Consulta de Horas del Estudiante:
    - Tabla (Fecha | Horas) con selección de fila.
    - Botón 'Eliminar' (Rojo): Borra la hora seleccionada SOLO si aún no está validada (roja).
    - Botón 'Imprimir PDF': Genera el reporte de horas del alumno.
    - Botón 'Justificación'.
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
        self.padding = ft.padding.symmetric(horizontal=20, vertical=10)

        self.registros_horas = self.firebase.obtener_horas_hechas_alumno(self.datos_estudiante)
        self.indice_seleccionado = None
        self.columna_filas = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

        self.content = self._construir_interfaz()
        self._renderizar_filas()

    def _construir_interfaz(self):
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))
        widget_escudo = (
            ft.Image(src=ruta_escudo, width=70, height=80, fit=ft.ImageFit.CONTAIN)
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=62)
        )

        lbl_titulo = ft.Text(
            "Mis Horas",
            font_family=FAMILIA_FUENTE, size=22, weight=ft.FontWeight.BOLD,
            color=COLOR_BLANCO, text_align=ft.TextAlign.CENTER
        )

        header_tabla = ft.Row(
            spacing=3,
            controls=[
                ft.Container(
                    expand=5, height=48, bgcolor=COLOR_AMARILLO_TARJETA,
                    border=ft.border.all(2, COLOR_BLANCO), alignment=ft.alignment.center,
                    content=ft.Text("Fecha", font_family=FAMILIA_FUENTE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO)
                ),
                ft.Container(
                    expand=5, height=48, bgcolor=COLOR_AMARILLO_TARJETA,
                    border=ft.border.all(2, COLOR_BLANCO), alignment=ft.alignment.center,
                    content=ft.Text("Horas", font_family=FAMILIA_FUENTE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO)
                )
            ]
        )

        contenedor_tabla = ft.Container(
            bgcolor=COLOR_AMARILLO_TARJETA, padding=3, width=340, height=275,
            content=ft.Column(spacing=3, controls=[header_tabla, ft.Container(expand=True, content=self.columna_filas)])
        )

        horas_restantes_val = str(self.datos_estudiante.get("cantidad_horas", 480))
        caja_horas_restantes = ft.Container(
            width=335, height=46, bgcolor=COLOR_BLANCO, border_radius=14,
            border=ft.border.all(2.5, COLOR_AMARILLO_TARJETA), padding=ft.padding.symmetric(horizontal=18),
            alignment=ft.alignment.center_left,
            content=ft.Text(horas_restantes_val, font_family=FAMILIA_FUENTE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO)
        )

        # Fila de botones de acción: Eliminar (solo no validadas) | Imprimir PDF
        btn_eliminar = ft.ElevatedButton(
            content=ft.Text("Eliminar hora", font_family=FAMILIA_FUENTE, size=14, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
            bgcolor=COLOR_ROJO_ELIMINAR, width=160, height=44,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=22)),
            on_click=self.clic_eliminar_hora
        )

        btn_imprimir = ft.ElevatedButton(
            content=ft.Text("Imprimir PDF", font_family=FAMILIA_FUENTE, size=14, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
            bgcolor=COLOR_AMARILLO_TARJETA, width=160, height=44,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=22)),
            on_click=self.clic_imprimir_pdf
        )

        btn_justificacion = ft.Container(
            width=325, height=60, bgcolor=COLOR_BLANCO, border_radius=22,
            border=ft.border.all(2.5, COLOR_AMARILLO_TARJETA), padding=ft.padding.symmetric(horizontal=18),
            ink=True,
            on_click=lambda e: self.ir_a_justificacion(self.datos_estudiante) if self.ir_a_justificacion else None,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(name=ft.icons.FIND_IN_PAGE_OUTLINED, color=COLOR_MORADO_FONDO, size=32),
                    ft.Text("Justificación", font_family=FAMILIA_FUENTE, size=20, weight=ft.FontWeight.BOLD, color=COLOR_AMARILLO_TARJETA)
                ]
            )
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            controls=[
                ft.GestureDetector(on_tap=lambda e: self.al_regresar(), content=widget_escudo),
                lbl_titulo,
                contenedor_tabla,
                ft.Container(
                    width=335,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=4,
                        controls=[
                            ft.Text("Horas restantes:", font_family=FAMILIA_FUENTE, size=17, weight=ft.FontWeight.BOLD, color=COLOR_AMARILLO_TARJETA),
                            caja_horas_restantes
                        ]
                    )
                ),
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=12, controls=[btn_eliminar, btn_imprimir]),
                ft.Container(padding=ft.padding.only(bottom=6), content=btn_justificacion)
            ]
        )

    def _renderizar_filas(self):
        self.columna_filas.controls.clear()

        for idx, reg in enumerate(self.registros_horas):
            esta_validado = bool(reg.get("validado", False))
            esta_sel = (idx == self.indice_seleccionado)
            color_texto = COLOR_MORADO_FONDO if esta_validado else COLOR_ROJO_ELIMINAR
            color_fondo = "#EAE0F6" if esta_sel else COLOR_BLANCO

            fila = ft.GestureDetector(
                on_tap=lambda e, i=idx: self._seleccionar_fila(i),
                content=ft.Row(
                    spacing=3,
                    controls=[
                        ft.Container(
                            expand=5, height=54, bgcolor=color_fondo,
                            border=ft.border.all(2, COLOR_AMARILLO_TARJETA), alignment=ft.alignment.center,
                            content=ft.Text(str(reg.get("fecha", "")), font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=color_texto)
                        ),
                        ft.Container(
                            expand=5, height=54, bgcolor=color_fondo,
                            border=ft.border.all(2, COLOR_AMARILLO_TARJETA), alignment=ft.alignment.center,
                            content=ft.Text(str(reg.get("horas", "")), font_family=FAMILIA_FUENTE, size=16, weight=ft.FontWeight.BOLD, color=color_texto)
                        )
                    ]
                )
            )
            self.columna_filas.controls.append(fila)

        self.page.update()

    def _seleccionar_fila(self, idx: int):
        self.indice_seleccionado = idx
        self._renderizar_filas()

    def mostrar_alerta(self, titulo: str, mensaje: str):
        def cerrar(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True, bgcolor=COLOR_BLANCO, shape=ft.RoundedRectangleBorder(radius=20),
            title=ft.Text(titulo, font_family=FAMILIA_FUENTE, size=17, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO, text_align=ft.TextAlign.CENTER),
            content=ft.Text(mensaje, font_family=FAMILIA_FUENTE, size=14, color="#000000", text_align=ft.TextAlign.CENTER),
            actions=[ft.ElevatedButton(text="Aceptar", bgcolor=COLOR_MORADO_FONDO, color=COLOR_BLANCO, on_click=cerrar)],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def clic_eliminar_hora(self, e):
        if self.indice_seleccionado is None:
            self.mostrar_alerta("Selecciona una fila", "Toca primero la fila roja (no validada) que deseas borrar.")
            return

        reg = self.registros_horas[self.indice_seleccionado]
        exito, msg = self.firebase.eliminar_hora_no_validada_estudiante(self.datos_estudiante, reg)
        if exito:
            self.registros_horas = self.firebase.obtener_horas_hechas_alumno(self.datos_estudiante)
            self.indice_seleccionado = None
            self._renderizar_filas()
        self.mostrar_alerta("Eliminado" if exito else "No permitido", msg)

    def clic_imprimir_pdf(self, e):
        exito, msg = generar_pdf_horas_alumno_movil(self.datos_estudiante, self.registros_horas)
        self.mostrar_alerta("Reporte PDF" if exito else "Error", msg)