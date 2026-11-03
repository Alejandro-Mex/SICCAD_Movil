import os
import json
import hashlib
from datetime import datetime
import requests
from config.settings import FIREBASE_PROJECT_ID


class FirebaseMobileClient:
    """
    Cliente Híbrido para SICAD Móvil:
    - En PC (Simulador): Usa firebase_admin o API REST.
    - En Android (.apk): Usa API REST oficial de Firestore (100% compatible con APK).
    """
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(FirebaseMobileClient, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self.project_id = FIREBASE_PROJECT_ID
        self.db_firestore = None

        # Detectar el project_id real desde config/serviceAccountKey.json (si existe)
        posibles_rutas = [
            os.path.join("config", "serviceAccountKey.json"),
            os.path.join("assets", "serviceAccountKey.json"),
            os.path.join("..", "SICCAD_Desktop", "config", "serviceAccountKey.json"),
        ]
        ruta_json = next((r for r in posibles_rutas if os.path.exists(r)), None)

        if ruta_json:
            try:
                with open(ruta_json, "r", encoding="utf-8") as f:
                    datos_key = json.load(f)
                    if datos_key.get("project_id"):
                        self.project_id = datos_key["project_id"]
            except Exception:
                pass

            # Intentar cargar firebase_admin si estamos en PC
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore
                if not firebase_admin._apps:
                    cred = credentials.Certificate(ruta_json)
                    firebase_admin.initialize_app(cred)
                self.db_firestore = firestore.client()
            except Exception:
                self.db_firestore = None

        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"
        self.usuario_actual = None

    @staticmethod
    def encriptar_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _desempaquetar_firestore(doc_json: dict) -> dict:
        fields = doc_json.get("fields", {})
        resultado = {}
        for k, v in fields.items():
            if "stringValue" in v:
                resultado[k] = v["stringValue"]
            elif "integerValue" in v:
                resultado[k] = int(v["integerValue"])
            elif "booleanValue" in v:
                resultado[k] = bool(v["booleanValue"])
        if "name" in doc_json:
            resultado["doc_id"] = doc_json["name"].split("/")[-1]
        return resultado

    @staticmethod
    def _empaquetar_firestore(datos: dict) -> dict:
        fields = {}
        for k, v in datos.items():
            if isinstance(v, bool):
                fields[k] = {"booleanValue": v}
            elif isinstance(v, int):
                fields[k] = {"integerValue": str(v)}
            elif v is not None:
                fields[k] = {"stringValue": str(v)}
        return {"fields": fields}

    # ================= LOGIN DUAL (EMPLEADO Y ESTUDIANTE) =================
    def validar_login_movil_empleado(self, usuario: str, password: str):
        usuario = str(usuario).strip()
        password = str(password).strip()
        pass_hash = self.encriptar_password(password)

        # A) Si estamos en PC con firebase_admin:
        if self.db_firestore is not None:
            try:
                doc_id = usuario.replace("/", "_")
                doc = self.db_firestore.collection("usuarios").document(doc_id).get()
                datos = doc.to_dict() if doc.exists else None
                if datos:
                    datos["doc_id"] = doc.id
                else:
                    q1 = list(self.db_firestore.collection("usuarios").where("usuario", "==", usuario).limit(1).stream())
                    if q1:
                        datos = q1[0].to_dict()
                        datos["doc_id"] = q1[0].id
                    else:
                        q2 = list(self.db_firestore.collection("usuarios").where("numero_empleado", "==", usuario).limit(1).stream())
                        if q2:
                            datos = q2[0].to_dict()
                            datos["doc_id"] = q2[0].id

                if not datos or datos.get("contrasena") not in [pass_hash, password]:
                    return False, "Usuario o contraseña incorrectos."

                self.usuario_actual = datos
                return True, datos
            except Exception as e:
                return False, f"Error de conexión: {e}"

        # B) Si estamos en el celular Android (.apk) vía REST:
        try:
            resp = requests.get(f"{self.base_url}/usuarios", timeout=10)
            if resp.status_code == 200:
                for doc in resp.json().get("documents", []):
                    d = self._desempaquetar_firestore(doc)
                    id_doc = d.get("doc_id", "")
                    if usuario in [id_doc, str(d.get("numero_empleado", "")), str(d.get("usuario", ""))]:
                        if d.get("contrasena") in [pass_hash, password]:
                            self.usuario_actual = d
                            return True, d
            return False, "Usuario o contraseña incorrectos."
        except Exception as e:
            return False, f"Verifica tu conexión a internet: {e}"

    # ================= 1. NO INVENTARIABLES =================
    def obtener_no_inventariables_empleado(self):
        if not self.usuario_actual:
            return []
        num_emp = str(self.usuario_actual.get("numero_empleado", "")).strip()
        nom_completo = f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip().lower()

        lista = []
        if self.db_firestore is not None:
            for doc in self.db_firestore.collection("no_inventariables").stream():
                item = doc.to_dict()
                item["clave"] = item.get("clave", doc.id)
                item["en_revision_rojo"] = False
                if num_emp.lower() == "admin" or str(item.get("id_empleado", "")) == num_emp or item.get("nombre_encargado", "").strip().lower() == nom_completo:
                    lista.append(item)
            return lista

        try:
            resp = requests.get(f"{self.base_url}/no_inventariables", timeout=10)
            if resp.status_code == 200:
                for doc in resp.json().get("documents", []):
                    item = self._desempaquetar_firestore(doc)
                    item["en_revision_rojo"] = False
                    if num_emp.lower() == "admin" or str(item.get("id_empleado", "")) == num_emp or item.get("nombre_encargado", "").strip().lower() == nom_completo:
                        lista.append(item)
        except Exception:
            pass
        return lista

    def actualizar_ubicacion_no_inventariable(self, clave: str, nueva_ubicacion: str):
        doc_id = str(clave).strip().replace("/", "_")
        if self.db_firestore is not None:
            self.db_firestore.collection("no_inventariables").document(doc_id).update({"ubicacion": nueva_ubicacion})
            return True, "Ubicación actualizada."

        url = f"{self.base_url}/no_inventariables/{doc_id}?updateMask.fieldPaths=ubicacion"
        requests.patch(url, json=self._empaquetar_firestore({"ubicacion": nueva_ubicacion}), timeout=10)
        return True, "Ubicación actualizada."

    def enviar_reporte_no_inventariable(self, datos_item: dict, comentario: str):
        clave = str(datos_item.get("clave", "")).strip()
        doc_id = clave.replace("/", "_")
        nombre_encargado = datos_item.get("nombre_encargado", "") or f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip()
        id_empleado = str(datos_item.get("id_empleado", "") or self.usuario_actual.get("numero_empleado", ""))

        nuevo_reporte = {
            "id": str(int(datetime.now().timestamp()) % 10000),
            "clave": clave,
            "comentarios": comentario.strip(),
            "id_empleado": id_empleado,
            "nombre_encargado": nombre_encargado,
            "tipo_bien": "no_inventariable",
            "validado": False
        }

        if self.db_firestore is not None:
            col = self.db_firestore.collection("no_inventariables").document(doc_id).collection("reportes")
            nuevo_reporte["id"] = str(len(list(col.stream())) + 1)
            col.add(nuevo_reporte)
            return True, "Reporte enviado exitosamente."

        requests.post(f"{self.base_url}/no_inventariables/{doc_id}/reportes", json=self._empaquetar_firestore(nuevo_reporte), timeout=10)
        return True, "Reporte enviado exitosamente."

    # ================= 2. INVENTARIABLES =================
    def obtener_inventariables_empleado(self):
        if not self.usuario_actual:
            return []
        num_emp = str(self.usuario_actual.get("numero_empleado", "")).strip()
        nom_completo = f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip().lower()

        lista = []
        if self.db_firestore is not None:
            for doc in self.db_firestore.collection("inventariables").stream():
                item = doc.to_dict()
                item["folio"] = str(item.get("folio", doc.id))
                item["en_revision_rojo"] = False
                if num_emp.lower() == "admin" or str(item.get("id_empleado", "")) == num_emp or item.get("nombre_encargado", "").strip().lower() == nom_completo:
                    lista.append(item)
            return lista

        try:
            resp = requests.get(f"{self.base_url}/inventariables", timeout=10)
            if resp.status_code == 200:
                for doc in resp.json().get("documents", []):
                    item = self._desempaquetar_firestore(doc)
                    item["en_revision_rojo"] = False
                    if num_emp.lower() == "admin" or str(item.get("id_empleado", "")) == num_emp or item.get("nombre_encargado", "").strip().lower() == nom_completo:
                        lista.append(item)
        except Exception:
            pass
        return lista

    def actualizar_ubicacion_inventariable(self, folio: str, nueva_ubicacion: str):
        doc_id = str(folio).strip().replace("/", "_")
        if self.db_firestore is not None:
            self.db_firestore.collection("inventariables").document(doc_id).update({"ubicacion": nueva_ubicacion})
            return True, "Ubicación actualizada."

        url = f"{self.base_url}/inventariables/{doc_id}?updateMask.fieldPaths=ubicacion"
        requests.patch(url, json=self._empaquetar_firestore({"ubicacion": nueva_ubicacion}), timeout=10)
        return True, "Ubicación actualizada."

    def enviar_reporte_inventariable(self, datos_item: dict, comentario: str):
        folio = str(datos_item.get("folio", "")).strip()
        doc_id = folio.replace("/", "_")
        nombre_encargado = datos_item.get("nombre_encargado", "") or f"{self.usuario_actual.get('nombres', '')} {self.usuario_actual.get('apellidos', '')}".strip()
        id_empleado = str(datos_item.get("id_empleado", "") or self.usuario_actual.get("numero_empleado", ""))

        nuevo_reporte = {
            "id": str(int(datetime.now().timestamp()) % 10000),
            "folio": folio,
            "comentarios": comentario.strip(),
            "id_empleado": id_empleado,
            "nombre_encargado": nombre_encargado,
            "tipo_bien": "inventariable",
            "validado": False
        }

        if self.db_firestore is not None:
            col = self.db_firestore.collection("inventariables").document(doc_id).collection("reportes")
            nuevo_reporte["id"] = str(len(list(col.stream())) + 1)
            col.add(nuevo_reporte)
            return True, "Reporte enviado exitosamente."

        requests.post(f"{self.base_url}/inventariables/{doc_id}/reportes", json=self._empaquetar_firestore(nuevo_reporte), timeout=10)
        return True, "Reporte enviado exitosamente."

    # ================= 3. CONSUMIBLES =================
    def obtener_consumibles_movil(self):
        lista = []
        if self.db_firestore is not None:
            for doc in self.db_firestore.collection("consumibles").stream():
                item = doc.to_dict()
                item["id"] = str(item.get("id", doc.id))
                item["doc_id"] = doc.id
                lista.append(item)
            return lista

        try:
            resp = requests.get(f"{self.base_url}/consumibles", timeout=10)
            if resp.status_code == 200:
                for doc in resp.json().get("documents", []):
                    lista.append(self._desempaquetar_firestore(doc))
        except Exception:
            pass
        return lista

    def modificar_cantidad_consumible(self, datos_item: dict, delta: int):
        cantidad_actual = int(datos_item.get("cantidad", 0))
        nueva_cantidad = max(0, cantidad_actual + delta)
        datos_item["cantidad"] = nueva_cantidad
        doc_id = str(datos_item.get("doc_id") or datos_item.get("id"))

        if self.db_firestore is not None:
            self.db_firestore.collection("consumibles").document(doc_id).update({"cantidad": nueva_cantidad})
            return True, nueva_cantidad

        url = f"{self.base_url}/consumibles/{doc_id}?updateMask.fieldPaths=cantidad"
        requests.patch(url, json=self._empaquetar_firestore({"cantidad": nueva_cantidad}), timeout=10)
        return True, nueva_cantidad

    # ================= 4. ALUMNOS Y SERVICIO SOCIAL =================
    def obtener_alumnos_movil(self):
        lista = []
        if self.db_firestore is not None:
            for doc in self.db_firestore.collection("usuarios").where("rol", "==", "estudiante").stream():
                item = doc.to_dict()
                item["id_usuario"] = str(item.get("id_usuario", doc.id))
                item["doc_id"] = doc.id
                item["nombre_mostrar"] = f"{item.get('nombres', '').strip()} {item.get('apellidos', '').strip()}".strip() or doc.id
                lista.append(item)
            return lista

        try:
            resp = requests.get(f"{self.base_url}/usuarios", timeout=10)
            if resp.status_code == 200:
                for doc in resp.json().get("documents", []):
                    item = self._desempaquetar_firestore(doc)
                    if item.get("rol") == "estudiante":
                        item["nombre_mostrar"] = f"{item.get('nombres', '').strip()} {item.get('apellidos', '').strip()}".strip()
                        lista.append(item)
        except Exception:
            pass
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
        doc_id = str(datos_alumno.get("doc_id") or datos_alumno.get("id_usuario") or datos_alumno.get("usuario")).replace("/", "_")
        lista = []

        if self.db_firestore is not None:
            doc_al = self.db_firestore.collection("usuarios").document(doc_id).get()
            if doc_al.exists and "cantidad_horas" in doc_al.to_dict():
                datos_alumno["cantidad_horas"] = doc_al.to_dict()["cantidad_horas"]

            for doc in self.db_firestore.collection("usuarios").document(doc_id).collection("control_horas").stream():
                d = doc.to_dict()
                horas = d.get("horas_calculadas") or self._calcular_horas_dia(d.get("hora_entrada", ""), d.get("hora_salida", ""))
                lista.append({"fecha": d.get("fecha", ""), "horas": horas, "validado": bool(d.get("validado", False))})
            return lista

        try:
            r_al = requests.get(f"{self.base_url}/usuarios/{doc_id}", timeout=10)
            if r_al.status_code == 200:
                d_al = self._desempaquetar_firestore(r_al.json())
                if "cantidad_horas" in d_al:
                    datos_alumno["cantidad_horas"] = d_al["cantidad_horas"]

            resp = requests.get(f"{self.base_url}/usuarios/{doc_id}/control_horas", timeout=10)
            if resp.status_code == 200:
                for doc in resp.json().get("documents", []):
                    d = self._desempaquetar_firestore(doc)
                    horas = d.get("horas_calculadas") or self._calcular_horas_dia(d.get("hora_entrada", ""), d.get("hora_salida", ""))
                    lista.append({"fecha": d.get("fecha", ""), "horas": horas, "validado": bool(d.get("validado", False))})
        except Exception:
            pass
        return lista

    def enviar_justificacion_estudiante(self, datos_alumno: dict, fecha: str, justificacion: str):
        doc_id = str(datos_alumno.get("doc_id") or datos_alumno.get("id_usuario") or datos_alumno.get("usuario")).replace("/", "_")
        nueva_just = {
            "id": str(int(datetime.now().timestamp()) % 10000),
            "fecha": fecha.strip(),
            "descripcion_justificacion": justificacion.strip(),
            "validado": False
        }

        if self.db_firestore is not None:
            col = self.db_firestore.collection("usuarios").document(doc_id).collection("control_justificaciones")
            nueva_just["id"] = str(len(list(col.stream())) + 1)
            col.add(nueva_just)
            return True, "Justificación enviada exitosamente."

        requests.post(f"{self.base_url}/usuarios/{doc_id}/control_justificaciones", json=self._empaquetar_firestore(nueva_just), timeout=10)
        return True, "Justificación enviada exitosamente."

    def agregar_horas_estudiante(self, datos_alumno: dict, hora_entrada: str, hora_salida: str):
        doc_id = str(datos_alumno.get("doc_id") or datos_alumno.get("id_usuario") or datos_alumno.get("usuario")).replace("/", "_")
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        horas_calc = self._calcular_horas_dia(hora_entrada, hora_salida)

        nuevo_registro = {
            "id": str(int(datetime.now().timestamp()) % 10000),
            "hora_entrada": hora_entrada.strip(),
            "hora_salida": hora_salida.strip(),
            "fecha": fecha_hoy,
            "horas_calculadas": horas_calc,
            "validado": False
        }

        if self.db_firestore is not None:
            col = self.db_firestore.collection("usuarios").document(doc_id).collection("control_horas")
            nuevo_registro["id"] = str(len(list(col.stream())) + 1)
            col.add(nuevo_registro)
            return True, f"Horas registradas ({horas_calc} hrs)."

        requests.post(f"{self.base_url}/usuarios/{doc_id}/control_horas", json=self._empaquetar_firestore(nuevo_registro), timeout=10)
        return True, f"Horas registradas ({horas_calc} hrs)."