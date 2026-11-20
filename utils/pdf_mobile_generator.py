import os
from datetime import datetime
from fpdf import FPDF


def _limpiar_latin1(texto) -> str:
    """ Convierte caracteres especiales a latin-1 seguro para FPDF estándar en Android """
    s = str(texto or "").replace("—", "-").replace("–", "-")
    return s.encode("latin-1", "replace").decode("latin-1")


def obtener_ruta_descargas(nombre_archivo: str) -> str:
    """ Guarda en la carpeta Descargas de Android (/storage/emulated/0/Download) o de Windows """
    rutas_posibles = [
        "/storage/emulated/0/Download",
        os.path.join(os.path.expanduser("~"), "Downloads"),
        os.path.abspath(".")
    ]
    for carpeta in rutas_posibles:
        if os.path.exists(carpeta) and os.access(carpeta, os.W_OK):
            return os.path.join(carpeta, nombre_archivo)
    return os.path.join(os.path.abspath("."), nombre_archivo)


def generar_pdf_inventario_movil(tipo_inventario: str, items: list, nombre_empleado_filtro="Todos") -> tuple:
    """
    Genera PDF en orientación HORIZONTAL (Landscape) de Bienes Inventariables o No Inventariables
    usando FPDF (100% puro Python, 100% compatible con APK Android) y SIN logo.
    """
    try:
        fecha_emision = datetime.now().strftime("%d/%m/%Y")
        fecha_file = datetime.now().strftime("%d_%m_%Y_%H%M")
        emp_limpio = nombre_empleado_filtro.replace(" ", "_")
        es_inv = (tipo_inventario.lower() == "inventariables")

        nombre_pdf = f"Reporte_{'Inventariables' if es_inv else 'No_Inventariables'}_{emp_limpio}_{fecha_file}.pdf"
        ruta_final = obtener_ruta_descargas(nombre_pdf)

        # Hoja Carta en Horizontal ('L' = Landscape, mm, 'Letter' -> 279.4 x 215.9 mm)
        pdf = FPDF(orientation="L", unit="mm", format="Letter")
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.add_page()

        # 1. BANNER SUPERIOR MORADO (#553a8f -> RGB 85, 58, 143) SIN LOGO
        pdf.set_fill_color(85, 58, 143)
        pdf.rect(10, 10, 259, 22, style="F")

        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 15)
        pdf.set_xy(15, 13)
        pdf.cell(160, 7, _limpiar_latin1("Centro de Alfabetización Digital"), ln=0)

        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_xy(190, 13)
        pdf.cell(74, 6, _limpiar_latin1(f"Fecha de emisión: {fecha_emision}"), align="R")

        pdf.set_font("Helvetica", "", 10)
        pdf.set_xy(15, 21)
        sub = f"Ayuntamiento de Mérida - Padrón de Bienes {'Inventariables' if es_inv else 'No Inventariables'} ({nombre_empleado_filtro})"
        pdf.cell(175, 6, _limpiar_latin1(sub), ln=0)

        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_xy(190, 20)
        pdf.cell(74, 6, _limpiar_latin1(f"Total de registros: {len(items)}"), align="R")

        pdf.set_xy(10, 38)
        pdf.set_text_color(0, 0, 0)

        # 2. TÍTULO DE LA TABLA (Gris claro #F2F4F8)
        pdf.set_fill_color(242, 244, 248)
        pdf.set_font("Helvetica", "B", 10.5)
        tit_tabla = f"Reporte General de Bienes {'Inventariables' if es_inv else 'No Inventariables'} - {nombre_empleado_filtro}"
        pdf.cell(259, 8, _limpiar_latin1(tit_tabla), border=1, ln=1, align="C", fill=True)

        # 3. ENCABEZADOS AMARILLOS (#FCCb2d -> RGB 252, 203, 45)
        pdf.set_fill_color(252, 203, 45)
        if es_inv:
            cols = [
                ("Folio", 22), ("Marca", 24), ("Modelo", 28), ("Descripción", 44),
                ("N° Serie", 25), ("Estado", 20), ("Ubicación", 26), ("Unidad Admin.", 30), ("Encargado", 40)
            ]
            pdf.set_font("Helvetica", "B", 8.5)
            for titulo, ancho in cols:
                pdf.cell(ancho, 8, _limpiar_latin1(titulo), border=1, align="C", fill=True)
            pdf.ln()

            pdf.set_font("Helvetica", "", 8)
            for it in items:
                vals = [
                    str(it.get("folio", "")), str(it.get("marca", "")), str(it.get("modelo", "")),
                    str(it.get("descripcion", ""))[:32], str(it.get("numero_serie", "")),
                    str(it.get("estado", "")), str(it.get("ubicacion", "")),
                    str(it.get("unidad_admin", ""))[:18], str(it.get("nombre_encargado", ""))[:26]
                ]
                for idx, val in enumerate(vals):
                    alinear = "L" if idx in [3, 8] else "C"
                    pdf.cell(cols[idx][1], 8, _limpiar_latin1(val), border=1, align=alinear)
                pdf.ln()
        else:
            cols = [("Clave", 55), ("Descripción", 84), ("Ubicación", 55), ("Encargado", 65)]
            pdf.set_font("Helvetica", "B", 9.5)
            for titulo, ancho in cols:
                pdf.cell(ancho, 8, _limpiar_latin1(titulo), border=1, align="C", fill=True)
            pdf.ln()

            pdf.set_font("Helvetica", "", 9)
            for it in items:
                vals = [
                    str(it.get("clave", "")), str(it.get("descripcion", ""))[:45],
                    str(it.get("ubicacion", "")), str(it.get("nombre_encargado", ""))[:35]
                ]
                for idx, val in enumerate(vals):
                    alinear = "L" if idx in [1, 3] else "C"
                    pdf.cell(cols[idx][1], 8, _limpiar_latin1(val), border=1, align=alinear)
                pdf.ln()

        pdf.output(ruta_final)

        try:
            if os.name == "nt":
                os.startfile(ruta_final)
        except Exception:
            pass

        return True, f"PDF guardado en Descargas:\n{nombre_pdf}"
    except Exception as e:
        return False, f"Error generando PDF: {e}"


