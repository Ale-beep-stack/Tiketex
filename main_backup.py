 # main.py
# Interfaz gráfica principal del generador de tickets

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import importlib

# Forzar recarga del módulo extractor para asegurar que use la versión más reciente
if 'extractor' in sys.modules:
    importlib.reload(sys.modules['extractor'])

from extractor import leer_pdf, extraer_qr_de_pdf
from ticket_genrator import generar_ticket, imprimir_ticket
from estilos import configurar_estilos, obtener_colores, crear_boton_personalizado
from inventario_manager import InventarioManager

class TicketGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Tickets")
        
        # Obtener colores del tema
        self.colores = obtener_colores()    
        
        # Configurar el estilo
        configurar_estilos()
        
        # Maximizar la ventana
        self.root.state('zoomed')  # Para Windows
        # Alternativa: self.root.attributes('-zoomed', True)  # Para Linux
        
        # Configurar color de fondo de la ventana principal
        self.root.configure(bg=self.colores["fondo"])
        
        self.datos_factura = None
        self.ruta_pdf_generado = None
        self.ruta_factura_cargada = None  # Para guardar la ruta de la factura cargada
        
        # Impresora seleccionada (se guarda después de la primera selección)
        self.impresora_seleccionada = None
        self.cargar_impresora_guardada()
        
        # Lista de emisores
        self.emisores = []
        self.cargar_emisores()
        
        # Inicializar manager de inventario
        self.inventario_manager = InventarioManager(self)
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Crear sistema de frames intercambiables (sin pestañas visibles)
        self.container = ttk.Frame(self.root, style="Custom.TFrame")
        self.container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar el grid para que se expanda
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)
        
        # ========== FRAME 1: TICKETS ==========
        self.frame_tickets = ttk.Frame(self.container, style="Custom.TFrame")
        self.frame_tickets.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ========== FRAME 2: INVENTARIO ==========
        self.frame_inventario = ttk.Frame(self.container, style="Custom.TFrame")
        self.frame_inventario.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Crear interfaces
        self.crear_interfaz_tickets()
        self.inventario_manager.crear_interfaz_inventario()
        
        # Mostrar inicialmente la pantalla de tickets
        self.mostrar_pantalla_tickets()
    
    def mostrar_pantalla_tickets(self):
        """Muestra la pantalla de tickets y oculta inventario."""
        self.frame_tickets.tkraise()
    
    def mostrar_pantalla_inventario(self):
        """Muestra la pantalla de inventario y oculta tickets."""
        self.frame_inventario.tkraise()
    
    def crear_interfaz_tickets(self):
        # Frame principal con dos columnas
        main_frame = ttk.Frame(self.frame_tickets, padding="10", style="Custom.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar el grid para que se expanda
        self.frame_tickets.columnconfigure(0, weight=1)
        self.frame_tickets.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Panel izquierdo
        main_frame.columnconfigure(1, weight=1)  # Panel derecho
        main_frame.rowconfigure(0, weight=1)
        
        # ========== PANEL IZQUIERDO ==========
        left_panel = ttk.Frame(main_frame, padding="5", style="Panel.TFrame")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_panel.columnconfigure(0, weight=1)
        left_panel.columnconfigure(1, weight=1)
        
        # Configurar filas para que la tabla de items se expanda
        left_panel.rowconfigure(5, weight=1)  # Fila de items se expande
        
        # Título
        titulo = ttk.Label(left_panel, text="Generador de Tickets", 
                          style="Title.TLabel")
        titulo.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Frame para selección de emisor
        emisor_frame = ttk.Frame(left_panel, style="Panel.TFrame")
        emisor_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='w', padx=20)
        
        ttk.Label(emisor_frame, text="Emisor:", style="Panel.TLabel", 
                 font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Combobox para seleccionar emisor
        self.combo_emisor = ttk.Combobox(emisor_frame, width=40, state='readonly',
                                        style="Custom.TCombobox")
        self.combo_emisor.grid(row=0, column=1, padx=5)
        self.combo_emisor.bind('<<ComboboxSelected>>', self.on_emisor_seleccionado)
        
        # Botón + para agregar emisor
        btn_agregar_emisor = ttk.Button(emisor_frame, text="+", width=3,
                                        command=self.agregar_emisor, style="Custom.TButton")
        btn_agregar_emisor.grid(row=0, column=2, padx=2)
        
        # Botón - para eliminar emisor
        btn_eliminar_emisor = ttk.Button(emisor_frame, text="-", width=3,
                                         command=self.eliminar_emisor, style="Custom.TButton")
        btn_eliminar_emisor.grid(row=0, column=3, padx=2)
        
        # Actualizar lista de emisores
        self.actualizar_combo_emisores()
        
        # Frame para botones de factura
        factura_btn_frame = ttk.Frame(left_panel, style="Panel.TFrame")
        factura_btn_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='w', padx=20)
        
        # Botón cargar factura
        btn_cargar = crear_boton_personalizado(factura_btn_frame, "📄 Cargar Factura", 
                                               self.cargar_factura, ancho=180, alto=35)
        btn_cargar.grid(row=0, column=0, padx=(0, 5))
        
        # Botón abrir factura
        self.btn_abrir_factura = crear_boton_personalizado(factura_btn_frame, "📂 Abrir Factura", 
                                                           self.abrir_factura_cargada, 
                                                           ancho=180, alto=35, estado="disabled")
        self.btn_abrir_factura.grid(row=0, column=1, padx=(5, 0))
        
        # Botón abrir carpeta de tickets
        btn_carpeta_tickets = crear_boton_personalizado(factura_btn_frame, "📁 Carpeta Tickets", 
                                                        self.abrir_carpeta_tickets, 
                                                        ancho=180, alto=35)
        btn_carpeta_tickets.grid(row=0, column=2, padx=(5, 0))
        
        # Botón gestionar inventario (cambia a la pestaña de inventario)
        btn_inventario = crear_boton_personalizado(factura_btn_frame, "📦 Gestionar Inventario", 
                                                   self.abrir_inventario, 
                                                   ancho=200, alto=35)
        btn_inventario.grid(row=0, column=3, padx=(5, 0))
        
        # Separador
        ttk.Separator(left_panel, orient='horizontal').grid(
            row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Frame de vista previa
        preview_frame = ttk.LabelFrame(left_panel, text="Vista Previa de Datos", 
                                       padding="10", style="Custom.TLabelframe")
        preview_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Datos básicos
        ttk.Label(preview_frame, text="Número de Control:", 
                 font=("Rockwell", 10, "bold"), style="PanelBold.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_control = ttk.Label(preview_frame, text="-",
                                     font=("Rockwell", 9), style="PanelResult.TLabel")
        self.lbl_control.grid(row=0, column=1, sticky=tk.W, pady=2, padx=10)
        
        ttk.Label(preview_frame, text="Fecha:", 
                 font=("Rockwell", 10, "bold"), style="PanelBold.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_fecha = ttk.Label(preview_frame, text="-", 
                                   font=("Rockwell", 9), style="PanelResult.TLabel")
        self.lbl_fecha.grid(row=1, column=1, sticky=tk.W, pady=2, padx=10)
        
        ttk.Label(preview_frame, text="Cliente:", 
                 font=("Rockwell", 10, "bold"), style="PanelBold.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_cliente = ttk.Label(preview_frame, text="-", 
                                     font=("Rockwell", 9), style="PanelResult.TLabel")
        self.lbl_cliente.grid(row=2, column=1, sticky=tk.W, pady=2, padx=10)
        
        ttk.Label(preview_frame, text="DUI:", 
                 font=("Rockwell", 10, "bold"), style="PanelBold.TLabel").grid(
            row=3, column=0, sticky=tk.W, pady=2)
        self.lbl_ruc = ttk.Label(preview_frame, text="-", 
                                font=("Rockwell", 9), style="PanelResult.TLabel")
        self.lbl_ruc.grid(row=3, column=1, sticky=tk.W, pady=2, padx=10)
        
        ttk.Label(preview_frame, text="Total:", 
                 font=("Rockwell", 10, "bold"), style="PanelBold.TLabel").grid(
            row=4, column=0, sticky=tk.W, pady=2)
        self.lbl_total = ttk.Label(preview_frame, text="-", 
                                   font=("Rockwell", 11, "bold"),
                                   style="PanelResult.TLabel")
        self.lbl_total.grid(row=4, column=1, sticky=tk.W, pady=2, padx=10)
        
        # Frame de items
        items_frame = ttk.LabelFrame(left_panel, text="Items", padding="10",
                                     style="Custom.TLabelframe")
        items_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        items_frame.rowconfigure(0, weight=1)
        
        # Treeview para items con columnas: N°, Cantidad, Unidad, Descripción, Precio Unitario
        columns = ("numero", "cantidad", "unidad", "descripcion", "precio")
        self.tree_items = ttk.Treeview(items_frame, columns=columns, 
                                       show="headings", height=8)
        
        self.tree_items.heading("numero", text="N°")
        self.tree_items.heading("cantidad", text="Cantidad")
        self.tree_items.heading("unidad", text="Unidad")
        self.tree_items.heading("descripcion", text="Descripción")
        self.tree_items.heading("precio", text="Precio Unitario")
        
        self.tree_items.column("numero", width=40)
        self.tree_items.column("cantidad", width=70)
        self.tree_items.column("unidad", width=80)
        self.tree_items.column("descripcion", width=250)
        self.tree_items.column("precio", width=100)
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, 
                                 command=self.tree_items.yview)
        self.tree_items.configure(yscroll=scrollbar.set)
        
        self.tree_items.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame de totales (debajo de la tabla de items)
        totales_frame = ttk.LabelFrame(left_panel, text="Resumen", padding="10",
                                      style="Custom.TLabelframe")
        totales_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Monto Total de la Operación
        ttk.Label(totales_frame, text="Monto Total de la Operación:",
                 font=("Rockwell", 10, "bold"), style="PanelBold.TLabel").grid(
            row=0, column=0, sticky=tk.E, pady=2, padx=5)
        self.lbl_monto_operacion = ttk.Label(totales_frame, text="$ 0.00", 
                                             font=("Rockwell", 10), style="PanelResult.TLabel")
        self.lbl_monto_operacion.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Total Otros Montos No Afectos
        ttk.Label(totales_frame, text="Total Otros Montos No Afectos:",
                 font=("Rockwell", 10, "bold"), style="PanelBold.TLabel").grid(
            row=1, column=0, sticky=tk.E, pady=2, padx=5)
        self.lbl_otros_montos = ttk.Label(totales_frame, text="$ 0.00", 
                                          font=("Rockwell", 10), style="PanelResult.TLabel")
        self.lbl_otros_montos.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Total a Pagar (destacado)
        ttk.Label(totales_frame, text="Total a Pagar:", 
                 font=("Rockwell", 11, "bold"), style="PanelBold.TLabel").grid(
            row=2, column=0, sticky=tk.E, pady=2, padx=5)
        self.lbl_total_pagar = ttk.Label(totales_frame, text="$ 0.00", 
                                        font=("Rockwell", 12, "bold"), 
                                        style="PanelResult.TLabel")
        self.lbl_total_pagar.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Botones de acción (siempre visibles al final)
        btn_frame = ttk.Frame(left_panel, style="Panel.TFrame")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10, sticky='ew')
        
        # Centrar los botones (ahora solo 3 botones)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.columnconfigure(3, weight=1)
        btn_frame.columnconfigure(4, weight=1)
        
        self.btn_imprimir = crear_boton_personalizado(btn_frame, "🖨️ Imprimir", 
                                                      self.imprimir_ticket, 
                                                      ancho=200, alto=40, estado="disabled")
        self.btn_imprimir.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_abrir = crear_boton_personalizado(btn_frame, "� Abrir Ticket", 
                                                   self.abrir_pdf, 
                                                   ancho=200, alto=40, estado="disabled")
        self.btn_abrir.grid(row=0, column=2, padx=5, pady=5)
        
        # Botón limpiar tickets antiguos
        btn_limpiar = crear_boton_personalizado(btn_frame, "🗑️ Limpiar Tickets", 
                                                self.limpiar_tickets_antiguos, 
                                                ancho=200, alto=40)
        btn_limpiar.grid(row=0, column=3, padx=5, pady=5)
        
        # ========== PANEL DERECHO - VISTA PREVIA DEL TICKET ==========
        right_panel = ttk.LabelFrame(main_frame, text="Vista Previa del Ticket", padding="10",
                                     style="Custom.TLabelframe")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # Área de texto para mostrar el ticket
        ticket_frame = ttk.Frame(right_panel)
        ticket_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        ticket_frame.columnconfigure(0, weight=1)
        ticket_frame.rowconfigure(0, weight=1)
        
        # Scrollbar para el área de texto
        scrollbar_ticket = ttk.Scrollbar(ticket_frame, orient=tk.VERTICAL)
        scrollbar_ticket.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Text widget para mostrar el ticket (EDITABLE)
        self.txt_ticket_preview = tk.Text(ticket_frame, 
                                          font=("Courier", 10),
                                          width=50,
                                          height=40,
                                          wrap=tk.WORD,
                                          yscrollcommand=scrollbar_ticket.set,
                                          bg="#ffffff",  # Fondo blanco para indicar que es editable
                                          fg="#000000",  # Texto negro
                                          relief=tk.SUNKEN,
                                          borderwidth=2,
                                          insertbackground="#000000")  # Cursor negro
        self.txt_ticket_preview.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_ticket.config(command=self.txt_ticket_preview.yview)
        
        # Botón para regenerar ticket con cambios
        btn_regenerar = crear_boton_personalizado(right_panel, "💾 Aplicar Cambios al Ticket", 
                                                  self.aplicar_cambios_ticket, 
                                                  ancho=250, alto=35, estado="disabled")
        btn_regenerar.grid(row=1, column=0, pady=10)
        self.btn_regenerar = btn_regenerar
        
        # Mensaje inicial
        self.txt_ticket_preview.insert("1.0", "\n\n\n\n\n\n"
                                              "          📄 VISTA PREVIA DEL TICKET\n\n"
                                              "     Carga una factura y genera el ticket\n"
                                              "     para ver la vista previa aquí.\n\n"
                                              "     Puedes EDITAR el texto directamente\n"
                                              "     y luego presionar 'Aplicar Cambios'\n"
                                              "     para regenerar el ticket.")
        self.txt_ticket_preview.config(state=tk.DISABLED)
    
    def cargar_factura(self):
        """Carga una factura desde un archivo PDF y genera el ticket automáticamente."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar Factura",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        
        if not ruta:
            return
        
        try:
            # Limpiar datos anteriores
            self.limpiar_interfaz()
            
            # Guardar la ruta de la factura cargada
            self.ruta_factura_cargada = ruta
            
            # Extraer código QR del PDF
            print("Extrayendo código QR del PDF...")
            qr_path = extraer_qr_de_pdf(ruta)
            
            # Extraer datos del PDF
            self.datos_factura = leer_pdf(ruta)
            
            if not self.datos_factura.get("exito", False):
                messagebox.showerror("Error", 
                    self.datos_factura.get("error", "Error al leer el PDF"))
                return
            
            # Agregar la ruta del QR a los datos
            if qr_path:
                self.datos_factura["qr_path"] = qr_path
                print(f"✓ Código QR extraído: {qr_path}")
            else:
                print("⚠ No se encontró código QR en el PDF")
            
            # Actualizar vista previa
            self.actualizar_vista_previa()
            
            # Habilitar botón de abrir factura
            self.btn_abrir_factura.config(state=tk.NORMAL)
            
            # Generar ticket automáticamente
            self.generar_ticket_automatico()
            
            # Procesar inventario si está habilitado
            self.inventario_manager.procesar_inventario_factura(self.datos_factura)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la factura: {str(e)}")
    
    def procesar_inventario_factura(self):
        """Procesa la factura en el inventario y muestra resultados."""
        print("DEBUG INVENTARIO: Iniciando procesamiento de inventario...")
        try:
            from inventario_integracion import integrar_inventario_con_factura
            
            print("DEBUG INVENTARIO: Módulo de integración importado correctamente")
            print(f"DEBUG INVENTARIO: Items en factura: {len(self.datos_factura.get('items', []))}")
            
            # Procesar factura en inventario
            resultado = integrar_inventario_con_factura(self.datos_factura)
            
            print(f"DEBUG INVENTARIO: Resultado del procesamiento: {resultado}")
            
            # Si hay productos procesados, actualizar la tabla del inventario SIEMPRE
            if resultado['productos_procesados']:
                print("DEBUG INVENTARIO: Productos procesados, actualizando inventario...")
                self.actualizar_inventario_si_visible()
            
            # Mostrar resultados si hay algo relevante
            if (resultado['productos_procesados'] or 
                resultado['productos_no_encontrados'] or 
                resultado['alertas'] or
                resultado['errores']):  # Agregar errores también
                
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
        from inventario_integracion import InventarioIntegracion
        
        integracion = InventarioIntegracion()
        reporte = integracion.generar_reporte_procesamiento(resultado)
        
        # Crear ventana de reporte
        ventana_reporte = tk.Toplevel(self.root)
        ventana_reporte.title("Resultado del Procesamiento de Inventario")
        ventana_reporte.geometry("600x500")
        ventana_reporte.transient(self.root)
        
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
            if hasattr(self, 'inventario_integrado'):
                print("DEBUG INVENTARIO: Actualizando tabla del inventario automáticamente...")
                
                # Usar after() para asegurar que la actualización se haga en el hilo principal
                self.root.after(100, self._actualizar_inventario_delayed)
                
        except Exception as e:
            print(f"DEBUG INVENTARIO: Error al programar actualización: {e}")
    
    def _actualizar_inventario_delayed(self):
        """Actualiza el inventario con un pequeño delay para evitar conflictos."""
        try:
            if hasattr(self, 'inventario_integrado'):
                self.inventario_integrado.cargar_productos()
                self.inventario_integrado.actualizar_estadisticas()
                print("DEBUG INVENTARIO: Tabla del inventario actualizada automáticamente")
        except Exception as e:
            print(f"DEBUG INVENTARIO: Error al actualizar tabla: {e}")
    
    def generar_ticket_automatico(self):
        """Genera el ticket automáticamente sin mostrar mensaje de éxito."""
        if not self.datos_factura:
            return
        
        try:
            # Obtener el emisor seleccionado
            emisor = self.obtener_emisor_seleccionado()
            if emisor:
                self.datos_factura["emisor"] = emisor
            
            self.ruta_pdf_generado = generar_ticket(self.datos_factura)
            
            # Mostrar vista previa del ticket en el panel derecho
            self.mostrar_vista_previa_ticket()
            
            # Habilitar botones de imprimir y abrir
            self.btn_imprimir.config(state=tk.NORMAL)
            self.btn_abrir.config(state=tk.NORMAL)
            
            # Mostrar mensaje breve en la barra de estado o consola
            print(f"✓ Ticket generado: {self.ruta_pdf_generado}")
            
        except Exception as e:
            messagebox.showerror("Error", 
                f"Error al generar el ticket: {str(e)}")
    
    def limpiar_interfaz(self):
        """Limpia todos los datos de la interfaz."""
        # Limpiar labels
        self.lbl_control.config(text="-")
        self.lbl_fecha.config(text="-")
        self.lbl_cliente.config(text="-")
        self.lbl_ruc.config(text="-")
        self.lbl_total.config(text="$ 0.00")
        
        # Limpiar tabla de items
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
        
        # Limpiar totales
        self.lbl_monto_operacion.config(text="$ 0.00")
        self.lbl_otros_montos.config(text="$ 0.00")
        self.lbl_total_pagar.config(text="$ 0.00")
        
        # Limpiar vista previa del ticket
        self.txt_ticket_preview.config(state=tk.NORMAL)
        self.txt_ticket_preview.delete("1.0", tk.END)
        self.txt_ticket_preview.insert("1.0", "\n\n\n\n\n\n"
                                              "          📄 VISTA PREVIA DEL TICKET\n\n"
                                              "     Carga una factura y genera el ticket\n"
                                              "     para ver la vista previa aquí.\n\n"
                                              "     Puedes EDITAR el texto directamente\n"
                                              "     y luego presionar 'Aplicar Cambios'\n"
                                              "     para regenerar el ticket.")
        self.txt_ticket_preview.config(state=tk.DISABLED)
        
        # Deshabilitar botones
        self.btn_imprimir.config(state=tk.DISABLED)
        self.btn_abrir.config(state=tk.DISABLED)
        self.btn_abrir_factura.config(state=tk.DISABLED)
        self.btn_regenerar.config(state=tk.DISABLED)
        
        # Limpiar datos
        self.datos_factura = None
        self.ruta_pdf_generado = None
        self.ruta_factura_cargada = None
    
    def actualizar_vista_previa(self):
        """Actualiza la vista previa con los datos de la factura."""
        if not self.datos_factura:
            return
        
        # Actualizar labels
        numero_control = self.datos_factura.get("numero_control", "-")
        self.lbl_control.config(text=numero_control)
        self.lbl_fecha.config(text=self.datos_factura.get("fecha", "-"))
        
        cliente = self.datos_factura.get("cliente", {})
        self.lbl_cliente.config(text=cliente.get("nombre", "-"))
        self.lbl_ruc.config(text=cliente.get("ruc_dni", "-"))
        
        total = self.datos_factura.get("total", 0)
        self.lbl_total.config(text=f"$ {total:.2f}")
        
        # Limpiar items anteriores
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
        
        # Agregar items
        items = self.datos_factura.get("items", [])
        for idx, item in enumerate(items, 1):
            self.tree_items.insert("", tk.END, values=(
                idx,  # N°
                item.get("cantidad", 0),
                item.get("unidad", "Unidad"),
                item.get("descripcion", ""),
                f"$ {item.get('precio_unitario', 0):.2f}"
            ))
        
        # Actualizar totales
        total = self.datos_factura.get("total", 0)
        subtotal = self.datos_factura.get("subtotal", total)
        otros_montos = self.datos_factura.get("otros_montos", 0)
        
        self.lbl_monto_operacion.config(text=f"$ {subtotal:.2f}")
        self.lbl_otros_montos.config(text=f"$ {otros_montos:.2f}")
        self.lbl_total_pagar.config(text=f"$ {total:.2f}")
    
    
    def aplicar_cambios_ticket(self):
        """Aplica los cambios editados en la vista previa y regenera el ticket."""
        if not self.datos_factura:
            messagebox.showwarning("Advertencia", 
                "No hay datos de factura cargados")
            return
        
        try:
            # Obtener el texto editado
            texto_editado = self.txt_ticket_preview.get("1.0", tk.END)
            
            # Guardar el texto editado en los datos
            self.datos_factura["texto_ticket_editado"] = texto_editado
            
            # Regenerar el ticket con el texto editado
            emisor = self.obtener_emisor_seleccionado()
            if emisor:
                self.datos_factura["emisor"] = emisor
            
            self.ruta_pdf_generado = generar_ticket(self.datos_factura)
            
            # Habilitar botones
            self.btn_imprimir.config(state=tk.NORMAL)
            self.btn_abrir.config(state=tk.NORMAL)
            
            messagebox.showinfo("Éxito", 
                "Ticket regenerado con los cambios aplicados")
            
        except Exception as e:
            messagebox.showerror("Error", 
                f"Error al aplicar cambios: {str(e)}")
    
    def mostrar_vista_previa_ticket(self):
        """Muestra una vista previa del ticket en el panel derecho."""
        if not self.datos_factura:
            return
        
        # Habilitar edición temporalmente
        self.txt_ticket_preview.config(state=tk.NORMAL)
        
        # Limpiar el área de texto
        self.txt_ticket_preview.delete("1.0", tk.END)
        
        # Construir la vista previa del ticket
        ticket_text = self.construir_texto_ticket()
        
        # Insertar el texto
        self.txt_ticket_preview.insert("1.0", ticket_text)
        
        # Mantener editable para que el usuario pueda modificar
        # self.txt_ticket_preview.config(state=tk.NORMAL)  # Ya está en NORMAL
        
        # Habilitar botón de regenerar
        self.btn_regenerar.config(state=tk.NORMAL)
    
    def construir_texto_ticket(self):
        """Construye el texto del ticket para la vista previa."""
        # Obtener emisor seleccionado
        emisor = self.obtener_emisor_seleccionado()
        if not emisor:
            emisor = {"nombre": "EMISOR", "nit": "00000000-0"}
        
        linea = "-" * 40
        texto = "\n"
        texto += "     COMPROBANTE DE VENTA\n"
        texto += "            FACTURA\n\n"
        
        # Número de control
        numero_control = self.datos_factura.get("numero_control", "")
        texto += f"  REF. {numero_control}\n\n"
        
        # Emisor
        texto += f"EMISOR: {emisor['nombre']}\n"
        texto += f"NIT: {emisor['nit']}\n"
        texto += "CALLE JOSE MARIANO MENDEZ 6 AV. SUR,\n"
        texto += "SANTA ANA, SANTA ANA\n\n"
        
        # Código de Generación (si existe)
        codigo_generacion = self.datos_factura.get("codigo_generacion", "")
        if codigo_generacion:
            texto += "Código de Generación:\n"
            texto += f"{codigo_generacion}\n\n"
        
        # Sello de Recepción (si existe)
        sello_recepcion = self.datos_factura.get("sello_recepcion", "")
        if sello_recepcion:
            texto += "Sello de Recepción:\n"
            texto += f"{sello_recepcion}\n\n"
        
        # Fecha y hora
        fecha = self.datos_factura.get("fecha", "")
        if fecha:
            texto += f"Fecha: {fecha}\n"
        texto += "\n"
        
        # Receptor
        cliente = self.datos_factura.get("cliente", {})
        texto += f"RECEPTOR: {cliente.get('nombre', '')}\n\n"
        
        # Línea separadora
        texto += linea + "\n"
        texto += "CANT. DESCRIPCIÓN         VALOR\n"
        texto += linea + "\n"
        
        # Items
        items = self.datos_factura.get("items", [])
        for item in items:
            cantidad = item.get("cantidad", 0)
            unidad = item.get("unidad", "Unidad")
            descripcion = item.get("descripcion", "")[:20]
            precio = item.get("precio_unitario", 0)
            
            linea_item = f"{cantidad:.2f} {unidad} {descripcion:<15} {precio:>6.2f}\n"
            texto += linea_item
        
        # Línea separadora
        texto += linea + "\n\n"
        
        # Total
        total = self.datos_factura.get("total", 0)
        texto += f"TOTAL US$...            **{total:.2f}**\n\n"
        
        # Total en letras (simplificado)
        texto += f"SON: {self.numero_a_letras_simple(total)}.\n\n"
        
        # Nota legal
        texto += "(ESTE TICKET ES UNA REPRESENTACIÓN\n"
        texto += "     GRÁFICA DEL DTE OFICIAL)\n\n"
        
        # Mensaje de agradecimiento
        texto += "      GRACIAS POR SU COMPRA\n"
        texto += linea + "\n"
        
        return texto
    
    def numero_a_letras_simple(self, numero):
        """Conversión simple de número a letras."""
        entero = int(numero)
        if entero < 100:
            return f"{entero} DÓLARES"
        return "DÓLARES"
    
    def imprimir_ticket(self):
        """Imprime el ticket generado."""
        if not self.ruta_pdf_generado:
            messagebox.showwarning("Advertencia", 
                "Primero debe generar el ticket")
            return
        
        try:
            # Si no hay impresora seleccionada, mostrar diálogo de selección
            if not self.impresora_seleccionada:
                if not self.seleccionar_impresora():
                    return  # Usuario canceló la selección
            
            # Importar la función de impresión
            from ticket_genrator import imprimir_ticket as imprimir_pdf
            
            # Imprimir con la impresora seleccionada
            exito = imprimir_pdf(self.ruta_pdf_generado, self.impresora_seleccionada)
            if exito:
                messagebox.showinfo("Éxito", "Ticket enviado a la impresora")
            else:
                messagebox.showwarning("Advertencia", 
                    "No se pudo imprimir automáticamente. Abra el PDF manualmente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al imprimir: {str(e)}")
            messagebox.showerror("Error", f"Error al imprimir: {str(e)}")
    
    def abrir_pdf(self):
        """Abre el PDF generado con el visor predeterminado."""
        if not self.ruta_pdf_generado:
            messagebox.showwarning("Advertencia", 
                "Primero debe generar el ticket")
            return
        
        try:
            os.startfile(self.ruta_pdf_generado)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el PDF: {str(e)}")
    
    def abrir_factura_cargada(self):
        """Abre la factura PDF cargada con el visor predeterminado."""
        if not self.ruta_factura_cargada:
            messagebox.showwarning("Advertencia", 
                "Primero debe cargar una factura")
            return
        
        try:
            os.startfile(self.ruta_factura_cargada)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir la factura: {str(e)}")
    
    def abrir_carpeta_tickets(self):
        """Abre la carpeta donde se guardan los tickets generados."""
        from settings import RUTA_TICKETS
        
        # Crear la carpeta si no existe
        if not os.path.exists(RUTA_TICKETS):
            os.makedirs(RUTA_TICKETS)
        
        try:
            os.startfile(RUTA_TICKETS)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir la carpeta: {str(e)}")
    
    def crear_interfaz_inventario(self):
        """Crea la interfaz de inventario integrada en la pestaña."""
        try:
            from inventario_integrado import InventarioIntegrado
            
            # Crear la interfaz directamente en el frame
            self.inventario_integrado = InventarioIntegrado(self.frame_inventario, self)
            
        except Exception as e:
            # Si hay error, mostrar mensaje en la pestaña
            error_label = ttk.Label(self.frame_inventario, 
                                   text=f"Error al cargar inventario: {str(e)}", 
                                   font=("Arial", 12))
            error_label.grid(row=0, column=0, padx=20, pady=20)
    
    def abrir_inventario(self):
        """Cambia a la pantalla de inventario."""
        self.mostrar_pantalla_inventario()
    
    def limpiar_tickets_antiguos(self):
        """Permite limpiar tickets antiguos de la carpeta y archivos temporales PNG."""
        from settings import RUTA_TICKETS
        import glob
        from datetime import datetime, timedelta
        
        if not os.path.exists(RUTA_TICKETS):
            messagebox.showinfo("Información", "No hay tickets para limpiar")
            return
        
        # Contar tickets PDF
        tickets = glob.glob(os.path.join(RUTA_TICKETS, "ticket_*.pdf"))
        total_tickets = len(tickets)
        
        # Contar archivos PNG temporales en el directorio actual
        archivos_png = glob.glob("temp_qr*.png")
        total_png = len(archivos_png)
        
        if total_tickets == 0 and total_png == 0:
            messagebox.showinfo("Información", "No hay tickets ni archivos temporales para limpiar")
            return
        
        # Crear diálogo de opciones
        dialog = tk.Toplevel(self.root)
        dialog.title("Limpiar Tickets y Archivos Temporales")
        dialog.geometry("450x280")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar el diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text=f"Total de tickets PDF: {total_tickets}", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        
        ttk.Label(frame, text=f"Total de archivos PNG temporales: {total_png}", 
                 font=("Arial", 11, "bold")).grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Label(frame, text="Seleccione qué archivos eliminar:").grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Variable para la opción seleccionada
        opcion_var = tk.StringVar(value="todos")
        
        ttk.Radiobutton(frame, text="Todos los tickets y archivos temporales", 
                       variable=opcion_var, value="todos").grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(frame, text="Tickets de hace más de 7 días", 
                       variable=opcion_var, value="7dias").grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(frame, text="Tickets de hace más de 30 días", 
                       variable=opcion_var, value="30dias").grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        def ejecutar_limpieza():
            opcion = opcion_var.get()
            eliminados_pdf = 0
            eliminados_png = 0
            
            try:
                if opcion == "todos":
                    respuesta = messagebox.askyesno("Confirmar", 
                        f"¿Está seguro de eliminar TODOS los {total_tickets} tickets PDF y {total_png} archivos PNG temporales?",
                        parent=dialog)
                    if respuesta:
                        # Eliminar tickets PDF
                        for ticket in tickets:
                            os.remove(ticket)
                            eliminados_pdf += 1
                        
                        # Eliminar archivos PNG temporales
                        for png in archivos_png:
                            os.remove(png)
                            eliminados_png += 1
                else:
                    dias = 7 if opcion == "7dias" else 30
                    fecha_limite = datetime.now() - timedelta(days=dias)
                    
                    # Eliminar tickets PDF antiguos
                    for ticket in tickets:
                        fecha_archivo = datetime.fromtimestamp(os.path.getmtime(ticket))
                        if fecha_archivo < fecha_limite:
                            os.remove(ticket)
                            eliminados_pdf += 1
                    
                    # Los PNG temporales siempre se eliminan si existen (son temporales)
                    if total_png > 0:
                        respuesta_png = messagebox.askyesno("Archivos temporales", 
                            f"¿Desea eliminar también los {total_png} archivos PNG temporales?",
                            parent=dialog)
                        if respuesta_png:
                            for png in archivos_png:
                                os.remove(png)
                                eliminados_png += 1
                
                dialog.destroy()
                
                mensaje = []
                if eliminados_pdf > 0:
                    mensaje.append(f"{eliminados_pdf} ticket(s) PDF")
                if eliminados_png > 0:
                    mensaje.append(f"{eliminados_png} archivo(s) PNG")
                
                if mensaje:
                    messagebox.showinfo("Éxito", 
                        f"Se eliminaron: {' y '.join(mensaje)}")
                else:
                    messagebox.showinfo("Información", 
                        "No se encontraron archivos para eliminar con los criterios seleccionados")
                        
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar archivos: {str(e)}")
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Eliminar", command=ejecutar_limpieza).grid(
            row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).grid(
            row=0, column=1, padx=5)
    
    def cargar_emisores(self):
        """Carga la lista de emisores desde un archivo JSON."""
        import json
        import os
        
        archivo_emisores = "emisores.json"
        
        if os.path.exists(archivo_emisores):
            try:
                with open(archivo_emisores, 'r', encoding='utf-8') as f:
                    self.emisores = json.load(f)
            except:
                self.emisores = []
        
        # Si no hay emisores, agregar uno por defecto
        if len(self.emisores) == 0:
            from settings import EMPRESA
            self.emisores = [{
                "nombre": EMPRESA.get("nombre", "Mi Empresa S.A."),
                "nit": EMPRESA.get("ruc", "00000000-0")
            }]
            self.guardar_emisores()
    
    def guardar_emisores(self):
        """Guarda la lista de emisores en un archivo JSON."""
        import json
        
        with open("emisores.json", 'w', encoding='utf-8') as f:
            json.dump(self.emisores, f, indent=2, ensure_ascii=False)
    
    def actualizar_combo_emisores(self):
        """Actualiza el combobox con la lista de emisores."""
        valores = [f"{e['nombre']} - NIT: {e['nit']}" for e in self.emisores]
        self.combo_emisor['values'] = valores
        if len(valores) > 0:
            self.combo_emisor.current(0)
    
    def on_emisor_seleccionado(self, event):
        """Se ejecuta cuando se selecciona un emisor del combobox."""
        pass  # El emisor seleccionado se usará al generar el ticket
    
    def agregar_emisor(self):
        """Abre un diálogo para agregar un nuevo emisor."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Emisor")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar el diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Nombre del emisor
        ttk.Label(frame, text="Nombre del Emisor:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_nombre = ttk.Entry(frame, width=40)
        entry_nombre.grid(row=0, column=1, pady=5, padx=5)
        entry_nombre.focus()
        
        # NIT
        ttk.Label(frame, text="NIT:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_nit = ttk.Entry(frame, width=40)
        entry_nit.grid(row=1, column=1, pady=5, padx=5)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            nit = entry_nit.get().strip()
            
            if not nombre or not nit:
                messagebox.showwarning("Advertencia", "Debe completar todos los campos")
                return
            
            self.emisores.append({"nombre": nombre, "nit": nit})
            self.guardar_emisores()
            self.actualizar_combo_emisores()
            self.combo_emisor.current(len(self.emisores) - 1)
            dialog.destroy()
            messagebox.showinfo("Éxito", "Emisor agregado correctamente")
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="Guardar", command=guardar).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).grid(row=0, column=1, padx=5)
    
    def eliminar_emisor(self):
        """Elimina el emisor seleccionado."""
        if len(self.emisores) <= 1:
            messagebox.showwarning("Advertencia", "Debe haber al menos un emisor")
            return
        
        indice = self.combo_emisor.current()
        if indice < 0:
            return
        
        emisor = self.emisores[indice]
        respuesta = messagebox.askyesno("Confirmar", 
            f"¿Está seguro de eliminar el emisor:\n{emisor['nombre']}?")
        
        if respuesta:
            self.emisores.pop(indice)
            self.guardar_emisores()
            self.actualizar_combo_emisores()
            messagebox.showinfo("Éxito", "Emisor eliminado correctamente")
    
    def obtener_emisor_seleccionado(self):
        """Retorna el emisor actualmente seleccionado."""
        indice = self.combo_emisor.current()
        if indice >= 0 and indice < len(self.emisores):
            return self.emisores[indice]
        return self.emisores[0] if len(self.emisores) > 0 else None
    
    def seleccionar_impresora(self):
        """
        Muestra un diálogo para seleccionar la impresora.
        Retorna True si se seleccionó una impresora, False si se canceló.
        """
        from ticket_genrator import obtener_impresoras_disponibles, obtener_impresora_predeterminada
        
        # Obtener impresoras disponibles
        impresoras = obtener_impresoras_disponibles()
        
        if not impresoras:
            messagebox.showwarning("Advertencia", 
                "No se encontraron impresoras instaladas en el sistema")
            return False
        
        # Crear diálogo de selección
        dialog = tk.Toplevel(self.root)
        dialog.title("Seleccionar Impresora")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar el diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Seleccione la impresora para los tickets:", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Esta configuración se guardará para futuras impresiones.", 
                 font=("Arial", 9)).grid(row=1, column=0, columnspan=2, pady=5)
        
        # Lista de impresoras
        ttk.Label(frame, text="Impresoras disponibles:").grid(
            row=2, column=0, sticky=tk.W, pady=10)
        
        # Listbox con scrollbar
        list_frame = ttk.Frame(frame)
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set,
                            font=("Arial", 10))
        scrollbar.config(command=listbox.yview)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Agregar impresoras a la lista
        impresora_predeterminada = obtener_impresora_predeterminada()
        for i, impresora in enumerate(impresoras):
            texto = impresora
            if impresora == impresora_predeterminada:
                texto += " (Predeterminada)"
            listbox.insert(tk.END, texto)
            if impresora == impresora_predeterminada:
                listbox.selection_set(i)
                listbox.see(i)
        
        # Variable para guardar el resultado
        resultado = [False]
        
        def confirmar_seleccion():
            seleccion = listbox.curselection()
            if not seleccion:
                messagebox.showwarning("Advertencia", 
                    "Debe seleccionar una impresora", parent=dialog)
                return
            
            indice = seleccion[0]
            self.impresora_seleccionada = impresoras[indice]
            self.guardar_impresora_seleccionada()
            resultado[0] = True
            dialog.destroy()
        
        def cambiar_impresora_despues():
            """Información sobre cómo cambiar la impresora después."""
            messagebox.showinfo("Cambiar Impresora", 
                "Para cambiar la impresora en el futuro:\n\n"
                "1. Cierra el programa\n"
                "2. Elimina el archivo 'impresora_config.json'\n"
                "3. Vuelve a abrir el programa\n\n"
                "O puedes editar directamente el archivo 'impresora_config.json'",
                parent=dialog)
        
        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Confirmar", command=confirmar_seleccion).grid(
            row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).grid(
            row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="¿Cómo cambiar después?", 
                  command=cambiar_impresora_despues).grid(row=0, column=2, padx=5)
        
        # Esperar a que se cierre el diálogo
        dialog.wait_window()
        
        return resultado[0]
    
    def guardar_impresora_seleccionada(self):
        """Guarda la impresora seleccionada en un archivo JSON."""
        import json
        
        config = {
            "impresora": self.impresora_seleccionada
        }
        
        with open("impresora_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Impresora guardada: {self.impresora_seleccionada}")
    
    def cargar_impresora_guardada(self):
        """Carga la impresora guardada desde el archivo JSON."""
        import json
        import os
        
        if os.path.exists("impresora_config.json"):
            try:
                with open("impresora_config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.impresora_seleccionada = config.get("impresora")
                    if self.impresora_seleccionada:
                        print(f"✓ Impresora cargada: {self.impresora_seleccionada}")
            except Exception as e:
                print(f"Error al cargar configuración de impresora: {e}")
                self.impresora_seleccionada = None
        else:
            self.impresora_seleccionada = None

def main():
    root = tk.Tk()
    app = TicketGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

