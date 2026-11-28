
USE `base_inegi_correccion_final`;
SET NAMES utf8mb4;

DROP PROCEDURE IF EXISTS `sp_informacion_establecimiento`;

DELIMITER $$

CREATE PROCEDURE `sp_informacion_establecimiento` (
    IN p_id_establecimiento INT
)
BEGIN
    DECLARE v_existe INT DEFAULT 0;

    -- Manejador de errores SQL
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SELECT
            'ERROR' AS estado_operacion,
            'Ocurrió un error SQL al consultar la información del establecimiento.' AS mensaje;
    END;

    -- Validar parámetro de entrada
    IF p_id_establecimiento IS NULL OR p_id_establecimiento <= 0 THEN
        SELECT
            'ERROR' AS estado_operacion,
            'Debe proporcionar un ID de establecimiento válido.' AS mensaje;
    ELSE
        -- Verificar si el establecimiento existe
        SELECT COUNT(*)
        INTO v_existe
        FROM establecimiento
        WHERE id_establecimiento = p_id_establecimiento;

        IF v_existe = 0 THEN
            SELECT
                'SIN_RESULTADOS' AS estado_operacion,
                'No se encontró ningún establecimiento con el ID especificado.' AS mensaje,
                p_id_establecimiento AS id_establecimiento;
        ELSE
            SELECT
                -- Datos generales del establecimiento (sin codigo_actividad ni id_direccion crudos)
                e.id_establecimiento,
                e.clee,
                e.nombre_establecimiento,
                e.razon_social,
                a.nombre_actividad AS actividad,
                e.personal_ocupado,
                e.telefono,
                e.correo_electronico,
                e.sitio_web,
                e.tipo_unidad_economica,
                e.fecha_alta,
                -- Ubicación geográfica y administrativa completa de la dirección
                ent.nombre_entidad AS estado,
                m.nombre_municipio AS municipio,
                l.nombre_localidad AS localidad,
                aset.tipo_asentamiento,
                (SELECT GROUP_CONCAT(
                            TRIM(CONCAT_WS(' ', tv.nombre_tipo_vialidad, dv.nombre_vialidad))
                            ORDER BY dv.id_detalle_vialidad
                            SEPARATOR ', '
                        )
                 FROM detalle_vialidad dv
                 LEFT JOIN tipo_vialidad tv ON dv.id_tipo_vialidad = tv.id_tipo_vialidad
                 WHERE dv.id_direccion = d.id_direccion) AS vialidades,
                -- Resto de información de la tabla direccion
                d.codigo_postal,
                d.numero_exterior,
                d.letra_exterior,
                d.edificio,
                d.edificio_e,
                d.numero_interior,
                d.letra_interior,
                d.tipo_centro_comercial,
                d.nombre_centro_comercial,
                d.numero_local,
                d.ageb,
                d.manzana,
                d.latitud,
                d.longitud
            FROM establecimiento e
            INNER JOIN actividad a ON e.codigo_actividad = a.codigo_actividad
            INNER JOIN direccion d ON e.id_direccion = d.id_direccion
            INNER JOIN asentamiento aset ON d.id_asentamiento = aset.id_asentamiento
            INNER JOIN localidad l ON d.id_localidad = l.id_localidad
            INNER JOIN municipio m ON l.cve_ent = m.cve_ent AND l.cve_mun = m.cve_mun
            INNER JOIN entidad ent ON m.cve_ent = ent.cve_ent
            WHERE e.id_establecimiento = p_id_establecimiento;
        END IF;
    END IF;
END $$

DELIMITER ;


DROP PROCEDURE IF EXISTS `sp_insetar_detalle_vialidad`;

DELIMITER $$

