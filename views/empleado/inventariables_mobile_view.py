import os
import time
import unicodedata
import flet as ft
from config.settings import (
    COLOR_MORADO_FONDO, COLOR_AMARILLO_TARJETA, COLOR_BLANCO,
    COLOR_ROJO_ELIMINAR, FAMILIA_FUENTE
)
from database.firebase_mobile_client import FirebaseMobileClient
from utils.pdf_mobile_generator import generar_pdf_inventario_movil

LISTA_UBICACIONES = [
    "Oficina",
    "Recepción",
    "CAD",
    "Bodega",
    "Extensión de oficina"
]


class ListaInventariablesMobileView(ft.Container):
    def __init__(self, page: ft.Page, al_regresar, ir_a_detalle):
        super().__init__()
        self.page = page
        self.al_regresar = al_regresar
        self.ir_a_detalle = ir_a_detalle
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_MORADO_FONDO
        self.padding = ft.padding.symmetric(horizontal=22, vertical=12)

        self.items = self.firebase.obtener_inventariables_empleado()
        self.indice_seleccionado = None
        self.ultimo_clic_tiempo = 0
        self.ultimo_indice_clic = -1

        self.columna_filas = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
        self.content = self._construir_interfaz()
        self._renderizar_filas()

    def _construir_interfaz(self):
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))
        widget_escudo = (
            ft.Image(src=ruta_escudo, width=80, height=90, fit=ft.ImageFit.CONTAIN)
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=70)
        )

        lbl_titulo = ft.Text(
            "Lista de inventariables",
            font_family=FAMILIA_FUENTE, size=22, weight=ft.FontWeight.BOLD,
            color=COLOR_BLANCO, text_align=ft.TextAlign.CENTER
        )

        header_tabla = ft.Row(
            spacing=3,
            controls=[
                ft.Container(
                    expand=4, height=54, bgcolor=COLOR_AMARILLO_TARJETA,
                    border=ft.border.all(2, COLOR_BLANCO), alignment=ft.alignment.center,
                    content=ft.Text("Folio", font_family=FAMILIA_FUENTE, size=19, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO)
                ),
                ft.Container(
                    expand=6, height=54, bgcolor=COLOR_AMARILLO_TARJETA,
                    border=ft.border.all(2, COLOR_BLANCO), alignment=ft.alignment.center,
                    content=ft.Text("Ubicación", font_family=FAMILIA_FUENTE, size=19, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO)
                )
            ]
        )

        contenedor_tabla = ft.Container(
            bgcolor=COLOR_AMARILLO_TARJETA, padding=3, width=340, height=325,
            content=ft.Column(spacing=3, controls=[header_tabla, ft.Container(expand=True, content=self.columna_filas)])
        )

        btn_poner_rojo = ft.ElevatedButton(
            content=ft.Text("Revisar", font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
            bgcolor=COLOR_ROJO_ELIMINAR, width=155, height=44,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=22)),
            on_click=self.clic_poner_todos_rojo
        )

        btn_regresar_amarillo = ft.ElevatedButton(
            content=ft.Text("Verificado", font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
            bgcolor=COLOR_AMARILLO_TARJETA, width=155, height=44,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=22)),
            on_click=self.clic_regresar_a_amarillo
        )

        btn_imprimir_pdf = ft.ElevatedButton(
            content=ft.Text("Imprimir reporte PDF", font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
            bgcolor=COLOR_BLANCO, width=250, height=44,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=22)),
            on_click=self.clic_imprimir_pdf
        )

        btn_volver_menu = ft.TextButton(
            content=ft.Text("« Volver al menú", font_family=FAMILIA_FUENTE, size=14, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
            on_click=lambda e: self.al_regresar()
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True,
            controls=[
                ft.GestureDetector(on_tap=lambda e: self.al_regresar(), content=widget_escudo),
                lbl_titulo,
                contenedor_tabla,
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=14, controls=[btn_poner_rojo, btn_regresar_amarillo]),
                        btn_imprimir_pdf,
                        btn_volver_menu
                    ]
                )
            ]
        )

    def _renderizar_filas(self):
        self.columna_filas.controls.clear()

        for idx, item in enumerate(self.items):
            en_rojo = item.get("en_revision_rojo", False)
            esta_seleccionado = (idx == self.indice_seleccionado)

            color_borde = COLOR_ROJO_ELIMINAR if en_rojo else COLOR_AMARILLO_TARJETA
            color_texto = COLOR_ROJO_ELIMINAR if en_rojo else COLOR_MORADO_FONDO
            color_fondo = "#EAE0F6" if esta_seleccionado else COLOR_BLANCO

            fila = ft.GestureDetector(
                on_tap=lambda e, i=idx: self._manejar_clic_fila(i),
                content=ft.Row(
                    spacing=3,
                    controls=[
                        ft.Container(
                            expand=4, height=60, bgcolor=color_fondo,
                            border=ft.border.all(2, color_borde), alignment=ft.alignment.center,
                            content=ft.Text(str(item.get("folio", "")), font_family=FAMILIA_FUENTE, size=16, weight=ft.FontWeight.W_500, color=color_texto)
                        ),
                        ft.Container(
                            expand=6, height=60, bgcolor=color_fondo,
                            border=ft.border.all(2, color_borde), alignment=ft.alignment.center,
                            content=ft.Text(str(item.get("ubicacion", "")), font_family=FAMILIA_FUENTE, size=16, weight=ft.FontWeight.W_500, color=color_texto)
                        )
                    ]
                )
            )
            self.columna_filas.controls.append(fila)

        self.page.update()

    def _manejar_clic_fila(self, idx: int):
        ahora = time.time()
        if idx == self.ultimo_indice_clic and (ahora - self.ultimo_clic_tiempo) < 0.45:
            self.ir_a_detalle(self.items[idx])
            return

        self.ultimo_indice_clic = idx
        self.ultimo_clic_tiempo = ahora
        self.indice_seleccionado = idx
        self._renderizar_filas()

    def clic_poner_todos_rojo(self, e):
        for item in self.items:
            folio_str = str(item.get("folio", "")).strip()
            item["en_revision_rojo"] = True
            self.firebase.folios_en_rojo.add(folio_str)
        self._renderizar_filas()

    def clic_regresar_a_amarillo(self, e):
        if self.indice_seleccionado is None:
            return
        item_sel = self.items[self.indice_seleccionado]
        folio_str = str(item_sel.get("folio", "")).strip()
        item_sel["en_revision_rojo"] = False
        self.firebase.folios_en_rojo.discard(folio_str)
        self._renderizar_filas()

    def clic_imprimir_pdf(self, e):
        u = self.firebase.usuario_actual or {}
        nom_emp = f"{u.get('nombres', '')} {u.get('apellidos', '')}".strip() or "Empleado"
        exito, msg = generar_pdf_inventario_movil("Inventariables", self.items, nombre_empleado_filtro=nom_emp)

        def cerrar(ev):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True, bgcolor=COLOR_BLANCO, shape=ft.RoundedRectangleBorder(radius=20),
            title=ft.Text("Reporte PDF" if exito else "Error", font_family=FAMILIA_FUENTE, size=17, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO, text_align=ft.TextAlign.CENTER),
            content=ft.Text(msg, font_family=FAMILIA_FUENTE, size=14, color="#000000", text_align=ft.TextAlign.CENTER),
            actions=[ft.ElevatedButton(text="Aceptar", bgcolor=COLOR_MORADO_FONDO, color=COLOR_BLANCO, on_click=cerrar)],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()


