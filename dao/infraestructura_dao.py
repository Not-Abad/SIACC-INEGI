"""DAO del Modulo 2: Infraestructura Urbana.

Tablas: tipo_vialidad, asentamiento, detalle_vialidad.
- Altas, modificaciones y bajas se hacen SOLO con los procedimientos
  almacenados sp_m2_* (database/modulo2_infraestructura.sql), que son
  transaccionales y validan existencia de llaves foraneas.
- Las consultas usan SELECT parametrizados (%s).
- Ningun SQL vive en views/.
"""
from mysql.connector import Error

from config.db import conectar, desconectar

LIMITE_RESULTADOS = 200


class InfraestructuraError(Exception):
    """Error de negocio o de base de datos con un mensaje legible."""


def _mensaje(error):
    # Los SIGNAL de los procedimientos llegan con errno 1644 y el texto en .msg
    return getattr(error, "msg", None) or str(error)


def _consultar(sql, params=()):
    conn = cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    except Error as e:
        raise InfraestructuraError(_mensaje(e)) from e
    finally:
        desconectar(conn, cursor)


def _llamar(procedimiento, args):
    """Ejecuta un procedimiento y devuelve los argumentos (incluye los OUT)."""
    conn = cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        resultado = cursor.callproc(procedimiento, args)
        conn.commit()
        return resultado
    except Error as e:
        if conn is not None and conn.is_connected():
            conn.rollback()
        raise InfraestructuraError(_mensaje(e)) from e
    finally:
        desconectar(conn, cursor)


# ----------------------------- TIPO_VIALIDAD -----------------------------
def listar_tipos_vialidad(texto=""):
    return _consultar(
        "SELECT id_tipo_vialidad, nombre_tipo_vialidad "
        "FROM tipo_vialidad WHERE nombre_tipo_vialidad LIKE %s "
        "ORDER BY id_tipo_vialidad",
        (f"%{texto.strip()}%",),
    )


def alta_tipo_vialidad(nombre):
    return _llamar("sp_m2_tipo_vialidad_alta", (nombre, 0))[1]


def modificar_tipo_vialidad(id_tipo, nombre):
    _llamar("sp_m2_tipo_vialidad_modificar", (id_tipo, nombre))


def eliminar_tipo_vialidad(id_tipo):
    _llamar("sp_m2_tipo_vialidad_eliminar", (id_tipo,))


# ------------------------------ ASENTAMIENTO -----------------------------
def listar_asentamientos(texto=""):
    return _consultar(
        "SELECT id_asentamiento, tipo_asentamiento "
        "FROM asentamiento WHERE tipo_asentamiento LIKE %s "
        "ORDER BY id_asentamiento",
        (f"%{texto.strip()}%",),
    )


def alta_asentamiento(tipo):
    return _llamar("sp_m2_asentamiento_alta", (tipo, 0))[1]


def modificar_asentamiento(id_asentamiento, tipo):
    _llamar("sp_m2_asentamiento_modificar", (id_asentamiento, tipo))


def eliminar_asentamiento(id_asentamiento):
    _llamar("sp_m2_asentamiento_eliminar", (id_asentamiento,))


# ---------------------------- DETALLE_VIALIDAD ---------------------------
_SQL_VIALIDADES = (
    "SELECT dv.id_detalle_vialidad, dv.id_direccion, "
    "       IFNULL(tv.nombre_tipo_vialidad, '(sin tipo)') AS tipo, "
    "       dv.nombre_vialidad, a.tipo_asentamiento, d.codigo_postal, "
    "       l.nombre_localidad, m.nombre_municipio, e.nombre_entidad "
    "FROM detalle_vialidad dv "
    "JOIN direccion d     ON d.id_direccion = dv.id_direccion "
    "JOIN asentamiento a  ON a.id_asentamiento = d.id_asentamiento "
    "JOIN localidad l     ON l.id_localidad = d.id_localidad "
    "JOIN municipio m     ON m.cve_ent = l.cve_ent AND m.cve_mun = l.cve_mun "
    "JOIN entidad e       ON e.cve_ent = m.cve_ent "
    "LEFT JOIN tipo_vialidad tv ON tv.id_tipo_vialidad = dv.id_tipo_vialidad "
)


def buscar_vialidades(nombre="", id_direccion=None):
    """Busca por nombre (LIKE) y/o id de direccion. Maximo 200 filas."""
    condiciones, params = [], []
    if nombre.strip():
        condiciones.append("dv.nombre_vialidad LIKE %s")
        params.append(f"%{nombre.strip()}%")
    if id_direccion is not None:
        condiciones.append("dv.id_direccion = %s")
        params.append(id_direccion)
    where = ("WHERE " + " AND ".join(condiciones) + " ") if condiciones else ""
    sql = _SQL_VIALIDADES + where + "ORDER BY dv.id_detalle_vialidad DESC LIMIT %s"
    params.append(LIMITE_RESULTADOS)
    return _consultar(sql, tuple(params))


def obtener_vialidad(id_detalle):
    filas = _consultar(
        "SELECT id_detalle_vialidad, id_direccion, id_tipo_vialidad, nombre_vialidad "
        "FROM detalle_vialidad WHERE id_detalle_vialidad = %s",
        (id_detalle,),
    )
    return filas[0] if filas else None


def alta_vialidad(id_direccion, id_tipo, nombre):
    return _llamar("sp_m2_detalle_vialidad_alta", (id_direccion, id_tipo, nombre, 0))[3]


def modificar_vialidad(id_detalle, id_direccion, id_tipo, nombre):
    _llamar("sp_m2_detalle_vialidad_modificar", (id_detalle, id_direccion, id_tipo, nombre))


def eliminar_vialidad(id_detalle):
    _llamar("sp_m2_detalle_vialidad_eliminar", (id_detalle,))


# -------------------------------- BITACORA -------------------------------
def listar_bitacora(limite=100):
    return _consultar(
        "SELECT id_bitacora, tabla, operacion, id_registro, valor_anterior, "
        "       valor_nuevo, usuario, fecha "
        "FROM bitacora_infraestructura ORDER BY id_bitacora DESC LIMIT %s",
        (limite,),
    )
