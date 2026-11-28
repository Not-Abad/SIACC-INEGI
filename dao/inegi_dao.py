import os
import mysql.connector

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from config import db as db_config
except ImportError:
    db_config = None


DEFAULT_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3307)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "admin"),
    "database": os.getenv("DB_NAME", "base_inegi_correccion_final"),
}


class ProcedimientoError(Exception):
    """Error controlado devuelto por un SP mediante estado_operacion = 'ERROR' o 'SIN_RESULTADOS'."""

    def __init__(self, detalle, codigo_http=400):
        super().__init__(detalle.get("mensaje", "Error en procedimiento almacenado"))
        self.detalle = detalle
        self.codigo_http = codigo_http


class InegiDAO:
    CONSULTAS = {
        "entidades": """
            SELECT cve_ent, nombre_entidad
            FROM entidad
            ORDER BY cve_ent
        """,
        "tipos_vialidad": """
            SELECT id_tipo_vialidad, nombre_tipo_vialidad
            FROM tipo_vialidad
            ORDER BY id_tipo_vialidad
        """,
        "asentamientos": """
            SELECT id_asentamiento, tipo_asentamiento
            FROM asentamiento
            ORDER BY id_asentamiento
            LIMIT 200
        """,
        "detalles_vialidad": """
            SELECT
                dv.id_detalle_vialidad,
                dv.id_direccion,
                dv.id_tipo_vialidad,
                tv.nombre_tipo_vialidad,
                dv.nombre_vialidad
            FROM detalle_vialidad dv
            LEFT JOIN tipo_vialidad tv
                ON dv.id_tipo_vialidad = tv.id_tipo_vialidad
            ORDER BY dv.id_detalle_vialidad
            LIMIT 200
        """,
        "actividades": """
            SELECT codigo_actividad, nombre_actividad
            FROM actividad
            ORDER BY codigo_actividad
            LIMIT 200
        """,
        "establecimientos": """
            SELECT *
            FROM vw_establecimientos_completo
            LIMIT 200
        """,
    }

    RANGOS = {
        "municipios": """
            SELECT cve_ent, cve_mun, nombre_municipio
            FROM municipio
            WHERE cve_mun BETWEEN %s AND %s
            ORDER BY cve_mun
        """,
        "localidades": """
            SELECT id_localidad, cve_ent, cve_mun, cve_loc, nombre_localidad
            FROM localidad
            WHERE cve_loc BETWEEN %s AND %s
            ORDER BY cve_loc
            LIMIT 200
        """,
    }

    # =========================================================================
    # REGISTRO ESTANDARIZADO DE PROCEDIMIENTOS ALMACENADOS
    # Cada entrada queda expuesta automáticamente en: /api/sp/<clave>
    # =========================================================================
    PROCEDIMIENTOS = {
        # --- Procedimientos de Jesús Abad (database/procedimientos/01_abad_procedimientos.sql) ---
        "informacion_establecimiento": {
            "sp": "sp_informacion_establecimiento",
            "metodo": "GET",
            "params": ["id_establecimiento"],
            "opcionales": [],
            "descripcion": "Consulta ficha general y ubicación completa de un establecimiento por ID.",
        },
        "insertar_detalle_vialidad": {
            "sp": "sp_insetar_detalle_vialidad",
            "metodo": "POST",
            "params": ["id_direccion", "id_tipo_vialidad", "nombre_vialidad"],
            "opcionales": [],
            "descripcion": "Inserta un detalle de vialidad validando dirección y tipo de vialidad.",
        },
        "insertar_localidad": {
            "sp": "sp_insertar_localidad",
            "metodo": "POST",
            "params": ["nombre_entidad", "nombre_municipio", "nombre_localidad", "cve_loc"],
            "opcionales": [],
            "descripcion": "Inserta una localidad validando entidad, municipio y clave cve_loc.",
        },

        # --- 15 espacios reservados para los compañeros del equipo ---
        "sp_companero_01": {"sp": "sp_pendiente_01", "metodo": "GET", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_02": {"sp": "sp_pendiente_02", "metodo": "GET", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_03": {"sp": "sp_pendiente_03", "metodo": "GET", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_04": {"sp": "sp_pendiente_04", "metodo": "GET", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_05": {"sp": "sp_pendiente_05", "metodo": "GET", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_06": {"sp": "sp_pendiente_06", "metodo": "POST", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_07": {"sp": "sp_pendiente_07", "metodo": "POST", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_08": {"sp": "sp_pendiente_08", "metodo": "POST", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_09": {"sp": "sp_pendiente_09", "metodo": "POST", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_10": {"sp": "sp_pendiente_10", "metodo": "POST", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_11": {"sp": "sp_pendiente_11", "metodo": "PUT", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_12": {"sp": "sp_pendiente_12", "metodo": "PUT", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_13": {"sp": "sp_pendiente_13", "metodo": "PUT", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_14": {"sp": "sp_pendiente_14", "metodo": "DELETE", "params": [], "opcionales": [], "descripcion": "Disponible"},
        "sp_companero_15": {"sp": "sp_pendiente_15", "metodo": "DELETE", "params": [], "opcionales": [], "descripcion": "Disponible"},
    }

    def __init__(self, config=None):
        self.config = config

    def _conectar(self):
        if self.config:
            return mysql.connector.connect(**self.config)

        if db_config is not None:
            for fn_name in ("get_connection", "conectar", "create_connection"):
                fn = getattr(db_config, fn_name, None)
                if callable(fn):
                    return fn()
            for cfg_name in ("DB_CONFIG", "CONFIG"):
                cfg = getattr(db_config, cfg_name, None)
                if isinstance(cfg, dict):
                    return mysql.connector.connect(**cfg)

        return mysql.connector.connect(**DEFAULT_CONFIG)

    # -------------------------------------------------------------------------
    # EJECUCIÓN SQL Y PROCEDIMIENTOS ALMACENADOS
    # -------------------------------------------------------------------------
    def ejecutar_sql(self, sql, params=()):
        con = self._conectar()
        cur = con.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            filas = cur.fetchall() if cur.with_rows else []
            con.commit()
            return filas
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def _interpretar_respuesta_sp(self, filas):
        if not filas:
            return {"estado_operacion": "EXITO", "mensaje": "Operación realizada correctamente"}

        primera = filas[0]
        if "estado_operacion" in primera:
            estado = str(primera["estado_operacion"]).upper()
            if estado == "ERROR":
                raise ProcedimientoError(primera, codigo_http=400)
            if estado == "SIN_RESULTADOS":
                raise ProcedimientoError(primera, codigo_http=404)

            datos_extra = {
                k: v for k, v in primera.items()
                if k not in ("estado_operacion", "mensaje")
            }
            return {
                "estado_operacion": estado,
                "mensaje": primera.get("mensaje", "Operación realizada correctamente"),
                "datos": datos_extra,
            }

        return filas

    def llamar_sp(self, nombre_sp, args=()):
        con = self._conectar()
        cur = con.cursor(dictionary=True)
        try:
            cur.callproc(nombre_sp, list(args))
            conjuntos = [resultado.fetchall() for resultado in cur.stored_results()]
            con.commit()
            filas = conjuntos[0] if conjuntos else []
            return self._interpretar_respuesta_sp(filas)
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    # -------------------------------------------------------------------------
    # DESPACHADOR ESTANDARIZADO PARA /api/sp/<clave>
    # -------------------------------------------------------------------------
    def catalogo_sp(self):
        return [
            {
                "clave": clave,
                "endpoint": f"/api/sp/{clave}",
                "sp": cfg["sp"],
                "metodo": cfg["metodo"],
                "params": cfg["params"],
                "opcionales": cfg.get("opcionales", []),
                "descripcion": cfg.get("descripcion", ""),
            }
            for clave, cfg in self.PROCEDIMIENTOS.items()
        ]

    def ejecutar_sp(self, clave, metodo_http, payload):
        if clave not in self.PROCEDIMIENTOS:
            raise KeyError(f"El procedimiento '{clave}' no está registrado en InegiDAO.")

        cfg = self.PROCEDIMIENTOS[clave]
        metodo_esperado = cfg["metodo"].upper()
        if metodo_http.upper() != metodo_esperado:
            raise PermissionError(
                f"Método {metodo_http} no permitido para '{clave}'. Usa {metodo_esperado}."
            )

        opcionales = set(cfg.get("opcionales", []))
        faltantes = [
            p for p in cfg["params"]
            if p not in opcionales and payload.get(p) in (None, "")
        ]
        if faltantes:
            raise ValueError(f"Faltan parámetros obligatorios: {', '.join(faltantes)}")

        args = [
            None if payload.get(p) in (None, "") else payload.get(p)
            for p in cfg["params"]
        ]
        return self.llamar_sp(cfg["sp"], args)

    # -------------------------------------------------------------------------
    # CONSULTAS Y OPERACIONES BASE DEL FRONTEND INYECTADO
    # -------------------------------------------------------------------------
    def listar_recurso(self, recurso, q="", desde="", hasta=""):
        if recurso in self.RANGOS:
            largo = 3 if recurso == "municipios" else 4
            desde_norm = desde.strip().ljust(largo, "0")
            hasta_norm = (hasta.strip() or desde.strip()).ljust(largo, "9")
            return self.ejecutar_sql(self.RANGOS[recurso], (desde_norm, hasta_norm))

        if recurso == "establecimientos" and q.strip():
            texto = f"%{q.strip()}%"
            return self.ejecutar_sql(
                """
                SELECT *
                FROM vw_establecimientos_completo
                WHERE nombre_establecimiento LIKE %s
                   OR clee LIKE %s
                LIMIT 200
                """,
                (texto, texto),
            )

        if recurso == "actividades" and q.strip():
            texto = f"%{q.strip()}%"
            return self.ejecutar_sql(
                """
                SELECT codigo_actividad, nombre_actividad
                FROM actividad
                WHERE codigo_actividad LIKE %s
                   OR nombre_actividad LIKE %s
                ORDER BY codigo_actividad
                LIMIT 200
                """,
                (texto, texto),
            )

        if recurso not in self.CONSULTAS:
            raise KeyError(f"Recurso '{recurso}' no encontrado")

        return self.ejecutar_sql(self.CONSULTAS[recurso])

    def crear_tipo_vialidad(self, nombre_tipo_vialidad):
        self.ejecutar_sql(
            "INSERT INTO tipo_vialidad (nombre_tipo_vialidad) VALUES (%s)",
            (nombre_tipo_vialidad.strip(),),
        )
        return {"mensaje": "Tipo de vialidad guardado"}

    def crear_asentamiento(self, tipo_asentamiento, id_asentamiento=None):
        con = self._conectar()
        cur = con.cursor(dictionary=True)
        try:
            if id_asentamiento in (None, ""):
                cur.execute("SELECT COALESCE(MAX(id_asentamiento), 0) + 1 AS siguiente FROM asentamiento")
                id_asentamiento = cur.fetchone()["siguiente"]

            cur.execute(
                "INSERT INTO asentamiento (id_asentamiento, tipo_asentamiento) VALUES (%s, %s)",
                (int(id_asentamiento), tipo_asentamiento.strip().upper()),
            )
            con.commit()
            return {"mensaje": "Asentamiento guardado"}
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def crear_detalle_vialidad(
        self, id_direccion, id_tipo_vialidad=None, nombre_vialidad=None, id_detalle_vialidad=None
    ):
        con = self._conectar()
        cur = con.cursor(dictionary=True)
        try:
            if id_detalle_vialidad in (None, ""):
                cur.execute(
                    "SELECT COALESCE(MAX(id_detalle_vialidad), 0) + 1 AS siguiente FROM detalle_vialidad"
                )
                id_detalle_vialidad = cur.fetchone()["siguiente"]

            id_tipo = int(id_tipo_vialidad) if id_tipo_vialidad not in (None, "") else None
            nombre = (
                nombre_vialidad.strip()
                if isinstance(nombre_vialidad, str) and nombre_vialidad.strip()
                else None
            )

            cur.execute(
                """
                INSERT INTO detalle_vialidad
                    (id_detalle_vialidad, id_direccion, id_tipo_vialidad, nombre_vialidad)
                VALUES (%s, %s, %s, %s)
                """,
                (int(id_detalle_vialidad), int(id_direccion), id_tipo, nombre),
            )
            con.commit()
            return {"mensaje": "Detalle de vialidad guardado"}
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def alta_actividad(self, codigo_actividad, nombre_actividad):
        return self.llamar_sp("sp_actividad_alta", [codigo_actividad.strip(), nombre_actividad.strip()])

    def actualizar_actividad(self, codigo_actividad, nombre_actividad):
        return self.llamar_sp(
            "sp_actividad_actualizar", [codigo_actividad.strip(), nombre_actividad.strip()]
        )

    def alta_direccion(self, id_localidad, id_asentamiento, codigo_postal, numero_exterior):
        return self.llamar_sp(
            "sp_direccion_alta", [id_localidad, id_asentamiento, codigo_postal, numero_exterior]
        )

    def alta_establecimiento(
        self,
        clee,
        nombre_establecimiento,
        razon_social,
        codigo_actividad,
        id_direccion,
        tipo_unidad_economica,
    ):
        return self.llamar_sp(
            "sp_establecimiento_alta",
            [
                clee,
                nombre_establecimiento,
                razon_social,
                codigo_actividad,
                id_direccion,
                tipo_unidad_economica,
            ],
        )

    def actualizar_establecimiento(
        self, id_establecimiento, nombre_establecimiento, razon_social, telefono
    ):
        return self.llamar_sp(
            "sp_establecimiento_actualizar",
            [id_establecimiento, nombre_establecimiento, razon_social, telefono],
        )

    def baja_establecimiento(self, id_establecimiento):
        return self.llamar_sp("sp_establecimiento_baja", [id_establecimiento])