# inventario_gui.py
# Interfaz gráfica para el sistema de inventario

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
from inventario_db import InventarioDB
from estilos import configurar_estilos, obtener_colores, crear_boton_personalizado

class InventarioWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = InventarioDB()
        self.colores = obtener_colores()
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Inventario - La Mascota")
        self.window.geometry("1200x800")
        self.window.configure(bg=self.colores["fondo"])
        
        # Centrar ventana
        self.centrar_ventana()
        
        # Configurar estilos
        configurar_estilos()
        
        # Variables
        self.productos = []
        self.producto_seleccionado = None
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar datos iniciales
        self.cargar_productos()
        self.actualizar_estadisticas()
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def crear_interfaz(self):
        """Crea la interfaz principal del inventario."""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10", style="Custom.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # ========== PANEL IZQUIERDO - ESTADÍSTICAS Y ALERTAS ==========
        left_panel = ttk.LabelFrame(main_frame, text="Dashboard", padding="10",
                                   style="Custom.TLabelframe")
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                       padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        
        # Estadísticas
        stats_frame = ttk.LabelFrame(left_panel, text="Estadísticas", padding="10",
                                    style="Custom.TLabelframe")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Labels de estadísticas
        self.lbl_total_productos = ttk.Label(stats_frame, text="Total Productos: 0",
                                           font=("Arial", 10, "bold"))
        self.lbl_total_productos.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.lbl_stock_bajo = ttk.Label(stats_frame, text="Stock Bajo: 0",
                                       font=("Arial", 10), foreground="red")
        self.lbl_stock_bajo.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.lbl_valor_inventario = ttk.Label(stats_frame, text="Valor Inventario: $0.00",
                                            font=("Arial", 10, "bold"))
        self.lbl_valor_inventario.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.lbl_por_vencer = ttk.Label(stats_frame, text="Por Vencer (30d): 0",
                                       font=("Arial", 10), foreground="orange")
        self.lbl_por_vencer.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Alertas
        alertas_frame = ttk.LabelFrame(left_panel, text="Alertas", padding="10",
                                      style="Custom.TLabelframe")
        alertas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        alertas_frame.columnconfigure(0, weight=1)
        alertas_frame.rowconfigure(0, weight=1)
        
        # Lista de alertas
        self.tree_alertas = ttk.Treeview(alertas_frame, columns=("tipo", "producto", "detalle"),
                                        show="headings", height=8)
        self.tree_alertas.heading("tipo", text="Tipo")
        self.tree_alertas.heading("producto", text="Producto")
        self.tree_alertas.heading("detalle", text="Detalle")
        
        self.tree_alertas.column("tipo", width=80)
        self.tree_alertas.column("producto", width=150)
        self.tree_alertas.column("detalle", width=100)
        
        scrollbar_alertas = ttk.Scrollbar(alertas_frame, orient=tk.VERTICAL,
                                         command=self.tree_alertas.yview)
        self.tree_alertas.configure(yscroll=scrollbar_alertas.set)
        
        self.tree_alertas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_alertas.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Botones de acción rápida
        botones_frame = ttk.Frame(left_panel)
        botones_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        botones_frame.columnconfigure(0, weight=1)
        
        btn_actualizar = crear_boton_personalizado(botones_frame, "🔄 Actualizar",
                                                  self.actualizar_todo, ancho=200, alto=35)
        btn_actualizar.grid(row=0, column=0, pady=2)
        
        btn_reportes = crear_boton_personalizado(botones_frame, "📊 Reportes",
                                               self.abrir_reportes, ancho=200, alto=35)
        btn_reportes.grid(row=1, column=0, pady=2)
        
        # ========== PANEL DERECHO - GESTIÓN DE PRODUCTOS ==========
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Barra de herramientas
        toolbar_frame = ttk.Frame(right_panel, padding="5")
        toolbar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones de la barra de herramientas
        btn_agregar = crear_boton_personalizado(toolbar_frame, "➕ Agregar Producto",
                                               self.agregar_producto, ancho=150, alto=35)
        btn_agregar.grid(row=0, column=0, padx=(0, 5))
        
        btn_editar = crear_boton_personalizado(toolbar_frame, "✏️ Editar",
                                              self.editar_producto, ancho=120, alto=35)
        btn_editar.grid(row=0, column=1, padx=5)
        
        btn_eliminar = crear_boton_personalizado(toolbar_frame, "🗑️ Eliminar",
                                                self.eliminar_producto, ancho=120, alto=35)
        btn_eliminar.grid(row=0, column=2, padx=5)
        
        # Búsqueda
        search_frame = ttk.Frame(toolbar_frame)
        search_frame.grid(row=0, column=3, padx=(20, 0))
        
        ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, padx=(0, 5))
        
        self.entry_buscar = ttk.Entry(search_frame, width=20)
        self.entry_buscar.grid(row=0, column=1, padx=5)
        self.entry_buscar.bind('<KeyRelease>', self.buscar_productos)
        
        # Filtro por categoría
        ttk.Label(search_frame, text="Categoría:").grid(row=0, column=2, padx=(20, 5))
        
        self.combo_categoria = ttk.Combobox(search_frame, width=15, state='readonly')
        self.combo_categoria.grid(row=0, column=3, padx=5)
        self.combo_categoria.bind('<<ComboboxSelected>>', self.filtrar_por_categoria)
        
        # Cargar categorías
        self.cargar_categorias()
        
        # Lista de productos
        productos_frame = ttk.LabelFrame(right_panel, text="Productos", padding="10",
                                        style="Custom.TLabelframe")
        productos_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        productos_frame.columnconfigure(0, weight=1)
        productos_frame.rowconfigure(0, weight=1)
        
        # Treeview de productos
        columns = ("codigo", "nombre", "categoria", "stock", "minimo", "precio", "vencimiento")
        self.tree_productos = ttk.Treeview(productos_frame, columns=columns,
                                          show="headings", height=15)
        
        # Configurar columnas
        self.tree_productos.heading("codigo", text="Código")
        self.tree_productos.heading("nombre", text="Nombre")
        self.tree_productos.heading("categoria", text="Categoría")
        self.tree_productos.heading("stock", text="Stock")
        self.tree_productos.heading("minimo", text="Mínimo")
        self.tree_productos.heading("precio", text="Precio")
        self.tree_productos.heading("vencimiento", text="Vencimiento")
        
        self.tree_productos.column("codigo", width=80)
        self.tree_productos.column("nombre", width=200)
        self.tree_productos.column("categoria", width=120)
        self.tree_productos.column("stock", width=60)
        self.tree_productos.column("minimo", width=60)
        self.tree_productos.column("precio", width=80)
        self.tree_productos.column("vencimiento", width=100)
        
        # Scrollbar para productos
        scrollbar_productos = ttk.Scrollbar(productos_frame, orient=tk.VERTICAL,
                                           command=self.tree_productos.yview)
        self.tree_productos.configure(yscroll=scrollbar_productos.set)
        
        self.tree_productos.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_productos.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind eventos
        self.tree_productos.bind('<Double-1>', self.editar_producto)
        self.tree_productos.bind('<Button-3>', self.mostrar_menu_contextual)
    
    def cargar_categorias(self):
        """Carga las categorías en el combobox."""
        categorias = self.db.obtener_categorias()
        valores = ["Todas"] + [cat['nombre'] for cat in categorias]
        self.combo_categoria['values'] = valores
        self.combo_categoria.set("Todas")
    
    def cargar_productos(self, filtro="", categoria_id=None):
        """Carga los productos en la tabla."""
        # Limpiar tabla
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        # Obtener productos
        self.productos = self.db.obtener_productos(filtro, categoria_id)
        
        # Llenar tabla
        for producto in self.productos:
            # Formatear fecha de vencimiento
            vencimiento = ""
            if producto['fecha_vencimiento']:
                try:
                    fecha = datetime.strptime(producto['fecha_vencimiento'], '%Y-%m-%d').date()
                    vencimiento = fecha.strftime('%d/%m/%Y')
                except:
                    vencimiento = producto['fecha_vencimiento']
            
            # Determinar color según stock
            tags = []
            if producto['stock_actual'] <= producto['stock_minimo']:
                tags.append('stock_bajo')
            
            # Insertar en tabla
            item = self.tree_productos.insert("", tk.END, values=(
                producto['codigo'] or '',
                producto['nombre'],
                producto['categoria_nombre'] or '',
                producto['stock_actual'],
                producto['stock_minimo'],
                f"${producto['precio_venta']:.2f}",
                vencimiento
            ), tags=tags)
        
        # Configurar colores
        self.tree_productos.tag_configure('stock_bajo', background='#ffcccc')
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del dashboard."""
        stats = self.db.obtener_estadisticas()
        
        self.lbl_total_productos.config(text=f"Total Productos: {stats['total_productos']}")
        self.lbl_stock_bajo.config(text=f"Stock Bajo: {stats['productos_stock_bajo']}")
        self.lbl_valor_inventario.config(text=f"Valor Inventario: ${stats['valor_inventario']:.2f}")
        self.lbl_por_vencer.config(text=f"Por Vencer (30d): {stats['productos_por_vencer']}")
        
        # Cargar alertas
        self.cargar_alertas()
    
    def cargar_alertas(self):
        """Carga las alertas en la tabla."""
        # Limpiar alertas
        for item in self.tree_alertas.get_children():
            self.tree_alertas.delete(item)
        
        # Productos con stock bajo
        productos_stock_bajo = self.db.obtener_productos_stock_bajo()
        for producto in productos_stock_bajo:
            self.tree_alertas.insert("", tk.END, values=(
                "Stock Bajo",
                producto['nombre'],
                f"{producto['stock_actual']}/{producto['stock_minimo']}"
            ))
        
        # Productos por vencer
        productos_por_vencer = self.db.obtener_productos_por_vencer(30)
        for producto in productos_por_vencer:
            if producto['fecha_vencimiento']:
                try:
                    fecha = datetime.strptime(producto['fecha_vencimiento'], '%Y-%m-%d').date()
                    dias = (fecha - date.today()).days
                    self.tree_alertas.insert("", tk.END, values=(
                        "Vencimiento",
                        producto['nombre'],
                        f"{dias} días"
                    ))
                except:
                    pass
    
    def buscar_productos(self, event=None):
        """Busca productos según el texto ingresado."""
        filtro = self.entry_buscar.get()
        categoria_id = self.obtener_categoria_seleccionada()
        self.cargar_productos(filtro, categoria_id)
    
    def filtrar_por_categoria(self, event=None):
        """Filtra productos por categoría."""
        filtro = self.entry_buscar.get()
        categoria_id = self.obtener_categoria_seleccionada()
        self.cargar_productos(filtro, categoria_id)
    
    def obtener_categoria_seleccionada(self):
        """Obtiene el ID de la categoría seleccionada."""
        categoria_nombre = self.combo_categoria.get()
        if categoria_nombre == "Todas" or not categoria_nombre:
            return None
        
        categorias = self.db.obtener_categorias()
        for cat in categorias:
            if cat['nombre'] == categoria_nombre:
                return cat['id']
        return None
    
    def agregar_producto(self):
        """Abre el diálogo para agregar un nuevo producto."""
        dialog = ProductoDialog(self.window, self.db)
        if dialog.resultado:
            self.cargar_productos()
            self.actualizar_estadisticas()
    
    def editar_producto(self, event=None):
        """Edita el producto seleccionado."""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
        
        # Obtener producto seleccionado
        item = seleccion[0]
        valores = self.tree_productos.item(item)['values']
        
        # Buscar producto por nombre (ya que no tenemos ID en la vista)
        nombre_producto = valores[1]
        producto = None
        for p in self.productos:
            if p['nombre'] == nombre_producto:
                producto = p
                break
        
        if producto:
            dialog = ProductoDialog(self.window, self.db, producto)
            if dialog.resultado:
                self.cargar_productos()
                self.actualizar_estadisticas()
    
    def eliminar_producto(self):
        """Elimina el producto seleccionado."""
        seleccion = self.tree_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        # Obtener producto seleccionado
        item = seleccion[0]
        valores = self.tree_productos.item(item)['values']
        nombre_producto = valores[1]
        
        # Buscar producto por nombre para obtener su ID
        producto = None
        for p in self.productos:
            if p['nombre'] == nombre_producto:
                producto = p
                break
        
        if not producto:
            messagebox.showerror("Error", "No se pudo encontrar el producto seleccionado")
            return
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Está seguro de eliminar el producto '{producto['nombre']}'?\n\n"
            f"Esta acción marcará el producto como inactivo.\n"
            f"Stock actual: {producto['stock_actual']} {producto['unidad_medida']}"
        )
        
        if respuesta:
            try:
                # Eliminar producto (marcar como inactivo)
                if self.db.eliminar_producto(producto['id']):
                    messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                    # Actualizar la vista
                    self.cargar_productos()
                    self.actualizar_estadisticas()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el producto")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
    
    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual."""
        # Implementar menú contextual
        pass
    
    def actualizar_todo(self):
        """Actualiza todos los datos."""
        self.cargar_productos()
        self.actualizar_estadisticas()
        messagebox.showinfo("Éxito", "Datos actualizados correctamente")
    
    def abrir_reportes(self):
        """Abre la ventana de reportes."""
        from reportes_gui import ReportesWindow
        ReportesWindow(self.window)