def generar_pdf_horas_alumno_movil(datos_alumno: dict, registros: list) -> tuple:
    """ Genera el PDF oficial de Reporte de Horas del Alumno (vertical, 20 renglones, SIN logo) """
    try:
        nombre_completo = f"{datos_alumno.get('nombres', '').strip()} {datos_alumno.get('apellidos', '').strip()}".strip() or datos_alumno.get("nombre_mostrar", "Alumno")
        escuela = datos_alumno.get("nombre_escuela", "").strip()
        fecha_inicio = datos_alumno.get("fecha_inicio", "").strip()
        fecha_fin = datos_alumno.get("fecha_fin", "").strip()
        fecha_emision = datetime.now().strftime("%d/%m/%Y")

        nombre_pdf = f"Reporte_Horas_{nombre_completo.replace(' ', '_')}_{datetime.now().strftime('%d_%m_%Y')}.pdf"
        ruta_final = obtener_ruta_descargas(nombre_pdf)

        registros_val = [r for r in registros if r.get("validado", False)]
        total_hechas = 0
        filas_asist = []
        for r in registros_val:
            h_ent = str(r.get("hora_entrada", "")).strip()
            h_sal = str(r.get("hora_salida", "")).strip()
            h_calc = int(r.get("horas", r.get("horas_calculadas", 4)))
            total_hechas += h_calc
            h_sal_txt = f"Justificado ({h_calc} h)" if h_ent.lower() == "justificado" else h_sal
            filas_asist.append((str(r.get("fecha", "")), h_ent, h_sal_txt, str(h_calc)))

        meta_total = int(datos_alumno.get("cantidad_horas", 480)) + total_hechas

        # Hoja Carta Vertical ('P' = Portrait -> 215.9 x 279.4 mm)
        pdf = FPDF(orientation="P", unit="mm", format="Letter")
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.add_page()

        # 1. BANNER SUPERIOR MORADO (#553a8f) SIN LOGO
        pdf.set_fill_color(85, 58, 143)
        pdf.rect(12, 10, 192, 22, style="F")

        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_xy(17, 13)
        pdf.cell(110, 7, _limpiar_latin1("Centro de Alfabetización Digital"))

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_xy(125, 13)
        pdf.cell(74, 6, _limpiar_latin1(f"Escuela: {escuela}"), align="R")

        pdf.set_font("Helvetica", "", 10)
        pdf.set_xy(17, 21)
        pdf.cell(110, 6, _limpiar_latin1("Ayuntamiento de Mérida - Reporte de Horas"))

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_xy(125, 20)
        pdf.cell(74, 6, _limpiar_latin1(f"Emisión: {fecha_emision}"), align="R")

        pdf.set_xy(12, 38)
        pdf.set_text_color(0, 0, 0)

        # 2. FILA 0: Nombre completo del alumno (Gris claro)
        pdf.set_fill_color(242, 244, 248)
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.cell(192, 8.5, _limpiar_latin1(nombre_completo), border=1, ln=1, align="C", fill=True)

        # 3. FILA 1: Fechas de inicio y final
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_x(12)
        pdf.cell(48, 8, _limpiar_latin1("Fecha inicio:"), border=1, align="L")
        pdf.cell(48, 8, _limpiar_latin1(fecha_inicio), border=1, align="R")
        pdf.cell(48, 8, _limpiar_latin1("Fecha final:"), border=1, align="L")
        pdf.cell(48, 8, _limpiar_latin1(fecha_fin), border=1, ln=1, align="R")

        # 4. FILA 2: Encabezados amarillos (#FCCb2d)
        pdf.set_fill_color(252, 203, 45)
        pdf.set_x(12)
        for col_tit in ["Fecha", "Hora entrada", "Hora salida", "Horas hechas"]:
            pdf.cell(48, 8.5, _limpiar_latin1(col_tit), border=1, align="C", fill=True)
        pdf.ln()

        # 5. FILAS DE ASISTENCIA + RELLENO HASTA 20 RENGLONES
        pdf.set_font("Helvetica", "", 9.5)
        total_renglones = max(20, len(filas_asist))
        for i in range(total_renglones):
            pdf.set_x(12)
            if i < len(filas_asist):
                f_str, he_str, hs_str, hh_str = filas_asist[i]
                pdf.cell(48, 7.8, _limpiar_latin1(f_str), border=1, align="C")
                pdf.cell(48, 7.8, _limpiar_latin1(he_str), border=1, align="C")
                pdf.cell(48, 7.8, _limpiar_latin1(hs_str), border=1, align="C")
                pdf.cell(48, 7.8, _limpiar_latin1(hh_str), border=1, ln=1, align="C")
            else:
                pdf.cell(48, 7.8, "", border=1)
                pdf.cell(48, 7.8, "", border=1)
                pdf.cell(48, 7.8, "", border=1)
                pdf.cell(48, 7.8, "", border=1, ln=1)

        # 6. ÚLTIMA FILA: Total de horas hechas
        pdf.set_fill_color(242, 244, 248)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_x(12)
        pdf.cell(144, 8.5, _limpiar_latin1("Total de horas hechas:  "), border=1, align="R", fill=True)
        pdf.cell(48, 8.5, _limpiar_latin1(f"{total_hechas} / {meta_total}"), border=1, ln=1, align="C", fill=True)

        pdf.output(ruta_final)

        try:
            if os.name == "nt":
                os.startfile(ruta_final)
        except Exception:
            pass

        return True, f"Reporte PDF guardado en Descargas:\n{nombre_pdf}"
    except Exception as e:
        return False, f"Error generando PDF: {e}"