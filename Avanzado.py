import datetime
import mysql.connector
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from tkcalendar import Calendar, DateEntry

# Configuración de la conexión a la base de MariaDB en AmazonWebService
db_config = {
    'user': 'joaodevc_nicolas',
    'password': ',(2x#?9Na$xa',
    'host': '201.159.169.120',
    'database': 'joaodevc_cafeplanta3',
    'raise_on_warnings': True
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()


def iniciar_sesion():
    root = tk.Tk()
    root.title("Inicio de Sesión")
    root.state('zoomed')  # Pantalla completa

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
    tk.Button(root, text="Cocina", command=login_cocina).pack(pady=5)  # Nuevo botón para cocina

    root.mainloop()


def cocina():
    cocina_root = tk.Tk()
    cocina_root.title("Interfaz de Cocina")
    cocina_root.state('zoomed')  # Pantalla completa

    tk.Label(cocina_root, text="Comandas Generadas", font=('Helvetica', 16)).pack(pady=20)

    columns = ("ID Venta", "Producto", "Cantidad", "Mesa", "Comentario", "Estado")
    tree = ttk.Treeview(cocina_root, columns=columns, show="headings", selectmode="extended")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

    def cargar_comandas():
        try:
            for i in tree.get_children():
                tree.delete(i)
            cursor.execute("""
                SELECT v.venta_id, p.nombre, v.cantidad, v.mesa, v.comentario, v.estado_venta
                FROM ventas v
                JOIN productos p ON v.producto_id = p.producto_id
                WHERE v.estado_venta = 'Pendiente'
            """)
            rows = cursor.fetchall()
            for row in rows:
                tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al cargar las comandas: {err}")

    def marcar_como_listo():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Seleccione uno o más productos para marcar como listos")
            return

        try:
            for item in selected_items:
                venta_id = tree.item(item, "values")[0]
                cursor.execute("UPDATE ventas SET estado_venta = 'Listo' WHERE venta_id = %s", (venta_id,))
            conn.commit()
            messagebox.showinfo("Éxito", "Productos marcados como listos")
            cargar_comandas()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al actualizar el estado: {err}")

    def cerrar_cocina():
        cocina_root.destroy()
        iniciar_sesion()

    tk.Button(cocina_root, text="Marcar como Listo", command=marcar_como_listo).pack(pady=20)
    tk.Button(cocina_root, text="Cerrar", command=cerrar_cocina).pack(pady=20)

    cargar_comandas()
    cocina_root.mainloop()


def verificar_admins_o_crear():
    admins = obtener_admins()
    if not admins:
        crear_admin()
        verificar_admins_o_crear()
    else:
        login_admin_func(admins)


def obtener_admins():
    try:
        cursor.execute("SELECT rut, nombre, contraseña FROM personas WHERE responsabilidad = 'administrador'")
        resultados = cursor.fetchall()
        print(resultados)  # Agrega esta línea para depuración
        return resultados
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error en la base de datos: {err}")
        return []


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
    root.mainloop()


def crear_admin():
    root = tk.Tk()
    root.withdraw()
    rut = simpledialog.askstring("Nuevo Administrador", "Ingrese RUT:")
    nombre = simpledialog.askstring("Nuevo Administrador", "Ingrese Nombre:")
    usuario = simpledialog.askstring("Nuevo Administrador", "Ingrese Usuario:")
    contraseña = simpledialog.askstring("Nuevo Administrador", "Ingrese Contraseña:", show='*')
    contacto = simpledialog.askstring("Nuevo Administrador", "Ingrese Contacto:")
    cursor.execute(
        "INSERT INTO personas (rut, nombre, usuario, contraseña, contacto, responsabilidad) VALUES (%s, %s, %s, %s, %s, 'administrador')",
        (rut, nombre, usuario, contraseña, contacto))
    conn.commit()
    root.destroy()


def login_mesero_func():
    root = tk.Tk()
    root.title("Inicio de Sesión de Mesero")

    tk.Label(root, text="Seleccione su usuario:").pack(pady=10)

    cursor.execute(
        "SELECT rut, nombre, usuario, contraseña FROM personas WHERE responsabilidad IN ('mesero', 'administrador')")
    usuarios = cursor.fetchall()

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
    root.mainloop()


def admin_principal():
    root = tk.Tk()
    root.title("Panel de Administración")
    root.state('zoomed')

    tk.Button(root, text="Gestión de Personas", command=gestion_personas, height=3, width=20).pack(pady=20)
    tk.Button(root, text="Gestión de Productos", command=gestion_productos, height=3, width=20).pack(pady=20)
    tk.Button(root, text="Reportes", command=abrir_reportes, height=3, width=20).pack(pady=20)
    tk.Button(root, text="Calcular Propinas", command=calcular_propinas, height=3, width=20).pack(pady=20)

    root.mainloop()


def calcular_propinas():
    propinas_root = tk.Toplevel()
    propinas_root.title("Calcular Propinas")
    propinas_root.geometry("800x600")

    tk.Label(propinas_root, text="Calcular Propinas de Meseros", font=('Helvetica', 16)).pack(pady=20)

    tk.Label(propinas_root, text="Seleccione un mesero:").pack(pady=5)
    meseros_combo = ttk.Combobox(propinas_root, state="readonly")
    meseros_combo.pack(pady=5)

    cursor.execute("SELECT rut, nombre FROM personas WHERE responsabilidad IN ('mesero', 'administrador')")
    meseros = cursor.fetchall()
    meseros_combo['values'] = [f"{mesero[1]} ({mesero[0]})" for mesero in meseros]

    tk.Label(propinas_root, text="Seleccione una fecha:").pack(pady=5)
    fecha_entry = DateEntry(propinas_root, width=12, background='darkblue',
                            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    fecha_entry.pack(pady=5)

    def calcular():
        selected_mesero = meseros[meseros_combo.current()]
        selected_fecha = fecha_entry.get_date()

        cursor.execute("""
            SELECT SUM(propina) as total_propinas,
                   SUM(CASE WHEN metodo = 'Efectivo' THEN propina ELSE 0 END) as efectivo,
                   SUM(CASE WHEN metodo = 'Tarjeta' THEN propina ELSE 0 END) as tarjeta,
                   SUM(CASE WHEN metodo = 'Transferencia' THEN propina ELSE 0 END) as transferencia
            FROM ventas
            WHERE rut_mesero = %s AND DATE(fecha_venta) = %s
        """, (selected_mesero[0], selected_fecha))

        resultado = cursor.fetchone()
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
    propinas_root.mainloop()


def abrir_reportes():
    print("Abrir reportes")


def acceder_como_mesero(rut_usuario):
    mesero_root = tk.Tk()
    mesero_root.title("Interfaz de Mesero")
    mesero_root.state('zoomed')  # Pantalla completa

    tk.Label(mesero_root, text="Bienvenido a la Interfaz de Mesero", font=('Helvetica', 16)).pack(pady=20)

    tk.Button(mesero_root, text="Generar Comanda", command=lambda: generar_comanda(rut_usuario), height=3, width=20).pack(pady=20)
    tk.Button(mesero_root, text="Finalizar Venta", command=lambda: finalizar_venta(rut_usuario), height=3, width=20).pack(pady=20)

    def cerrar_sesion():
        mesero_root.destroy()
        iniciar_sesion()

    tk.Button(mesero_root, text="Cerrar Sesión", command=cerrar_sesion).pack(pady=20)

    mesero_root.mainloop()


def generar_comanda(rut_usuario):
    comanda_root = tk.Toplevel()
    comanda_root.title("Generar Comanda")
    comanda_root.state('zoomed')  # Pantalla completa

    tk.Label(comanda_root, text="Generar Comanda", font=('Helvetica', 16)).pack(pady=20)

    tk.Label(comanda_root, text="Seleccione un producto:").pack(pady=5)
    productos_combo = ttk.Combobox(comanda_root, state="readonly")
    productos_combo.pack(pady=5)

    cursor.execute("SELECT producto_id, nombre FROM productos")
    productos = cursor.fetchall()
    productos_combo['values'] = [f"{producto[1]} ({producto[0]})" for producto in productos]

    tk.Label(comanda_root, text="Cantidad:").pack(pady=5)
    cantidad_entry = tk.Entry(comanda_root)
    cantidad_entry.pack(pady=5)

    tk.Label(comanda_root, text="Mesa:").pack(pady=5)
    mesa_entry = tk.Entry(comanda_root)
    mesa_entry.pack(pady=5)

    tk.Label(comanda_root, text="Comentario:").pack(pady=5)
    comentario_entry = tk.Entry(comanda_root)
    comentario_entry.pack(pady=5)

    comanda_list = tk.Listbox(comanda_root, width=100)  # Aumentar el ancho de la lista
    comanda_list.pack(pady=20, expand=True, fill='both')

    def agregar_producto():
        producto = productos[productos_combo.current()]
        cantidad = cantidad_entry.get()
        mesa = mesa_entry.get()
        comentario = comentario_entry.get()
        comanda_list.insert(tk.END,
                            f"{producto[1]} (ID: {producto[0]}, Cantidad: {cantidad}, Mesa: {mesa}, Comentario: {comentario})")

    def guardar_comanda():
        try:
            for item in comanda_list.get(0, tk.END):
                # Extraer la información del item
                producto_id = int(item.split('ID: ')[1].split(',')[0])
                cantidad = int(item.split('Cantidad: ')[1].split(',')[0])
                mesa = item.split('Mesa: ')[1].split(',')[0]
                comentario = item.split('Comentario: ')[1].split(')')[0]
                fecha_venta = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                metodo = "Pendiente"
                propina = 0.0
                estado_venta = "Pendiente"
                id_local = 1

                cursor.execute("""
                    INSERT INTO ventas (rut_mesero, producto_id, cantidad, fecha_venta, metodo, propina, comentario, estado_venta, mesa, id_local)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    rut_usuario, producto_id, cantidad, fecha_venta, metodo, propina, comentario, estado_venta, mesa,
                    id_local))
            conn.commit()
            messagebox.showinfo("Éxito", "Comanda guardada con éxito")
            comanda_root.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error en la base de datos: {err}")
        except ValueError:
            messagebox.showerror("Error de entrada",
                                 "Por favor, asegúrese de que los campos de cantidad son números válidos.")

    # Crear un frame para los botones en la parte inferior y organizar los botones horizontalmente
    button_frame = tk.Frame(comanda_root)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Agregar Producto", command=agregar_producto).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Guardar Comanda", command=guardar_comanda).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Cerrar", command=comanda_root.destroy).pack(side=tk.LEFT, padx=10)

    comanda_root.mainloop()


def finalizar_venta(rut_usuario):
    finalizar_root = tk.Toplevel()
    finalizar_root.title("Finalizar Venta")
    finalizar_root.state('zoomed')  # Pantalla completa

    tk.Label(finalizar_root, text="Finalizar Venta", font=('Helvetica', 16)).pack(pady=20)

    columns = ("ID Venta", "Producto", "Cantidad", "Mesa", "Comentario", "Estado")
    tree = ttk.Treeview(finalizar_root, columns=columns, show="headings", selectmode="extended")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

    def cargar_ventas_pendientes():
        try:
            for i in tree.get_children():
                tree.delete(i)
            cursor.execute("""
                SELECT v.venta_id, p.nombre, v.cantidad, v.mesa, v.comentario, v.estado_venta
                FROM ventas v
                JOIN productos p ON v.producto_id = p.producto_id
                WHERE v.estado_venta = 'Listo' AND v.rut_mesero = %s
            """, (rut_usuario,))
            rows = cursor.fetchall()
            for row in rows:
                tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al cargar las ventas pendientes: {err}")

    def calcular_totales():
        selected_items = tree.selection()
        subtotal = 0.0
        for item in selected_items:
            venta_id = tree.item(item, "values")[0]
            cursor.execute(
                "SELECT SUM(p.precio * v.cantidad) FROM ventas v JOIN productos p ON v.producto_id = p.producto_id WHERE v.venta_id = %s",
                (venta_id,))
            total_venta = cursor.fetchone()[0]
            subtotal += float(total_venta)

        propina = 0.0
        if propina_10_var.get():
            propina = subtotal * 0.10
        elif propina_personalizada_var.get():
            propina_personalizada = entry_propina_personalizada.get()
            if propina_personalizada:
                try:
                    propina = float(propina_personalizada)
                except ValueError:
                    propina = 0.0

        total = subtotal + propina

        subtotal_var.set(f"{subtotal:.2f}")
        propina_var.set(f"{propina:.2f}")
        total_var.set(f"{total:.2f}")

    def finalizar_venta_seleccionada():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Seleccione una venta para finalizar")
            return

        metodo_pago = metodo_pago_var.get()
        if not metodo_pago:
            messagebox.showerror("Error", "Seleccione un método de pago")
            return

        try:
            for item in selected_items:
                venta_id = tree.item(item, "values")[0]
                cursor.execute(
                    "SELECT SUM(p.precio * v.cantidad) FROM ventas v JOIN productos p ON v.producto_id = p.producto_id WHERE v.venta_id = %s",
                    (venta_id,))
                total_venta = cursor.fetchone()[0]

                if propina_10_var.get():
                    propina = float(total_venta) * 0.10
                elif propina_personalizada_var.get():
                    try:
                        propina = float(entry_propina_personalizada.get())
                    except ValueError:
                        messagebox.showerror("Error", "Ingrese una propina personalizada válida")
                        return
                else:
                    propina = 0.0

                cursor.execute("""
                    UPDATE ventas 
                    SET estado_venta = 'Pagado', metodo = %s, propina = %s
                    WHERE venta_id = %s
                """, (metodo_pago, propina, venta_id))
            conn.commit()
            messagebox.showinfo("Éxito", "Venta finalizada con éxito")
            cargar_ventas_pendientes()
            calcular_totales()  # Actualizar los totales después de finalizar la venta
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al finalizar la venta: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"Un error ocurrió: {str(e)}")

    metodo_pago_var = tk.StringVar()
    propina_10_var = tk.BooleanVar()
    propina_personalizada_var = tk.BooleanVar()
    subtotal_var = tk.StringVar()
    propina_var = tk.StringVar()
    total_var = tk.StringVar()

    tk.Label(finalizar_root, text="Método de Pago:").pack(pady=5)
    tk.Radiobutton(finalizar_root, text="Efectivo", variable=metodo_pago_var, value="Efectivo").pack(anchor=tk.W)
    tk.Radiobutton(finalizar_root, text="Tarjeta", variable=metodo_pago_var, value="Tarjeta").pack(anchor=tk.W)
    tk.Radiobutton(finalizar_root, text="Transferencia", variable=metodo_pago_var, value="Transferencia").pack(anchor=tk.W)

    tk.Label(finalizar_root, text="Propina:").pack(pady=5)
    tk.Checkbutton(finalizar_root, text="10%", variable=propina_10_var, command=lambda: (propina_personalizada_var.set(False), calcular_totales())).pack(anchor=tk.W)
    tk.Checkbutton(finalizar_root, text="Personalizada", variable=propina_personalizada_var, command=lambda: (propina_10_var.set(False), calcular_totales())).pack(anchor=tk.W)
    entry_propina_personalizada = tk.Entry(finalizar_root)
    entry_propina_personalizada.pack(anchor=tk.W, padx=20)
    entry_propina_personalizada.bind("<KeyRelease>", lambda event: calcular_totales())  # Actualizar totales al cambiar la propina personalizada

    # Frame para los totales
    totales_frame = tk.Frame(finalizar_root)
    totales_frame.pack(pady=10)

    tk.Label(totales_frame, text="Subtotal:").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(totales_frame, textvariable=subtotal_var).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(totales_frame, text="Propina:").grid(row=1, column=0, padx=10, pady=5)
    tk.Label(totales_frame, textvariable=propina_var).grid(row=1, column=1, padx=10, pady=5)

    tk.Label(totales_frame, text="Total:").grid(row=2, column=0, padx=10, pady=5)
    tk.Label(totales_frame, textvariable=total_var).grid(row=2, column=1, padx=10, pady=5)

    tk.Button(finalizar_root, text="Finalizar Venta Seleccionada", command=finalizar_venta_seleccionada).pack(pady=20)
    tk.Button(finalizar_root, text="Cerrar", command=finalizar_root.destroy).pack(pady=20)

    cargar_ventas_pendientes()
    tree.bind("<<TreeviewSelect>>", lambda event: calcular_totales())  # Actualizar totales al seleccionar ventas
    finalizar_root.mainloop()



def gestion_personas():
    gestion_root = tk.Toplevel()
    gestion_root.title("Gestión de Personas")
    gestion_root.state('zoomed')  # Pantalla completa

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
    combo_responsabilidad = ttk.Combobox(gestion_root, values=["mesero", "administrador", "cocinero"],
                                         state="readonly")
    combo_responsabilidad.grid(row=11, column=1, padx=10, pady=10)

    btn_guardar = tk.Button(gestion_root, text="Guardar Persona", command=lambda: guardar_persona(
        entry_rut.get(), entry_nombre.get(), entry_usuario.get(), entry_contraseña.get(), entry_contacto.get(),
        entry_calle.get(), entry_numero.get(), combo_comuna.get(), combo_ciudad.get(), combo_region.get(),
        combo_pais.get(), combo_responsabilidad.get()))
    btn_guardar.grid(row=12, column=1, padx=10, pady=20)

    btn_modificar_persona = tk.Button(gestion_root, text="Modificar Persona", command=modificar_persona)
    btn_modificar_persona.grid(row=14, column=0, padx=10, pady=20, columnspan=2)

    gestion_root.mainloop()


def obtener_datos_unicos(campo):
    cursor.execute(f"SELECT DISTINCT {campo} FROM personas WHERE {campo} IS NOT NULL")
    resultados = cursor.fetchall()
    return [item[0] for item in resultados]


def guardar_persona(rut, nombre, usuario, contraseña, contacto, calle, numero, comuna, ciudad, region, pais,
                    responsabilidad):
    try:
        cursor.execute(
            "INSERT INTO personas (rut, nombre, usuario, contraseña, contacto, calle, numero, comuna, ciudad, region, pais, responsabilidad) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (rut, nombre, usuario, contraseña, contacto, calle, int(numero), comuna, ciudad, region, pais,
             responsabilidad))
        conn.commit()
        messagebox.showinfo("Éxito", "Persona guardada con éxito")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error en la base de datos: {err}")
    except ValueError as ve:
        messagebox.showerror("Error de Tipo", "Por favor, asegúrese de que el número de calle es un valor numérico.")


def obtener_ruts():
    cursor.execute("SELECT rut FROM personas")
    return [rut[0] for rut in cursor.fetchall()]


def modificar_persona():
    mod_root = tk.Toplevel()
    mod_root.title("Modificar Persona")
    mod_root.geometry("600x800")

    tk.Label(mod_root, text="Seleccione RUT:").grid(row=0, column=0, padx=10, pady=10)
    combo_rut = ttk.Combobox(mod_root, values=obtener_ruts())
    combo_rut.grid(row=0, column=1, padx=10, pady=10)

    entries = {}
    for i, field in enumerate(
            ["Nombre", "Usuario", "Contraseña", "Contacto", "Calle", "Número", "Comuna", "Ciudad", "Región", "País",
             "Responsabilidad"], start=1):
        tk.Label(mod_root, text=f"{field}:").grid(row=i, column=0, padx=10, pady=10)
        entry = ttk.Entry(mod_root)
        entry.grid(row=i, column=1, padx=10, pady=10)
        entries[field.lower()] = entry

    def cargar_datos():
        rut = combo_rut.get()
        cursor.execute(
            "SELECT nombre, usuario, contraseña, contacto, calle, numero, comuna, ciudad, region, pais, responsabilidad FROM personas WHERE rut = %s",
            (rut,))
        datos = cursor.fetchone()
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
            cursor.execute(
                "UPDATE personas SET nombre=%s, usuario=%s, contraseña=%s, contacto=%s, calle=%s, numero=%s, comuna=%s, ciudad=%s, region=%s, pais=%s, responsabilidad=%s WHERE rut=%s",
                tuple(updates))
            conn.commit()
            messagebox.showinfo("Éxito", "Datos actualizados con éxito")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error en la base de datos: {err}")

    btn_guardar = tk.Button(mod_root, text="Guardar Cambios", command=guardar_cambios)
    btn_guardar.grid(row=13, column=1, padx=10, pady=20)

    mod_root.mainloop()


def gestion_productos():
    productos_root = tk.Toplevel()
    productos_root.title("Gestión de Productos")
    productos_root.state('zoomed')  # Pantalla completa

    tk.Button(productos_root, text="Añadir Producto", command=añadir_producto).pack(pady=5)
    tk.Button(productos_root, text="Modificar Producto", command=lambda: modificar_producto(tree)).pack(pady=5)
    tk.Button(productos_root, text="Eliminar Producto", command=lambda: eliminar_producto(tree)).pack(pady=5)

    columns = ("ID", "Nombre", "Precio", "Descripción")
    tree = ttk.Treeview(productos_root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

    cargar_productos(tree)
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
            cursor.execute("INSERT INTO productos (nombre, precio, descripción, costo) VALUES (%s, %s, %s, %s)",
                           (nombre.get(), float(precio.get()), descripcion.get(), float(costo.get())))
            conn.commit()
            messagebox.showinfo("Guardado", "Producto guardado con éxito")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error en la base de datos: {err}")
        except ValueError:
            messagebox.showerror("Error de entrada",
                                 "Por favor, asegúrese de que los campos de precio y costo son números válidos.")
        add_root.destroy()

    tk.Button(add_root, text="Guardar", command=guardar_producto).grid(row=4, column=1)
    add_root.mainloop()


def cargar_productos(tree):
    try:
        for i in tree.get_children():
            tree.delete(i)
        cursor.execute("SELECT producto_id, nombre, precio, descripción, costo FROM productos")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert('', 'end', values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al cargar los productos: {err}")
    except Exception as e:
        messagebox.showerror("Error", f"Un error ocurrió: {str(e)}")


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
            cursor.execute(
                "UPDATE productos SET nombre=%s, precio=%s, descripción=%s, costo=%s WHERE producto_id=%s",
                (updated_values[0], float(updated_values[1]), updated_values[2], float(updated_values[3]), producto_id)
            )
            conn.commit()
            cargar_productos(tree)
            messagebox.showinfo("Éxito", "Producto actualizado con éxito")
            mod_root.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error en la base de datos: {err}")
        except ValueError:
            messagebox.showerror("Error de entrada",
                                 "Por favor, asegúrese de que los campos de precio y costo sean números válidos.")

    tk.Button(mod_root, text="Actualizar", command=actualizar_producto).grid(row=len(labels), column=1, pady=10)
    mod_root.mainloop()


def eliminar_producto(tree):
    if not tree.selection():
        messagebox.showerror("Error", "Seleccione un producto para eliminar")
        return

    selected_item = tree.selection()[0]
    item_id = tree.item(selected_item, "values")[0]

    if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este producto?"):
        try:
            cursor.execute("DELETE FROM productos WHERE producto_id = %s", (item_id,))
            conn.commit()
            cargar_productos(tree)
            messagebox.showinfo("Eliminado", "Producto eliminado con éxito")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al intentar eliminar el producto: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"Un error ocurrió: {str(e)}")


if __name__ == "__main__":
    iniciar_sesion()