CREATE PROCEDURE `sp_insetar_detalle_vialidad` (
    IN p_id_direccion INT,
    IN p_id_tipo_vialidad INT,
    IN p_nombre_vialidad VARCHAR(160)
)
BEGIN
    DECLARE v_existe_direccion INT DEFAULT 0;
    DECLARE v_existe_tipo_vialidad INT DEFAULT 0;
    DECLARE v_nuevo_id INT DEFAULT 1;

    -- Manejador de errores SQL con reversión de transacción
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT
            'ERROR' AS estado_operacion,
            'Error SQL al intentar guardar el detalle de vialidad. Se revirtió la transacción.' AS mensaje;
    END;

    -- Validación básica de parámetros
    IF p_id_direccion IS NULL OR p_id_tipo_vialidad IS NULL
       OR p_nombre_vialidad IS NULL OR TRIM(p_nombre_vialidad) = '' THEN
        SELECT
            'ERROR' AS estado_operacion,
            'Los parámetros p_id_direccion, p_id_tipo_vialidad y p_nombre_vialidad son obligatorios.' AS mensaje;
    ELSE
        -- 1. Corroborar que la dirección exista
        SELECT COUNT(*)
        INTO v_existe_direccion
        FROM direccion
        WHERE id_direccion = p_id_direccion;

        -- 2. Corroborar que el tipo de vialidad exista
        SELECT COUNT(*)
        INTO v_existe_tipo_vialidad
        FROM tipo_vialidad
        WHERE id_tipo_vialidad = p_id_tipo_vialidad;

        IF v_existe_direccion = 0 THEN
            SELECT
                'ERROR' AS estado_operacion,
                'La dirección especificada no existe en la tabla direccion.' AS mensaje,
                p_id_direccion AS id_direccion;

        ELSEIF v_existe_tipo_vialidad = 0 THEN
            SELECT
                'ERROR' AS estado_operacion,
                'El tipo de vialidad especificado no existe en la tabla tipo_vialidad.' AS mensaje,
                p_id_tipo_vialidad AS id_tipo_vialidad;

        ELSE
            START TRANSACTION;

            -- Obtener el siguiente ID disponible (la tabla no usa AUTO_INCREMENT)
            SELECT COALESCE(MAX(id_detalle_vialidad), 0) + 1
            INTO v_nuevo_id
            FROM detalle_vialidad
            FOR UPDATE;

            INSERT INTO detalle_vialidad (
                id_detalle_vialidad,
                id_direccion,
                id_tipo_vialidad,
                nombre_vialidad
            )
            VALUES (
                v_nuevo_id,
                p_id_direccion,
                p_id_tipo_vialidad,
                TRIM(p_nombre_vialidad)
            );

            COMMIT;

            SELECT
                'EXITO' AS estado_operacion,
                'Detalle de vialidad guardado correctamente.' AS mensaje,
                v_nuevo_id AS id_detalle_vialidad,
                p_id_direccion AS id_direccion,
                p_id_tipo_vialidad AS id_tipo_vialidad,
                TRIM(p_nombre_vialidad) AS nombre_vialidad;
        END IF;
    END IF;
END $$

DELIMITER ;

DROP PROCEDURE IF EXISTS `sp_insertar_localidad`;

DELIMITER $$

