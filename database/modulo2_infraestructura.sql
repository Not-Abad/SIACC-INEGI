-- =====================================================================
-- SIACC - Modulo 2: Infraestructura Urbana
-- Tablas: tipo_vialidad, asentamiento, detalle_vialidad
-- Contenido:
--   1. Tabla bitacora_infraestructura (auditoria del modulo)
--   2. Triggers de auditoria AFTER INSERT / AFTER UPDATE / AFTER DELETE
--   3. Procedimientos almacenados transaccionales
--      (START TRANSACTION / COMMIT / ROLLBACK) para altas,
--      modificaciones, bajas y validaciones de existencia.
-- Se puede ejecutar varias veces: borra y vuelve a crear sus objetos.
-- No modifica ni borra datos de las 9 tablas oficiales.
-- =====================================================================

USE base_inegi_correccion_final;

-- ---------------------------------------------------------------------
-- 1. Tabla bitacora del modulo
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bitacora_infraestructura (
    id_bitacora    INT          NOT NULL AUTO_INCREMENT,
    tabla          VARCHAR(30)  NOT NULL,
    operacion      VARCHAR(10)  NOT NULL,
    id_registro    INT          NOT NULL,
    valor_anterior VARCHAR(255) DEFAULT NULL,
    valor_nuevo    VARCHAR(255) DEFAULT NULL,
    usuario        VARCHAR(100) NOT NULL,
    fecha          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_bitacora)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 2. Triggers de auditoria
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_m2_tipo_vialidad_ai;
DROP TRIGGER IF EXISTS trg_m2_tipo_vialidad_au;
DROP TRIGGER IF EXISTS trg_m2_tipo_vialidad_ad;
DROP TRIGGER IF EXISTS trg_m2_asentamiento_ai;
DROP TRIGGER IF EXISTS trg_m2_asentamiento_au;
DROP TRIGGER IF EXISTS trg_m2_asentamiento_ad;
DROP TRIGGER IF EXISTS trg_m2_detalle_vialidad_ai;
DROP TRIGGER IF EXISTS trg_m2_detalle_vialidad_au;
DROP TRIGGER IF EXISTS trg_m2_detalle_vialidad_ad;

DELIMITER $$

-- tipo_vialidad --------------------------------------------------------
CREATE TRIGGER trg_m2_tipo_vialidad_ai
AFTER INSERT ON tipo_vialidad
FOR EACH ROW
BEGIN
    INSERT INTO bitacora_infraestructura
        (tabla, operacion, id_registro, valor_anterior, valor_nuevo, usuario)
    VALUES ('tipo_vialidad', 'INSERT', NEW.id_tipo_vialidad,
            NULL, NEW.nombre_tipo_vialidad, USER());
END$$

CREATE TRIGGER trg_m2_tipo_vialidad_au
AFTER UPDATE ON tipo_vialidad
FOR EACH ROW
BEGIN
    -- Solo se registra si el nombre cambio de verdad
    IF NOT (OLD.nombre_tipo_vialidad <=> NEW.nombre_tipo_vialidad) THEN
        INSERT INTO bitacora_infraestructura
            (tabla, operacion, id_registro, valor_anterior, valor_nuevo, usuario)
        VALUES ('tipo_vialidad', 'UPDATE', NEW.id_tipo_vialidad,
                OLD.nombre_tipo_vialidad, NEW.nombre_tipo_vialidad, USER());
    END IF;
END$$

CREATE TRIGGER trg_m2_tipo_vialidad_ad
AFTER DELETE ON tipo_vialidad
FOR EACH ROW
BEGIN
    INSERT INTO bitacora_infraestructura
        (tabla, operacion, id_registro, valor_anterior, valor_nuevo, usuario)
    VALUES ('tipo_vialidad', 'DELETE', OLD.id_tipo_vialidad,
            OLD.nombre_tipo_vialidad, NULL, USER());
END$$

