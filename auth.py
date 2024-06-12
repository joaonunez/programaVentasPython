# auth.py
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from db import fetch_all, execute_query
from admin import admin_principal
from mesero import acceder_como_mesero
from cocina import cocina

def iniciar_sesion():
    root = tk.Tk()
    root.title("Inicio de Sesión")
    root.state('zoomed')

    tk.Label(root, text="Seleccione su rol:").pack(pady=10)

    def login_admin():
        root.destroy()
        verificar_admins_o_crear()

    def login_mesero():
        root.destroy()
        login_mesero_func()

    def login_cocina():
        root.destroy()
        cocina()

    tk.Button(root, text="Administrador", command=login_admin).pack(pady=5)
    tk.Button(root, text="Mesero", command=login_mesero).pack(pady=5)
    tk.Button(root, text="Cocina", command=login_cocina).pack(pady=5)

    root.mainloop()

def verificar_admins_o_crear():
    admins = obtener_admins()
    if not admins:
        crear_admin()
        verificar_admins_o_crear()
    else:
        login_admin_func(admins)

def obtener_admins():
    query = "SELECT rut, nombre, contraseña FROM personas WHERE responsabilidad = 'administrador'"
    return fetch_all(query)

def login_admin_func(admins):
    root = tk.Tk()
    root.title("Inicio de sesión de Administrador")

    tk.Label(root, text="Seleccione un administrador:").pack(pady=10)

    combo = ttk.Combobox(root, values=[f"{adm[1]} ({adm[0]})" for adm in admins], state="readonly")
    combo.pack(pady=5)

    def on_login_clicked():
        selected_admin = admins[combo.current()]
        contraseña = simpledialog.askstring("Inicio de Sesión", "Ingrese contraseña de administrador:", show='*')
        if contraseña == selected_admin[2]:
            messagebox.showinfo("Bienvenido", f"Bienvenido {selected_admin[1]}")
            rut_usuario = selected_admin[0]
            root.destroy()
            admin_principal()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    tk.Button(root, text="Iniciar sesión", command=on_login_clicked).pack(pady=20)
    tk.Button(root, text="Volver", command=lambda: (root.destroy(), iniciar_sesion())).pack(pady=20)
    root.mainloop()

def crear_admin():
    root = tk.Tk()
    root.withdraw()
    rut = simpledialog.askstring("Nuevo Administrador", "Ingrese RUT:")
    nombre = simpledialog.askstring("Nuevo Administrador", "Ingrese Nombre:")
    usuario = simpledialog.askstring("Nuevo Administrador", "Ingrese Usuario:")
    contraseña = simpledialog.askstring("Nuevo Administrador", "Ingrese Contraseña:", show='*')
    contacto = simpledialog.askstring("Nuevo Administrador", "Ingrese Contacto:")

    query = "INSERT INTO personas (rut, nombre, usuario, contraseña, contacto, responsabilidad) VALUES (%s, %s, %s, %s, %s, 'administrador')"
    execute_query(query, (rut, nombre, usuario, contraseña, contacto))
    root.destroy()

def login_mesero_func():
    root = tk.Tk()
    root.title("Inicio de Sesión de Mesero")

    tk.Label(root, text="Seleccione su usuario:").pack(pady=10)

    query = "SELECT rut, nombre, usuario, contraseña FROM personas WHERE responsabilidad IN ('mesero', 'administrador')"
    usuarios = fetch_all(query)

    combo = ttk.Combobox(root, values=[f"{usuario[1]} ({usuario[2]})" for usuario in usuarios], state="readonly")
    combo.pack(pady=5)

    tk.Label(root, text="Ingrese su contraseña:").pack(pady=10)
    contraseña_entry = tk.Entry(root, show='*')
    contraseña_entry.pack(pady=5)

    def on_login_clicked():
        selected_usuario = usuarios[combo.current()]
        contraseña = contraseña_entry.get()
        if contraseña == selected_usuario[3]:
            messagebox.showinfo("Bienvenido", f"Bienvenido {selected_usuario[1]}")
            rut_usuario = selected_usuario[0]
            root.destroy()
            if selected_usuario[2] == 'administrador':
                admin_principal()
            else:
                acceder_como_mesero(rut_usuario)
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    tk.Button(root, text="Iniciar sesión", command=on_login_clicked).pack(pady=20)
    tk.Button(root, text="Volver", command=lambda: (root.destroy(), iniciar_sesion())).pack(pady=20)
    root.mainloop()
