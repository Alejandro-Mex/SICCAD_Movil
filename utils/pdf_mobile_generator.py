import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String


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
    Genera PDF horizontal de Bienes Inventariables o No Inventariables filtrado por empleado (sin logo).
    """
    try:
        fecha_emision = datetime.now().strftime("%d/%m/%Y")
        fecha_file = datetime.now().strftime("%d_%m_%Y_%H%M")
        emp_limpio = nombre_empleado_filtro.replace(" ", "_")
        es_inv = (tipo_inventario.lower() == "inventariables")

        nombre_pdf = f"Reporte_{'Inventariables' if es_inv else 'No_Inventariables'}_{emp_limpio}_{fecha_file}.pdf"
        ruta_final = obtener_ruta_descargas(nombre_pdf)

        doc = SimpleDocTemplate(
            ruta_final, pagesize=landscape(letter),
            leftMargin=26, rightMargin=26, topMargin=24, bottomMargin=24
        )
        elementos = []

        ancho_banner = 740
        alto_banner = 60
        banner = Drawing(ancho_banner, alto_banner)
        banner.add(Rect(0, 0, ancho_banner, alto_banner, rx=10, ry=10, fillColor=colors.HexColor("#553a8f"), strokeColor=colors.HexColor("#553a8f")))
        subtitulo = f"Ayuntamiento de Mérida — Padrón de Bienes {'Inventariables' if es_inv else 'No Inventariables'} ({nombre_empleado_filtro})"
        banner.add(String(22, 35, "Centro de Alfabetización Digital", fontName="Helvetica-Bold", fontSize=16, fillColor=colors.white))
        banner.add(String(22, 17, subtitulo, fontName="Helvetica", fontSize=10, fillColor=colors.white))
        banner.add(String(ancho_banner - 18, 35, f"Fecha de emisión: {fecha_emision}", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.white, textAnchor="end"))
        banner.add(String(ancho_banner - 18, 19, f"Total de registros: {len(items)}", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.white, textAnchor="end"))

        elementos.append(banner)
        elementos.append(Spacer(1, 14))

        estilos = getSampleStyleSheet()
        est_izq = ParagraphStyle("I", parent=estilos["Normal"], fontName="Helvetica", fontSize=8.5, leading=11, alignment=TA_LEFT)
        est_cen = ParagraphStyle("C", parent=estilos["Normal"], fontName="Helvetica", fontSize=8.5, leading=11, alignment=TA_CENTER)
        est_hdr = ParagraphStyle("H", parent=estilos["Normal"], fontName="Helvetica-Bold", fontSize=9, alignment=TA_CENTER)
        est_tit = ParagraphStyle("T", parent=estilos["Normal"], fontName="Helvetica-Bold", fontSize=10.5, alignment=TA_CENTER)

        if es_inv:
            datos_tabla = [
                [Paragraph(f"Reporte de Bienes Inventariables — {nombre_empleado_filtro}", est_tit), "", "", "", "", "", "", "", ""],
                [
                    Paragraph("Folio", est_hdr), Paragraph("Marca", est_hdr), Paragraph("Modelo", est_hdr),
                    Paragraph("Descripción", est_hdr), Paragraph("N° Serie", est_hdr), Paragraph("Estado", est_hdr),
                    Paragraph("Ubicación", est_hdr), Paragraph("Unidad Admin.", est_hdr), Paragraph("Encargado", est_hdr)
                ]
            ]
            for it in items:
                datos_tabla.append([
                    Paragraph(str(it.get("folio", "")), est_cen), Paragraph(str(it.get("marca", "")), est_cen),
                    Paragraph(str(it.get("modelo", "")), est_cen), Paragraph(str(it.get("descripcion", "")), est_izq),
                    Paragraph(str(it.get("numero_serie", "")), est_cen), Paragraph(str(it.get("estado", "")), est_cen),
                    Paragraph(str(it.get("ubicacion", "")), est_cen), Paragraph(str(it.get("unidad_admin", "")), est_cen),
                    Paragraph(str(it.get("nombre_encargado", "")), est_izq)
                ])
            anchos = [62, 68, 82, 118, 72, 62, 74, 86, 116]
            ult_col = 8
        else:
            datos_tabla = [
                [Paragraph(f"Reporte de Bienes No Inventariables — {nombre_empleado_filtro}", est_tit), "", "", ""],
                [Paragraph("Clave", est_hdr), Paragraph("Descripción", est_hdr), Paragraph("Ubicación", est_hdr), Paragraph("Encargado", est_hdr)]
            ]
            for it in items:
                datos_tabla.append([
                    Paragraph(str(it.get("clave", "")), est_cen),
                    Paragraph(str(it.get("descripcion", "")), est_izq),
                    Paragraph(str(it.get("ubicacion", "")), est_cen),
                    Paragraph(str(it.get("nombre_encargado", "")), est_izq)
                ])
            anchos = [155, 225, 165, 195]
            ult_col = 3

        tabla = Table(datos_tabla, colWidths=anchos, repeatRows=2)
        tabla.setStyle(TableStyle([
            ("SPAN", (0, 0), (ult_col, 0)),
            ("BACKGROUND", (0, 0), (ult_col, 0), colors.HexColor("#F2F4F8")),
            ("ALIGN", (0, 0), (ult_col, 0), "CENTER"),
            ("BACKGROUND", (0, 1), (ult_col, 1), colors.HexColor("#FCCb2d")),
            ("ALIGN", (0, 1), (ult_col, 1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elementos.append(tabla)
        doc.build(elementos)

        try:
            if os.name == "nt":
                os.startfile(ruta_final)
        except Exception:
            pass

        return True, f"PDF guardado en Descargas:\n{nombre_pdf}"
    except Exception as e:
        return False, f"Error generando PDF: {e}"


def generar_pdf_horas_alumno_movil(datos_alumno: dict, registros: list) -> tuple:
    """ Genera el PDF oficial de Reporte de Horas del Alumno (sin logo) """
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

        doc = SimpleDocTemplate(ruta_final, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=28, bottomMargin=28)
        elementos = []

        banner = Drawing(540, 62)
        banner.add(Rect(0, 0, 540, 62, rx=10, ry=10, fillColor=colors.HexColor("#553a8f"), strokeColor=colors.HexColor("#553a8f")))
        banner.add(String(22, 36, "Centro de Alfabetización Digital", fontName="Helvetica-Bold", fontSize=15, fillColor=colors.white))
        banner.add(String(22, 18, "Ayuntamiento de Mérida — Reporte de Horas", fontName="Helvetica", fontSize=10.5, fillColor=colors.white))
        banner.add(String(524, 36, f"Escuela: {escuela}", fontName="Helvetica-Bold", fontSize=9.5, fillColor=colors.white, textAnchor="end"))
        banner.add(String(524, 20, f"Emisión: {fecha_emision}", fontName="Helvetica-Bold", fontSize=9.5, fillColor=colors.white, textAnchor="end"))

        elementos.append(banner)
        elementos.append(Spacer(1, 16))

        estilos = getSampleStyleSheet()
        est_c = ParagraphStyle("C", parent=estilos["Normal"], fontName="Helvetica", fontSize=9.5, alignment=TA_CENTER)
        est_bc = ParagraphStyle("BC", parent=estilos["Normal"], fontName="Helvetica-Bold", fontSize=10, alignment=TA_CENTER)
        est_bi = ParagraphStyle("BI", parent=estilos["Normal"], fontName="Helvetica-Bold", fontSize=9.5, alignment=TA_LEFT)
        est_bd = ParagraphStyle("BD", parent=estilos["Normal"], fontName="Helvetica-Bold", fontSize=9.5, alignment=TA_RIGHT)

        datos_tabla = [
            [Paragraph(nombre_completo, est_bc), "", "", ""],
            [Paragraph("Fecha inicio:", est_bi), Paragraph(fecha_inicio, est_bd), Paragraph("Fecha final:", est_bi), Paragraph(fecha_fin, est_bd)],
            [Paragraph("Fecha", est_bc), Paragraph("Hora entrada", est_bc), Paragraph("Hora salida", est_bc), Paragraph("Horas hechas", est_bc)]
        ]

        total_filas = max(20, len(filas_asist))
        for i in range(total_filas):
            if i < len(filas_asist):
                datos_tabla.append([Paragraph(x, est_c) for x in filas_asist[i]])
            else:
                datos_tabla.append(["", "", "", ""])

        ult_fila = len(datos_tabla)
        datos_tabla.append([Paragraph("Total de horas hechas:", est_bd), "", "", Paragraph(f"{total_hechas} / {meta_total}", est_bc)])

        tabla = Table(datos_tabla, colWidths=[135, 135, 135, 135], rowHeights=[24, 22, 24] + [21] * total_filas + [24], repeatRows=3)
        tabla.setStyle(TableStyle([
            ("SPAN", (0, 0), (3, 0)),
            ("BACKGROUND", (0, 0), (3, 0), colors.HexColor("#F2F4F8")),
            ("BACKGROUND", (0, 2), (3, 2), colors.HexColor("#FCCb2d")),
            ("SPAN", (0, ult_fila), (2, ult_fila)),
            ("BACKGROUND", (0, ult_fila), (3, ult_fila), colors.HexColor("#F2F4F8")),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elementos.append(tabla)
        doc.build(elementos)

        try:
            if os.name == "nt":
                os.startfile(ruta_final)
        except Exception:
            pass

        return True, f"Reporte PDF guardado en Descargas:\n{nombre_pdf}"
    except Exception as e:
        return False, f"Error generando PDF: {e}"