class DetalleInventariableMobileView(ft.Container):
    def __init__(self, page: ft.Page, datos_item: dict, al_regresar, ir_a_reporte=None):
        super().__init__()
        self.page = page
        self.datos_item = datos_item or {}
        self.al_regresar = al_regresar
        self.ir_a_reporte = ir_a_reporte
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_BLANCO
        self.padding = 0

        self.contenedor_mapa = ft.Container()
        self.content = self._construir_interfaz()

    def _crear_caja_lectura(self, texto: str, alto=42):
        return ft.Container(
            width=330, height=alto, bgcolor=COLOR_BLANCO, border_radius=14,
            border=ft.border.all(2.2, COLOR_MORADO_FONDO),
            padding=ft.padding.symmetric(horizontal=14, vertical=6),
            alignment=ft.alignment.center_left if alto < 60 else ft.alignment.top_left,
            content=ft.Text(str(texto), font_family=FAMILIA_FUENTE, size=14, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO)
        )

    def _dibujar_croquis_cad_movil(self, ubicacion_actual=""):
        ubi = "".join(c for c in unicodedata.normalize("NFD", str(ubicacion_actual).lower().strip()) if unicodedata.category(c) != "Mn")

        def borde_zona(zona):
            activo = (
                (zona == "extension" and ("extens" in ubi or "extenc" in ubi))
                or (zona == "oficina" and ubi == "oficina")
                or (zona == "recepcion" and "recep" in ubi)
                or (zona == "cad" and ubi == "cad")
                or (zona == "bodega" and "bodega" in ubi)
            )
            return ft.border.all(3.5, COLOR_AMARILLO_TARJETA) if activo else ft.border.all(0.5, "#2B4C6F")

        return ft.Container(
            width=220, height=210, bgcolor=COLOR_BLANCO,
            content=ft.Stack(controls=[
                ft.Container(left=0, top=0, width=88, height=44, bgcolor="#7A8B9E", border=borde_zona("extension"), alignment=ft.alignment.center,
                             content=ft.Text("Extensión de la\noficina", size=7.5, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO, text_align=ft.TextAlign.CENTER)),
                ft.Container(left=88, top=0, width=132, height=44, bgcolor="#803505", border=borde_zona("oficina"), alignment=ft.alignment.center,
                             content=ft.Text("Oficina", size=7.5, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO)),
                ft.Container(left=0, top=44, width=88, height=44, bgcolor="#537E35", border=borde_zona("recepcion"), alignment=ft.alignment.center,
                             content=ft.Text("Recepción", size=7.5, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO)),
                ft.Container(left=88, top=44, width=132, height=130, bgcolor="#6E2C91", border=borde_zona("cad"), alignment=ft.alignment.center,
                             content=ft.Text("CAD", size=7.5, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO)),
                ft.Container(left=0, top=116, width=88, height=58, bgcolor="#4171B8", border=ft.border.all(0.5, "#2B4C6F"), alignment=ft.alignment.center,
                             content=ft.Text("Baño", size=7.5, color=COLOR_BLANCO)),
                ft.Container(left=0, top=174, width=172, height=36, bgcolor="#4171B8", border=ft.border.all(0.5, "#2B4C6F"), alignment=ft.alignment.center,
                             content=ft.Text("Baño", size=7.5, color=COLOR_BLANCO)),
                ft.Container(left=172, top=174, width=48, height=36, bgcolor="#B38909", border=borde_zona("bodega"), alignment=ft.alignment.center,
                             content=ft.Text("Bodega", size=7.5, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO)),
            ])
        )

    def _al_cambiar_ubicacion(self, e):
        self.contenedor_mapa.content = self._dibujar_croquis_cad_movil(self.dropdown_ubicacion.value)
        self.page.update()

    def _construir_interfaz(self):
        ruta_escudo = "logos/escudo_merida.png"
        existe_escudo = os.path.exists(os.path.join("assets", ruta_escudo))
        widget_escudo = (
            ft.Image(src=ruta_escudo, width=52, height=62, fit=ft.ImageFit.CONTAIN)
            if existe_escudo
            else ft.Icon(name=ft.icons.ACCOUNT_BALANCE, color=COLOR_BLANCO, size=46)
        )

        header_morado = ft.Container(
            bgcolor=COLOR_MORADO_FONDO, height=88,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border_radius=ft.border_radius.only(bottom_left=16, bottom_right=16),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12,
                controls=[
                    ft.GestureDetector(on_tap=lambda e: self.al_regresar(), content=widget_escudo),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER, spacing=0,
                        controls=[
                            ft.Text("Centro de", font_family=FAMILIA_FUENTE, size=17, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
                            ft.Text("Alfabetización Digital", font_family=FAMILIA_FUENTE, size=17, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
                        ]
                    )
                ]
            )
        )

        ubicacion_inicial = self.datos_item.get("ubicacion", "CAD")
        opciones_ubi = list(LISTA_UBICACIONES)
        if ubicacion_inicial and ubicacion_inicial not in opciones_ubi:
            opciones_ubi.append(ubicacion_inicial)

        self.dropdown_ubicacion = ft.Dropdown(
            width=330, height=46, value=ubicacion_inicial,
            bgcolor=COLOR_BLANCO, color=COLOR_MORADO_FONDO,
            border_color=COLOR_MORADO_FONDO, border_width=2.2, border_radius=14,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=6),
            text_style=ft.TextStyle(font_family=FAMILIA_FUENTE, size=14, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
            options=[ft.dropdown.Option(u) for u in opciones_ubi],
            on_change=self._al_cambiar_ubicacion
        )

        self.contenedor_mapa.content = self._dibujar_croquis_cad_movil(ubicacion_inicial)

        btn_reporte = ft.ElevatedButton(
            content=ft.Text("Reporte", font_family=FAMILIA_FUENTE, size=20, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
            bgcolor=COLOR_AMARILLO_TARJETA, width=235, height=44,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24), elevation=3),
            on_click=lambda e: self.ir_a_reporte(self.datos_item) if self.ir_a_reporte else None
        )

        btn_guardar = ft.ElevatedButton(
            content=ft.Text("Guardar", font_family=FAMILIA_FUENTE, size=20, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
            bgcolor=COLOR_MORADO_FONDO, width=235, height=44,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24), elevation=3),
            on_click=self.clic_guardar
        )

        cuerpo_scroll = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO, expand=True, spacing=4,
            controls=[
                ft.Container(
                    width=330, padding=ft.padding.only(top=6),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START, spacing=3,
                        controls=[
                            ft.Text("Folio:", font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self._crear_caja_lectura(self.datos_item.get("folio", "")),
                            ft.Text("Marca:", font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self._crear_caja_lectura(self.datos_item.get("marca", "")),
                            ft.Text("Modelo:", font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self._crear_caja_lectura(self.datos_item.get("modelo", "")),
                            ft.Text("Número de serie:", font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self._crear_caja_lectura(self.datos_item.get("numero_serie", "")),
                            ft.Text("Descripción:", font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self._crear_caja_lectura(self.datos_item.get("descripcion", ""), alto=72),
                            ft.Text("Ubicación:", font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self.dropdown_ubicacion,
                        ]
                    )
                ),
                ft.Container(height=6),
                self.contenedor_mapa,
                ft.Container(height=6),
                btn_reporte,
                ft.Container(height=4),
                btn_guardar,
                ft.Container(height=14),
            ]
        )

        return ft.Column(spacing=0, expand=True, controls=[header_morado, cuerpo_scroll])

    def clic_guardar(self, e):
        nueva_ubicacion = self.dropdown_ubicacion.value
        folio = self.datos_item.get("folio", "")
        self.datos_item["ubicacion"] = nueva_ubicacion
        self.firebase.actualizar_ubicacion_inventariable(folio, nueva_ubicacion)
        self.al_regresar()


class ReporteInventariableMobileView(ft.Container):
    def __init__(self, page: ft.Page, datos_item: dict, al_regresar):
        super().__init__()
        self.page = page
        self.datos_item = datos_item or {}
        self.al_regresar = al_regresar
        self.firebase = FirebaseMobileClient()

        self.expand = True
        self.bgcolor = COLOR_BLANCO
        self.padding = 0

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
            bgcolor=COLOR_MORADO_FONDO, height=95,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border_radius=ft.border_radius.only(bottom_left=16, bottom_right=16),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12,
                controls=[
                    ft.GestureDetector(on_tap=lambda e: self.al_regresar(), content=widget_escudo),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER, spacing=0,
                        controls=[
                            ft.Text("Centro de", font_family=FAMILIA_FUENTE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
                            ft.Text("Alfabetización Digital", font_family=FAMILIA_FUENTE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
                        ]
                    )
                ]
            )
        )

        caja_folio = ft.Container(
            width=330, height=52, bgcolor=COLOR_BLANCO, border_radius=16,
            border=ft.border.all(2.5, COLOR_MORADO_FONDO), padding=ft.padding.symmetric(horizontal=18),
            alignment=ft.alignment.center_left,
            content=ft.Text(str(self.datos_item.get("folio", "")), font_family=FAMILIA_FUENTE, size=17, weight=ft.FontWeight.W_500, color=COLOR_MORADO_FONDO)
        )

        self.txt_comentario = ft.TextField(
            width=330, min_lines=10, max_lines=12, multiline=True,
            bgcolor=COLOR_BLANCO, color=COLOR_MORADO_FONDO,
            border_color=COLOR_MORADO_FONDO, border_width=2.5, border_radius=18,
            content_padding=ft.padding.all(16),
            text_style=ft.TextStyle(font_family=FAMILIA_FUENTE, size=15, weight=ft.FontWeight.W_500, color=COLOR_MORADO_FONDO)
        )

        self.btn_enviar = ft.ElevatedButton(
            content=ft.Text("Enviar", font_family=FAMILIA_FUENTE, size=24, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
            bgcolor=COLOR_AMARILLO_TARJETA, width=245, height=54,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=28), elevation=3),
            on_click=self.clic_enviar
        )

        cuerpo = ft.Container(
            expand=True, padding=ft.padding.symmetric(horizontal=26, vertical=20),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=True,
                controls=[
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START, spacing=8,
                        controls=[
                            ft.Text("Folio:", font_family=FAMILIA_FUENTE, size=20, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            caja_folio,
                            ft.Container(height=12),
                            ft.Text("Comentario:", font_family=FAMILIA_FUENTE, size=20, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO),
                            self.txt_comentario,
                        ]
                    ),
                    ft.Container(padding=ft.padding.only(bottom=15), content=self.btn_enviar)
                ]
            )
        )

        return ft.Column(spacing=0, expand=True, controls=[header_morado, cuerpo])

    def mostrar_alerta(self, titulo: str, mensaje: str, regresar_al_cerrar=False):
        def cerrar(e):
            dlg.open = False
            self.page.update()
            if regresar_al_cerrar:
                self.al_regresar()

        dlg = ft.AlertDialog(
            modal=True, bgcolor=COLOR_BLANCO, shape=ft.RoundedRectangleBorder(radius=20),
            title=ft.Text(titulo, font_family=FAMILIA_FUENTE, size=18, weight=ft.FontWeight.BOLD, color=COLOR_MORADO_FONDO, text_align=ft.TextAlign.CENTER),
            content=ft.Text(mensaje, font_family=FAMILIA_FUENTE, size=14, color="#000000", text_align=ft.TextAlign.CENTER),
            actions=[ft.ElevatedButton(text="Aceptar", bgcolor=COLOR_MORADO_FONDO, color=COLOR_BLANCO, on_click=cerrar)],
            actions_alignment=ft.MainAxisAlignment.CENTER
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def clic_enviar(self, e):
        comentario = (self.txt_comentario.value or "").strip()
        if not comentario:
            self.mostrar_alerta("Campo vacío", "Por favor escribe el comentario del reporte antes de enviar.")
            return

        self.btn_enviar.disabled = True
        self.page.update()

        exito, msg = self.firebase.enviar_reporte_inventariable(self.datos_item, comentario)

        self.btn_enviar.disabled = False
        self.page.update()

        if exito:
            self.mostrar_alerta("Reporte enviado", msg, regresar_al_cerrar=True)
        else:
            self.mostrar_alerta("Error", msg, regresar_al_cerrar=False)