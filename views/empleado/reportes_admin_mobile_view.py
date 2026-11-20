import os
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient
from utils.pdf_mobile_generator import generar_pdf_inventario_movil


class ReportesAdminMobileView(ft.Container):
    """ Pantalla exclusiva de Administrador: Selector de Empleado + Tipo de Inventario para imprimir PDF """
    def __init__(self, page: ft.Page, al_regresar):
        super().__init__()
        self.page = page
        self.al_regresar = al_regresar
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_BLANCO
        self.padding = 0

        self.empleados = self.firebase.obtener_lista_empleados_movil()
        self.mapa_ids = {e["nombre_completo"]: str(e.get("numero_empleado", "")) for e in self.empleados}

        self.content = self._construir_interfaz()

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
            height=95,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border_radius=ft.border_radius.only(bottom_left=16, bottom_right=16),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.GestureDetector(on_tap=lambda e: self.al_regresar(), content=widget_escudo),
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

        # Selector 1: Empleados ("Todos" + cada empleado registrado)
        opciones_emp = [ft.dropdown.Option("Todos")] + [
            ft.dropdown.Option(e["nombre_completo"]) for e in self.empleados
        ]
        self.dd_empleado = ft.Dropdown(
            width=330,
            value="Todos",
            bgcolor=COLOR_BLANCO,
            color=COLOR_MORADO_FONDO,
            border_color=COLOR_AMARILLO_TARJETA,
            border_width=2.5,
            border_radius=16,
            text_style=ft.TextStyle(font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
            options=opciones_emp
        )

        # Selector 2: Tipo de inventario
        self.dd_tipo = ft.Dropdown(
            width=330,
            value="Inventariables",
            bgcolor=COLOR_BLANCO,
            color=COLOR_MORADO_FONDO,
            border_color=COLOR_AMARILLO_TARJETA,
            border_width=2.5,
            border_radius=16,
            text_style=ft.TextStyle(font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
            options=[
                ft.dropdown.Option("Inventariables"),
                ft.dropdown.Option("No Inventariables")
            ]
        )

        self.btn_generar = ft.ElevatedButton(
            content=ft.Text("Imprimir Reporte PDF", font_family=FAMILIA_FUENTE, size=19, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
            bgcolor=COLOR_MORADO_FONDO,
            width=270,
            height=54,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=26), elevation=3),
            on_click=self.clic_generar_pdf
        )

        cuerpo = ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=26, vertical=28),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Text("Reportes de Inventario", font_family=FAMILIA_FUENTE, size=23, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=8,
                        controls=[
                            ft.Text("Seleccionar empleado:", font_family=FAMILIA_FUENTE, size=17, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self.dd_empleado,
                            ft.Container(height=14),
                            ft.Text("Tipo de inventario:", font_family=FAMILIA_FUENTE, size=17, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self.dd_tipo,
                        ]
                    ),
                    ft.Container(height=28),
                    self.btn_generar
                ]
            )
        )

        return ft.Column(spacing=0, expand=True, controls=[header_morado, cuerpo])

    def mostrar_alerta(self, titulo: str, mensaje: str):
        def cerrar(e):
            dlg.open = False
            self.page.update()

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

    def clic_generar_pdf(self, e):
        emp_sel = self.dd_empleado.value or "Todos"
        tipo_sel = self.dd_tipo.value or "Inventariables"
        id_emp = self.mapa_ids.get(emp_sel, "")

        self.btn_generar.disabled = True
        self.page.update()

        items = self.firebase.obtener_inventario_por_empleado(tipo_sel, nombre_empleado=emp_sel, id_empleado=id_emp)
        exito, msg = generar_pdf_inventario_movil(tipo_sel, items, nombre_empleado_filtro=emp_sel)

        self.btn_generar.disabled = False
        self.page.update()

        self.mostrar_alerta("Reporte PDF" if exito else "Error", msg)