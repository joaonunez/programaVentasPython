# cocina.py
import tkinter as tk
from tkinter import ttk, messagebox
from db import fetch_all, execute_query

def cocina():
    root = tk.Tk()
    root.title("Interfaz de Cocina")
    root.state('zoomed')

    tk.Label(root, text="Comandas Generadas", font=('Helvetica', 16)).pack(pady=20)

    columns = ("ID Venta", "Producto", "Cantidad", "Mesa", "Comentario", "Estado")
    tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="extended")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(expand=True, fill='both')

    def cargar_comandas():
        query = """
            SELECT v.venta_id, p.nombre, v.cantidad, v.mesa, v.comentario, v.estado_venta
            FROM ventas v
            JOIN productos p ON v.producto_id = p.producto_id
            WHERE v.estado_venta = 'Pendiente'
        """
        rows = fetch_all(query)
        for row in rows:
            tree.insert('', 'end', values=row)

    def marcar_como_listo():
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Seleccione uno o más productos para marcar como listos")
            return

        for item in selected_items:
            venta_id = tree.item(item, "values")[0]
            query = "UPDATE ventas SET estado_venta = 'Listo' WHERE venta_id = %s"
            execute_query(query, (venta_id,))
        messagebox.showinfo("Éxito", "Productos marcados como listos")
        cargar_comandas()

    def cerrar_cocina():
        root.destroy()
        from auth import iniciar_sesion
        iniciar_sesion()

    tk.Button(root, text="Marcar como Listo", command=marcar_como_listo).pack(pady=20)
    tk.Button(root, text="Cerrar", command=cerrar_cocina).pack(pady=20)
    tk.Button(root, text="Volver", command=lambda: (root.destroy(), from auth import iniciar_sesion, iniciar_sesion())).pack(pady=20)

    cargar_comandas()
    root.mainloop()
