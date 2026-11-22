# Guía de Flujo de Trabajo (Workflow & Git Standards)

Este documento define las reglas de colaboración para el equipo de **SIACC-INEGI**. Todos los integrantes deben seguir este ciclo de vida y respetar la arquitectura del proyecto para garantizar entregas estables sin romper la aplicación.

---

## Estrategia de Ramas (Git Branching)

El proyecto utiliza una variante aislada de **Git Flow**:

* **`main`**: Código estable y probado de cada iteración. **Prohibido hacer `git push` directo a esta rama sin revisión de otro compañero.**
* **`feature/<modulo>-<descripcion-corta>`**: Ramas individuales para cada Issue atómica.

### Nomenclatura de Ramas por Módulo

Al iniciar una Issue, crea tu rama local siguiendo la nomenclatura indicada en la tarjeta del proyecto:

* `feature/db-<tarea>` — Ajustes al script SQL, índices o tablas de autenticación (`database/`).
* `feature/crud-<entidad>` — Formularios y operaciones de altas, bajas y cambios (`dao/` y `views/`).
* `feature/consultas-<tarea>` — Buscador multicriterio y tablas de resultados (`dao/` y `views/`).
* `feature/graficas-<tarea>` — Consultas agregadas y renderizado en Matplotlib (`dao/`, `utils/` y `views/`).
* `feature/pdf-<tarea>` — Exportación de consultas y gráficas a PDF con `fpdf2` (`utils/`).
* `feature/auth-<tarea>` — Pantalla de inicio de sesión y control de permisos por rol (`dao/` y `views/`).

---

## Ciclo de Vida de una Issue (Paso a Paso)

### 1. Seleccionar la Issue en GitHub Projects

1. Entra al **[Tablero del Proyecto](https://github.com/Not-Abad/SIACC-INEGI/projects)** (pestaña *Projects* del repositorio).
2. Ve a la columna **Backlog** (o **Ready**).
3. Haz clic en la Issue que vas a desarrollar y en el panel lateral derecho asigna tu usuario en **Assignees**.
4. Mueve la tarjeta a la columna **In Progress**.

---

### 2. Crear la Rama en tu entorno local

Abre Git Bash o tu terminal integrada en VS Code dentro de la carpeta `Sistema_SIACC` y ejecuta:

#### 2.1. Asegúrate de tener lo último de `main`

```bash
git checkout main
git pull origin main
```

#### 2.2. Crea y cámbiate a tu nueva rama de `feature`

```bash
git checkout -b feature/<modulo>-<descripcion-corta>
```

*(Ejemplo: `git checkout -b feature/crud-establecimientos`)*

#### 2.3. Desarrollar y realizar Commits atómicos

Trabaja únicamente en los archivos correspondientes a tu módulo y verifica que todo ejecute sin errores dentro de `.venv`. Realiza commits claros usando **Conventional Commits** (`feat:`, `fix:`, `db:`, `docs:`, `refactor:`):

```bash
git add .
git commit -m "feat(dao): implementar consultas CRUD para tabla actividad"
```

#### 2.4. Subir la rama y abrir Pull Request (PR)

Cuando completes todos los Criterios de Aceptación de la Issue:

```bash
git push -u origin feature/<modulo>-<descripcion-corta>
```

1. Ve al repositorio en GitHub y haz clic en **Compare & pull request**.
2. **IMPORTANTE:** Asegúrate de que la rama base (`base`) sea **`main`**.
3. En la descripción del Pull Request, vincula la Issue usando la palabra clave `Closes #` o `Fixes #` seguida del número de la Issue:

   ```markdown
   ### Descripción del cambio
   Se implementó el DAO y el formulario en CustomTkinter para dar de alta y editar actividades económicas con validación de campos obligatorios.

   Closes #4
   ```

4. Asigna a un compañero en **Reviewers** para revisión de código.

#### 2.5. Finalizar la Issue

Una vez revisado y aprobado el Pull Request:

1. Se realiza el **Merge** a la rama `main`.
2. La Issue se cerrará automáticamente y la tarjeta del tablero pasará a **Done**.
3. Elimina la rama remota en GitHub (botón *Delete branch*) y limpia tu rama local para mantener ordenado el repositorio:

```bash
git checkout main
git pull origin main
git branch -d feature/<modulo>-<descripcion-corta>
```

---

## Estándares de Arquitectura y Código del Equipo

Para evitar conflictos al fusionar ramas y mantener limpia la estructura del proyecto:

1. **Separación estricta entre `dao/` y `views/`:**
   * Nunca escribas sentencias SQL (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) dentro de los archivos de `views/`.
   * Toda interacción con MySQL debe vivir en funciones dentro de `dao/`, usando consultas parametrizadas (`%s`) para prevenir inyección SQL.
2. **Uso obligatorio del gestor de conexión (`config/db.py`):**
   * Abre y cierra siempre tus conexiones llamando a `conectar()` y `desconectar(conn, cursor)` dentro de bloques `try / except / finally`.
3. **Protección de archivos privados:**
   * Nunca subas tu archivo `.env`, la carpeta `.venv/`, configuraciones locales de `.vscode/` ni los archivos `.pdf` o `.png` generados durante tus pruebas.
4. **Prueba antes de abrir PR:**
   * Ejecuta `python main.py` (o el módulo correspondiente con `python -m ...`) antes de hacer `git push` para confirmar que no hay errores de importación ni excepciones sin capturar.