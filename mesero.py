# mesero.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db import fetch_all, execute_query, fetch_one
import datetime

def iniciar_sesion():
    from auth import iniciar_sesion
    iniciar_sesion()

def acceder_como_mesero(rut_usuario):
    root = tk.Tk()
    root.title("Interfaz de Mesero")
    root.state('zoomed')

    tk.Label(root, text="Bienvenido a la Interfaz de Mesero", font=('Helvetica', 16)).pack(pady=20)

    tk.Button(root, text="Generar Comanda", command=lambda: generar_comanda(rut_usuario), height=3, width=20).pack(pady=20)
    tk.Button(root, text="Finalizar Venta", command=lambda: finalizar_venta(rut_usuario), height=3, width=20).pack(pady=20)
    tk.Button(root, text="Volver", command=lambda: (root.destroy(), iniciar_sesion())).pack(pady=20)

    def cerrar_sesion():
        root.destroy()
        iniciar_sesion()

    tk.Button(root, text="Cerrar Sesión", command=cerrar_sesion).pack(pady=20)

    root.mainloop()

def generar_comanda(rut_usuario):
    comanda_root = tk.Toplevel()
    comanda_root.title("Generar Comanda")
    comanda_root.state('zoomed')

    tk.Label(comanda_root, text="Generar Comanda", font=('Helvetica', 16)).pack(pady=20)

    tk.Label(comanda_root, text="Seleccione un producto:").pack(pady=5)
    productos_combo = ttk.Combobox(comanda_root, state="readonly")
    productos_combo.pack(pady=5)

    query = "SELECT producto_id, nombre FROM productos"
    productos = fetch_all(query)
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

    comanda_list = tk.Listbox(comanda_root, width=100)
    comanda_list.pack(pady=20, expand=True, fill='both')

    def agregar_producto():
        producto = productos[productos_combo.current()]
        cantidad = cantidad_entry.get()
        mesa = mesa_entry.get()
        comentario = comentario_entry.get()
        comanda_list.insert(tk.END, f"{producto[1]} (ID: {producto[0]}, Cantidad: {cantidad}, Mesa: {mesa}, Comentario: {comentario})")

    def guardar_comanda():
        try:
            for item in comanda_list.get(0, tk.END):
                producto_id = int(item.split('ID: ')[1].split(',')[0])
                cantidad = int(item.split('Cantidad: ')[1].split(',')[0])
                mesa = item.split('Mesa: ')[1].split(',')[0]
                comentario = item.split('Comentario: ')[1].split(')')[0]
                fecha_venta = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                metodo = "Pendiente"
                propina = 0.0
                estado_venta = "Pendiente"
                id_local = 1

                query = """
                    INSERT INTO ventas (rut_mesero, producto_id, cantidad, fecha_venta, metodo, propina, comentario, estado_venta, mesa, id_local)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                execute_query(query, (rut_usuario, producto_id, cantidad, fecha_venta, metodo, propina, comentario, estado_venta, mesa, id_local))
            messagebox.showinfo("Éxito", "Comanda guardada con éxito")
            comanda_root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar comanda: {e}")

    button_frame = tk.Frame(comanda_root)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Agregar Producto", command=agregar_producto).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Guardar Comanda", command=guardar_comanda).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Cerrar", command=comanda_root.destroy).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Volver", command=lambda: (comanda_root.destroy(), acceder_como_mesero(rut_usuario))).pack(side=tk.LEFT, padx=10)

    comanda_root.mainloop()

def finalizar_venta(rut_usuario):
    finalizar_root = tk.Toplevel()
    finalizar_root.title("Finalizar Venta")
    finalizar_root.state('zoomed')

    tk.Label(finalizar_root, text="Finalizar Venta", font=('Helvetica', 16)).pack(pady=20)

    columns = ("ID Venta", "Producto", "Cantidad", "Mesa", "Comentario", "Estado")
    tree = ttk.Treeview(finalizar_root, columns=columns, show="headings", selectmode="extended")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

    def cargar_ventas_pendientes():
        query = """
            SELECT v.venta_id, p.nombre, v.cantidad, v.mesa, v.comentario, v.estado_venta
            FROM ventas v
            JOIN productos p ON v.producto_id = p.producto_id
            WHERE v.estado_venta = 'Listo' AND v.rut_mesero = %s
        """
        rows = fetch_all(query, (rut_usuario,))
        for row in rows:
            tree.insert('', 'end', values=row)

    def calcular_totales():
        selected_items = tree.selection()
        subtotal = 0.0
        for item in selected_items:
            venta_id = tree.item(item, "values")[0]
            query = "SELECT SUM(p.precio * v.cantidad) FROM ventas v JOIN productos p ON v.producto_id = p.producto_id WHERE v.venta_id = %s"
            total_venta = fetch_one(query, (venta_id,))
            subtotal += float(total_venta[0])

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
                query = "SELECT SUM(p.precio * v.cantidad) FROM ventas v JOIN productos p ON v.producto_id = p.producto_id WHERE v.venta_id = %s"
                total_venta = fetch_one(query, (venta_id,))

                if propina_10_var.get():
                    propina = float(total_venta[0]) * 0.10
                elif propina_personalizada_var.get():
                    try:
                        propina = float(entry_propina_personalizada.get())
                    except ValueError:
                        messagebox.showerror("Error", "Ingrese una propina personalizada válida")
                        return
                else:
                    propina = 0.0

                query = "UPDATE ventas SET estado_venta = 'Pagado', metodo = %s, propina = %s WHERE venta_id = %s"
                execute_query(query, (metodo_pago, propina, venta_id))
            messagebox.showinfo("Éxito", "Venta finalizada con éxito")
            cargar_ventas_pendientes()
            calcular_totales()
        except Exception as e:
            messagebox.showerror("Error", f"Error al finalizar venta: {e}")

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
    entry_propina_personalizada.bind("<KeyRelease>", lambda event: calcular_totales())

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
    tk.Button(finalizar_root, text="Volver", command=lambda: (finalizar_root.destroy(), acceder_como_mesero(rut_usuario))).pack(pady=20)

    cargar_ventas_pendientes()
    tree.bind("<<TreeviewSelect>>", lambda event: calcular_totales())
    finalizar_root.mainloop()
