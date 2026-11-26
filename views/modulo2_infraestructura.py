"""Vista del Modulo 2: Infraestructura Urbana (CustomTkinter).

Pestanas: Tipos de vialidad | Asentamientos | Vialidades | Bitacora.
No contiene SQL: todo pasa por dao/infraestructura_dao.py.

Prueba independiente (desde la carpeta del proyecto):
    python -m views.modulo2_infraestructura
"""
import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from dao import infraestructura_dao as dao
from dao.infraestructura_dao import InfraestructuraError


def _tabla(master, columnas, anchos):
    """Crea un Treeview con barra de desplazamiento."""
    contenedor = ctk.CTkFrame(master)
    arbol = ttk.Treeview(contenedor, columns=columnas, show="headings", height=14)
    for col, ancho in zip(columnas, anchos):
        arbol.heading(col, text=col)
        arbol.column(col, width=ancho, anchor="w")
    barra = ttk.Scrollbar(contenedor, orient="vertical", command=arbol.yview)
    arbol.configure(yscrollcommand=barra.set)
    arbol.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return contenedor, arbol


def _llenar(arbol, filas):
    arbol.delete(*arbol.get_children())
    for fila in filas:
        arbol.insert("", "end", values=["" if v is None else v for v in fila])


# ----------------------------------------------------------------------
# Pestana generica para catalogos de 2 columnas (id, nombre)
# ----------------------------------------------------------------------
class CatalogoTab:
    def __init__(self, master, etiqueta, listar, alta, modificar, eliminar):
        self.listar, self.alta = listar, alta
        self.modificar, self.eliminar = modificar, eliminar
        self.etiqueta = etiqueta

        form = ctk.CTkFrame(master)
        form.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(form, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.var_id = tk.StringVar()
        ctk.CTkEntry(form, textvariable=self.var_id, width=80, state="disabled").grid(
            row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text=f"{etiqueta}:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.var_nombre = tk.StringVar()
        ctk.CTkEntry(form, textvariable=self.var_nombre, width=260).grid(
            row=0, column=3, padx=5, pady=5)

        botones = ctk.CTkFrame(master, fg_color="transparent")
        botones.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(botones, text="Agregar", command=self.on_agregar).pack(side="left", padx=4)
        ctk.CTkButton(botones, text="Modificar", command=self.on_modificar).pack(side="left", padx=4)
        ctk.CTkButton(botones, text="Eliminar", fg_color="#B71C1C", hover_color="#7F0000",
                      command=self.on_eliminar).pack(side="left", padx=4)
        ctk.CTkButton(botones, text="Limpiar", fg_color="gray", command=self.limpiar).pack(
            side="left", padx=4)

        self.var_buscar = tk.StringVar()
        ctk.CTkButton(botones, text="Buscar", command=self.cargar).pack(side="right", padx=4)
        ctk.CTkEntry(botones, textvariable=self.var_buscar, width=200).pack(side="right", padx=4)
        ctk.CTkLabel(botones, text="Buscar nombre:").pack(side="right", padx=4)

        cont, self.arbol = _tabla(master, ("ID", etiqueta), (80, 400))
        cont.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.arbol.bind("<<TreeviewSelect>>", self.on_seleccionar)

        self.cargar()

    def cargar(self):
        try:
            _llenar(self.arbol, self.listar(self.var_buscar.get()))
        except InfraestructuraError as e:
            messagebox.showerror("Error", str(e))

    def limpiar(self):
        self.var_id.set("")
        self.var_nombre.set("")
        self.arbol.selection_remove(self.arbol.selection())

    def on_seleccionar(self, _evento=None):
        sel = self.arbol.selection()
        if sel:
            id_, nombre = self.arbol.item(sel[0], "values")
            self.var_id.set(id_)
            self.var_nombre.set(nombre)

    def on_agregar(self):
        try:
            nuevo_id = self.alta(self.var_nombre.get())
            messagebox.showinfo("Alta", f"{self.etiqueta} agregado con ID {nuevo_id}.")
            self.limpiar()
            self.cargar()
        except InfraestructuraError as e:
            messagebox.showerror("No se pudo agregar", str(e))

    def on_modificar(self):
        if not self.var_id.get():
            messagebox.showwarning("Modificar", "Selecciona un registro de la tabla.")
            return
        try:
            self.modificar(int(self.var_id.get()), self.var_nombre.get())
            messagebox.showinfo("Modificar", "Registro actualizado.")
            self.cargar()
        except InfraestructuraError as e:
            messagebox.showerror("No se pudo modificar", str(e))

    def on_eliminar(self):
        if not self.var_id.get():
            messagebox.showwarning("Eliminar", "Selecciona un registro de la tabla.")
            return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar el registro ID {self.var_id.get()}?"):
            return
        try:
            self.eliminar(int(self.var_id.get()))
            messagebox.showinfo("Eliminar", "Registro eliminado.")
            self.limpiar()
            self.cargar()
        except InfraestructuraError as e:
            messagebox.showerror("No se pudo eliminar", str(e))


# ----------------------------------------------------------------------
# Pestana de vialidades (detalle_vialidad)
# ----------------------------------------------------------------------
class VialidadesTab:
    SIN_TIPO = "(sin tipo)"

    def __init__(self, master):
        form = ctk.CTkFrame(master)
        form.pack(fill="x", padx=10, pady=(10, 5))

        self.var_id = tk.StringVar()
        self.var_dir = tk.StringVar()
        self.var_tipo = tk.StringVar(value=self.SIN_TIPO)
        self.var_nombre = tk.StringVar()

        ctk.CTkLabel(form, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form, textvariable=self.var_id, width=90, state="disabled").grid(
            row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(form, text="ID dirección:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form, textvariable=self.var_dir, width=100).grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(form, text="Tipo:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.combo_tipo = ctk.CTkOptionMenu(form, variable=self.var_tipo, values=[self.SIN_TIPO],
                                            width=180)
        self.combo_tipo.grid(row=0, column=5, padx=5, pady=5)
        ctk.CTkLabel(form, text="Nombre:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form, textvariable=self.var_nombre, width=420).grid(
            row=1, column=1, columnspan=5, padx=5, pady=5, sticky="w")

        botones = ctk.CTkFrame(master, fg_color="transparent")
        botones.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(botones, text="Agregar", command=self.on_agregar).pack(side="left", padx=4)
        ctk.CTkButton(botones, text="Modificar", command=self.on_modificar).pack(side="left", padx=4)
        ctk.CTkButton(botones, text="Eliminar", fg_color="#B71C1C", hover_color="#7F0000",
                      command=self.on_eliminar).pack(side="left", padx=4)
        ctk.CTkButton(botones, text="Limpiar", fg_color="gray", command=self.limpiar).pack(
            side="left", padx=4)

        busq = ctk.CTkFrame(master, fg_color="transparent")
        busq.pack(fill="x", padx=10, pady=5)
        self.var_b_nombre = tk.StringVar()
        self.var_b_dir = tk.StringVar()
        ctk.CTkLabel(busq, text="Buscar nombre:").pack(side="left", padx=4)
        ctk.CTkEntry(busq, textvariable=self.var_b_nombre, width=200).pack(side="left", padx=4)
        ctk.CTkLabel(busq, text="ID dirección:").pack(side="left", padx=4)
        ctk.CTkEntry(busq, textvariable=self.var_b_dir, width=100).pack(side="left", padx=4)
        ctk.CTkButton(busq, text="Buscar", command=self.cargar).pack(side="left", padx=4)
        ctk.CTkLabel(busq, text=f"(máx. {dao.LIMITE_RESULTADOS} filas)").pack(side="left", padx=4)

        columnas = ("ID", "ID dir.", "Tipo", "Nombre vialidad", "Asentamiento", "C.P.",
                    "Localidad", "Municipio", "Entidad")
        anchos = (70, 70, 110, 220, 120, 60, 140, 140, 120)
        cont, self.arbol = _tabla(master, columnas, anchos)
        cont.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.arbol.bind("<<TreeviewSelect>>", self.on_seleccionar)

        self.tipos = {}  # nombre -> id
        self.recargar_tipos()
        self.cargar()

    # --- utilidades ---
    def recargar_tipos(self):
        try:
            filas = dao.listar_tipos_vialidad()
        except InfraestructuraError as e:
            messagebox.showerror("Error", str(e))
            return
        self.tipos = {nombre: id_ for id_, nombre in filas}
        self.combo_tipo.configure(values=[self.SIN_TIPO] + list(self.tipos))

    def _id_tipo(self):
        return self.tipos.get(self.var_tipo.get())  # None si es "(sin tipo)"

    def _entero(self, texto, campo):
        texto = texto.strip()
        if not texto.isdigit():
            raise InfraestructuraError(f"{campo} debe ser un número entero.")
        return int(texto)

    def cargar(self):
        try:
            id_dir = self._entero(self.var_b_dir.get(), "ID dirección") \
                if self.var_b_dir.get().strip() else None
            _llenar(self.arbol, dao.buscar_vialidades(self.var_b_nombre.get(), id_dir))
        except InfraestructuraError as e:
            messagebox.showerror("Error", str(e))

    def limpiar(self):
        for var in (self.var_id, self.var_dir, self.var_nombre):
            var.set("")
        self.var_tipo.set(self.SIN_TIPO)
        self.arbol.selection_remove(self.arbol.selection())

    def on_seleccionar(self, _evento=None):
        sel = self.arbol.selection()
        if not sel:
            return
        id_detalle = self.arbol.item(sel[0], "values")[0]
        try:
            fila = dao.obtener_vialidad(int(id_detalle))
        except InfraestructuraError as e:
            messagebox.showerror("Error", str(e))
            return
        if fila:
            id_, id_dir, id_tipo, nombre = fila
            self.var_id.set(id_)
            self.var_dir.set(id_dir)
            self.var_nombre.set(nombre or "")
            nombre_tipo = next((n for n, i in self.tipos.items() if i == id_tipo), self.SIN_TIPO)
            self.var_tipo.set(nombre_tipo)

    # --- acciones ---
    def on_agregar(self):
        try:
            id_dir = self._entero(self.var_dir.get(), "ID dirección")
            nuevo = dao.alta_vialidad(id_dir, self._id_tipo(), self.var_nombre.get())
            messagebox.showinfo("Alta", f"Vialidad agregada con ID {nuevo}.")
            self.var_b_nombre.set("")
            self.var_b_dir.set(str(id_dir))
            self.limpiar()
            self.cargar()
        except InfraestructuraError as e:
            messagebox.showerror("No se pudo agregar", str(e))

    def on_modificar(self):
        if not self.var_id.get():
            messagebox.showwarning("Modificar", "Selecciona una vialidad de la tabla.")
            return
        try:
            id_dir = self._entero(self.var_dir.get(), "ID dirección")
            dao.modificar_vialidad(int(self.var_id.get()), id_dir, self._id_tipo(),
                                   self.var_nombre.get())
            messagebox.showinfo("Modificar", "Vialidad actualizada.")
            self.cargar()
        except InfraestructuraError as e:
            messagebox.showerror("No se pudo modificar", str(e))

    def on_eliminar(self):
        if not self.var_id.get():
            messagebox.showwarning("Eliminar", "Selecciona una vialidad de la tabla.")
            return
        if not messagebox.askyesno("Eliminar", f"¿Eliminar la vialidad ID {self.var_id.get()}?"):
            return
        try:
            dao.eliminar_vialidad(int(self.var_id.get()))
            messagebox.showinfo("Eliminar", "Vialidad eliminada.")
            self.limpiar()
            self.cargar()
        except InfraestructuraError as e:
            messagebox.showerror("No se pudo eliminar", str(e))


# ----------------------------------------------------------------------
# Pestana de bitacora
# ----------------------------------------------------------------------
class BitacoraTab:
    def __init__(self, master):
        barra = ctk.CTkFrame(master, fg_color="transparent")
        barra.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(barra, text="Últimos 100 movimientos registrados por los triggers").pack(
            side="left", padx=4)
        ctk.CTkButton(barra, text="Actualizar", command=self.cargar).pack(side="right", padx=4)

        columnas = ("ID", "Tabla", "Operación", "ID registro", "Valor anterior",
                    "Valor nuevo", "Usuario", "Fecha")
        anchos = (50, 120, 80, 80, 220, 220, 130, 140)
        cont, self.arbol = _tabla(master, columnas, anchos)
        cont.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.cargar()

    def cargar(self):
        try:
            _llenar(self.arbol, dao.listar_bitacora())
        except InfraestructuraError as e:
            messagebox.showerror("Error", str(e))


# ----------------------------------------------------------------------
# Frame del modulo (lo que se integra en la ventana principal)
# ----------------------------------------------------------------------
class Modulo2Frame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text="Módulo 2 · Infraestructura Urbana",
                     font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)
        for nombre in ("Tipos de vialidad", "Asentamientos", "Vialidades", "Bitácora"):
            tabs.add(nombre)

        CatalogoTab(tabs.tab("Tipos de vialidad"), "Tipo de vialidad",
                    dao.listar_tipos_vialidad, dao.alta_tipo_vialidad,
                    dao.modificar_tipo_vialidad, dao.eliminar_tipo_vialidad)
        CatalogoTab(tabs.tab("Asentamientos"), "Tipo de asentamiento",
                    dao.listar_asentamientos, dao.alta_asentamiento,
                    dao.modificar_asentamiento, dao.eliminar_asentamiento)
        self.vialidades = VialidadesTab(tabs.tab("Vialidades"))
        self.bitacora = BitacoraTab(tabs.tab("Bitácora"))

        # Al entrar a una pestana se refresca lo que pudo cambiar en otra
        def al_cambiar():
            actual = tabs.get()
            if actual == "Vialidades":
                self.vialidades.recargar_tipos()
            elif actual == "Bitácora":
                self.bitacora.cargar()
        tabs.configure(command=al_cambiar)


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.title("SIACC - Módulo 2: Infraestructura Urbana")
    app.geometry("1150x650")
    Modulo2Frame(app).pack(fill="both", expand=True)
    app.mainloop()