CREATE PROCEDURE `sp_insertar_localidad` (
    IN p_nombre_entidad VARCHAR(60),
    IN p_nombre_municipio VARCHAR(100),
    IN p_nombre_localidad VARCHAR(120),
    IN p_cve_loc CHAR(4)
)
BEGIN
    DECLARE v_cve_ent CHAR(2) DEFAULT NULL;
    DECLARE v_cve_mun CHAR(3) DEFAULT NULL;
    DECLARE v_existe_nombre_loc INT DEFAULT 0;
    DECLARE v_existe_cve_loc INT DEFAULT 0;
    DECLARE v_nuevo_id_localidad INT DEFAULT 0;

    -- Manejador de errores SQL con reversión de transacción
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT
            'ERROR' AS estado_operacion,
            'Error SQL al intentar insertar la nueva localidad. Se revirtió la transacción.' AS mensaje;
    END;

    -- Validación de parámetros obligatorios
    IF p_nombre_entidad IS NULL OR TRIM(p_nombre_entidad) = ''
       OR p_nombre_municipio IS NULL OR TRIM(p_nombre_municipio) = ''
       OR p_nombre_localidad IS NULL OR TRIM(p_nombre_localidad) = ''
       OR p_cve_loc IS NULL OR CHAR_LENGTH(TRIM(p_cve_loc)) <> 4 THEN

        SELECT
            'ERROR' AS estado_operacion,
            'Todos los parámetros son obligatorios y p_cve_loc debe tener exactamente 4 caracteres.' AS mensaje;
    ELSE
        -- 1. Revisar que la entidad exista y obtener su clave cve_ent
        SELECT cve_ent
        INTO v_cve_ent
        FROM entidad
        WHERE UPPER(TRIM(nombre_entidad)) = UPPER(TRIM(p_nombre_entidad))
        LIMIT 1;

        IF v_cve_ent IS NULL THEN
            SELECT
                'ERROR' AS estado_operacion,
                'La entidad especificada no existe en la base de datos.' AS mensaje,
                TRIM(p_nombre_entidad) AS entidad_recibida;
        ELSE
            -- 2. Revisar que el municipio exista dentro de dicha entidad
            SELECT cve_mun
            INTO v_cve_mun
            FROM municipio
            WHERE cve_ent = v_cve_ent
              AND UPPER(TRIM(nombre_municipio)) = UPPER(TRIM(p_nombre_municipio))
            LIMIT 1;

            IF v_cve_mun IS NULL THEN
                SELECT
                    'ERROR' AS estado_operacion,
                    'El municipio especificado no existe dentro de la entidad indicada.' AS mensaje,
                    TRIM(p_nombre_entidad) AS entidad,
                    TRIM(p_nombre_municipio) AS municipio_recibido;
            ELSE
                -- 3. Revisar que la localidad no exista previamente en ese municipio en concreto
                SELECT COUNT(*)
                INTO v_existe_nombre_loc
                FROM localidad
                WHERE cve_ent = v_cve_ent
                  AND cve_mun = v_cve_mun
                  AND UPPER(TRIM(nombre_localidad)) = UPPER(TRIM(p_nombre_localidad));

                SELECT COUNT(*)
                INTO v_existe_cve_loc
                FROM localidad
                WHERE cve_ent = v_cve_ent
                  AND cve_mun = v_cve_mun
                  AND cve_loc = TRIM(p_cve_loc);

                IF v_existe_nombre_loc > 0 THEN
                    SELECT
                        'ERROR' AS estado_operacion,
                        'Ya existe una localidad con ese nombre dentro del municipio especificado.' AS mensaje,
                        TRIM(p_nombre_entidad) AS entidad,
                        TRIM(p_nombre_municipio) AS municipio,
                        TRIM(p_nombre_localidad) AS localidad_duplicada;

                ELSEIF v_existe_cve_loc > 0 THEN
                    SELECT
                        'ERROR' AS estado_operacion,
                        'Ya existe una localidad con esa clave (cve_loc) dentro del municipio especificado.' AS mensaje,
                        TRIM(p_nombre_entidad) AS entidad,
                        TRIM(p_nombre_municipio) AS municipio,
                        TRIM(p_cve_loc) AS cve_loc_duplicada;

                ELSE
                    START TRANSACTION;

                    INSERT INTO localidad (
                        cve_ent,
                        cve_mun,
                        cve_loc,
                        nombre_localidad
                    )
                    VALUES (
                        v_cve_ent,
                        v_cve_mun,
                        TRIM(p_cve_loc),
                        TRIM(p_nombre_localidad)
                    );

                    SET v_nuevo_id_localidad = LAST_INSERT_ID();

                    COMMIT;

                    SELECT
                        'EXITO' AS estado_operacion,
                        'Localidad registrada correctamente en el municipio indicado.' AS mensaje,
                        v_nuevo_id_localidad AS id_localidad,
                        v_cve_ent AS cve_ent,
                        TRIM(p_nombre_entidad) AS entidad,
                        v_cve_mun AS cve_mun,
                        TRIM(p_nombre_municipio) AS municipio,
                        TRIM(p_cve_loc) AS cve_loc,
                        TRIM(p_nombre_localidad) AS nombre_localidad;
                END IF;
            END IF;
        END IF;
    END IF;
END $$

DELIMITER ;