-- asentamiento ---------------------------------------------------------
CREATE TRIGGER trg_m2_asentamiento_ai
AFTER INSERT ON asentamiento
FOR EACH ROW
BEGIN
    INSERT INTO bitacora_infraestructura
        (tabla, operacion, id_registro, valor_anterior, valor_nuevo, usuario)
    VALUES ('asentamiento', 'INSERT', NEW.id_asentamiento,
            NULL, NEW.tipo_asentamiento, USER());
END$$

CREATE TRIGGER trg_m2_asentamiento_au
AFTER UPDATE ON asentamiento
FOR EACH ROW
BEGIN
    IF NOT (OLD.tipo_asentamiento <=> NEW.tipo_asentamiento) THEN
        INSERT INTO bitacora_infraestructura
            (tabla, operacion, id_registro, valor_anterior, valor_nuevo, usuario)
        VALUES ('asentamiento', 'UPDATE', NEW.id_asentamiento,
                OLD.tipo_asentamiento, NEW.tipo_asentamiento, USER());
    END IF;
END$$

CREATE TRIGGER trg_m2_asentamiento_ad
AFTER DELETE ON asentamiento
FOR EACH ROW
BEGIN
    INSERT INTO bitacora_infraestructura
        (tabla, operacion, id_registro, valor_anterior, valor_nuevo, usuario)
    VALUES ('asentamiento', 'DELETE', OLD.id_asentamiento,
            OLD.tipo_asentamiento, NULL, USER());
END$$

-- detalle_vialidad -----------------------------------------------------
-- Formato del valor: id_direccion | id_tipo_vialidad | nombre_vialidad
CREATE TRIGGER trg_m2_detalle_vialidad_ai
AFTER INSERT ON detalle_vialidad
FOR EACH ROW
BEGIN
    INSERT INTO bitacora_infraestructura
        (tabla, operacion, id_registro, valor_anterior, valor_nuevo, usuario)
    VALUES ('detalle_vialidad', 'INSERT', NEW.id_detalle_vialidad, NULL,
            LEFT(CONCAT(NEW.id_direccion, ' | ', IFNULL(NEW.id_tipo_vialidad, 'NULL'),
                        ' | ', IFNULL(NEW.nombre_vialidad, 'NULL')), 255),
            USER());
END$$

CREATE TRIGGER trg_m2_detalle_vialidad_au
AFTER UPDATE ON detalle_vialidad
FOR EACH ROW
BEGIN
    IF NOT (OLD.id_direccion     <=> NEW.id_direccion)
       OR NOT (OLD.id_tipo_vialidad <=> NEW.id_tipo_vialidad)
       OR NOT (OLD.nombre_vialidad  <=> NEW.nombre_vialidad) THEN
        INSERT INTO bitacora_infraestructura
            (tabla, operacion, id_registro, valor_anterior, valor_nuevo, usuario)
        VALUES ('detalle_vialidad', 'UPDATE', NEW.id_detalle_vialidad,
                LEFT(CONCAT(OLD.id_direccion, ' | ', IFNULL(OLD.id_tipo_vialidad, 'NULL'),
                            ' | ', IFNULL(OLD.nombre_vialidad, 'NULL')), 255),
                LEFT(CONCAT(NEW.id_direccion, ' | ', IFNULL(NEW.id_tipo_vialidad, 'NULL'),
                            ' | ', IFNULL(NEW.nombre_vialidad, 'NULL')), 255),
                USER());
    END IF;
END$$

CREATE TRIGGER trg_m2_detalle_vialidad_ad
AFTER DELETE ON detalle_vialidad
FOR EACH ROW
BEGIN
    INSERT INTO bitacora_infraestructura
        (tabla, operacion, id_registro, valor_anterior, valor_nuevo, usuario)
    VALUES ('detalle_vialidad', 'DELETE', OLD.id_detalle_vialidad,
            LEFT(CONCAT(OLD.id_direccion, ' | ', IFNULL(OLD.id_tipo_vialidad, 'NULL'),
                        ' | ', IFNULL(OLD.nombre_vialidad, 'NULL')), 255),
            NULL, USER());
