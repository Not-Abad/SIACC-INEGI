import customtkinter as ctk
from config.db import conectar, desconectar


def iniciar_app():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Sistema_SIACC - DENUE INEGI")
    app.geometry("900x600")

    # Verificación rápida al arrancar
    conn = conectar()
    estado = f"Conectado a {conn.database}" if conn.is_connected() else "Sin conexión"
    desconectar(conn)

    lbl = ctk.CTkLabel(app, text=f"Sistema_SIACC listo ({estado})", font=("Segoe UI", 18))
    lbl.pack(expand=True)

    app.mainloop()


if __name__ == "__main__":
    iniciar_app()
