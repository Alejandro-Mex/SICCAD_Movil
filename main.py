import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, FAMILIA_FUENTE, ANCHO_MOVIL, ALTO_MOVIL
)
from database.firebase_mobile_client import FirebaseMobileClient
from views.login_mobile_view import LoginMobileView
from views.empleado.menu_empleado_view import MenuEmpleadoView
from views.empleado.no_inventariables_mobile_view import (
    ListaNoInventariablesMobileView,
    DetalleNoInventariableMobileView
)
from views.empleado.no_inventariables_mobile_view import (
    ListaNoInventariablesMobileView,
    DetalleNoInventariableMobileView,
    ReporteNoInventariableMobileView
)
from views.empleado.inventariables_mobile_view import (
    ListaInventariablesMobileView,
    DetalleInventariableMobileView,
    ReporteInventariableMobileView
)
from views.empleado.consumibles_mobile_view import (
    ListaConsumiblesMobileView,
    DetalleConsumibleMobileView
)
from views.empleado.alumnos_mobile_view import (
    ListaAlumnosMobileView,
    HorasHechasAlumnoMobileView
)
from views.estudiante.menu_estudiante_view import MenuEstudianteView
from views.estudiante.consulta_horas_estudiante_view import ConsultaHorasEstudianteView
from views.estudiante.justificacion_estudiante_view import JustificacionEstudianteView
from views.estudiante.agregar_horas_estudiante_view import AgregarHorasEstudianteView


