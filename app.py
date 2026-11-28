from flask import Flask, jsonify, redirect, render_template, request
from dao.inegi_dao import InegiDAO, ProcedimientoError

app = Flask(__name__)
dao = InegiDAO()


def datos_json():
    return request.get_json(silent=True) or {}


def validar_campos(datos, requeridos):
    faltantes = [campo for campo in requeridos if datos.get(campo) in (None, "")]
    if faltantes:
        return jsonify({"mensaje": f"Faltan campos obligatorios: {', '.join(faltantes)}"}), 400
    return None


@app.errorhandler(ProcedimientoError)
def error_procedimiento(e):
    return jsonify(e.detalle), e.codigo_http


@app.errorhandler(KeyError)
def error_no_encontrado(e):
    return jsonify({"estado_operacion": "ERROR", "mensaje": str(e).strip("'")}), 404


@app.errorhandler(ValueError)
def error_validacion(e):
    return jsonify({"estado_operacion": "ERROR", "mensaje": str(e)}), 400


@app.errorhandler(PermissionError)
def error_metodo(e):
    return jsonify({"estado_operacion": "ERROR", "mensaje": str(e)}), 405


@app.errorhandler(Exception)
def error_general(e):
    return jsonify({"estado_operacion": "ERROR", "mensaje": "Error: " + str(e)}), 500


@app.get("/")
def inicio():
    return render_template("index.html")


@app.get("/procedimientos")
def vista_procedimientos():
    return render_template("procedimientos.html")


@app.get("/procedimientos.html")
def vista_procedimientos_alias():
    return redirect("/procedimientos", code=302)


# -----------------------------------------------------------------------------
# ENDPOINTS DEL FRONTEND PRINCIPAL (templates/index.html)
# -----------------------------------------------------------------------------
@app.get("/api/<recurso>")
def listar(recurso):
    return jsonify(
        dao.listar_recurso(
            recurso=recurso,
            q=request.args.get("q", ""),
            desde=request.args.get("desde", ""),
            hasta=request.args.get("hasta", ""),
        )
    )


@app.post("/api/tipos_vialidad")
def alta_tipo_vialidad():
    d = datos_json()
    error_val = validar_campos(d, ["nombre_tipo_vialidad"])
    if error_val:
        return error_val
    return jsonify(dao.crear_tipo_vialidad(d["nombre_tipo_vialidad"]))


@app.post("/api/asentamientos")
def alta_asentamiento():
    d = datos_json()
    error_val = validar_campos(d, ["tipo_asentamiento"])
    if error_val:
        return error_val
    return jsonify(dao.crear_asentamiento(d["tipo_asentamiento"], d.get("id_asentamiento")))


@app.post("/api/detalles_vialidad")
def alta_detalle_vialidad():
    d = datos_json()
    error_val = validar_campos(d, ["id_direccion"])
    if error_val:
        return error_val
    return jsonify(
        dao.crear_detalle_vialidad(
            id_direccion=d["id_direccion"],
            id_tipo_vialidad=d.get("id_tipo_vialidad"),
            nombre_vialidad=d.get("nombre_vialidad"),
            id_detalle_vialidad=d.get("id_detalle_vialidad"),
        )
    )


@app.post("/api/actividades")
def alta_actividad():
    d = datos_json()
    error_val = validar_campos(d, ["codigo_actividad", "nombre_actividad"])
    if error_val:
        return error_val
    return jsonify(dao.alta_actividad(d["codigo_actividad"], d["nombre_actividad"]))


@app.put("/api/actividades")
def actualizar_actividad():
    d = datos_json()
    error_val = validar_campos(d, ["codigo_actividad", "nombre_actividad"])
    if error_val:
        return error_val
    return jsonify(dao.actualizar_actividad(d["codigo_actividad"], d["nombre_actividad"]))


@app.post("/api/direcciones")
def alta_direccion():
    d = datos_json()
    error_val = validar_campos(
        d, ["id_localidad", "id_asentamiento", "codigo_postal", "numero_exterior"]
    )
    if error_val:
        return error_val
    return jsonify(
        dao.alta_direccion(
            d["id_localidad"],
            d["id_asentamiento"],
            d["codigo_postal"],
            d["numero_exterior"],
        )
    )


@app.post("/api/establecimientos")
def alta_establecimiento():
    d = datos_json()
    error_val = validar_campos(
        d,
        [
            "clee",
            "nombre_establecimiento",
            "razon_social",
            "codigo_actividad",
            "id_direccion",
            "tipo_unidad_economica",
        ],
    )
    if error_val:
        return error_val
    return jsonify(
        dao.alta_establecimiento(
            d["clee"],
            d["nombre_establecimiento"],
            d["razon_social"],
            d["codigo_actividad"],
            d["id_direccion"],
            d["tipo_unidad_economica"],
        )
    )


@app.put("/api/establecimientos")
def actualizar_establecimiento():
    d = datos_json()
    error_val = validar_campos(
        d, ["id_establecimiento", "nombre_establecimiento", "razon_social", "telefono"]
    )
    if error_val:
        return error_val
    return jsonify(
        dao.actualizar_establecimiento(
            d["id_establecimiento"],
            d["nombre_establecimiento"],
            d["razon_social"],
            d["telefono"],
        )
    )


@app.delete("/api/establecimientos")
def baja_establecimiento():
    d = datos_json()
    error_val = validar_campos(d, ["id_establecimiento"])
    if error_val:
        return error_val
    return jsonify(dao.baja_establecimiento(d["id_establecimiento"]))


# -----------------------------------------------------------------------------
# ENDPOINTS ESTANDARIZADOS PARA LOS PROCEDIMIENTOS DE TODO EL EQUIPO
# -----------------------------------------------------------------------------
@app.get("/api/sp")
def listar_procedimientos():
    return jsonify(dao.catalogo_sp())


@app.route("/api/sp/<clave>", methods=["GET", "POST", "PUT", "DELETE"])
def ejecutar_procedimiento(clave):
    payload = request.args.to_dict() if request.method == "GET" else datos_json()
    return jsonify(dao.ejecutar_sp(clave, request.method, payload))


if __name__ == "__main__":
    app.run(debug=True)
