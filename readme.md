# Sistema Integral de Automatización y Consulta Comercial (SIACC · DENUE - INEGI)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![HTML5](https://img.shields.io/badge/Frontend-HTML5_%2F_CSS3_%2F_JS-F65737?style=for-the-badge)
![Estado](https://img.shields.io/badge/Estado-En_Desarrollo-2EA44F?style=for-the-badge)
![Materia](https://img.shields.io/badge/ITSX-Taller_de_Base_de_Datos-6E40C9?style=for-the-badge)

---

Aplicación web desarrollada con **Python (Flask)** y **MySQL** para la gestión, consulta multicriterio y ejecución estandarizada de procedimientos almacenados sobre los datos económicos del Directorio Estadístico Nacional de Unidades Económicas (**DENUE - INEGI**).

---

## Stack Tecnológico

* **Backend y API REST:** Python 3.11 + Flask (`flask`)
* **Capa de Acceso a Datos (DAO):** MySQL / MariaDB (`mysql-connector-python`)
* **Frontend Web:** HTML5, CSS3 y JavaScript moderno (Fetch API)
* **Configuración:** Variables de entorno con `python-dotenv`

---

## Estructura del Proyecto

```text
SIACC-INEGI/
├── config/
│   ├── __init__.py
│   └── db.py                             # Configuración y parámetros de conexión a MySQL
├── dao/
│   ├── __init__.py
│   └── inegi_dao.py                      # Lógica SQL, transacciones y registro de SPs
├── database/
│   ├── base_inegi_correccion_final.sql   # Estructura principal, vistas y datos base
│   └── procedimientos/                   # Scripts SQL de procedimientos almacenados del equipo
│       └── 01_abad_procedimientos.sql    # Procedimientos iniciales (consulta e inserción)
├── static/
│   ├── css/
│   │   └── estilos.css                   # Hoja de estilos principal de SIACC
│   └── js/
│       └── app.js                        # Lógica del frontend para catálogos y CRUD
├── templates/
│   ├── index.html                        # Panel principal (Módulos 1 al 4)
│   └── procedimientos.html               # Módulo 5: Ejecutor dinámico de SPs del equipo
├── .env.example                          # Plantilla de variables de entorno
├── .gitignore                            # Archivos ignorados por Git
├── app.py                                # Servidor Flask y rutas de la API REST
├── README.md                             # Guía de instalación y uso
└── requirements.txt                      # Dependencias de Python
```

---

## Requisitos Previos

Antes de comenzar, verifica que tengas instalado en tu computadora:

1. **Python 3.11** (o superior) agregado al `PATH` del sistema.
2. **MySQL Server** (o MariaDB / XAMPP) activo y **MySQL Workbench** (opcional, recomendado).
3. **Git** para clonar y actualizar el repositorio.

---

## Guía Paso a Paso: Instalación y Ejecución Local

### Paso 1. Clonar el repositorio
Abre una terminal (Git Bash, PowerShell o CMD) en la carpeta donde guardas tus proyectos y ejecuta:

```bash
git clone https://github.com/Not-Abad/SIACC-INEGI.git
cd SIACC-INEGI
```

### Paso 2. Crear y activar el entorno virtual
* **En Git Bash (Windows):**
  ```bash
  py -3.11 -m venv .venv
  source .venv/Scripts/activate
  ```
* **En PowerShell (Windows):**
  ```powershell
  py -3.11 -m venv .venv
  Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
  .venv\Scripts\Activate.ps1
  ```
* **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

*(Sabrás que está activo cuando veas `(.venv)` al inicio de la línea en tu terminal.)*

### Paso 3. Instalar las dependencias de Python
Con el entorno virtual activo, instala los paquetes requeridos:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> **Nota:** Si tu archivo `requirements.txt` aún no incluye Flask, instala directamente los paquetes base ejecutando:
> `pip install flask mysql-connector-python python-dotenv`

### Paso 4. Importar la base de datos base en MySQL
1. Abre **MySQL Workbench** (o tu cliente MySQL preferido) y conéctate a tu servidor local.
2. Abre el archivo `database/base_inegi_correccion_final.sql`.
3. Ejecuta todo el script (ícono del rayo amarillo o `Ctrl + Shift + Enter`).
4. Verifica en el panel de esquemas que se haya creado la base de datos `base_inegi_correccion_final` con sus tablas, vistas y datos iniciales.

### Paso 5. Cargar los procedimientos almacenados del equipo
Los procedimientos almacenados se encuentran separados en la carpeta `database/procedimientos/` para evitar conflictos entre compañeros. **Debes ejecutarlos en tu MySQL local para que funcionen en la web:**

* **Opción A — Desde MySQL Workbench:**
  1. Abre cada archivo `.sql` ubicado dentro de `database/procedimientos/` (por ejemplo, `01_abad_procedimientos.sql`).
  2. Ejecútalo completo (`Ctrl + Shift + Enter`).
  3. Haz clic derecho sobre **Stored Procedures** dentro de `base_inegi_correccion_final` y selecciona **Refresh All** para confirmar que se crearon.

* **Opción B — Desde la terminal (todos los archivos de un solo golpe):**
  ```bash
  for f in database/procedimientos/*.sql; do mysql -h 127.0.0.1 -P 3306 -u root -p base_inegi_correccion_final < "$f"; done
  ```
  *(Cambia `-P 3306` por `-P 3307` si tu instancia de MySQL corre en el puerto 3307).*

### Paso 6. Configurar el archivo `.env`
Crea tu archivo privado `.env` copiando la plantilla `.env.example`:

```bash
cp .env.example .env
```

Abre el archivo `.env` y coloca los datos de tu servidor MySQL local:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=base_inegi_correccion_final
```

> **Importante:** Nunca subas tu archivo `.env` al repositorio (ya está protegido en `.gitignore`).

### Paso 7. Ejecutar la aplicación web
Con el entorno virtual activo y la base de datos lista, inicia el servidor Flask:

```bash
python app.py
```

Abre tu navegador e ingresa a:
* **Panel Principal (Catálogos y CRUD):** `http://127.0.0.1:5000/`
* **Módulo de Procedimientos Almacenados:** `http://127.0.0.1:5000/procedimientos`

---

## Módulos del Sistema

1. **Geografía y Territorialidad (`/`):** Consulta de estados, municipios y localidades con filtros por rangos de clave (`BETWEEN`).
2. **Infraestructura Urbana (`/`):** Alta y consulta de tipos de vialidad, asentamientos y detalles de vialidad.
3. **Clasificación Económica (`/`):** Alta, consulta y actualización de actividades económicas (SCIAN) mediante procedimientos almacenados.
4. **Establecimientos y Direcciones (`/`):** Gestión completa (alta, búsqueda por nombre o CLEE, actualización y baja controlada) de direcciones y establecimientos.
5. **Procedimientos Almacenados (`/procedimientos`):** Interfaz dinámica que detecta todos los procedimientos registrados en `InegiDAO`, genera sus formularios automáticamente y muestra los resultados o mensajes de validación de MySQL.

---

## Cómo Subir Nuevos Procedimientos Almacenados (Para el Equipo)

Si te corresponde agregar procedimientos almacenados al proyecto, sigue estas 3 reglas estándar para que funcionen automáticamente en la interfaz web sin modificar `app.py` ni el HTML:

1. **Crea tu archivo SQL en `database/procedimientos/`** (ejemplo: `02_tu_nombre_procedimientos.sql`):
   * Inicia con `USE base_inegi_correccion_final;` y `SET NAMES utf8mb4;`.
   * Incluye `DROP PROCEDURE IF EXISTS nombre_de_tu_sp;` antes de `CREATE PROCEDURE`.
   * **No dejes sentencias `CALL ...` de prueba al final del archivo** para no insertar registros basura en las bases de datos de tus compañeros.
   * Para mensajes de validación o confirmación, devuelve las columnas `estado_operacion` (`'EXITO'`, `'ERROR'` o `'SIN_RESULTADOS'`) y `mensaje`.

2. **Registra tu procedimiento en `dao/inegi_dao.py`**:
   Abre `dao/inegi_dao.py`, ubica el diccionario `PROCEDIMIENTOS` y reemplaza uno de los espacios reservados (`sp_companero_XX`) con los datos de tu SP:
   ```python
   "nombre_corto_ruta": {
       "sp": "nombre_exacto_en_mysql",
       "metodo": "GET",  # "GET" para consultas, "POST" para altas, "PUT" para cambios, "DELETE" para bajas
       "params": ["parametro_1", "parametro_2"],  # En el mismo orden que en CREATE PROCEDURE
       "opcionales": [],
       "descripcion": "Breve descripción de lo que hace tu procedimiento.",
   },
   ```

3. **Pruébalo antes de hacer `git push`**:
   * Ejecuta tu `.sql` en MySQL Workbench.
   * Entra a `http://127.0.0.1:5000/procedimientos`, selecciona tu procedimiento en la barra lateral y verifica que responda correctamente.
   * Cuando tus compañeros hagan `git pull`, recuerda avisarles que ejecuten tu nuevo archivo `.sql` en su MySQL local.

---

## Solución de Problemas Comunes

* **Error `Can't connect to MySQL server`:** Revisa que el servicio de MySQL esté iniciado y verifica en `.env` si tu MySQL usa el puerto `3306` o `3307`.
* **Error `PROCEDURE base_inegi_correccion_final.sp_... does not exist`:** Te falta ejecutar el script `.sql` correspondiente dentro de `database/procedimientos/` en tu MySQL local.
* **Cambios recientes de un compañero no funcionan:** Ejecuta `git pull` y vuelve a correr los archivos `.sql` nuevos o modificados dentro de `database/procedimientos/`.


---

## Colaboración y Flujo de Trabajo

Para conocer la estrategia de ramas, el ciclo de vida de las Issues, las convenciones de commits y las reglas de arquitectura del equipo, consulta la guía oficial en [WORKFLOW](workflow.md).