"""
Interfaz de reportes integrada como pestaña en la aplicación principal.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import os
from PIL import Image, ImageTk
from inventario_reportes import GeneradorReportes
from estilos import obtener_colores, obtener_ruta_recurso


class ReportesIntegrado:
    """Interfaz de reportes integrada en la aplicación."""
    
    def __init__(self, parent_frame, main_app):
        """Inicializa la interfaz de reportes."""
        self.parent_frame = parent_frame
        self.main_app = main_app
        self.generador = GeneradorReportes()
        self.colores = obtener_colores()
        
        # Cargar imágenes de botones
        self.imagenes_botones = {}
        self.cargar_imagenes_botones()
        
        # Crear interfaz
        self.crear_interfaz()
    
    def cargar_imagenes_botones(self):
        """Carga las imágenes de los botones."""
        try:
            # Botón celeste (azul)
            ruta_celeste = obtener_ruta_recurso(os.path.join("disenos", "button-859346_1280.png"))
            img_celeste = Image.open(ruta_celeste)
            img_celeste = img_celeste.resize((300, 50), Image.Resampling.LANCZOS)
            self.imagenes_botones['celeste'] = ImageTk.PhotoImage(img_celeste)
            
            # Botón naranja
            ruta_naranja = obtener_ruta_recurso(os.path.join("disenos", "botonaranja.png"))
            img_naranja = Image.open(ruta_naranja)
            img_naranja = img_naranja.resize((300, 50), Image.Resampling.LANCZOS)
            self.imagenes_botones['naranja'] = ImageTk.PhotoImage(img_naranja)
            
            # Botón rojo
            ruta_rojo = obtener_ruta_recurso(os.path.join("disenos", "botonrojo.png"))
            img_rojo = Image.open(ruta_rojo)
            img_rojo = img_rojo.resize((300, 50), Image.Resampling.LANCZOS)
            self.imagenes_botones['rojo'] = ImageTk.PhotoImage(img_rojo)
            
            # Botón verde (usar el celeste como base si no hay verde)
            self.imagenes_botones['verde'] = self.imagenes_botones['celeste']
            
            print("✓ Imágenes de botones de reportes cargadas correctamente")
        except Exception as e:
            print(f"Error al cargar imágenes de botones: {e}")
    
    def crear_boton_con_imagen(self, parent, texto, comando, color_imagen):
        """Crea un botón con imagen de fondo."""
        imagen = self.imagenes_botones.get(color_imagen)
        
        btn = tk.Button(
            parent,
            text=texto,
            command=comando,
            font=('Arial Black', 10, 'bold'),
            fg='#000000',  # Texto negro
            bg=self.colores['panel'],
            activebackground=self.colores['boton_hover'],
            activeforeground='#000000',
            relief='flat',
            borderwidth=0,
            cursor='hand2',
            compound='center'
        )
        
        if imagen:
            btn.config(image=imagen)
            btn.image = imagen  # Mantener referencia
        
        return btn
    
    def crear_interfaz(self):
        """Crea la interfaz de reportes."""
        # Frame principal con scroll
        main_frame = tk.Frame(self.parent_frame, bg=self.colores['fondo'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame para botones superiores
        botones_superior_frame = tk.Frame(main_frame, bg=self.colores['fondo'])
        botones_superior_frame.pack(fill='x', pady=(0, 20))
        
        # Botón regresar a la izquierda
        btn_regresar = self.crear_boton_con_imagen(
            botones_superior_frame, 
            "⬅️ REGRESAR A INVENTARIO", 
            self.regresar_a_inventario, 
            'celeste'
        )
        btn_regresar.pack(side='left', padx=(0, 10))
        
        # Botón abrir carpeta reportes a la derecha del botón regresar
        btn_carpeta_reportes = self.crear_boton_con_imagen(
            botones_superior_frame,
            "📁 ABRIR CARPETA DE REPORTES",
            self.abrir_carpeta_reportes,
            'naranja'
        )
        btn_carpeta_reportes.pack(side='left')
        
        # Título principal
        titulo_frame = tk.Frame(main_frame, bg=self.colores['fondo'])
        titulo_frame.pack(fill='x', pady=(0, 30))
        
        titulo = tk.Label(
            titulo_frame,
            text="📊 GENERADOR DE REPORTES",
            font=('Rockwell', 24, 'bold'),
            bg=self.colores['fondo'],
            fg='#FFFFFF'  # Texto blanco
        )
        titulo.pack()
        
        subtitulo = tk.Label(
            titulo_frame,
            text="Genera reportes detallados del inventario en formato PDF",
            font=('Rockwell', 11),
            bg=self.colores['fondo'],
            fg='#FFFFFF'  # Texto blanco
        )
        subtitulo.pack(pady=(5, 0))
        
        # Contenedor con scroll
        canvas = tk.Canvas(main_frame, bg=self.colores['fondo'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colores['fondo'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Secciones de reportes
        self.crear_seccion_reportes_basicos(scrollable_frame)
        self.crear_separador(scrollable_frame)
        self.crear_seccion_reportes_fechas(scrollable_frame)
        self.crear_separador(scrollable_frame)
        self.crear_seccion_reportes_adicionales(scrollable_frame)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def crear_separador(self, parent):
        """Crea un separador visual."""
        sep = tk.Frame(parent, height=2, bg='#CCCCCC')
        sep.pack(fill='x', pady=20, padx=50)
    
    def crear_seccion_reportes_basicos(self, parent):
        """Crea la sección de reportes básicos."""
        frame = tk.Frame(parent, bg=self.colores['fondo'])
        frame.pack(fill='x', pady=(0, 10), padx=50)
        
        # Título de sección
        titulo = tk.Label(
            frame,
            text="REPORTES BÁSICOS",
            font=('Rockwell', 16, 'bold'),
            bg=self.colores['fondo'],
            fg='#FFFFFF'  # Texto blanco
        )
        titulo.pack(pady=(0, 15))
        
        # Contenedor de botones
        botones_frame = tk.Frame(frame, bg=self.colores['fondo'])
        botones_frame.pack()
        
        # Botones de reportes básicos con imágenes
        botones = [
            ("📦 INVENTARIO ACTUAL", self.generar_inventario_actual, 'celeste'),
            ("⚠️ STOCK BAJO", self.generar_stock_bajo, 'rojo'),
        ]
        
        for texto, comando, color_img in botones:
            btn = self.crear_boton_con_imagen(botones_frame, texto, comando, color_img)
            btn.pack(pady=8)
    
    def crear_seccion_reportes_fechas(self, parent):
        """Crea la sección de reportes con rango de fechas."""
        frame = tk.Frame(parent, bg=self.colores['fondo'])
        frame.pack(fill='x', pady=(0, 10), padx=50)
        
        # Título de sección
        titulo = tk.Label(
            frame,
            text="REPORTES POR PERÍODO",
            font=('Rockwell', 16, 'bold'),
            bg=self.colores['fondo'],
            fg='#FFFFFF'  # Texto blanco
        )
        titulo.pack(pady=(0, 15))
        
        # Frame para selector de fechas
        fecha_frame = tk.Frame(frame, bg=self.colores['fondo'])
        fecha_frame.pack(pady=(0, 15))
        
        # Fecha inicio
        tk.Label(
            fecha_frame,
            text="Desde:",
            font=('Rockwell', 11, 'bold'),
            bg=self.colores['fondo'],
            fg='#FFFFFF'  # Texto blanco
        ).grid(row=0, column=0, padx=10, pady=5, sticky='e')
        
        self.fecha_inicio = DateEntry(
            fecha_frame,
            width=15,
            background='#2E7D32',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            font=('Rockwell', 10)
        )
        self.fecha_inicio.set_date(datetime.now() - timedelta(days=30))
        self.fecha_inicio.grid(row=0, column=1, padx=10, pady=5)
        
        # Fecha fin
        tk.Label(
            fecha_frame,
            text="Hasta:",
            font=('Rockwell', 11, 'bold'),
            bg=self.colores['fondo'],
            fg='#FFFFFF'  # Texto blanco
        ).grid(row=0, column=2, padx=10, pady=5, sticky='e')
        
        self.fecha_fin = DateEntry(
            fecha_frame,
            width=15,
            background='#2E7D32',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            font=('Rockwell', 10)
        )
        self.fecha_fin.set_date(datetime.now())
        self.fecha_fin.grid(row=0, column=3, padx=10, pady=5)
        
        # Contenedor de botones
        botones_frame = tk.Frame(frame, bg=self.colores['fondo'])
        botones_frame.pack()
        
        # Botones de reportes con fechas e imágenes
        botones = [
            ("📋 MOVIMIENTOS DE INVENTARIO", self.generar_movimientos, 'celeste'),
            ("🏆 PRODUCTOS MÁS VENDIDOS", self.generar_mas_vendidos, 'naranja'),
        ]
        
        for texto, comando, color_img in botones:
            btn = self.crear_boton_con_imagen(botones_frame, texto, comando, color_img)
            btn.pack(pady=8)
    
    def crear_seccion_reportes_adicionales(self, parent):
        """Crea la sección de reportes adicionales."""
        frame = tk.Frame(parent, bg=self.colores['fondo'])
        frame.pack(fill='x', pady=(0, 10), padx=50)
        
        # Título de sección
        titulo = tk.Label(
            frame,
            text="REPORTES ADICIONALES",
            font=('Rockwell', 16, 'bold'),
            bg=self.colores['fondo'],
            fg='#FFFFFF'  # Texto blanco
        )
        titulo.pack(pady=(0, 15))
        
        # Contenedor de botones
        botones_frame = tk.Frame(frame, bg=self.colores['fondo'])
        botones_frame.pack()
        
        # Botones de reportes adicionales con imágenes
        botones = [
            ("💰 VALORIZACIÓN DE INVENTARIO", self.generar_valorizacion, 'celeste'),
            ("📂 PRODUCTOS POR CATEGORÍA", self.generar_por_categoria, 'celeste'),
            ("⏰ PRODUCTOS POR VENCER", self.generar_por_vencer, 'naranja'),
        ]
        
        for texto, comando, color_img in botones:
            btn = self.crear_boton_con_imagen(botones_frame, texto, comando, color_img)
            btn.pack(pady=8)
    
    def abrir_pdf(self, ruta_archivo):
        """Abre el archivo PDF generado."""
        if ruta_archivo:
            # Convertir a ruta absoluta si es relativa
            if not os.path.isabs(ruta_archivo):
                ruta_archivo = os.path.abspath(ruta_archivo)
            
            if os.path.exists(ruta_archivo):
                try:
                    os.startfile(ruta_archivo)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
            else:
                messagebox.showerror("Error", f"El archivo no existe:\n{ruta_archivo}")
        else:
            messagebox.showerror("Error", "No se especificó una ruta de archivo")
    
    def regresar_a_inventario(self):
        """Regresa a la pantalla de inventario."""
        if hasattr(self.main_app, 'mostrar_pantalla_inventario'):
            self.main_app.mostrar_pantalla_inventario()
        else:
            messagebox.showinfo("Info", "No se puede regresar al inventario")
    
    def abrir_carpeta_reportes(self):
        """Abre la carpeta donde se guardan los reportes generados."""
        carpeta_reportes = os.path.abspath("reportes_generados")
        try:
            if not os.path.exists(carpeta_reportes):
                os.makedirs(carpeta_reportes)
            
            os.startfile(carpeta_reportes)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir la carpeta de reportes: {e}")
    
    def generar_inventario_actual(self):
        """Genera el reporte de inventario actual."""
        try:
            archivo = self.generador.generar_inventario_actual()
            if archivo:
                respuesta = messagebox.askyesno(
                    "Reporte Generado",
                    "✅ Reporte generado exitosamente.\n\n¿Desea abrirlo ahora?"
                )
                if respuesta:
                    self.abrir_pdf(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
    
    def generar_stock_bajo(self):
        """Genera el reporte de stock bajo."""
        try:
            archivo = self.generador.generar_stock_bajo()
            if archivo:
                respuesta = messagebox.askyesno(
                    "Reporte Generado",
                    "✅ Reporte generado exitosamente.\n\n¿Desea abrirlo ahora?"
                )
                if respuesta:
                    self.abrir_pdf(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
    
    def generar_movimientos(self):
        """Genera el reporte de movimientos."""
        try:
            fecha_inicio = self.fecha_inicio.get_date()
            fecha_fin = self.fecha_fin.get_date()
            
            if fecha_inicio > fecha_fin:
                messagebox.showwarning("Advertencia", "La fecha de inicio debe ser menor a la fecha fin")
                return
            
            archivo = self.generador.generar_movimientos(fecha_inicio, fecha_fin)
            if archivo:
                respuesta = messagebox.askyesno(
                    "Reporte Generado",
                    "✅ Reporte generado exitosamente.\n\n¿Desea abrirlo ahora?"
                )
                if respuesta:
                    self.abrir_pdf(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
    
    def generar_mas_vendidos(self):
        """Genera el reporte de productos más vendidos."""
        try:
            fecha_inicio = self.fecha_inicio.get_date()
            fecha_fin = self.fecha_fin.get_date()
            
            if fecha_inicio > fecha_fin:
                messagebox.showwarning("Advertencia", "La fecha de inicio debe ser menor a la fecha fin")
                return
            
            archivo = self.generador.generar_productos_mas_vendidos(fecha_inicio, fecha_fin)
            if archivo:
                respuesta = messagebox.askyesno(
                    "Reporte Generado",
                    "✅ Reporte generado exitosamente.\n\n¿Desea abrirlo ahora?"
                )
                if respuesta:
                    self.abrir_pdf(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
    
    def generar_valorizacion(self):
        """Genera el reporte de valorización."""
        try:
            archivo = self.generador.generar_valorizacion_inventario()
            if archivo:
                respuesta = messagebox.askyesno(
                    "Reporte Generado",
                    "✅ Reporte generado exitosamente.\n\n¿Desea abrirlo ahora?"
                )
                if respuesta:
                    self.abrir_pdf(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
    
    def generar_por_categoria(self):
        """Genera el reporte por categoría."""
        try:
            archivo = self.generador.generar_productos_por_categoria()
            if archivo:
                respuesta = messagebox.askyesno(
                    "Reporte Generado",
                    "✅ Reporte generado exitosamente.\n\n¿Desea abrirlo ahora?"
                )
                if respuesta:
                    self.abrir_pdf(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
    
    def generar_por_vencer(self):
        """Genera el reporte de productos por vencer."""
        try:
            archivo = self.generador.generar_productos_por_vencer(dias=30)
            if archivo:
                respuesta = messagebox.askyesno(
                    "Reporte Generado",
                    "✅ Reporte generado exitosamente.\n\n¿Desea abrirlo ahora?"
                )
                if respuesta:
                    self.abrir_pdf(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
