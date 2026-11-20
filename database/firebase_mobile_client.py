import hashlib
from datetime import datetime
import requests
from config.settings import GOOGLE_SHEETS_API_URL


class FirebaseMobileClient:
    """
    Cliente de Base de Datos de SICCAD Móvil conectado exactamente a las 10 pestañas
    de BD_SICCAD_PRODUCCION en Google Sheets:
    Usuario | Empleado | Estudiante | ControlHoras | ControlJustificaciones |
    NoInventariable | ReporteNoInventariable | Consumible | Inventariable | ReporteInventariable
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
            print(f"Error leyendo pestaña '{nombre_hoja}': {e}")
        return []

    def _sheet_upsert(self, nombre_hoja: str, key_col: str, key_val: str, datos: dict) -> bool:
        try:
            payload = {
                "action": "upsert",
                "sheet": nombre_hoja,
                "key_col": key_col,
                "key_val": str(key_val),
                "data": datos
            }
            resp = requests.post(self.api_url, json=payload, timeout=15, allow_redirects=True)
            return resp.status_code in [200, 201, 302]
        except Exception as e:
            print(f"Error actualizando pestaña '{nombre_hoja}': {e}")
            return False

    def _sheet_insert_auto_id(self, nombre_hoja: str, datos: dict) -> bool:
        try:
            payload = {
                "action": "insert_auto_id",
                "sheet": nombre_hoja,
                "data": datos
            }
            resp = requests.post(self.api_url, json=payload, timeout=15, allow_redirects=True)
            return resp.status_code in [200, 201, 302]
        except Exception as e:
            print(f"Error insertando en pestaña '{nombre_hoja}': {e}")
            return False

    def _sheet_eliminar(self, nombre_hoja: str, key_col: str, key_val: str) -> bool:
        try:
            payload = {
                "action": "delete",
                "sheet": nombre_hoja,
                "key_col": key_col,
                "key_val": str(key_val)
            }
            resp = requests.post(self.api_url, json=payload, timeout=15, allow_redirects=True)
            return resp.status_code in [200, 201, 302]
        except Exception as e:
            print(f"Error eliminando en pestaña '{nombre_hoja}': {e}")
            return False

    # ================= LOGIN DUAL (UNIENDO Usuario + Empleado / Estudiante) =================
    def validar_login_movil_empleado(self, usuario: str, password: str):
        usuario = str(usuario).strip()
        password = str(password).strip()
        pass_hash = self.encriptar_password(password)

        try:
            usuarios = self._sheet_leer("Usuario")
            for u in usuarios:
                ids_posibles = [
                    str(u.get("id_usuario", "")).strip(),
                    str(u.get("usuario", "")).strip()
                ]
                if usuario in ids_posibles:
                    pass_guardada = str(u.get("contrasena", "")).strip()
                    pass_vis = str(u.get("password_visible", "")).strip()
                    if pass_guardada in [pass_hash, password] or (pass_vis and pass_vis == password):
                        id_u = str(u.get("id_usuario", "")).strip()
                        rol = str(u.get("rol", "")).strip().lower()

                        perfil = dict(u)
                        perfil["doc_id"] = id_u
                        perfil["numero_empleado"] = id_u
                        perfil["password_visible"] = password

                        if rol in ["admin", "empleado"]:
                            # Unir con la pestaña 'Empleado' para leer sus permisos exactos
                            empleados = self._sheet_leer("Empleado")
                            emp_row = next(
                                (e for e in empleados if str(e.get("numero_empleado", "")).strip() == id_u),
                                {}
                            )
                            perfil["es_admin"] = (rol == "admin")
                            perfil["per_inventariables"] = True if rol == "admin" else self._a_bool(emp_row.get("per_inventariables", False))
                            perfil["per_no_inventariables"] = True if rol == "admin" else self._a_bool(emp_row.get("per_no_inventariables", False))
                            perfil["per_servicio_social"] = True if rol == "admin" else self._a_bool(emp_row.get("per_servicio_social", False))
                            perfil["per_bienes_consumo"] = True if rol == "admin" else self._a_bool(emp_row.get("per_bienes_consumo", False))

                        elif rol == "estudiante":
                            # Unir con la pestaña 'Estudiante' para leer sus horas, escuela y fechas
                            estudiantes = self._sheet_leer("Estudiante")
                            est_row = next(
                                (es for es in estudiantes if str(es.get("id_usuario", "")).strip() == id_u),
                                {}
                            )
                            perfil["edad"] = self._a_int(est_row.get("edad", 0), 0)
                            perfil["direccion"] = str(est_row.get("direccion", ""))
                            perfil["fecha_inicio"] = str(est_row.get("fecha_inicio", ""))
                            perfil["fecha_fin"] = str(est_row.get("fecha_fin", ""))
                            perfil["cantidad_horas"] = self._a_int(est_row.get("cantidad_horas", 500), 500)
                            perfil["nombre_escuela"] = str(est_row.get("nombre_escuela", ""))

                        self.usuario_actual = perfil
                        return True, perfil

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

        id_u = str(self.usuario_actual.get("id_usuario", "")).strip()
        cambios = {
            "usuario": nuevo_usuario,
            "nombres": nombres,
            "apellidos": apellidos,
            "correo": correo
        }
        if nueva_pass:
            cambios["contrasena"] = nueva_pass
            cambios["password_visible"] = nueva_pass

        ok = self._sheet_upsert("Usuario", "id_usuario", id_u, cambios)
        if ok:
            self.usuario_actual.update(cambios)
            return True, "Datos actualizados correctamente en Google Sheets."
        return False, "No se pudo actualizar en Google Sheets."

    # ================= 1. NO INVENTARIABLES (Pestañas: NoInventariable y ReporteNoInventariable) =================
    def obtener_no_inventariables_empleado(self):
        if not self.usuario_actual:
            return []
        rol = str(self.usuario_actual.get("rol", "")).strip().lower()
        num_emp = str(self.usuario_actual.get("id_usuario", "")).strip()
        nom_completo = f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip().lower()
        es_admin = (rol == "admin" or num_emp.lower() == "admin")

        todos = self._sheet_leer("NoInventariable")
        lista = []
        for item in todos:
            clave_str = str(item.get("clave", "")).strip()
            item["clave"] = clave_str
            item["en_revision_rojo"] = (clave_str in self.claves_en_rojo)
            if es_admin or str(item.get("id_empleado", "")).strip() == num_emp or str(item.get("nombre_encargado", "")).strip().lower() == nom_completo:
                lista.append(item)
        return lista

    def actualizar_ubicacion_no_inventariable(self, clave: str, nueva_ubicacion: str):
        clave_clean = str(clave).strip()
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        self.claves_en_rojo.discard(clave_clean)

        ok = self._sheet_upsert("NoInventariable", "clave", clave_clean, {
            "ubicacion": nueva_ubicacion,
            "ultima_actualizacion": fecha_hoy
        })
        return ok, "Ubicación actualizada." if ok else "Error al guardar."

    def enviar_reporte_no_inventariable(self, datos_item: dict, comentario: str):
        clave = str(datos_item.get("clave", "")).strip()
        nombre_encargado = datos_item.get("nombre_encargado", "") or f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip()
        id_empleado = str(datos_item.get("id_empleado", "") or self.usuario_actual.get("id_usuario", ""))

        nuevo_reporte = {
            "clave": clave,
            "id_empleado": id_empleado,
            "nombre_encargado": nombre_encargado,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "comentarios": comentario.strip(),
            "validado": False
        }
        ok = self._sheet_insert_auto_id("ReporteNoInventariable", nuevo_reporte)
        return ok, "Reporte enviado exitosamente." if ok else "Error al enviar reporte."

    # ================= 2. INVENTARIABLES (Pestañas: Inventariable y ReporteInventariable) =================
    def obtener_inventariables_empleado(self):
        if not self.usuario_actual:
            return []
        rol = str(self.usuario_actual.get("rol", "")).strip().lower()
        num_emp = str(self.usuario_actual.get("id_usuario", "")).strip()
        nom_completo = f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip().lower()
        es_admin = (rol == "admin" or num_emp.lower() == "admin")

        todos = self._sheet_leer("Inventariable")
        lista = []
        for item in todos:
            folio_str = str(item.get("folio", "")).strip()
            item["folio"] = folio_str
            item["en_revision_rojo"] = (folio_str in self.folios_en_rojo)
            if es_admin or str(item.get("id_empleado", "")).strip() == num_emp or str(item.get("nombre_encargado", "")).strip().lower() == nom_completo:
                lista.append(item)
        return lista

    def actualizar_ubicacion_inventariable(self, folio: str, nueva_ubicacion: str):
        folio_clean = str(folio).strip()
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        self.folios_en_rojo.discard(folio_clean)

        ok = self._sheet_upsert("Inventariable", "folio", folio_clean, {
            "ubicacion": nueva_ubicacion,
            "ultima_actualizacion": fecha_hoy
        })
        return ok, "Ubicación actualizada." if ok else "Error al guardar."

    def enviar_reporte_inventariable(self, datos_item: dict, comentario: str):
        folio = str(datos_item.get("folio", "")).strip()
        nombre_encargado = datos_item.get("nombre_encargado", "") or f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip()
        id_empleado = str(datos_item.get("id_empleado", "") or self.usuario_actual.get("id_usuario", ""))

        nuevo_reporte = {
            "folio": folio,
            "id_empleado": id_empleado,
            "nombre_encargado": nombre_encargado,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "comentarios": comentario.strip(),
            "validado": False
        }
        ok = self._sheet_insert_auto_id("ReporteInventariable", nuevo_reporte)
        return ok, "Reporte enviado exitosamente." if ok else "Error al enviar reporte."

    # ================= 3. CONSUMIBLES (Pestaña: Consumible) =================
    def obtener_consumibles_movil(self):
        todos = self._sheet_leer("Consumible")
        for it in todos:
            it["id"] = str(it.get("id", ""))
            it["doc_id"] = it["id"]
            it["cantidad"] = self._a_int(it.get("cantidad", 0), 0)
        return todos

    def modificar_cantidad_consumible(self, datos_item: dict, delta: int):
        cantidad_actual = self._a_int(datos_item.get("cantidad", 0), 0)
        nueva_cantidad = max(0, cantidad_actual + delta)
        datos_item["cantidad"] = nueva_cantidad
        id_con = str(datos_item.get("id", "")).strip()

        ok = self._sheet_upsert("Consumible", "id", id_con, {"cantidad": nueva_cantidad})
        return ok, nueva_cantidad

    # ================= 4. ALUMNOS, HORAS, JUSTIFICACIONES Y REPORTES ADMIN =================
    def obtener_alumnos_movil(self):
        usuarios = self._sheet_leer("Usuario")
        estudiantes = self._sheet_leer("Estudiante")
        mapa_est = {str(e.get("id_usuario", "")).strip(): e for e in estudiantes}

        lista = []
        for u in usuarios:
            if str(u.get("rol", "")).strip().lower() == "estudiante":
                id_u = str(u.get("id_usuario", "")).strip()
                info_est = mapa_est.get(id_u, {})
                combinado = dict(u)
                combinado["doc_id"] = id_u
                combinado["nombre_mostrar"] = f"{str(u.get('nombres', '')).strip()} {str(u.get('apellidos', '')).strip()}".strip() or id_u
                combinado["edad"] = self._a_int(info_est.get("edad", 0), 0)
                combinado["direccion"] = str(info_est.get("direccion", ""))
                combinado["fecha_inicio"] = str(info_est.get("fecha_inicio", ""))
                combinado["fecha_fin"] = str(info_est.get("fecha_fin", ""))
                combinado["cantidad_horas"] = self._a_int(info_est.get("cantidad_horas", 500), 500)
                combinado["nombre_escuela"] = str(info_est.get("nombre_escuela", ""))
                lista.append(combinado)
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
        id_est = str(datos_alumno.get("id_usuario") or datos_alumno.get("doc_id") or datos_alumno.get("usuario")).strip()

        # Refrescar horas restantes actuales desde la pestaña 'Estudiante'
        for es in self._sheet_leer("Estudiante"):
            if str(es.get("id_usuario", "")).strip() == id_est:
                if es.get("cantidad_horas") != "":
                    datos_alumno["cantidad_horas"] = self._a_int(es.get("cantidad_horas", 500), 500)
                break

        todos_horas = self._sheet_leer("ControlHoras")
        lista = []
        for d in todos_horas:
            if str(d.get("id_estudiante", "")).strip() == id_est:
                horas = self._a_int(d.get("horas_calculadas", 0), 0)
                if horas <= 0:
                    horas = self._calcular_horas_dia(d.get("hora_entrada", ""), d.get("hora_salida", ""))
                lista.append({
                    "doc_id": str(d.get("id", "")),
                    "id": str(d.get("id", "")),
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

        id_hora = str(reg_hora.get("id") or reg_hora.get("doc_id", "")).strip()
        if not id_hora:
            return False, "No se encontró el identificador de este registro."

        ok = self._sheet_eliminar("ControlHoras", "id", id_hora)
        return ok, "Registro de horas eliminado correctamente." if ok else "Error al eliminar en Google Sheets."

    def agregar_horas_estudiante(self, datos_alumno: dict, hora_entrada: str, hora_salida: str):
        id_est = str(datos_alumno.get("id_usuario") or datos_alumno.get("doc_id") or datos_alumno.get("usuario")).strip()
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        horas_calc = self._calcular_horas_dia(hora_entrada, hora_salida)

        nuevo_registro = {
            "id_estudiante": id_est,
            "hora_entrada": hora_entrada.strip(),
            "hora_salida": hora_salida.strip(),
            "fecha": fecha_hoy,
            "horas_calculadas": horas_calc,
            "validado": False
        }
        ok = self._sheet_insert_auto_id("ControlHoras", nuevo_registro)
        return ok, f"Horas registradas ({horas_calc} hrs)." if ok else "Error al guardar horas."

    def enviar_justificacion_estudiante(self, datos_alumno: dict, fecha: str, justificacion: str):
        id_est = str(datos_alumno.get("id_usuario") or datos_alumno.get("doc_id") or datos_alumno.get("usuario")).strip()

        nueva_just = {
            "id_estudiante": id_est,
            "fecha": fecha.strip(),
            "descripcion_justificacion": justificacion.strip(),
            "validado": False
        }
        ok = self._sheet_insert_auto_id("ControlJustificaciones", nueva_just)
        return ok, "Justificación enviada exitosamente." if ok else "Error al enviar justificación."

    def obtener_lista_empleados_movil(self):
        todos = self._sheet_leer("Usuario")
        lista = []
        for d in todos:
            if str(d.get("rol", "")).strip().lower() in ["empleado", "admin"]:
                d["numero_empleado"] = str(d.get("id_usuario", "")).strip()
                d["nombre_completo"] = f"{str(d.get('nombres', '')).strip()} {str(d.get('apellidos', '')).strip()}".strip() or d["numero_empleado"]
                lista.append(d)
        return lista

    def obtener_inventario_por_empleado(self, tipo_inventario: str, nombre_empleado="Todos", id_empleado=""):
        hoja = "Inventariable" if tipo_inventario.lower() == "inventariables" else "NoInventariable"
        todos = self._sheet_leer(hoja)

        if nombre_empleado == "Todos":
            return todos

        nom_norm = nombre_empleado.strip().lower()
        return [
            it for it in todos
            if (id_empleado and str(it.get("id_empleado", "")).strip() == str(id_empleado).strip())
            or str(it.get("nombre_encargado", "")).strip().lower() == nom_norm
        ]