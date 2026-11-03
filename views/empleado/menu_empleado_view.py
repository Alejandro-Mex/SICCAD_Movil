import os
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    FAMILIA_FUENTE
)


class MenuEmpleadoView(ft.Container):
    """ Interfaz 2 Móvil: Menú Principal del Empleado (Filtra botones según permisos) """
    def __init__(
        self, page: ft.Page, datos_empleado: dict,
        al_cerrar_sesion=None,
        ir_a_no_inventariables=None,
        ir_a_inventariables=None,
        ir_a_consumibles=None,
        ir_a_alumnos=None
    ):
        super().__init__()
        self.page = page
        self.datos_empleado = datos_empleado or {}
        self.al_cerrar_sesion = al_cerrar_sesion
        self.ir_a_no_inventariables = ir_a_no_inventariables
        self.ir_a_inventariables = ir_a_inventariables
        self.ir_a_consumibles = ir_a_consumibles
        self.ir_a_alumnos = ir_a_alumnos

        self.expand = True
        self.bgcolor = COLOR_BLANCO
        self.padding = 0

        self.content = self._construir_interfaz()

    def _obtener_icono(self, archivo_icono: str, icono_respaldo: str, color_respaldo: str, tamano=48):
        """ Carga el PNG desde assets/icons/ o muestra un ícono vectorial limpio si aún no está el archivo """
        ruta_relativa = f"icons/{archivo_icono}"
        if os.path.exists(os.path.join("assets", ruta_relativa)):
            return ft.Image(
                src=ruta_relativa,
                width=tamano,
                height=tamano,
                fit=ft.ImageFit.CONTAIN
            )
        return ft.Icon(name=icono_respaldo, color=color_respaldo, size=tamano - 8)

    def _crear_boton_menu(
        self, texto: str, widget_icono, bg_color: str,
        borde_color: str, texto_color: str, tamano_fuente: int, comando
    ):
        """ Crea cada botón redondeado exactamente como en el diseño móvil """
        return ft.Container(
            width=300,
            height=68,
            bgcolor=bg_color,
            border_radius=22,
            border=ft.border.all(2.5, borde_color),
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
                spacing=12,
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
                            color=texto_color,
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
                    # Tocar el escudo permite cerrar sesión rápidamente si se desea cambiar de usuario
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

        # ================= 2. SALUDO: "Bienvenido / Nombre del Empleado" =================
        nombres = self.datos_empleado.get("nombres", "").strip()
        apellidos = self.datos_empleado.get("apellidos", "").strip()
        nombre_completo = f"{nombres} {apellidos}".strip() or "Nombre del Empleado"

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

        # ================= 3. BOTONES DINÁMICOS SEGÚN PERMISOS =================
        es_admin = (
            self.datos_empleado.get("rol") == "admin"
            or str(self.datos_empleado.get("numero_empleado", "")).lower() == "admin"
        )

        botones_visibles = []

        # 1. No Inventariables (Morado con borde y letras amarillas)
        if es_admin or self.datos_empleado.get("per_no_inventariables", False):
            ico_no_inv = self._obtener_icono("no_inventariables.png", ft.icons.INVENTORY_2_OUTLINED, COLOR_AMARILLO_TARJETA)
            botones_visibles.append(
                self._crear_boton_menu(
                    texto="No Inventariables",
                    widget_icono=ico_no_inv,
                    bg_color=COLOR_MORADO_FONDO,
                    borde_color=COLOR_AMARILLO_TARJETA,
                    texto_color=COLOR_AMARILLO_TARJETA,
                    tamano_fuente=18,
                    comando=self.ir_a_no_inventariables
                )
            )

        # 2. Inventariables (Morado con borde y letras amarillas)
        if es_admin or self.datos_empleado.get("per_inventariables", False):
            ico_inv = self._obtener_icono("inventariados.png", ft.icons.FACT_CHECK_OUTLINED, COLOR_AMARILLO_TARJETA)
            botones_visibles.append(
                self._crear_boton_menu(
                    texto="Inventariables",
                    widget_icono=ico_inv,
                    bg_color=COLOR_MORADO_FONDO,
                    borde_color=COLOR_AMARILLO_TARJETA,
                    texto_color=COLOR_AMARILLO_TARJETA,
                    tamano_fuente=21,
                    comando=self.ir_a_inventariables
                )
            )

        # 3. Consumibles (Morado con borde y letras amarillas)
        if es_admin or self.datos_empleado.get("per_bienes_consumo", False):
            ico_con = self._obtener_icono("consumibles.png", ft.icons.SHOPPING_BASKET_OUTLINED, COLOR_AMARILLO_TARJETA)
            botones_visibles.append(
                self._crear_boton_menu(
                    texto="Consumibles",
                    widget_icono=ico_con,
                    bg_color=COLOR_MORADO_FONDO,
                    borde_color=COLOR_AMARILLO_TARJETA,
                    texto_color=COLOR_AMARILLO_TARJETA,
                    tamano_fuente=22,
                    comando=self.ir_a_consumibles
                )
            )

        # 4. Alumnos (Amarillo con borde y letras moradas, tal cual tu diseño)
        if es_admin or self.datos_empleado.get("per_servicio_social", False):
            ico_alu = self._obtener_icono("servicio_social.png", ft.icons. GROUPS_OUTLINED, COLOR_MORADO_FONDO)
            botones_visibles.append(
                self._crear_boton_menu(
                    texto="Alumnos",
                    widget_icono=ico_alu,
                    bg_color=COLOR_AMARILLO_TARJETA,
                    borde_color=COLOR_MORADO_FONDO,
                    texto_color=COLOR_MORADO_FONDO,
                    tamano_fuente=23,
                    comando=self.ir_a_alumnos
                )
            )

        # ================= 4. MASCOTA INFERIOR (CADcito) =================
        ruta_mascota = "logos/mascota_cad.png"
        existe_mascota = os.path.exists(os.path.join("assets", ruta_mascota))

        widget_mascota = (
            ft.Image(src=ruta_mascota, width=175, height=195, fit=ft.ImageFit.CONTAIN)
            if existe_mascota
            else ft.Container(
                height=160,
                alignment=ft.alignment.center,
                content=ft.Icon(name=ft.icons.SUPPORT_AGENT, color=COLOR_MORADO_FONDO, size=110)
            )
        )

        # ESTRUCTURA GENERAL DE LA PANTALLA
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            controls=[
                header_morado,
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                    controls=[
                        seccion_saludo,
                        ft.Container(height=4),
                        *botones_visibles
                    ]
                ),
                ft.Container(
                    padding=ft.padding.only(bottom=10),
                    content=widget_mascota
                )
            ]
        )