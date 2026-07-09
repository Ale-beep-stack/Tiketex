"""
Interfaz gráfica para la generación de reportes del inventario.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import os
import subprocess
from inventario_reportes import GeneradorReportes


class ReportesWindow:
    """Ventana para generar reportes del inventario."""
    
    def __init__(self, parent):
        """Inicializa la ventana de reportes."""
        self.window = tk.Toplevel(parent)
        self.window.title("Generador de Reportes")
        self.window.geometry("700x600")
        self.window.configure(bg='#f0f0f0')
        
        self.generador = GeneradorReportes()
        
        self.centrar_ventana()
        self.crear_interfaz()
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_interfaz(self):
        """Crea la interfaz de la ventana."""
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(
            main_frame,
            text="📊 Generador de Reportes",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg='#2E7D32'
        )
        titulo.pack(pady=(0, 20))
        
        # Frame de reportes básicos
        self.crear_seccion_reportes_basicos(main_frame)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Frame de reportes con fechas
        self.crear_seccion_reportes_fechas(main_frame)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Frame de reportes adicionales
        self.crear_seccion_reportes_adicionales(main_frame)
        
        # Botón cerrar
        btn_cerrar = tk.Button(
            main_frame,
            text="Cerrar",
            command=self.window.destroy,
            font=('Arial', 11),
            bg='#757575',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        btn_cerrar.pack(pady=(20, 0))
    
    def crear_seccion_reportes_basicos(self, parent):
        """Crea la sección de reportes básicos."""
        frame = tk.LabelFrame(
            parent,
            text="Reportes Básicos",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#1976D2',
            padx=15,
            pady=15
        )
        frame.pack(fill='x', pady=(0, 10))
        
        # Botones de reportes básicos
        botones = [
            ("📦 Inventario Actual", self.generar_inventario_actual, '#2E7D32'),
            ("⚠️ Stock Bajo", self.generar_stock_bajo, '#D32F2F'),
        ]
        
        for texto, comando, color in botones:
            btn = tk.Button(
                frame,
                text=texto,
                command=comando,
                font=('Arial', 11),
                bg=color,
                fg='white',
                cursor='hand2',
                relief=tk.FLAT,
                padx=20,
                pady=10,
                width=25
            )
            btn.pack(pady=5)
    
    def crear_seccion_reportes_fechas(self, parent):
        """Crea la sección de reportes con rango de fechas."""
        frame = tk.LabelFrame(
            parent,
            text="Reportes por Período",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#1976D2',
            padx=15,
            pady=15
        )
        frame.pack(fill='x', pady=(0, 10))
        
        # Frame para fechas
        fecha_frame = tk.Frame(frame, bg='#f0f0f0')
        fecha_frame.pack(pady=(0, 10))
        
        # Fecha inicio
        tk.Label(
            fecha_frame,
            text="Desde:",
            font=('Arial', 10),
            bg='#f0f0f0'
        ).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        self.fecha_inicio = DateEntry(
            fecha_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            locale='es_ES'
        )
        self.fecha_inicio.set_date(datetime.now() - timedelta(days=30))
        self.fecha_inicio.grid(row=0, column=1, padx=5, pady=5)
        
        # Fecha fin
        tk.Label(
            fecha_frame,
            text="Hasta:",
            font=('Arial', 10),
            bg='#f0f0f0'
        ).grid(row=0, column=2, padx=5, pady=5, sticky='e')
        
        self.fecha_fin = DateEntry(
            fecha_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            locale='es_ES'
        )
        self.fecha_fin.set_date(datetime.now())
        self.fecha_fin.grid(row=0, column=3, padx=5, pady=5)
        
        # Botones de reportes con fechas
        botones = [
            ("📋 Movimientos de Inventario", self.generar_movimientos, '#1976D2'),
            ("🏆 Productos Más Vendidos", self.generar_mas_vendidos, '#F57C00'),
        ]
        
        for texto, comando, color in botones:
            btn = tk.Button(
                frame,
                text=texto,
                command=comando,
                font=('Arial', 11),
                bg=color,
                fg='white',
                cursor='hand2',
                relief=tk.FLAT,
                padx=20,
                pady=10,
                width=25
            )
            btn.pack(pady=5)
    
    def crear_seccion_reportes_adicionales(self, parent):
        """Crea la sección de reportes adicionales."""
        frame = tk.LabelFrame(
            parent,
            text="Reportes Adicionales",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#1976D2',
            padx=15,
            pady=15
        )
        frame.pack(fill='x', pady=(0, 10))
        
        # Botones de reportes adicionales
        botones = [
            ("💰 Valorización de Inventario", self.generar_valorizacion, '#388E3C'),
            ("📂 Productos por Categoría", self.generar_por_categoria, '#1976D2'),
            ("⏰ Productos por Vencer", self.generar_por_vencer, '#F57C00'),
        ]
        
        for texto, comando, color in botones:
            btn = tk.Button(
                frame,
                text=texto,
                command=comando,
                font=('Arial', 11),
                bg=color,
                fg='white',
                cursor='hand2',
                relief=tk.FLAT,
                padx=20,
                pady=10,
                width=25
            )
            btn.pack(pady=5)
    
    def abrir_pdf(self, ruta_archivo):
        """Abre el archivo PDF generado."""
        if ruta_archivo and os.path.exists(ruta_archivo):
            try:
                os.startfile(ruta_archivo)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
    
    def generar_inventario_actual(self):
        """Genera el reporte de inventario actual."""
        try:
            archivo = self.generador.generar_inventario_actual()
            if archivo:
                respuesta = messagebox.askyesno(
                    "Reporte Generado",
                    "Reporte generado exitosamente.\n¿Desea abrirlo ahora?"
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
                    "Reporte generado exitosamente.\n¿Desea abrirlo ahora?"
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
                    "Reporte generado exitosamente.\n¿Desea abrirlo ahora?"
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
                    "Reporte generado exitosamente.\n¿Desea abrirlo ahora?"
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
                    "Reporte generado exitosamente.\n¿Desea abrirlo ahora?"
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
                    "Reporte generado exitosamente.\n¿Desea abrirlo ahora?"
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
                    "Reporte generado exitosamente.\n¿Desea abrirlo ahora?"
                )
                if respuesta:
                    self.abrir_pdf(archivo)
            else:
                messagebox.showerror("Error", "No se pudo generar el reporte")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
