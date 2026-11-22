# Sistema Integral de Automatización y Consulta Comercial (DENUE - INEGI)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1F6AA5?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Graficas-Matplotlib-11557C?style=for-the-badge)
![fpdf2](https://img.shields.io/badge/Reportes_PDF-fpdf2-B71C1C?style=for-the-badge)
![Estado](https://img.shields.io/badge/Estado-En_Desarrollo-2EA44F?style=for-the-badge)
![Materia](https://img.shields.io/badge/ITSX-Taller_de_Base_de_Datos-6E40C9?style=for-the-badge)

---

Sistema de escritorio desarrollado en Python para la gestión, consulta multicriterio, análisis estadístico y generación de reportes en PDF sobre datos económicos del Directorio Estadístico Nacional de Unidades Económicas (**DENUE - INEGI**).

---

## Stack Tecnológico

* **Lenguaje:** Python 3.11
* **Interfaz Gráfica:** CustomTkinter (`customtkinter`)
* **Base de Datos:** MySQL / MariaDB (`mysql-connector-python`)
* **Visualización de Datos:** Matplotlib (`matplotlib`)
* **Generación de Reportes:** FPDF2 (`fpdf2`)
* **Gestión de Configuración y Seguridad:** `python-dotenv`, `bcrypt`

---

## Estructura del Proyecto

```text
Sistema_SIACC/
├── config/                  # Configuración y conexión reutilizable a MySQL (conectar / desconectar)
│   ├── __init__.py
│   └── db.py
├── dao/                     # Data Access Objects: consultas SQL parametrizadas y operaciones CRUD
│   └── __init__.py
├── database/                # Scripts SQL de estructura y respaldo de la base de datos
│   └── base_inegi_correccion_final.sql
├── utils/                   # Generadores de gráficas, exportadores a PDF y validadores
│   └── __init__.py
├── views/                   # Pantallas e interfaces gráficas en CustomTkinter
│   └── __init__.py
├── .env.example             # Plantilla de variables de entorno para conexión a MySQL
├── .gitignore               # Archivos y carpetas excluidos del control de versiones
├── main.py                  # Punto de entrada principal de la aplicación
├── README.md                # Documentación general e instrucciones de instalación
└── requirements.txt         # Dependencias exactas del proyecto
```

---

## Requisitos Previos

Antes de configurar el proyecto, asegúrate de contar con:

1. **Python 3.11** instalado y agregado al `PATH` del sistema.
2. **MySQL Server** (o MariaDB / XAMPP) activo en tu equipo.
3. **Git** instalado para el control de versiones.

---

## Instalación y Configuración Local

Sigue estos pasos después de aceptar la invitación al repositorio:

### 1. Clonar el repositorio
```bash
git clone https://github.com/Not-Abad/SIACC-INEGI
cd SIACC-INEGI
```

### 2. Crear y activar el entorno virtual
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

### 3. Instalar las dependencias
Con el entorno virtual activo (`(.venv)` visible en la terminal), ejecuta:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Importar la base de datos
1. Abre tu gestor de base de datos (MySQL Workbench, phpMyAdmin o consola MySQL).
2. Ejecuta el script ubicado en `database/base_inegi_correccion_final.sql`.
3. Verifica que la base de datos `base_inegi_correccion_final` se haya creado con todas sus tablas y registros.

### 5. Configurar variables de entorno
Crea tu archivo privado `.env` a partir de la plantilla `.env.example`:
```bash
cp .env.example .env
```
Abre el archivo `.env` y ajusta únicamente los parámetros de tu instalación local de MySQL (puerto `3306` o `3307`, usuario y contraseña):
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña_local
DB_NAME=base_inegi_correccion_final
```

### 6. Ejecutar la aplicación
```bash
python main.py
```

---

## Módulos Principales del Sistema

* **1.- Geografía y Territorialidad (Estado, Municipio, Localidad):**  Consultas y catálogos territoriales con filtros por rangos (BETWEEN).
* **2.- Infraestructura Urbana (Vialidad, det_Vialidad, Asentamiento):**  Gestión de tipos de vialidad y asentamientos.
* **3.- Clasificación Económica (Actividad):** Altas, consultas y actualización de giros económicos mediante procedimientos almacenados.
* **4.- Núcleo de Establecimientos y Direcciones (Establecimiento, Direccion):** Pantallas completas para Almacenar (con validación de llaves foráneas), Consultar (vistas con múltiples JOIN), Actualizar y Eliminar (bajas controladas) locales comerciales.

---

## Colaboración y Flujo de Trabajo

Para conocer la estrategia de ramas, el ciclo de vida de las Issues, las convenciones de commits y las reglas de arquitectura del equipo, consulta la guía oficial en [WORKFLOW](workflow.md).