class AppSICADMovil:
    def __init__(self, page: ft.Page):
        self.page = page
        self.firebase = FirebaseMobileClient()
        self._configurar_pagina()
        self.mostrar_login()

    def _configurar_pagina(self):
        self.page.title = "SICAD Móvil - Empleado"
        self.page.bgcolor = COLOR_MORADO_FONDO
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT

        self.page.fonts = {
            "Poppins": "fonts/Poppins-Regular.ttf",
            "Poppins-Bold": "fonts/Poppins-Bold.ttf"
        }
        self.page.theme = ft.Theme(font_family=FAMILIA_FUENTE)

        self.page.window.width = ANCHO_MOVIL
        self.page.window.height = ALTO_MOVIL
        self.page.window.resizable = False

    def cambiar_pantalla(self, widget_vista):
        self.page.controls.clear()
        self.page.add(widget_vista)
        self.page.update()

    def mostrar_login(self):
        """ Interfaz 1 Móvil: Inicio de sesión """
        self.firebase.usuario_actual = None
        self.cambiar_pantalla(
            LoginMobileView(
                page=self.page,
                al_iniciar_sesion_exitoso=self.ir_a_menu_principal
            )
        )

    def ir_a_menu_principal(self, datos_usuario=None):
        """ Redirige automáticamente al Menú de Empleado o al Menú de Estudiante según su rol """
        if datos_usuario is None:
            datos_usuario = self.firebase.usuario_actual or {}

        if datos_usuario.get("rol") == "estudiante":
            self.ir_a_menu_estudiante(datos_usuario)
        else:
            self.cambiar_pantalla(
                MenuEmpleadoView(
                    page=self.page,
                    datos_empleado=datos_usuario,
                    al_cerrar_sesion=self.mostrar_login,
                    ir_a_no_inventariables=self.ir_a_lista_no_inventariables,
                    ir_a_inventariables=self.ir_a_lista_inventariables,
                    ir_a_consumibles=self.ir_a_lista_consumibles,
                    ir_a_alumnos=self.ir_a_lista_alumnos
                )
            )

    def ir_a_menu_estudiante(self, datos_estudiante=None):
        """ Menú Principal del Estudiante """
        if datos_estudiante is None:
            datos_estudiante = self.firebase.usuario_actual
        self.cambiar_pantalla(
            MenuEstudianteView(
                page=self.page,
                datos_estudiante=datos_estudiante,
                al_cerrar_sesion=self.mostrar_login,
                ir_a_horas=self.ir_a_consulta_horas_estudiante,
                ir_a_agregar_horas=self.ir_a_agregar_horas_estudiante  # <-- CONECTADO AQUÍ
            )
        )

    def ir_a_agregar_horas_estudiante(self):
        """ Pantalla de Agregar Horas del Estudiante """
        self.cambiar_pantalla(
            AgregarHorasEstudianteView(
                page=self.page,
                datos_estudiante=self.firebase.usuario_actual,
                al_regresar=self.ir_a_menu_estudiante
            )
        )

    def ir_a_consulta_horas_estudiante(self):
        """ Pantalla de Consulta de Horas del Estudiante """
        self.cambiar_pantalla(
            ConsultaHorasEstudianteView(
                page=self.page,
                datos_estudiante=self.firebase.usuario_actual,
                al_regresar=self.ir_a_menu_estudiante,
                ir_a_justificacion=self.ir_a_justificacion_estudiante  # <-- CONECTADO AQUÍ
            )
        )

    def ir_a_justificacion_estudiante(self, datos_estudiante=None):
        """ Formulario de Justificación del Estudiante """
        if datos_estudiante is None:
            datos_estudiante = self.firebase.usuario_actual
        self.cambiar_pantalla(
            JustificacionEstudianteView(
                page=self.page,
                datos_estudiante=datos_estudiante,
                al_regresar=self.ir_a_consulta_horas_estudiante
            )
        )

    def ir_a_lista_alumnos(self):
        """ Pantalla 1 de Alumnos Móvil """
        self.cambiar_pantalla(
            ListaAlumnosMobileView(
                page=self.page,
                al_regresar=self.ir_a_menu_principal,
                ir_a_horas_hechas=self.ir_a_horas_hechas_alumno
            )
        )

    def ir_a_horas_hechas_alumno(self, datos_alumno):
        """ Pantalla 2 de Alumnos Móvil (Horas hechas) """
        self.cambiar_pantalla(
            HorasHechasAlumnoMobileView(
                page=self.page,
                datos_alumno=datos_alumno,
                al_regresar=self.ir_a_lista_alumnos
            )
        )

    def ir_a_lista_consumibles(self):
        """ Pantalla 1 de Consumibles Móvil """
        self.cambiar_pantalla(
            ListaConsumiblesMobileView(
                page=self.page,
                al_regresar=self.ir_a_menu_principal,
                ir_a_detalle=self.ir_a_detalle_consumible
            )
        )

    def ir_a_detalle_consumible(self, datos_item):
        """ Pantalla 2 de Consumibles Móvil (+1 Agregar / -1 Usar) """
        self.cambiar_pantalla(
            DetalleConsumibleMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=self.ir_a_lista_consumibles
            )
        )

    def ir_a_lista_inventariables(self):
        """ Pantalla 1 de Inventariables Móvil """
        self.cambiar_pantalla(
            ListaInventariablesMobileView(
                page=self.page,
                al_regresar=self.ir_a_menu_principal,
                ir_a_detalle=self.ir_a_detalle_inventariable
            )
        )

    def ir_a_detalle_inventariable(self, datos_item):
        """ Pantalla 2 de Inventariables Móvil """
        self.cambiar_pantalla(
            DetalleInventariableMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=self.ir_a_lista_inventariables,
                ir_a_reporte=self.ir_a_reporte_inventariable
            )
        )

    def ir_a_reporte_inventariable(self, datos_item):
        """ Pantalla 3 de Inventariables Móvil (Enviar Reporte) """
        self.cambiar_pantalla(
            ReporteInventariableMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=lambda: self.ir_a_detalle_inventariable(datos_item)
            )
        )

    def ir_a_lista_no_inventariables(self):
        """ Pantalla 1 de No Inventariables Móvil """
        self.cambiar_pantalla(
            ListaNoInventariablesMobileView(
                page=self.page,
                al_regresar=self.ir_a_menu_principal,
                ir_a_detalle=self.ir_a_detalle_no_inventariable
            )
        )

    def ir_a_detalle_no_inventariable(self, datos_item):
        """ Pantalla 2 de No Inventariables Móvil (Detalle + Ubicación editable + Croquis) """
        self.cambiar_pantalla(
            DetalleNoInventariableMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=self.ir_a_lista_no_inventariables,
                ir_a_reporte=self.ir_a_reporte_no_inventariable  # <-- CONECTADO AQUÍ
            )
        )

    def ir_a_reporte_no_inventariable(self, datos_item):
        """ Pantalla 3 de No Inventariables Móvil (Enviar Reporte) """
        self.cambiar_pantalla(
            ReporteNoInventariableMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=lambda: self.ir_a_detalle_no_inventariable(datos_item)
            )
        )


def main(page: ft.Page):
    AppSICADMovil(page)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")