# admin.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from db import fetch_all, fetch_one, execute_query

def admin_principal():
    root = tk.Tk()
    root.title("Panel de Administración")
    root.state('zoomed')

    tk.Button(root, text="Gestión de Personas", command=gestion_personas, height=3, width=20).pack(pady=20)
    tk.Button(root, text="Gestión de Productos", command=gestion_productos, height=3, width=20).pack(pady=20)
    tk.Button(root, text="Reportes", command=abrir_reportes, height=3, width=20).pack(pady=20)
    tk.Button(root, text="Calcular Propinas", command=calcular_propinas, height=3, width=20).pack(pady=20)
    tk.Button(root, text="Volver", command=lambda: (root.destroy(), from auth import iniciar_sesion, iniciar_sesion())).pack(pady=20)

    root.mainloop()

def calcular_propinas():
    propinas_root = tk.Toplevel()
    propinas_root.title("Calcular Propinas")
    propinas_root.geometry("800x600")

    tk.Label(propinas_root, text="Calcular Propinas de Meseros", font=('Helvetica', 16)).pack(pady=20)

    tk.Label(propinas_root, text="Seleccione un mesero:").pack(pady=5)
    meseros_combo = ttk.Combobox(propinas_root, state="readonly")
    meseros_combo.pack(pady=5)

    query = "SELECT rut, nombre FROM personas WHERE responsabilidad IN ('mesero', 'administrador')"
    meseros = fetch_all(query)
    meseros_combo['values'] = [f"{mesero[1]} ({mesero[0]})" for mesero in meseros]

    tk.Label(propinas_root, text="Seleccione una fecha:").pack(pady=5)
    fecha_entry = DateEntry(propinas_root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    fecha_entry.pack(pady=5)

    def calcular():
        selected_mesero = meseros[meseros_combo.current()]
        selected_fecha = fecha_entry.get_date()

        query = """
            SELECT SUM(propina) as total_propinas,
                   SUM(CASE WHEN metodo = 'Efectivo' THEN propina ELSE 0 END) as efectivo,
                   SUM(CASE WHEN metodo = 'Tarjeta' THEN propina ELSE 0 END) as tarjeta,
                   SUM(CASE WHEN metodo = 'Transferencia' THEN propina ELSE 0 END) as transferencia
            FROM ventas
            WHERE rut_mesero = %s AND DATE(fecha_venta) = %s
        """
        resultado = fetch_one(query, (selected_mesero[0], selected_fecha))
        total_propinas, efectivo, tarjeta, transferencia = resultado

        tree.delete(*tree.get_children())
        tree.insert('', 'end', values=("Total Propinas", total_propinas))
        tree.insert('', 'end', values=("Efectivo", efectivo))
        tree.insert('', 'end', values=("Tarjeta", tarjeta))
        tree.insert('', 'end', values=("Transferencia", transferencia))

    tk.Button(propinas_root, text="Calcular", command=calcular).pack(pady=20)

    columns = ("Método", "Total")
    tree = ttk.Treeview(propinas_root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

    tk.Button(propinas_root, text="Cerrar", command=propinas_root.destroy).pack(pady=20)
    tk.Button(propinas_root, text="Volver", command=lambda: (propinas_root.destroy(), admin_principal())).pack(pady=20)
    propinas_root.mainloop()

def abrir_reportes():
    print("Abrir reportes")

def gestion_personas():
    gestion_root = tk.Toplevel()
    gestion_root.title("Gestión de Personas")
    gestion_root.state('zoomed')

    tk.Label(gestion_root, text="RUT:").grid(row=0, column=0, padx=10, pady=10)
    entry_rut = tk.Entry(gestion_root)
    entry_rut.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Nombre:").grid(row=1, column=0, padx=10, pady=10)
    entry_nombre = tk.Entry(gestion_root)
    entry_nombre.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Usuario:").grid(row=2, column=0, padx=10, pady=10)
    entry_usuario = tk.Entry(gestion_root)
    entry_usuario.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Contraseña:").grid(row=3, column=0, padx=10, pady=10)
    entry_contraseña = tk.Entry(gestion_root, show='*')
    entry_contraseña.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Contacto:").grid(row=4, column=0, padx=10, pady=10)
    entry_contacto = tk.Entry(gestion_root)
    entry_contacto.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Calle:").grid(row=5, column=0, padx=10, pady=10)
    entry_calle = tk.Entry(gestion_root)
    entry_calle.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Número:").grid(row=6, column=0, padx=10, pady=10)
    entry_numero = tk.Entry(gestion_root)
    entry_numero.grid(row=6, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="País:").grid(row=7, column=0, padx=10, pady=10)
    combo_pais = ttk.Combobox(gestion_root, values=obtener_datos_unicos('pais'))
    combo_pais.grid(row=7, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Región:").grid(row=8, column=0, padx=10, pady=10)
    combo_region = ttk.Combobox(gestion_root, values=obtener_datos_unicos('region'))
    combo_region.grid(row=8, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Ciudad:").grid(row=9, column=0, padx=10, pady=10)
    combo_ciudad = ttk.Combobox(gestion_root, values=obtener_datos_unicos('ciudad'))
    combo_ciudad.grid(row=9, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Comuna:").grid(row=10, column=0, padx=10, pady=10)
    combo_comuna = ttk.Combobox(gestion_root, values=obtener_datos_unicos('comuna'))
    combo_comuna.grid(row=10, column=1, padx=10, pady=10)

    tk.Label(gestion_root, text="Responsabilidad:").grid(row=11, column=0, padx=10, pady=10)
    combo_responsabilidad = ttk.Combobox(gestion_root, values=["mesero", "administrador", "cocinero"], state="readonly")
    combo_responsabilidad.grid(row=11, column=1, padx=10, pady=10)

    btn_guardar = tk.Button(gestion_root, text="Guardar Persona", command=lambda: guardar_persona(
        entry_rut.get(), entry_nombre.get(), entry_usuario.get(), entry_contraseña.get(), entry_contacto.get(),
        entry_calle.get(), entry_numero.get(), combo_comuna.get(), combo_ciudad.get(), combo_region.get(),
        combo_pais.get(), combo_responsabilidad.get()))
    btn_guardar.grid(row=12, column=1, padx=10, pady=20)

    btn_modificar_persona = tk.Button(gestion_root, text="Modificar Persona", command=modificar_persona)
    btn_modificar_persona.grid(row=14, column=0, padx=10, pady=20, columnspan=2)
    tk.Button(gestion_root, text="Volver", command=lambda: (gestion_root.destroy(), admin_principal())).pack(pady=20)

    gestion_root.mainloop()

def obtener_datos_unicos(campo):
    query = f"SELECT DISTINCT {campo} FROM personas WHERE {campo} IS NOT NULL"
    resultados = fetch_all(query)
    return [item[0] for item in resultados]

def guardar_persona(rut, nombre, usuario, contraseña, contacto, calle, numero, comuna, ciudad, region, pais,
                    responsabilidad):
    try:
        query = "INSERT INTO personas (rut, nombre, usuario, contraseña, contacto, calle, numero, comuna, ciudad, region, pais, responsabilidad) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        execute_query(query, (rut, nombre, usuario, contraseña, contacto, calle, int(numero), comuna, ciudad, region, pais, responsabilidad))
        messagebox.showinfo("Éxito", "Persona guardada con éxito")
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar persona: {e}")

def obtener_ruts():
    query = "SELECT rut FROM personas"
    return [rut[0] for rut in fetch_all(query)]

def modificar_persona():
    mod_root = tk.Toplevel()
    mod_root.title("Modificar Persona")
    mod_root.geometry("600x800")

    tk.Label(mod_root, text="Seleccione RUT:").grid(row=0, column=0, padx=10, pady=10)
    combo_rut = ttk.Combobox(mod_root, values=obtener_ruts())
    combo_rut.grid(row=0, column=1, padx=10, pady=10)

    entries = {}
    for i, field in enumerate(["Nombre", "Usuario", "Contraseña", "Contacto", "Calle", "Número", "Comuna", "Ciudad", "Región", "País", "Responsabilidad"], start=1):
        tk.Label(mod_root, text=f"{field}:").grid(row=i, column=0, padx=10, pady=10)
        entry = ttk.Entry(mod_root)
        entry.grid(row=i, column=1, padx=10, pady=10)
        entries[field.lower()] = entry

    def cargar_datos():
        rut = combo_rut.get()
        query = "SELECT nombre, usuario, contraseña, contacto, calle, numero, comuna, ciudad, region, pais, responsabilidad FROM personas WHERE rut = %s"
        datos = fetch_one(query, (rut,))
        if datos:
            for (key, entry), value in zip(entries.items(), datos):
                entry.delete(0, tk.END)
                entry.insert(0, value)

    btn_cargar = tk.Button(mod_root, text="Cargar Datos", command=cargar_datos)
    btn_cargar.grid(row=12, column=1, padx=10, pady=20)

    def guardar_cambios():
        try:
            updates = [entry.get() for entry in entries.values()]
            updates.append(combo_rut.get())
            query = "UPDATE personas SET nombre=%s, usuario=%s, contraseña=%s, contacto=%s, calle=%s, numero=%s, comuna=%s, ciudad=%s, region=%s, pais=%s, responsabilidad=%s WHERE rut=%s"
            execute_query(query, tuple(updates))
            messagebox.showinfo("Éxito", "Datos actualizados con éxito")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar persona: {e}")

    btn_guardar = tk.Button(mod_root, text="Guardar Cambios", command=guardar_cambios)
    btn_guardar.grid(row=13, column=1, padx=10, pady=20)

    mod_root.mainloop()

def gestion_productos():
    productos_root = tk.Toplevel()
    productos_root.title("Gestión de Productos")
    productos_root.state('zoomed')

    tk.Button(productos_root, text="Añadir Producto", command=añadir_producto).pack(pady=5)
    tk.Button(productos_root, text="Modificar Producto", command=lambda: modificar_producto(tree)).pack(pady=5)
    tk.Button(productos_root, text="Eliminar Producto", command=lambda: eliminar_producto(tree)).pack(pady=5)

    columns = ("ID", "Nombre", "Precio", "Descripción")
    tree = ttk.Treeview(productos_root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

    cargar_productos(tree)
    tk.Button(productos_root, text="Volver", command=lambda: (productos_root.destroy(), admin_principal())).pack(pady=20)
    productos_root.mainloop()

def añadir_producto():
    add_root = tk.Toplevel()
    add_root.title("Añadir Nuevo Producto")

    tk.Label(add_root, text="Nombre:").grid(row=0, column=0)
    nombre = tk.Entry(add_root)
    nombre.grid(row=0, column=1)

    tk.Label(add_root, text="Precio:").grid(row=1, column=0)
    precio = tk.Entry(add_root)
    precio.grid(row=1, column=1)

    tk.Label(add_root, text="Descripción:").grid(row=2, column=0)
    descripcion = tk.Entry(add_root)
    descripcion.grid(row=2, column=1)

    tk.Label(add_root, text="Costo:").grid(row=3, column=0)
    costo = tk.Entry(add_root)
    costo.grid(row=3, column=1)

    def guardar_producto():
        try:
            query = "INSERT INTO productos (nombre, precio, descripción, costo) VALUES (%s, %s, %s, %s)"
            execute_query(query, (nombre.get(), float(precio.get()), descripcion.get(), float(costo.get())))
            messagebox.showinfo("Guardado", "Producto guardado con éxito")
            add_root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar producto: {e}")

    tk.Button(add_root, text="Guardar", command=guardar_producto).grid(row=4, column=1)
    tk.Button(add_root, text="Volver", command=lambda: (add_root.destroy(), gestion_productos())).pack(pady=20)
    add_root.mainloop()

def cargar_productos(tree):
    try:
        for i in tree.get_children():
            tree.delete(i)
        query = "SELECT producto_id, nombre, precio, descripción, costo FROM productos"
        rows = fetch_all(query)
        for row in rows:
            tree.insert('', 'end', values=row)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar productos: {e}")

def modificar_producto(tree):
    if not tree.selection():
        messagebox.showerror("Error", "Seleccione un producto para modificar")
        return

    selected_item = tree.selection()[0]
    item_values = tree.item(selected_item, "values")
    producto_id = item_values[0]

    mod_root = tk.Toplevel()
    mod_root.title("Modificar Producto")

    labels = ["Nombre", "Precio", "Descripción", "Costo"]
    entries = {}
    for index, field in enumerate(labels):
        tk.Label(mod_root, text=f"{field}:").grid(row=index, column=0, sticky="e")
        entry = tk.Entry(mod_root, width=50)
        entry.insert(0, item_values[index + 1])
        entry.grid(row=index, column=1)
        entries[field.lower()] = entry

    def actualizar_producto():
        try:
            updated_values = [entry.get() for entry in entries.values()]
            query = "UPDATE productos SET nombre=%s, precio=%s, descripción=%s, costo=%s WHERE producto_id=%s"
            execute_query(query, (updated_values[0], float(updated_values[1]), updated_values[2], float(updated_values[3]), producto_id))
            cargar_productos(tree)
            messagebox.showinfo("Éxito", "Producto actualizado con éxito")
            mod_root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar producto: {e}")

    tk.Button(mod_root, text="Actualizar", command=actualizar_producto).grid(row=len(labels), column=1, pady=10)
    tk.Button(mod_root, text="Volver", command=lambda: (mod_root.destroy(), gestion_productos())).pack(pady=20)
    mod_root.mainloop()

def eliminar_producto(tree):
    if not tree.selection():
        messagebox.showerror("Error", "Seleccione un producto para eliminar")
        return

    selected_item = tree.selection()[0]
    item_id = tree.item(selected_item, "values")[0]

    if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este producto?"):
        try:
            query = "DELETE FROM productos WHERE producto_id = %s"
            execute_query(query, (item_id,))
            cargar_productos(tree)
            messagebox.showinfo("Eliminado", "Producto eliminado con éxito")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar producto: {e}")