class ProductoDialog:
    def __init__(self, parent, db, producto=None):
        self.parent = parent
        self.db = db
        self.producto = producto
        self.resultado = False
        
        print(f"DEBUG DIALOG: Iniciando diálogo, producto existente: {producto is not None}")
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Agregar Producto" if not producto else "Editar Producto")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar diálogo
        self.centrar_dialog()
        
        # Variables
        self.var_codigo = tk.StringVar(value=producto['codigo'] if producto else "")
        self.var_nombre = tk.StringVar(value=producto['nombre'] if producto else "")
        self.var_descripcion = tk.StringVar(value=producto['descripcion'] if producto else "")
        self.var_alias = tk.StringVar(value=producto.get('alias', '') if producto else "")
        self.var_precio_compra = tk.StringVar(value=str(producto['precio_compra']) if producto else "0")
        self.var_precio_venta = tk.StringVar(value=str(producto['precio_venta']) if producto else "0")
        self.var_stock_actual = tk.StringVar(value=str(producto['stock_actual']) if producto else "0")
        self.var_stock_minimo = tk.StringVar(value=str(producto['stock_minimo']) if producto else "5")
        self.var_unidad = tk.StringVar(value=producto['unidad_medida'] if producto else "Unidad")
        self.var_proveedor = tk.StringVar(value=producto['proveedor'] if producto else "")
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Esperar a que se cierre el diálogo
        self.dialog.wait_window()
        print(f"DEBUG DIALOG: Diálogo cerrado, resultado: {self.resultado}")
    
    def centrar_dialog(self):
        """Centra el diálogo."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Código
        ttk.Label(main_frame, text="Código (opcional):").grid(row=row, column=0, sticky=tk.W, pady=5)
        codigo_entry = ttk.Entry(main_frame, textvariable=self.var_codigo, width=30)
        codigo_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Nota sobre código
        ttk.Label(main_frame, text="(Dejar vacío para generar automáticamente)", 
                 font=("Arial", 8), foreground="gray").grid(
            row=row, column=1, sticky=tk.W, pady=(0, 5), padx=(10, 0))
        row += 1
        
        # Nombre (obligatorio)
        ttk.Label(main_frame, text="Nombre *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.var_nombre, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Alias (nombres alternativos)
        ttk.Label(main_frame, text="Alias:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.var_alias, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Nota sobre alias
        ttk.Label(main_frame, text="(Nombres alternativos separados por comas)", 
                 font=("Arial", 8), foreground="gray").grid(
            row=row, column=1, sticky=tk.W, pady=(0, 5), padx=(10, 0))
        row += 1
        
        # Descripción
        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.var_descripcion, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Categoría
        ttk.Label(main_frame, text="Categoría:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.combo_categoria = ttk.Combobox(main_frame, width=27, state='readonly')
        self.combo_categoria.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Cargar categorías
        categorias = self.db.obtener_categorias()
        self.combo_categoria['values'] = [cat['nombre'] for cat in categorias]
        if self.producto and self.producto['categoria_id']:
            for cat in categorias:
                if cat['id'] == self.producto['categoria_id']:
                    self.combo_categoria.set(cat['nombre'])
                    break
        row += 1
        
        # Precios
        ttk.Label(main_frame, text="Precio Compra:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.var_precio_compra, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        ttk.Label(main_frame, text="Precio Venta:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.var_precio_venta, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Stock
        ttk.Label(main_frame, text="Stock Actual:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.var_stock_actual, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        ttk.Label(main_frame, text="Stock Mínimo:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.var_stock_minimo, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Unidad de medida
        ttk.Label(main_frame, text="Unidad:").grid(row=row, column=0, sticky=tk.W, pady=5)
        combo_unidad = ttk.Combobox(main_frame, textvariable=self.var_unidad, width=27)
        combo_unidad['values'] = ['Unidad', 'Caja', 'Frasco', 'Sobre', 'Kg', 'Litro', 'Metro']
        combo_unidad.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Proveedor
        ttk.Label(main_frame, text="Proveedor:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.var_proveedor, width=30).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Fecha de vencimiento
        ttk.Label(main_frame, text="Vencimiento:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(DD/MM/AAAA)", font=("Arial", 8)).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        self.var_vencimiento = tk.StringVar()
        if self.producto and self.producto['fecha_vencimiento']:
            try:
                fecha = datetime.strptime(self.producto['fecha_vencimiento'], '%Y-%m-%d').date()
                self.var_vencimiento.set(fecha.strftime('%d/%m/%Y'))
            except:
                pass
        
        ttk.Entry(main_frame, textvariable=self.var_vencimiento, width=30).grid(
            row=row-1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        row += 1
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).grid(
            row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).grid(
            row=0, column=1, padx=10)
    
    def guardar(self):
        """Guarda el producto."""
        # Validar campos obligatorios
        if not self.var_nombre.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            # Obtener categoría ID
            categoria_id = None
            categoria_nombre = self.combo_categoria.get()
            if categoria_nombre:
                categorias = self.db.obtener_categorias()
                for cat in categorias:
                    if cat['nombre'] == categoria_nombre:
                        categoria_id = cat['id']
                        break
            
            # Procesar fecha de vencimiento
            fecha_vencimiento = None
            if self.var_vencimiento.get().strip():
                try:
                    fecha = datetime.strptime(self.var_vencimiento.get(), '%d/%m/%Y').date()
                    fecha_vencimiento = fecha.strftime('%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha inválido (DD/MM/AAAA)")
                    return
            
            # Preparar datos
            datos_producto = {
                'codigo': self.var_codigo.get().strip() or None,
                'nombre': self.var_nombre.get().strip(),
                'descripcion': self.var_descripcion.get().strip(),
                'alias': self.var_alias.get().strip() or None,
                'categoria_id': categoria_id,
                'precio_compra': float(self.var_precio_compra.get() or 0),
                'precio_venta': float(self.var_precio_venta.get() or 0),
                'stock_actual': int(self.var_stock_actual.get() or 0),
                'stock_minimo': int(self.var_stock_minimo.get() or 5),
                'unidad_medida': self.var_unidad.get() or 'Unidad',
                'fecha_vencimiento': fecha_vencimiento,
                'proveedor': self.var_proveedor.get().strip()
            }
            
            # Guardar
            if self.producto:
                # Editar producto existente
                print(f"DEBUG: Intentando actualizar producto ID {self.producto['id']}: {datos_producto}")
                try:
                    if self.db.actualizar_producto(self.producto['id'], datos_producto):
                        print(f"DEBUG: Producto actualizado correctamente")
                        self.resultado = True
                        messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                        self.dialog.destroy()
                    else:
                        messagebox.showerror("Error", "No se pudo actualizar el producto")
                except ValueError as ve:
                    # Error de validación (código duplicado, etc.)
                    messagebox.showerror("Error de Validación", str(ve))
                    return
                except Exception as e:
                    # Otros errores de base de datos
                    messagebox.showerror("Error", f"Error al actualizar en base de datos: {str(e)}")
                    return
            else:
                # Agregar nuevo producto
                print(f"DEBUG: Intentando agregar producto: {datos_producto}")
                try:
                    producto_id = self.db.agregar_producto(datos_producto)
                    print(f"DEBUG: Producto agregado con ID: {producto_id}")
                    self.resultado = True
                    messagebox.showinfo("Éxito", "Producto agregado correctamente")
                    self.dialog.destroy()
                except ValueError as ve:
                    # Error de validación (código duplicado, etc.)
                    messagebox.showerror("Error de Validación", str(ve))
                    return
                except Exception as e:
                    # Otros errores de base de datos
                    messagebox.showerror("Error", f"Error al guardar en base de datos: {str(e)}")
                    return
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error en los datos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def cancelar(self):
        """Cancela el diálogo."""
        self.dialog.destroy()