END$$

DELIMITER ;

-- ---------------------------------------------------------------------
-- 3. Procedimientos almacenados transaccionales
--    Todos usan un EXIT HANDLER: ante cualquier error (incluidas las
--    validaciones con SIGNAL) hacen ROLLBACK y devuelven el mensaje.
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_m2_tipo_vialidad_alta;
DROP PROCEDURE IF EXISTS sp_m2_tipo_vialidad_modificar;
DROP PROCEDURE IF EXISTS sp_m2_tipo_vialidad_eliminar;
DROP PROCEDURE IF EXISTS sp_m2_asentamiento_alta;
DROP PROCEDURE IF EXISTS sp_m2_asentamiento_modificar;
DROP PROCEDURE IF EXISTS sp_m2_asentamiento_eliminar;
DROP PROCEDURE IF EXISTS sp_m2_detalle_vialidad_alta;
DROP PROCEDURE IF EXISTS sp_m2_detalle_vialidad_modificar;
DROP PROCEDURE IF EXISTS sp_m2_detalle_vialidad_eliminar;

DELIMITER $$

-- =========================== TIPO_VIALIDAD ===========================
CREATE PROCEDURE sp_m2_tipo_vialidad_alta(
    IN  p_nombre VARCHAR(255),
    OUT p_id     INT
)
BEGIN
    DECLARE v_nombre VARCHAR(255);
    DECLARE v_msg    VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_nombre = UPPER(TRIM(p_nombre));
    IF v_nombre IS NULL OR v_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre del tipo de vialidad es obligatorio.';
    END IF;

    START TRANSACTION;
        IF EXISTS (SELECT 1 FROM tipo_vialidad WHERE nombre_tipo_vialidad = v_nombre) THEN
            SET v_msg = CONCAT('Ya existe el tipo de vialidad ', v_nombre, '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        SELECT IFNULL(MAX(id_tipo_vialidad), 0) + 1 INTO p_id
        FROM tipo_vialidad FOR UPDATE;

        INSERT INTO tipo_vialidad (id_tipo_vialidad, nombre_tipo_vialidad)
        VALUES (p_id, v_nombre);
    COMMIT;
END$$

CREATE PROCEDURE sp_m2_tipo_vialidad_modificar(
    IN p_id     INT,
    IN p_nombre VARCHAR(255)
)
BEGIN
    DECLARE v_nombre VARCHAR(255);
    DECLARE v_msg    VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_nombre = UPPER(TRIM(p_nombre));
    IF v_nombre IS NULL OR v_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre del tipo de vialidad es obligatorio.';
    END IF;

    START TRANSACTION;
        IF NOT EXISTS (SELECT 1 FROM tipo_vialidad WHERE id_tipo_vialidad = p_id FOR UPDATE) THEN
            SET v_msg = CONCAT('No existe el tipo de vialidad con id ', IFNULL(p_id, 'NULL'), '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;
        IF EXISTS (SELECT 1 FROM tipo_vialidad
                   WHERE nombre_tipo_vialidad = v_nombre AND id_tipo_vialidad <> p_id) THEN
            SET v_msg = CONCAT('Ya existe otro tipo de vialidad llamado ', v_nombre, '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        UPDATE tipo_vialidad
        SET nombre_tipo_vialidad = v_nombre
        WHERE id_tipo_vialidad = p_id;
    COMMIT;
END$$

CREATE PROCEDURE sp_m2_tipo_vialidad_eliminar(
    IN p_id INT
)
BEGIN
    DECLARE v_usos INT DEFAULT 0;
    DECLARE v_msg  VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        IF NOT EXISTS (SELECT 1 FROM tipo_vialidad WHERE id_tipo_vialidad = p_id FOR UPDATE) THEN
            SET v_msg = CONCAT('No existe el tipo de vialidad con id ', IFNULL(p_id, 'NULL'), '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        -- Baja controlada: no se borra si alguna vialidad lo usa
        SELECT COUNT(*) INTO v_usos FROM detalle_vialidad WHERE id_tipo_vialidad = p_id;
        IF v_usos > 0 THEN
            SET v_msg = CONCAT('No se puede eliminar: ', v_usos,
                               ' vialidades usan este tipo de vialidad.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        DELETE FROM tipo_vialidad WHERE id_tipo_vialidad = p_id;
    COMMIT;
END$$

-- ============================ ASENTAMIENTO ===========================
CREATE PROCEDURE sp_m2_asentamiento_alta(
    IN  p_tipo VARCHAR(30),
    OUT p_id   INT
)
BEGIN
    DECLARE v_tipo VARCHAR(30);
    DECLARE v_msg  VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_tipo = UPPER(TRIM(p_tipo));
    IF v_tipo IS NULL OR v_tipo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tipo de asentamiento es obligatorio.';
    END IF;

    START TRANSACTION;
        IF EXISTS (SELECT 1 FROM asentamiento WHERE tipo_asentamiento = v_tipo) THEN
            SET v_msg = CONCAT('Ya existe el tipo de asentamiento ', v_tipo, '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        SELECT IFNULL(MAX(id_asentamiento), 0) + 1 INTO p_id
        FROM asentamiento FOR UPDATE;

        INSERT INTO asentamiento (id_asentamiento, tipo_asentamiento)
        VALUES (p_id, v_tipo);
    COMMIT;
END$$

CREATE PROCEDURE sp_m2_asentamiento_modificar(
    IN p_id   INT,
    IN p_tipo VARCHAR(30)
)
BEGIN
    DECLARE v_tipo VARCHAR(30);
    DECLARE v_msg  VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_tipo = UPPER(TRIM(p_tipo));
    IF v_tipo IS NULL OR v_tipo = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El tipo de asentamiento es obligatorio.';
    END IF;

    START TRANSACTION;
        IF NOT EXISTS (SELECT 1 FROM asentamiento WHERE id_asentamiento = p_id FOR UPDATE) THEN
            SET v_msg = CONCAT('No existe el asentamiento con id ', IFNULL(p_id, 'NULL'), '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;
        IF EXISTS (SELECT 1 FROM asentamiento
                   WHERE tipo_asentamiento = v_tipo AND id_asentamiento <> p_id) THEN
            SET v_msg = CONCAT('Ya existe otro asentamiento llamado ', v_tipo, '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        UPDATE asentamiento
        SET tipo_asentamiento = v_tipo
        WHERE id_asentamiento = p_id;
    COMMIT;
END$$

CREATE PROCEDURE sp_m2_asentamiento_eliminar(
    IN p_id INT
)
BEGIN
    DECLARE v_usos INT DEFAULT 0;
    DECLARE v_msg  VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        IF NOT EXISTS (SELECT 1 FROM asentamiento WHERE id_asentamiento = p_id FOR UPDATE) THEN
            SET v_msg = CONCAT('No existe el asentamiento con id ', IFNULL(p_id, 'NULL'), '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        -- Baja controlada: no se borra si alguna direccion lo usa
        SELECT COUNT(*) INTO v_usos FROM direccion WHERE id_asentamiento = p_id;
        IF v_usos > 0 THEN
            SET v_msg = CONCAT('No se puede eliminar: ', v_usos,
                               ' direcciones usan este asentamiento.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        DELETE FROM asentamiento WHERE id_asentamiento = p_id;
    COMMIT;
END$$

-- ========================== DETALLE_VIALIDAD =========================
-- p_id_tipo puede ser NULL (la tabla lo permite).
CREATE PROCEDURE sp_m2_detalle_vialidad_alta(
    IN  p_id_direccion INT,
    IN  p_id_tipo      INT,
    IN  p_nombre       VARCHAR(160),
    OUT p_id           INT
)
BEGIN
    DECLARE v_nombre VARCHAR(160);
    DECLARE v_msg    VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_nombre = TRIM(p_nombre);
    IF v_nombre IS NULL OR v_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de la vialidad es obligatorio.';
    END IF;

    START TRANSACTION;
        -- Validacion de llaves foraneas
        IF NOT EXISTS (SELECT 1 FROM direccion WHERE id_direccion = p_id_direccion) THEN
            SET v_msg = CONCAT('No existe la direccion con id ', IFNULL(p_id_direccion, 'NULL'), '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;
        IF p_id_tipo IS NOT NULL
           AND NOT EXISTS (SELECT 1 FROM tipo_vialidad WHERE id_tipo_vialidad = p_id_tipo) THEN
            SET v_msg = CONCAT('No existe el tipo de vialidad con id ', p_id_tipo, '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        SELECT IFNULL(MAX(id_detalle_vialidad), 0) + 1 INTO p_id
        FROM detalle_vialidad FOR UPDATE;

        INSERT INTO detalle_vialidad (id_detalle_vialidad, id_direccion, id_tipo_vialidad, nombre_vialidad)
        VALUES (p_id, p_id_direccion, p_id_tipo, v_nombre);
    COMMIT;
END$$

CREATE PROCEDURE sp_m2_detalle_vialidad_modificar(
    IN p_id           INT,
    IN p_id_direccion INT,
    IN p_id_tipo      INT,
    IN p_nombre       VARCHAR(160)
)
BEGIN
    DECLARE v_nombre VARCHAR(160);
    DECLARE v_msg    VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_nombre = TRIM(p_nombre);
    IF v_nombre IS NULL OR v_nombre = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de la vialidad es obligatorio.';
    END IF;

    START TRANSACTION;
        IF NOT EXISTS (SELECT 1 FROM detalle_vialidad WHERE id_detalle_vialidad = p_id FOR UPDATE) THEN
            SET v_msg = CONCAT('No existe la vialidad con id ', IFNULL(p_id, 'NULL'), '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;
        IF NOT EXISTS (SELECT 1 FROM direccion WHERE id_direccion = p_id_direccion) THEN
            SET v_msg = CONCAT('No existe la direccion con id ', IFNULL(p_id_direccion, 'NULL'), '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;
        IF p_id_tipo IS NOT NULL
           AND NOT EXISTS (SELECT 1 FROM tipo_vialidad WHERE id_tipo_vialidad = p_id_tipo) THEN
            SET v_msg = CONCAT('No existe el tipo de vialidad con id ', p_id_tipo, '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        UPDATE detalle_vialidad
        SET id_direccion     = p_id_direccion,
            id_tipo_vialidad = p_id_tipo,
            nombre_vialidad  = v_nombre
        WHERE id_detalle_vialidad = p_id;
    COMMIT;
END$$

CREATE PROCEDURE sp_m2_detalle_vialidad_eliminar(
    IN p_id INT
)
BEGIN
    DECLARE v_msg VARCHAR(255);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        IF NOT EXISTS (SELECT 1 FROM detalle_vialidad WHERE id_detalle_vialidad = p_id FOR UPDATE) THEN
            SET v_msg = CONCAT('No existe la vialidad con id ', IFNULL(p_id, 'NULL'), '.');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
        END IF;

        DELETE FROM detalle_vialidad WHERE id_detalle_vialidad = p_id;
    COMMIT;
END$$

DELIMITER ;

-- ---------------------------------------------------------------------
-- Verificacion rapida (opcional)
-- SHOW TRIGGERS LIKE 'tipo_vialidad';
-- SHOW PROCEDURE STATUS WHERE Db = 'base_inegi_correccion_final' AND Name LIKE 'sp_m2%';
-- ---------------------------------------------------------------------
