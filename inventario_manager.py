# inventario_manager.py
# Maneja toda la lógica de inventario para la aplicación principal

import tkinter as tk
from tkinter import ttk, messagebox

class InventarioManager:
    def __init__(self, main_app):
        self.main_app = main_app
        self.inventario_integrado = None
    
    def crear_interfaz_inventario(self):
        """Crea la interfaz de inventario integrada en la pestaña."""
        try:
            from inventario_integrado import InventarioIntegrado
            
            # Crear la interfaz directamente en el frame
            self.inventario_integrado = InventarioIntegrado(
                self.main_app.frame_inventario, 
                self.main_app
            )
            
        except Exception as e:
            # Si hay error, mostrar mensaje en la pestaña
            error_label = ttk.Label(
                self.main_app.frame_inventario, 
                text=f"Error al cargar inventario: {str(e)}", 
                font=("Arial", 12)
            )
            error_label.grid(row=0, column=0, padx=20, pady=20)
    
    def procesar_inventario_factura(self, datos_factura):
        """Procesa la factura en el inventario y muestra resultados."""
        print("DEBUG INVENTARIO: Iniciando procesamiento de inventario...")
        try:
            from inventario_integracion import integrar_inventario_con_factura
            
            print("DEBUG INVENTARIO: Módulo de integración importado correctamente")
            print(f"DEBUG INVENTARIO: Items en factura: {len(datos_factura.get('items', []))}")
            
            # Procesar factura en inventario
            resultado = integrar_inventario_con_factura(datos_factura)
            
            print(f"DEBUG INVENTARIO: Resultado del procesamiento: {resultado}")
            
            # Si hay productos procesados, actualizar la tabla del inventario SIEMPRE
            if resultado['productos_procesados']:
                print("DEBUG INVENTARIO: Productos procesados, actualizando inventario...")
                self.actualizar_inventario_si_visible()
            
            # Mostrar resultados si hay algo relevante
            # Si es factura duplicada, siempre mostrar advertencia
            if resultado.get('factura_duplicada', False):
                print("DEBUG INVENTARIO: Factura duplicada detectada, mostrando advertencia...")
                self.mostrar_resultado_inventario(resultado)
            elif (resultado['productos_procesados'] or 
                resultado['productos_no_encontrados'] or 
                resultado['alertas'] or
                resultado['errores']):
                
                print("DEBUG INVENTARIO: Mostrando ventana de resultados...")
                self.mostrar_resultado_inventario(resultado)
            else:
                print("DEBUG INVENTARIO: No hay resultados relevantes para mostrar")
                
        except ImportError as e:
            # Si no está disponible el módulo de inventario, continuar sin error
            print(f"DEBUG INVENTARIO: Error de importación: {e}")
        except Exception as e:
            print(f"DEBUG INVENTARIO: Error al procesar inventario: {e}")
            import traceback
            traceback.print_exc()
    
    def mostrar_resultado_inventario(self, resultado):
        """Muestra el resultado del procesamiento de inventario."""
        # Si es una factura duplicada, mostrar advertencia especial
        if resultado.get('factura_duplicada', False):
            mensaje_error = "\n".join(resultado.get('errores', []))
            messagebox.showwarning(
                "⚠️ Factura Duplicada",
                mensaje_error,
                icon='warning'
            )
            return
        
        from inventario_integracion import InventarioIntegracion
        
        integracion = InventarioIntegracion()
        reporte = integracion.generar_reporte_procesamiento(resultado)
        
        # Crear ventana de reporte
        ventana_reporte = tk.Toplevel(self.main_app.root)
        ventana_reporte.title("Resultado del Procesamiento de Inventario")
        ventana_reporte.geometry("600x500")
        ventana_reporte.transient(self.main_app.root)
        
        # Centrar ventana
        ventana_reporte.update_idletasks()
        x = (ventana_reporte.winfo_screenwidth() // 2) - (300)
        y = (ventana_reporte.winfo_screenheight() // 2) - (250)
        ventana_reporte.geometry(f"600x500+{x}+{y}")
        
        # Frame principal
        frame = ttk.Frame(ventana_reporte, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ventana_reporte.columnconfigure(0, weight=1)
        ventana_reporte.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Área de texto con scroll
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Insertar reporte
        text_widget.insert("1.0", reporte)
        text_widget.config(state=tk.DISABLED)
        
        # Botón cerrar
        ttk.Button(frame, text="Cerrar", command=ventana_reporte.destroy).grid(
            row=1, column=0, pady=10)
    
    def actualizar_inventario_si_visible(self):
        """Actualiza la tabla del inventario si la pantalla de inventario está visible."""
        try:
            # Verificar si tenemos el inventario integrado y está visible
            if self.inventario_integrado:
                print("DEBUG INVENTARIO: Actualizando tabla del inventario automáticamente...")
                
                # Usar after() para asegurar que la actualización se haga en el hilo principal
                self.main_app.root.after(100, self._actualizar_inventario_delayed)
                
        except Exception as e:
            print(f"DEBUG INVENTARIO: Error al programar actualización: {e}")
    
    def _actualizar_inventario_delayed(self):
        """Actualiza el inventario con un pequeño delay para evitar conflictos."""
        try:
            if self.inventario_integrado:
                self.inventario_integrado.cargar_productos()
                self.inventario_integrado.actualizar_estadisticas()
                print("DEBUG INVENTARIO: Tabla del inventario actualizada automáticamente")
        except Exception as e:
            print(f"DEBUG INVENTARIO: Error al actualizar tabla: {e}")