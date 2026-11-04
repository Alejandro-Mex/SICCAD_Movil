import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, FAMILIA_FUENTE, ANCHO_MOVIL, ALTO_MOVIL
)
from database.firebase_mobile_client import FirebaseMobileClient
from views.login_mobile_view import LoginMobileView
from views.empleado.menu_empleado_view import MenuEmpleadoView
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
        self.funcion_atras_actual = None

        self._configurar_pagina()
        self.mostrar_login()

    def _configurar_pagina(self):
        self.page.title = "SICAD Móvil"
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

        # Interceptar el botón físico / gesto "Atrás" de Android
        self.page.on_view_pop = self._al_presionar_atras_telefono

    def _al_presionar_atras_telefono(self, e):
        """ Se ejecuta automáticamente cuando el usuario presiona 'Atrás' en su celular Android """
        if self.funcion_atras_actual is not None:
            self.funcion_atras_actual()

    def cambiar_pantalla(self, widget_vista, accion_boton_atras=None):
        """
        Cambia la pantalla actual y configura a dónde debe regresar el botón 'Atrás' del celular.
        """
        self.funcion_atras_actual = accion_boton_atras
        self.page.views.clear()

        # En Android, si hay una pantalla anterior disponible, ponemos una vista base detrás
        # para que el sistema operativo Android active el gesto de retroceso sin cerrar la app
        if accion_boton_atras is not None:
            self.page.views.append(
                ft.View(route="/base", bgcolor=COLOR_MORADO_FONDO, padding=0, controls=[])
            )

        self.page.views.append(
            ft.View(
                route="/actual",
                bgcolor=COLOR_MORADO_FONDO,
                padding=0,
                controls=[widget_vista]
            )
        )
        self.page.update()

    # ================= NAVEGACIÓN GENERAL =================
    def mostrar_login(self):
        self.firebase.usuario_actual = None
        self.cambiar_pantalla(
            LoginMobileView(
                page=self.page,
                al_iniciar_sesion_exitoso=self.ir_a_menu_principal
            ),
            accion_boton_atras=None  # En Login ya estamos al inicio
        )

    def ir_a_menu_principal(self, datos_usuario=None):
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
                ),
                accion_boton_atras=self.mostrar_login
            )

    # ================= NAVEGACIÓN DE EMPLEADO =================
    def ir_a_lista_no_inventariables(self):
        self.cambiar_pantalla(
            ListaNoInventariablesMobileView(
                page=self.page,
                al_regresar=self.ir_a_menu_principal,
                ir_a_detalle=self.ir_a_detalle_no_inventariable
            ),
            accion_boton_atras=self.ir_a_menu_principal
        )

    def ir_a_detalle_no_inventariable(self, datos_item):
        self.cambiar_pantalla(
            DetalleNoInventariableMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=self.ir_a_lista_no_inventariables,
                ir_a_reporte=self.ir_a_reporte_no_inventariable
            ),
            accion_boton_atras=self.ir_a_lista_no_inventariables
        )

    def ir_a_reporte_no_inventariable(self, datos_item):
        self.cambiar_pantalla(
            ReporteNoInventariableMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=lambda: self.ir_a_detalle_no_inventariable(datos_item)
            ),
            accion_boton_atras=lambda: self.ir_a_detalle_no_inventariable(datos_item)
        )

    def ir_a_lista_inventariables(self):
        self.cambiar_pantalla(
            ListaInventariablesMobileView(
                page=self.page,
                al_regresar=self.ir_a_menu_principal,
                ir_a_detalle=self.ir_a_detalle_inventariable
            ),
            accion_boton_atras=self.ir_a_menu_principal
        )

    def ir_a_detalle_inventariable(self, datos_item):
        self.cambiar_pantalla(
            DetalleInventariableMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=self.ir_a_lista_inventariables,
                ir_a_reporte=self.ir_a_reporte_inventariable
            ),
            accion_boton_atras=self.ir_a_lista_inventariables
        )

    def ir_a_reporte_inventariable(self, datos_item):
        self.cambiar_pantalla(
            ReporteInventariableMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=lambda: self.ir_a_detalle_inventariable(datos_item)
            ),
            accion_boton_atras=lambda: self.ir_a_detalle_inventariable(datos_item)
        )

    def ir_a_lista_consumibles(self):
        self.cambiar_pantalla(
            ListaConsumiblesMobileView(
                page=self.page,
                al_regresar=self.ir_a_menu_principal,
                ir_a_detalle=self.ir_a_detalle_consumible
            ),
            accion_boton_atras=self.ir_a_menu_principal
        )

    def ir_a_detalle_consumible(self, datos_item):
        self.cambiar_pantalla(
            DetalleConsumibleMobileView(
                page=self.page,
                datos_item=datos_item,
                al_regresar=self.ir_a_lista_consumibles
            ),
            accion_boton_atras=self.ir_a_lista_consumibles
        )

    def ir_a_lista_alumnos(self):
        self.cambiar_pantalla(
            ListaAlumnosMobileView(
                page=self.page,
                al_regresar=self.ir_a_menu_principal,
                ir_a_horas_hechas=self.ir_a_horas_hechas_alumno
            ),
            accion_boton_atras=self.ir_a_menu_principal
        )

    def ir_a_horas_hechas_alumno(self, datos_alumno):
        self.cambiar_pantalla(
            HorasHechasAlumnoMobileView(
                page=self.page,
                datos_alumno=datos_alumno,
                al_regresar=self.ir_a_lista_alumnos
            ),
            accion_boton_atras=self.ir_a_lista_alumnos
        )

    # ================= NAVEGACIÓN DE ESTUDIANTE =================
    def ir_a_menu_estudiante(self, datos_estudiante=None):
        if datos_estudiante is None:
            datos_estudiante = self.firebase.usuario_actual
        self.cambiar_pantalla(
            MenuEstudianteView(
                page=self.page,
                datos_estudiante=datos_estudiante,
                al_cerrar_sesion=self.mostrar_login,
                ir_a_horas=self.ir_a_consulta_horas_estudiante,
                ir_a_agregar_horas=self.ir_a_agregar_horas_estudiante
            ),
            accion_boton_atras=self.mostrar_login
        )

    def ir_a_consulta_horas_estudiante(self):
        self.cambiar_pantalla(
            ConsultaHorasEstudianteView(
                page=self.page,
                datos_estudiante=self.firebase.usuario_actual,
                al_regresar=self.ir_a_menu_estudiante,
                ir_a_justificacion=self.ir_a_justificacion_estudiante
            ),
            accion_boton_atras=self.ir_a_menu_estudiante
        )

    def ir_a_justificacion_estudiante(self, datos_estudiante=None):
        if datos_estudiante is None:
            datos_estudiante = self.firebase.usuario_actual
        self.cambiar_pantalla(
            JustificacionEstudianteView(
                page=self.page,
                datos_estudiante=datos_estudiante,
                al_regresar=self.ir_a_consulta_horas_estudiante
            ),
            accion_boton_atras=self.ir_a_consulta_horas_estudiante
        )

    def ir_a_agregar_horas_estudiante(self):
        self.cambiar_pantalla(
            AgregarHorasEstudianteView(
                page=self.page,
                datos_estudiante=self.firebase.usuario_actual,
                al_regresar=self.ir_a_menu_estudiante
            ),
            accion_boton_atras=self.ir_a_menu_estudiante
        )


def main(page: ft.Page):
    AppSICADMovil(page)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")