import os
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    FAMILIA_FUENTE
)


class MenuEstudianteView(ft.Container):
    """ Menú Principal del Estudiante (Rol == 'estudiante') """
    def __init__(
        self, page: ft.Page, datos_estudiante: dict,
        al_cerrar_sesion=None,
        ir_a_horas=None,
        ir_a_agregar_horas=None
    ):
        super().__init__()
        self.page = page
        self.datos_estudiante = datos_estudiante or {}
        self.al_cerrar_sesion = al_cerrar_sesion
        self.ir_a_horas = ir_a_horas
        self.ir_a_agregar_horas = ir_a_agregar_horas

        self.expand = True
        self.bgcolor = COLOR_BLANCO
        self.padding = 0

        self.content = self._construir_interfaz()

    def _obtener_icono(self, archivo_icono: str, icono_respaldo: str, tamano=50):
        ruta_relativa = f"icons/{archivo_icono}"
        if os.path.exists(os.path.join("assets", ruta_relativa)):
            return ft.Image(
                src=ruta_relativa,
                width=tamano,
                height=tamano,
                fit=ft.ImageFit.CONTAIN
            )
        return ft.Icon(name=icono_respaldo, color=COLOR_MORADO_FONDO, size=tamano - 6)

    def _crear_boton_estudiante(self, texto: str, widget_icono, tamano_fuente: int, comando):
        """ Crea el botón amarillo (#FCCb2d) con borde y texto morado (#553a8f) """
        return ft.Container(
            width=305,
            height=72,
            bgcolor=COLOR_AMARILLO_TARJETA,
            border_radius=22,
            border=ft.border.all(2.5, COLOR_MORADO_FONDO),
            padding=ft.padding.symmetric(horizontal=16, vertical=6),
            ink=True,
            on_click=lambda e: comando() if comando else None,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=5,
                color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                offset=ft.Offset(0, 3)
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    widget_icono,
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            texto,
                            font_family=FAMILIA_FUENTE,
                            size=tamano_fuente,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_MORADO_FONDO,
                            text_align=ft.TextAlign.CENTER
                        )
                    )
                ]
            )
        )

    def _construir_interfaz(self):
        # ================= 1. BARRA SUPERIOR MORADA (HEADER) =================
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))

        widget_escudo = (
            ft.Image(src=ruta_escudo, width=62, height=72, fit=ft.ImageFit.CONTAIN)
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=52)
        )

        header_morado = ft.Container(
            bgcolor=COLOR_MORADO_FONDO,
            height=105,
            padding=ft.padding.symmetric(horizontal=18, vertical=12),
            border_radius=ft.border_radius.only(bottom_left=18, bottom_right=18),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                controls=[
                    # Tocar el escudo regresa al Login (Cerrar sesión)
                    ft.GestureDetector(
                        on_tap=lambda e: self.al_cerrar_sesion() if self.al_cerrar_sesion else None,
                        content=widget_escudo
                    ),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=0,
                        controls=[
                            ft.Text(
                                "Centro de",
                                font_family=FAMILIA_FUENTE,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BLANCO
                            ),
                            ft.Text(
                                "Alfabetización Digital",
                                font_family=FAMILIA_FUENTE,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BLANCO
                            )
                        ]
                    )
                ]
            )
        )

        # ================= 2. SALUDO: "Bienvenido / Nombre del Alumno" =================
        nombres = self.datos_estudiante.get("nombres", "").strip()
        apellidos = self.datos_estudiante.get("apellidos", "").strip()
        nombre_completo = f"{nombres} {apellidos}".strip() or "Nombre del Alumno"

        seccion_saludo = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
            controls=[
                ft.Text(
                    "Bienvenido",
                    font_family=FAMILIA_FUENTE,
                    size=21,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_MORADO_FONDO,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    nombre_completo,
                    font_family=FAMILIA_FUENTE,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_MORADO_FONDO,
                    text_align=ft.TextAlign.CENTER
                )
            ]
        )

        # ================= 3. LOS 2 BOTONES: "Horas" y "Agregar horas" =================
        ico_horas = self._obtener_icono("servicio_social.png", ft.icons.GROUPS_OUTLINED, tamano=52)
        btn_horas = self._crear_boton_estudiante(
            texto="Horas",
            widget_icono=ico_horas,
            tamano_fuente=24,
            comando=self.ir_a_horas
        )

        ico_agregar = self._obtener_icono("agregar_horas.png", ft.icons.ACCESS_TIME_FILLED, tamano=50)
        btn_agregar_horas = self._crear_boton_estudiante(
            texto="Agregar horas",
            widget_icono=ico_agregar,
            tamano_fuente=21,
            comando=self.ir_a_agregar_horas
        )

        # ================= 4. MASCOTA INFERIOR (CADcito) =================
        ruta_mascota = "logos/mascota_cad.png"
        existe_mascota = os.path.exists(os.path.join("assets", ruta_mascota))

        widget_mascota = (
            ft.Image(src=ruta_mascota, width=215, height=235, fit=ft.ImageFit.CONTAIN)
            if existe_mascota
            else ft.Container(
                height=190,
                alignment=ft.alignment.center,
                content=ft.Icon(name=ft.icons.SUPPORT_AGENT, color=COLOR_MORADO_FONDO, size=130)
            )
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            controls=[
                header_morado,
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=24,
                    controls=[
                        seccion_saludo,
                        ft.Container(height=6),
                        btn_horas,
                        btn_agregar_horas
                    ]
                ),
                ft.Container(
                    padding=ft.padding.only(bottom=12),
                    content=widget_mascota
                )
            ]
        )