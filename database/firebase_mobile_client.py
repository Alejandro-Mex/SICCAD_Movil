import hashlib
from datetime import datetime
import requests
from config.settings import GOOGLE_SHEETS_API_URL


class FirebaseMobileClient:
    """
    Motor de Base de Datos de SICCAD Móvil conectado a Google Sheets (vía Apps Script Web App).
    Mantiene exactamente la misma interfaz de métodos para todas las vistas móviles.
    """
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(FirebaseMobileClient, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self.api_url = GOOGLE_SHEETS_API_URL
        self.usuario_actual = None
        self.claves_en_rojo = set()
        self.folios_en_rojo = set()
        self._asegurar_admin_inicial()

    @staticmethod
    def encriptar_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _a_bool(val) -> bool:
        if isinstance(val, bool):
            return val
        return str(val).strip().lower() in ["true", "1", "si", "sí", "verdadero"]

    @staticmethod
    def _a_int(val, defecto=0) -> int:
        try:
            return int(float(str(val).strip()))
        except Exception:
            return defecto

    # ================= COMUNICACIÓN HTTP CON GOOGLE SHEETS =================
    def _sheet_leer(self, nombre_hoja: str) -> list:
        try:
            resp = requests.get(
                self.api_url,
                params={"sheet": nombre_hoja},
                timeout=15,
                allow_redirects=True
            )
            if resp.status_code == 200:
                js = resp.json()
                if js.get("ok"):
                    return js.get("data", [])
        except Exception as e:
            print(f"Error leyendo hoja '{nombre_hoja}' en Google Sheets: {e}")
        return []

    def _sheet_guardar(self, nombre_hoja: str, doc_id: str, datos: dict) -> bool:
        try:
            payload = {
                "action": "upsert",
                "sheet": nombre_hoja,
                "doc_id": str(doc_id),
                "data": datos
            }
            resp = requests.post(
                self.api_url,
                json=payload,
                timeout=15,
                allow_redirects=True
            )
            return resp.status_code in [200, 201, 302]
        except Exception as e:
            print(f"Error guardando en hoja '{nombre_hoja}': {e}")
            return False

    def _sheet_eliminar(self, nombre_hoja: str, doc_id: str) -> bool:
        try:
            payload = {
                "action": "delete",
                "sheet": nombre_hoja,
                "doc_id": str(doc_id)
            }
            resp = requests.post(
                self.api_url,
                json=payload,
                timeout=15,
                allow_redirects=True
            )
            return resp.status_code in [200, 201, 302]
        except Exception as e:
            print(f"Error eliminando en hoja '{nombre_hoja}': {e}")
            return False

    def _asegurar_admin_inicial(self):
        """ Si la hoja 'usuarios' está nueva y vacía, crea automáticamente admin / 12345 """
        try:
            usuarios = self._sheet_leer("usuarios")
            if not usuarios:
                self._sheet_guardar("usuarios", "admin", {
                    "doc_id": "admin",
                    "id_usuario": "admin",
                    "usuario": "admin",
                    "numero_empleado": "admin",
                    "contrasena": self.encriptar_password("12345"),
                    "password_visible": "12345",
                    "rol": "admin",
                    "es_admin": True,
                    "nombres": "Administrador",
                    "apellidos": "CAD Mérida",
                    "correo": "admin@merida.gob.mx",
                    "per_inventariables": True,
                    "per_no_inventariables": True,
                    "per_servicio_social": True,
                    "per_bienes_consumo": True
                })
        except Exception:
            pass

    # ================= LOGIN DUAL (EMPLEADO, ADMIN Y ESTUDIANTE) =================
    def validar_login_movil_empleado(self, usuario: str, password: str):
        usuario = str(usuario).strip()
        password = str(password).strip()
        pass_hash = self.encriptar_password(password)

        try:
            usuarios = self._sheet_leer("usuarios")
            for u in usuarios:
                ids_posibles = [
                    str(u.get("doc_id", "")).strip(),
                    str(u.get("numero_empleado", "")).strip(),
                    str(u.get("usuario", "")).strip(),
                    str(u.get("id_usuario", "")).strip()
                ]
                if usuario in ids_posibles:
                    pass_guardada = str(u.get("contrasena", "")).strip()
                    pass_vis = str(u.get("password_visible", "")).strip()
                    if pass_guardada in [pass_hash, password] or (pass_vis and pass_vis == password):
                        # Normalizar permisos booleanos
                        u["es_admin"] = self._a_bool(u.get("es_admin", False))
                        u["per_inventariables"] = self._a_bool(u.get("per_inventariables", False))
                        u["per_no_inventariables"] = self._a_bool(u.get("per_no_inventariables", False))
                        u["per_servicio_social"] = self._a_bool(u.get("per_servicio_social", False))
                        u["per_bienes_consumo"] = self._a_bool(u.get("per_bienes_consumo", False))
                        u["password_visible"] = password
                        if u.get("cantidad_horas") != "":
                            u["cantidad_horas"] = self._a_int(u.get("cantidad_horas", 480), 480)
                        self.usuario_actual = u
                        return True, u

            return False, "Usuario o contraseña incorrectos."
        except Exception as e:
            return False, f"Error de conexión con Google Sheets:\n{e}"

    def actualizar_datos_perfil_movil(self, datos_nuevos: dict):
        if not self.usuario_actual:
            return False, "No hay sesión activa."

        nombres = datos_nuevos.get("nombres", "").strip()
        apellidos = datos_nuevos.get("apellidos", "").strip()
        correo = datos_nuevos.get("correo", "").strip()
        nuevo_usuario = datos_nuevos.get("usuario", "").strip()
        nueva_pass = datos_nuevos.get("contrasena", "").strip()

        if not nombres or not apellidos or not nuevo_usuario:
            return False, "Por favor completa Nombres, Apellidos y Usuario."

        doc_id_actual = str(
            self.usuario_actual.get("doc_id")
            or self.usuario_actual.get("numero_empleado")
            or self.usuario_actual.get("id_usuario")
            or self.usuario_actual.get("usuario")
        ).strip()

        doc_actualizado = dict(self.usuario_actual)
        doc_actualizado["nombres"] = nombres
        doc_actualizado["apellidos"] = apellidos
        doc_actualizado["correo"] = correo
        doc_actualizado["usuario"] = nuevo_usuario
        doc_actualizado["numero_empleado"] = nuevo_usuario

        if nueva_pass:
            doc_actualizado["contrasena"] = self.encriptar_password(nueva_pass)
            doc_actualizado["password_visible"] = nueva_pass

        ok = self._sheet_guardar("usuarios", doc_id_actual, doc_actualizado)
        if ok:
            self.usuario_actual = doc_actualizado
            return True, "Datos actualizados correctamente en Google Sheets."
        return False, "No se pudo actualizar en Google Sheets."

    # ================= 1. NO INVENTARIABLES =================
    def obtener_no_inventariables_empleado(self):
        if not self.usuario_actual:
            return []
        rol = str(self.usuario_actual.get("rol", "")).strip().lower()
        num_emp = str(self.usuario_actual.get("numero_empleado", "")).strip()
        nom_completo = f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip().lower()
        es_admin = (rol == "admin" or num_emp.lower() == "admin" or self._a_bool(self.usuario_actual.get("es_admin", False)))

        todos = self._sheet_leer("no_inventariables")
        lista = []
        for item in todos:
            clave_str = str(item.get("clave", item.get("doc_id", ""))).strip()
            item["clave"] = clave_str
            item["en_revision_rojo"] = (clave_str in self.claves_en_rojo)
            if es_admin or str(item.get("id_empleado", "")).strip() == num_emp or str(item.get("nombre_encargado", "")).strip().lower() == nom_completo:
                lista.append(item)
        return lista

    def actualizar_ubicacion_no_inventariable(self, clave: str, nueva_ubicacion: str):
        clave_clean = str(clave).strip()
        doc_id = clave_clean.replace("/", "_")
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        self.claves_en_rojo.discard(clave_clean)

        # Buscar doc_id exacto en la hoja
        todos = self._sheet_leer("no_inventariables")
        for it in todos:
            if str(it.get("clave", "")).strip() == clave_clean:
                doc_id = str(it.get("doc_id") or doc_id)
                break

        ok = self._sheet_guardar("no_inventariables", doc_id, {
            "ubicacion": nueva_ubicacion,
            "ultima_actualizacion": fecha_hoy
        })
        return ok, "Ubicación actualizada." if ok else "Error al guardar."

    def enviar_reporte_no_inventariable(self, datos_item: dict, comentario: str):
        clave = str(datos_item.get("clave", "")).strip()
        doc_bien_id = str(datos_item.get("doc_id") or clave.replace("/", "_"))
        nombre_encargado = datos_item.get("nombre_encargado", "") or f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip()
        id_empleado = str(datos_item.get("id_empleado", "") or self.usuario_actual.get("numero_empleado", ""))

        rep_id = f"RNI-{int(datetime.now().timestamp()) % 100000}"
        nuevo_reporte = {
            "doc_id": rep_id,
            "id": rep_id,
            "bien_doc_id": doc_bien_id,
            "clave": clave,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "comentarios": comentario.strip(),
            "id_empleado": id_empleado,
            "nombre_encargado": nombre_encargado,
            "tipo_bien": "no_inventariable",
            "validado": False
        }
        ok = self._sheet_guardar("reportes_no_inventariables", rep_id, nuevo_reporte)
        return ok, "Reporte enviado exitosamente." if ok else "Error al enviar reporte."

    # ================= 2. INVENTARIABLES =================
    def obtener_inventariables_empleado(self):
        if not self.usuario_actual:
            return []
        rol = str(self.usuario_actual.get("rol", "")).strip().lower()
        num_emp = str(self.usuario_actual.get("numero_empleado", "")).strip()
        nom_completo = f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip().lower()
        es_admin = (rol == "admin" or num_emp.lower() == "admin" or self._a_bool(self.usuario_actual.get("es_admin", False)))

        todos = self._sheet_leer("inventariables")
        lista = []
        for item in todos:
            folio_str = str(item.get("folio", item.get("doc_id", ""))).strip()
            item["folio"] = folio_str
            item["en_revision_rojo"] = (folio_str in self.folios_en_rojo)
            if es_admin or str(item.get("id_empleado", "")).strip() == num_emp or str(item.get("nombre_encargado", "")).strip().lower() == nom_completo:
                lista.append(item)
        return lista

    def actualizar_ubicacion_inventariable(self, folio: str, nueva_ubicacion: str):
        folio_clean = str(folio).strip()
        doc_id = folio_clean.replace("/", "_")
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        self.folios_en_rojo.discard(folio_clean)

        todos = self._sheet_leer("inventariables")
        for it in todos:
            if str(it.get("folio", "")).strip() == folio_clean:
                doc_id = str(it.get("doc_id") or doc_id)
                break

        ok = self._sheet_guardar("inventariables", doc_id, {
            "ubicacion": nueva_ubicacion,
            "ultima_actualizacion": fecha_hoy
        })
        return ok, "Ubicación actualizada." if ok else "Error al guardar."

    def enviar_reporte_inventariable(self, datos_item: dict, comentario: str):
        folio = str(datos_item.get("folio", "")).strip()
        doc_bien_id = str(datos_item.get("doc_id") or folio.replace("/", "_"))
        nombre_encargado = datos_item.get("nombre_encargado", "") or f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip()
        id_empleado = str(datos_item.get("id_empleado", "") or self.usuario_actual.get("numero_empleado", ""))

        rep_id = f"RI-{int(datetime.now().timestamp()) % 100000}"
        nuevo_reporte = {
            "doc_id": rep_id,
            "id": rep_id,
            "bien_doc_id": doc_bien_id,
            "folio": folio,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "comentarios": comentario.strip(),
            "id_empleado": id_empleado,
            "nombre_encargado": nombre_encargado,
            "tipo_bien": "inventariable",
            "validado": False
        }
        ok = self._sheet_guardar("reportes_inventariables", rep_id, nuevo_reporte)
        return ok, "Reporte enviado exitosamente." if ok else "Error al enviar reporte."

    # ================= 3. CONSUMIBLES =================
    def obtener_consumibles_movil(self):
        todos = self._sheet_leer("consumibles")
        for it in todos:
            it["id"] = str(it.get("id") or it.get("doc_id", ""))
            it["cantidad"] = self._a_int(it.get("cantidad", 0), 0)
        return todos

    def modificar_cantidad_consumible(self, datos_item: dict, delta: int):
        cantidad_actual = self._a_int(datos_item.get("cantidad", 0), 0)
        nueva_cantidad = max(0, cantidad_actual + delta)
        datos_item["cantidad"] = nueva_cantidad
        doc_id = str(datos_item.get("doc_id") or datos_item.get("id"))

        ok = self._sheet_guardar("consumibles", doc_id, {"cantidad": nueva_cantidad})
        return ok, nueva_cantidad

    # ================= 4. ALUMNOS, HORAS, JUSTIFICACIONES Y REPORTES ADMIN =================
    def obtener_alumnos_movil(self):
        todos = self._sheet_leer("usuarios")
        lista = []
        for item in todos:
            if str(item.get("rol", "")).strip().lower() == "estudiante":
                item["id_usuario"] = str(item.get("id_usuario") or item.get("doc_id", ""))
                item["nombre_mostrar"] = f"{str(item.get('nombres', '')).strip()} {str(item.get('apellidos', '')).strip()}".strip() or item["id_usuario"]
                item["cantidad_horas"] = self._a_int(item.get("cantidad_horas", 480), 480)
                lista.append(item)
        return lista

    @staticmethod
    def _calcular_horas_dia(entrada_str: str, salida_str: str) -> int:
        try:
            limpio_ent = str(entrada_str).lower().replace("am", "").replace("pm", "").strip()
            limpio_sal = str(salida_str).lower().replace("am", "").replace("pm", "").strip()
            h_ent = int(limpio_ent.split(":")[0])
            h_sal = int(limpio_sal.split(":")[0])
            if "pm" in str(salida_str).lower() and h_sal < 12:
                h_sal += 12
            diff = h_sal - h_ent
            return diff if diff > 0 else 4
        except Exception:
            return 4

    def obtener_horas_hechas_alumno(self, datos_alumno: dict):
        id_est = str(datos_alumno.get("doc_id") or datos_alumno.get("id_usuario") or datos_alumno.get("usuario")).strip()

        # Refrescar horas restantes actuales desde la pestaña 'usuarios'
        for u in self._sheet_leer("usuarios"):
            if str(u.get("doc_id", "")).strip() == id_est or str(u.get("id_usuario", "")).strip() == id_est:
                if u.get("cantidad_horas") != "":
                    datos_alumno["cantidad_horas"] = self._a_int(u.get("cantidad_horas", 480), 480)
                break

        todos_horas = self._sheet_leer("control_horas")
        lista = []
        for d in todos_horas:
            if str(d.get("id_estudiante", "")).strip() == id_est:
                horas = self._a_int(d.get("horas_calculadas", 0), 0)
                if horas <= 0:
                    horas = self._calcular_horas_dia(d.get("hora_entrada", ""), d.get("hora_salida", ""))
                lista.append({
                    "doc_id": str(d.get("doc_id", "")),
                    "fecha": str(d.get("fecha", "")),
                    "hora_entrada": str(d.get("hora_entrada", "")),
                    "hora_salida": str(d.get("hora_salida", "")),
                    "horas": horas,
                    "validado": self._a_bool(d.get("validado", False))
                })
        return lista

    def eliminar_hora_no_validada_estudiante(self, datos_alumno: dict, reg_hora: dict):
        if self._a_bool(reg_hora.get("validado", False)):
            return False, "No puedes eliminar un registro de horas que ya fue validado."

        doc_id_hora = str(reg_hora.get("doc_id", "")).strip()
        if not doc_id_hora:
            return False, "No se encontró el identificador de este registro."

        ok = self._sheet_eliminar("control_horas", doc_id_hora)
        return ok, "Registro de horas eliminado correctamente." if ok else "Error al eliminar en Google Sheets."

    def agregar_horas_estudiante(self, datos_alumno: dict, hora_entrada: str, hora_salida: str):
        id_est = str(datos_alumno.get("doc_id") or datos_alumno.get("id_usuario") or datos_alumno.get("usuario")).strip()
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        horas_calc = self._calcular_horas_dia(hora_entrada, hora_salida)

        doc_h_id = f"HR-{int(datetime.now().timestamp()) % 1000000}"
        nuevo_registro = {
            "doc_id": doc_h_id,
            "id": doc_h_id,
            "id_estudiante": id_est,
            "hora_entrada": hora_entrada.strip(),
            "hora_salida": hora_salida.strip(),
            "fecha": fecha_hoy,
            "horas_calculadas": horas_calc,
            "validado": False
        }
        ok = self._sheet_guardar("control_horas", doc_h_id, nuevo_registro)
        return ok, f"Horas registradas ({horas_calc} hrs)." if ok else "Error al guardar horas."

    def enviar_justificacion_estudiante(self, datos_alumno: dict, fecha: str, justificacion: str):
        id_est = str(datos_alumno.get("doc_id") or datos_alumno.get("id_usuario") or datos_alumno.get("usuario")).strip()
        doc_j_id = f"JUS-{int(datetime.now().timestamp()) % 1000000}"

        nueva_just = {
            "doc_id": doc_j_id,
            "id": doc_j_id,
            "id_estudiante": id_est,
            "fecha": fecha.strip(),
            "descripcion_justificacion": justificacion.strip(),
            "validado": False
        }
        ok = self._sheet_guardar("control_justificaciones", doc_j_id, nueva_just)
        return ok, "Justificación enviada exitosamente." if ok else "Error al enviar justificación."

    def obtener_lista_empleados_movil(self):
        todos = self._sheet_leer("usuarios")
        lista = []
        for d in todos:
            if str(d.get("rol", "")).strip().lower() in ["empleado", "admin"]:
                d["nombre_completo"] = f"{str(d.get('nombres', '')).strip()} {str(d.get('apellidos', '')).strip()}".strip() or str(d.get("doc_id", ""))
                lista.append(d)
        return lista

    def obtener_inventario_por_empleado(self, tipo_inventario: str, nombre_empleado="Todos", id_empleado=""):
        hoja = "inventariables" if tipo_inventario.lower() == "inventariables" else "no_inventariables"
        todos = self._sheet_leer(hoja)

        if nombre_empleado == "Todos":
            return todos

        nom_norm = nombre_empleado.strip().lower()
        return [
            it for it in todos
            if (id_empleado and str(it.get("id_empleado", "")).strip() == str(id_empleado).strip())
            or str(it.get("nombre_encargado", "")).strip().lower() == nom_norm
        ]