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

# Importar auto-actualizador
try:
    from auto_actualizador import verificar_actualizacion_al_iniciar
    AUTO_ACTUALIZADOR_DISPONIBLE = True
except ImportError:
    print("⚠ Módulo auto_actualizador no disponible")
    AUTO_ACTUALIZADOR_DISPONIBLE = False

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
        
        # Verificar actualizaciones al iniciar (después de crear la interfaz)
        if AUTO_ACTUALIZADOR_DISPONIBLE:
            # Esperar 2 segundos para que la ventana se muestre completamente
            self.root.after(2000, lambda: verificar_actualizacion_al_iniciar(self.root))
    
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
        
        # ========== FRAME 3: REPORTES ==========
        self.frame_reportes = ttk.Frame(self.container, style="Custom.TFrame")
        self.frame_reportes.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Crear interfaces
        self.crear_interfaz_tickets()
        self.inventario_manager.crear_interfaz_inventario()
        self.crear_interfaz_reportes()
        
        # Mostrar inicialmente la pantalla de tickets
        self.mostrar_pantalla_tickets()
    
    def mostrar_pantalla_tickets(self):
        """Muestra la pantalla de tickets y oculta inventario."""
        self.frame_tickets.tkraise()
    
    def mostrar_pantalla_inventario(self):
        """Muestra la pantalla de inventario y oculta tickets."""
        self.frame_inventario.tkraise()
    
    def mostrar_pantalla_reportes(self):
        """Muestra la pantalla de reportes."""
        self.frame_reportes.tkraise()
    
    def crear_interfaz_reportes(self):
        """Crea la interfaz de reportes integrada en la pestaña."""
        try:
            from reportes_integrado import ReportesIntegrado
            
            # Crear la interfaz directamente en el frame
            self.reportes_integrado = ReportesIntegrado(self.frame_reportes, self)
            
        except Exception as e:
            # Si hay error, mostrar mensaje en la pestaña
            import tkinter as tk
            from estilos import obtener_colores
            colores = obtener_colores()
            error_label = tk.Label(
                self.frame_reportes, 
                text=f"Error al cargar reportes: {str(e)}", 
                font=("Arial", 12),
                bg=colores['fondo'],
                fg='white'
            )
            error_label.pack(padx=20, pady=20)
            print(f"Error al crear interfaz de reportes: {e}")
            import traceback
            traceback.print_exc()    

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
        
        # Cargar imágenes para los botones de emisor
        try:
            from PIL import Image, ImageTk
            import numpy as np
            
            # Obtener el color de fondo del panel en formato RGB
            # El color es #595959 (gris oscuro)
            color_fondo_rgb = (89, 89, 89)
            
            def reemplazar_fondo_transparente(img_path, color_reemplazo):
                """Reemplaza píxeles transparentes y blancos con el color del fondo."""
                img = Image.open(img_path)
                img = img.convert("RGBA")
                
                # Convertir a numpy array
                data = np.array(img)
                
                # Obtener los canales
                r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
                
                # Crear máscara para píxeles que deben ser reemplazados:
                # 1. Píxeles con alpha bajo (< 128) - transparentes o semi-transparentes
                # 2. Píxeles blancos o casi blancos (RGB > 200)
                mascara_transparente = a < 128
                mascara_blanco = (r > 200) & (g > 200) & (b > 200)
                mascara_reemplazar = mascara_transparente | mascara_blanco
                
                # Reemplazar con el color del fondo y alpha completo
                data[mascara_reemplazar] = [color_reemplazo[0], color_reemplazo[1], color_reemplazo[2], 255]
                
                # Crear imagen procesada
                img_procesada = Image.fromarray(data, mode='RGBA')
                
                # Crear fondo sólido con el color del panel
                fondo = Image.new("RGB", img_procesada.size, color_reemplazo)
                
                # Pegar la imagen sobre el fondo (esto maneja cualquier alpha restante)
                fondo.paste(img_procesada, (0, 0), img_procesada)
                
                return fondo
            
            # Cargar y procesar imagen del botón +
            img_mas = reemplazar_fondo_transparente("disenos/botonmas.png", color_fondo_rgb)
            img_mas = img_mas.resize((40, 40), Image.Resampling.LANCZOS)
            self.img_mas = ImageTk.PhotoImage(img_mas)
            
            # Cargar y procesar imagen del botón editar
            img_editar = reemplazar_fondo_transparente("disenos/botoneditar.png", color_fondo_rgb)
            img_editar = img_editar.resize((30, 30), Image.Resampling.LANCZOS)
            self.img_editar = ImageTk.PhotoImage(img_editar)
            
            # Cargar y procesar imagen del botón -
            img_menos = reemplazar_fondo_transparente("disenos/botonmenos.png", color_fondo_rgb)
            img_menos = img_menos.resize((30, 30), Image.Resampling.LANCZOS)
            self.img_menos = ImageTk.PhotoImage(img_menos)
            
            print("✓ Imágenes de botones cargadas y procesadas correctamente")
            
        except Exception as e:
            print(f"Error al cargar imágenes de botones: {e}")
            import traceback
            traceback.print_exc()
            self.img_mas = None
            self.img_editar = None
            self.img_menos = None
        
        # Botón + para agregar emisor (con imagen)
        if self.img_mas:
            btn_agregar_emisor = tk.Button(emisor_frame, image=self.img_mas, 
                                          command=self.agregar_emisor,
                                          bd=0, relief=tk.FLAT, cursor="hand2",
                                          bg=self.colores["panel"], activebackground=self.colores["panel"],
                                          highlightthickness=0)
        else:
            btn_agregar_emisor = ttk.Button(emisor_frame, text="+", width=3,
                                           command=self.agregar_emisor, style="Custom.TButton")
        btn_agregar_emisor.grid(row=0, column=2, padx=10)  # Aumentado de 2 a 10
        
        # Botón ✏️ para editar emisor (con imagen)
        if self.img_editar:
            btn_editar_emisor = tk.Button(emisor_frame, image=self.img_editar,
                                         command=self.editar_emisor,
                                         bd=0, relief=tk.FLAT, cursor="hand2",
                                         bg=self.colores["panel"], activebackground=self.colores["panel"],
                                         highlightthickness=0)
        else:
            btn_editar_emisor = ttk.Button(emisor_frame, text="✏️", width=3,
                                          command=self.editar_emisor, style="Custom.TButton")
        btn_editar_emisor.grid(row=0, column=3, padx=10)  # Aumentado de 2 a 10
        
        # Botón - para eliminar emisor (con imagen)
        if self.img_menos:
            btn_eliminar_emisor = tk.Button(emisor_frame, image=self.img_menos,
                                           command=self.eliminar_emisor,
                                           bd=0, relief=tk.FLAT, cursor="hand2",
                                           bg=self.colores["panel"], activebackground=self.colores["panel"],
                                           highlightthickness=0)
        else:
            btn_eliminar_emisor = ttk.Button(emisor_frame, text="-", width=3,
                                            command=self.eliminar_emisor, style="Custom.TButton")
        btn_eliminar_emisor.grid(row=0, column=4, padx=10)  # Aumentado de 2 a 10
        
        # Actualizar lista de emisores
        self.actualizar_combo_emisores()
        
        # Frame para botones de factura
        factura_btn_frame = ttk.Frame(left_panel, style="Panel.TFrame")
        factura_btn_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='w', padx=20)
        
        # Botón cargar factura
        btn_cargar = crear_boton_personalizado(factura_btn_frame, "📄 Cargar Factura", 
                                               self.cargar_factura, ancho=160, alto=35)
        btn_cargar.grid(row=0, column=0, padx=(0, 1))
        
        # Botón abrir factura
        self.btn_abrir_factura = crear_boton_personalizado(factura_btn_frame, "📂 Abrir Factura", 
                                                           self.abrir_factura_cargada, 
                                                           ancho=160, alto=35, estado="disabled")
        self.btn_abrir_factura.grid(row=0, column=1, padx=1)
        
        # Botón abrir carpeta de tickets
        btn_carpeta_tickets = crear_boton_personalizado(factura_btn_frame, "📁 Carpeta Tickets", 
                                                        self.abrir_carpeta_tickets, 
                                                        ancho=160, alto=35)
        btn_carpeta_tickets.grid(row=0, column=2, padx=1)
        
        # Botón gestionar inventario (cambia a la pestaña de inventario)
        btn_inventario = crear_boton_personalizado(factura_btn_frame, "📦 Gestionar Inventario", 
                                                   self.abrir_inventario, 
                                                   ancho=200, alto=35)
        btn_inventario.grid(row=0, column=3, padx=(1, 0))
        
        # Frame para checkbox de inventario (mejor diseño)
        inventario_config_frame = ttk.Frame(factura_btn_frame, style="Panel.TFrame")
        inventario_config_frame.grid(row=1, column=0, columnspan=4, pady=(15, 0), sticky='w')
        
        # Checkbox para habilitar/deshabilitar inventario automático
        self.inventario_habilitado = tk.BooleanVar(value=True)  # Por defecto habilitado
        self.cargar_configuracion_inventario()
        
        # Icono para el checkbox
        label_icono = ttk.Label(inventario_config_frame, text="📦", 
                               font=("Arial", 12), style="Panel.TLabel")
        label_icono.grid(row=0, column=0, padx=(0, 5))
        
        check_inventario = ttk.Checkbutton(
            inventario_config_frame, 
            text="Descontar inventario automáticamente al generar ticket",
            variable=self.inventario_habilitado,
            command=self.guardar_configuracion_inventario,
            style="Custom.TCheckbutton"
        )
        check_inventario.grid(row=0, column=1, sticky='w')
        
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
                                       show="headings", height=15)
        
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
        
        # Botones de acción (siempre visibles al final)
        btn_frame = ttk.Frame(left_panel, style="Panel.TFrame")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky='ew')
        
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
        
        self.btn_abrir = crear_boton_personalizado(btn_frame, "📄 Abrir Ticket", 
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
            
            # Procesar inventario solo si está habilitado
            if self.inventario_habilitado.get():
                self.inventario_manager.procesar_inventario_factura(self.datos_factura)
            else:
                print("DEBUG INVENTARIO: Inventario deshabilitado, no se procesará")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la factura: {str(e)}")
    
    def abrir_inventario(self):
        """Cambia a la pantalla de inventario."""
        self.mostrar_pantalla_inventario()
    
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
        
        # Limpiar totales (ya no se usan en la interfaz, solo en Vista Previa de Datos)
        # self.lbl_monto_operacion.config(text="$ 0.00")
        # self.lbl_otros_montos.config(text="$ 0.00")
        # self.lbl_total_pagar.config(text="$ 0.00")
        
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
        
        # Estos labels ya no existen en la interfaz (se eliminó la sección Resumen)
        # self.lbl_monto_operacion.config(text=f"$ {subtotal:.2f}")
        # self.lbl_otros_montos.config(text=f"$ {otros_montos:.2f}")
        # self.lbl_total_pagar.config(text=f"$ {total:.2f}")
    
    def aplicar_cambios_ticket(self):
        """Aplica los cambios editados en la vista previa y regenera el ticket."""
        if not self.datos_factura:
            messagebox.showwarning("Advertencia", 
                "No hay datos de factura cargados")
            return
        
        try:
            # Obtener el texto editado de la vista previa
            texto_editado = self.txt_ticket_preview.get("1.0", tk.END)
            
            # Eliminar el ticket anterior si existe
            if self.ruta_pdf_generado and os.path.exists(self.ruta_pdf_generado):
                try:
                    import time
                    time.sleep(0.3)  # Pequeña pausa para cerrar visores
                    os.remove(self.ruta_pdf_generado)
                    print(f"DEBUG: Ticket anterior eliminado: {self.ruta_pdf_generado}")
                except Exception as e:
                    print(f"DEBUG: No se pudo eliminar ticket anterior: {e}")
            
            # Generar ticket desde el texto editado
            from ticket_desde_texto import generar_ticket_desde_texto
            
            # Obtener ruta del QR - probar diferentes claves
            ruta_qr = None
            if "ruta_qr_extraido" in self.datos_factura:
                ruta_qr = self.datos_factura["ruta_qr_extraido"]
            elif "qr_path" in self.datos_factura:
                ruta_qr = self.datos_factura["qr_path"]
            
            print(f"DEBUG: Ruta QR encontrada: {ruta_qr}")
            if ruta_qr:
                print(f"DEBUG: QR existe en disco: {os.path.exists(ruta_qr) if ruta_qr else False}")
            
            numero_factura = self.datos_factura.get("numero_factura", "EDITADO")
            
            # Generar el nuevo ticket desde el texto
            self.ruta_pdf_generado = generar_ticket_desde_texto(
                texto_editado, 
                ruta_qr, 
                numero_factura
            )
            
            print(f"DEBUG: Nuevo ticket generado desde texto editado: {self.ruta_pdf_generado}")
            
            # Habilitar botones
            self.btn_imprimir.config(state=tk.NORMAL)
            self.btn_abrir.config(state=tk.NORMAL)
            
            messagebox.showinfo("Éxito", 
                "✅ Ticket regenerado con tus cambios.\n\nEl nuevo ticket refleja exactamente lo que editaste en la vista previa.")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
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
            emisor = {"nombre": "EMISOR", "nit": "00000000-0", "direccion": "", "gmail": "", "telefono": ""}
        
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
        
        # Dirección del emisor (si existe)
        direccion = emisor.get("direccion", "")
        if direccion:
            # Dividir la dirección en líneas si es muy larga (máximo 40 caracteres por línea)
            palabras = direccion.split()
            lineas_direccion = []
            linea_actual = ""
            
            for palabra in palabras:
                if len(linea_actual + " " + palabra) <= 40:
                    linea_actual += (" " if linea_actual else "") + palabra
                else:
                    if linea_actual:
                        lineas_direccion.append(linea_actual)
                    linea_actual = palabra
            
            if linea_actual:
                lineas_direccion.append(linea_actual)
            
            # Agregar cada línea de dirección
            for linea_dir in lineas_direccion:
                texto += f"{linea_dir}\n"
            texto += "\n"
        
        # Código de Generación (si existe)
        codigo_generacion = self.datos_factura.get("codigo_generacion", "")
        if codigo_generacion:
            texto += f"CÓDIGO DE GENERACIÓN:\n{codigo_generacion}\n\n"
        
        # Sello de Recepción (si existe)
        sello_recepcion = self.datos_factura.get("sello_recepcion", "")
        if sello_recepcion:
            texto += f"SELLO DE RECEPCIÓN:\n{sello_recepcion}\n\n"
        
        # Cliente
        cliente = self.datos_factura.get("cliente", {})
        texto += f"CLIENTE: {cliente.get('nombre', 'N/A')}\n"
        texto += f"DUI: {cliente.get('ruc_dni', 'N/A')}\n\n"
        
        # Fecha
        fecha = self.datos_factura.get("fecha", "")
        texto += f"FECHA: {fecha}\n\n"
        
        texto += linea + "\n"
        texto += "DESCRIPCIÓN\n"
        texto += linea + "\n"
        
        # Items
        items = self.datos_factura.get("items", [])
        for item in items:
            descripcion = item.get("descripcion", "")
            cantidad = item.get("cantidad", 0)
            precio = item.get("precio_unitario", 0)
            total_item = cantidad * precio
            
            texto += f"{descripcion}\n"
            texto += f"  {cantidad} x ${precio:.2f} = ${total_item:.2f}\n\n"
        
        texto += linea + "\n"
        
        # Totales
        total = self.datos_factura.get("total", 0)
        texto += f"TOTAL: ${total:.2f}\n"
        texto += f"SON: {self.numero_a_letras_simple(total)}\n\n"
        
        texto += "GRACIAS POR SU COMPRA\n"
        texto += linea + "\n"
        
        # Gmail y Teléfono del emisor (si existen)
        gmail = emisor.get("gmail", "")
        telefono = emisor.get("telefono", "")
        
        if gmail:
            texto += f"Gmail: {gmail}\n"
        if telefono:
            texto += f"Teléfono: {telefono}\n"
        
        return texto
    
    def numero_a_letras_simple(self, numero):
        """Conversión simple de número a letras."""
        entero = int(numero)
        if entero == 0:
            return "CERO DÓLARES"
        return "DÓLARES"
    
    def imprimir_ticket(self):
        """Imprime el ticket generado."""
        if not self.ruta_pdf_generado:
            messagebox.showwarning("Advertencia", 
                "No hay ticket generado para imprimir")
            return
        
        try:
            # Auto-seleccionar primera impresora si no hay una seleccionada
            if not self.impresora_seleccionada:
                try:
                    import win32print
                    # Obtener lista de impresoras
                    impresoras = [printer[2] for printer in win32print.EnumPrinters(
                        win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
                    
                    if not impresoras:
                        messagebox.showwarning("Advertencia", 
                            "No se encontraron impresoras instaladas.\n"
                            "Por favor, instale una impresora primero.")
                        return
                    
                    # Usar la primera impresora disponible
                    self.impresora_seleccionada = impresoras[0]
                    print(f"Auto-seleccionada impresora: {self.impresora_seleccionada}")
                    
                except ImportError:
                    # Si no está win32print, intentar obtener la predeterminada
                    try:
                        import win32print
                        self.impresora_seleccionada = win32print.GetDefaultPrinter()
                    except:
                        # Usar None para que el sistema use la predeterminada
                        self.impresora_seleccionada = None
                        print("Usando impresora predeterminada del sistema")
            
            # Imprimir usando la función del módulo ticket_genrator
            print(f"Imprimiendo en: {self.impresora_seleccionada}")
            resultado = imprimir_ticket(self.ruta_pdf_generado, self.impresora_seleccionada)
            
            if resultado:
                messagebox.showinfo("Impresión Enviada", 
                    f"Ticket enviado a la impresora:\n{self.impresora_seleccionada or 'Predeterminada'}\n\n"
                    "El ticket se está imprimiendo...")
            else:
                messagebox.showwarning("Impresión", 
                    "No se pudo confirmar la impresión.\n"
                    "Verifica el estado de la impresora.")
            
        except Exception as e:
            messagebox.showerror("Error al Imprimir", 
                f"Error: {str(e)}\n\n"
                "Intenta:\n"
                "1. Usar el botón 'Abrir PDF' e imprimir manualmente\n"
                "2. Verificar que la impresora esté correctamente instalada\n"
                "3. Revisar los permisos del programa")
            import traceback
            traceback.print_exc()
    
    def abrir_pdf(self):
        """Abre el PDF generado con el visor predeterminado."""
        if not self.ruta_pdf_generado:
            messagebox.showwarning("Advertencia", 
                "No hay ticket generado para abrir")
            return
        
        try:
            os.startfile(self.ruta_pdf_generado)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el PDF: {str(e)}")
    
    def abrir_factura_cargada(self):
        """Abre la factura PDF cargada con el visor predeterminado."""
        if not self.ruta_factura_cargada:
            messagebox.showwarning("Advertencia", 
                "No hay factura cargada para abrir")
            return
        
        try:
            os.startfile(self.ruta_factura_cargada)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir la factura: {str(e)}")
    
    def abrir_carpeta_tickets(self):
        """Abre la carpeta donde se guardan los tickets generados."""
        from settings import RUTA_TICKETS
        try:
            if not os.path.exists(RUTA_TICKETS):
                os.makedirs(RUTA_TICKETS)
            
            os.startfile(RUTA_TICKETS)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir la carpeta: {str(e)}")
    
    def abrir_carpeta_reportes(self):
        """Abre la carpeta donde se guardan los reportes generados."""
        carpeta_reportes = os.path.abspath("reportes_generados")
        try:
            if not os.path.exists(carpeta_reportes):
                os.makedirs(carpeta_reportes)
            
            os.startfile(carpeta_reportes)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir la carpeta de reportes: {str(e)}")
    
    def limpiar_tickets_antiguos(self):
        """Permite limpiar tickets antiguos de la carpeta y archivos temporales PNG."""
        from settings import RUTA_TICKETS
        
        respuesta = messagebox.askyesno("Confirmar", 
            "¿Desea limpiar todos los tickets antiguos y archivos temporales?\n\n"
            "Esta acción eliminará:\n"
            "• Todos los archivos PDF de la carpeta de tickets\n"
            "• Todos los archivos PNG temporales\n\n"
            "¿Continuar?")
        
        if not respuesta:
            return
        
        try:
            archivos_eliminados = 0
            
            # Limpiar carpeta de tickets
            if os.path.exists(RUTA_TICKETS):
                for archivo in os.listdir(RUTA_TICKETS):
                    if archivo.endswith('.pdf'):
                        ruta_archivo = os.path.join(RUTA_TICKETS, archivo)
                        os.remove(ruta_archivo)
                        archivos_eliminados += 1
            
            # Limpiar archivos PNG temporales del directorio actual
            directorio_actual = os.getcwd()
            for archivo in os.listdir(directorio_actual):
                if archivo.endswith('.png') and ('qr_' in archivo or 'temp_' in archivo):
                    try:
                        os.remove(archivo)
                        archivos_eliminados += 1
                    except:
                        pass  # Ignorar errores al eliminar archivos temporales
            
            messagebox.showinfo("Éxito", 
                f"Se eliminaron {archivos_eliminados} archivos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al limpiar archivos: {str(e)}")
    
    # Funciones de emisores
    def cargar_emisores(self):
        """Carga la lista de emisores desde un archivo JSON."""
        import json
        try:
            if os.path.exists("emisores.json"):
                with open("emisores.json", "r", encoding="utf-8") as f:
                    self.emisores = json.load(f)
                    
                # Asegurar que todos los emisores tengan los campos nuevos
                for emisor in self.emisores:
                    if "direccion" not in emisor:
                        emisor["direccion"] = ""
                    if "gmail" not in emisor:
                        emisor["gmail"] = ""
                    if "telefono" not in emisor:
                        emisor["telefono"] = ""
                
                # Guardar los cambios si se agregaron campos
                self.guardar_emisores()
            else:
                # Emisor por defecto con todos los campos
                self.emisores = [{
                    "nombre": "La Mascota",
                    "nit": "03988873-6",
                    "direccion": "CALLE JOSE MARIANO MENDEZ 6 AV. SUR, SANTA ANA, SANTA ANA",
                    "gmail": "lamascotasantaana@gmail.com",
                    "telefono": "7731 0643"
                }]
                self.guardar_emisores()
        except Exception as e:
            print(f"Error al cargar emisores: {e}")
            self.emisores = [{
                "nombre": "La Mascota",
                "nit": "03988873-6",
                "direccion": "CALLE JOSE MARIANO MENDEZ 6 AV. SUR, SANTA ANA, SANTA ANA",
                "gmail": "lamascotasantaana@gmail.com",
                "telefono": "7731 0643"
            }]
    
    def guardar_emisores(self):
        """Guarda la lista de emisores en un archivo JSON."""
        import json
        try:
            with open("emisores.json", "w", encoding="utf-8") as f:
                json.dump(self.emisores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar emisores: {e}")
    
    def actualizar_combo_emisores(self):
        """Actualiza el combobox con la lista de emisores."""
        valores = [f"{emisor['nombre']} - NIT: {emisor['nit']}" for emisor in self.emisores]
        self.combo_emisor['values'] = valores
        if valores:
            self.combo_emisor.set(valores[0])
    
    def obtener_emisor_seleccionado(self):
        """Obtiene el emisor seleccionado del combobox."""
        seleccion = self.combo_emisor.get()
        if not seleccion:
            return None
        
        # Extraer el nombre del emisor de la selección
        try:
            nombre_emisor = seleccion.split(" - NIT:")[0]
            for emisor in self.emisores:
                if emisor["nombre"] == nombre_emisor:
                    return emisor
        except:
            pass
        
        return None
    
    def on_emisor_seleccionado(self, event=None):
        """Maneja la selección de un emisor."""
        # Actualizar la vista previa del ticket cuando cambia el emisor
        if hasattr(self, 'text_preview') and self.datos_factura:
            self.mostrar_vista_previa_ticket()
    
    def agregar_emisor(self):
        """Abre un diálogo para agregar un nuevo emisor."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Emisor")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar el diálogo
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Frame principal con scrollbar
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(main_frame, text="Nombre del Emisor:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_nombre = ttk.Entry(main_frame, width=35)
        entry_nombre.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="NIT:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_nit = ttk.Entry(main_frame, width=35)
        entry_nit.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Dirección:").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_direccion = ttk.Entry(main_frame, width=35)
        entry_direccion.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Gmail:").grid(row=3, column=0, sticky=tk.W, pady=5)
        entry_gmail = ttk.Entry(main_frame, width=35)
        entry_gmail.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Teléfono:").grid(row=4, column=0, sticky=tk.W, pady=5)
        entry_telefono = ttk.Entry(main_frame, width=35)
        entry_telefono.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            nit = entry_nit.get().strip()
            direccion = entry_direccion.get().strip()
            gmail = entry_gmail.get().strip()
            telefono = entry_telefono.get().strip()
            
            if not nombre or not nit:
                messagebox.showwarning("Advertencia", "Nombre y NIT son obligatorios")
                return
            
            # Verificar que no exista ya
            for emisor in self.emisores:
                if emisor["nombre"].lower() == nombre.lower() or emisor["nit"] == nit:
                    messagebox.showwarning("Advertencia", "Ya existe un emisor con ese nombre o NIT")
                    return
            
            # Agregar el nuevo emisor con todos los campos
            nuevo_emisor = {
                "nombre": nombre,
                "nit": nit,
                "direccion": direccion if direccion else "",
                "gmail": gmail if gmail else "",
                "telefono": telefono if telefono else ""
            }
            
            self.emisores.append(nuevo_emisor)
            self.guardar_emisores()
            self.actualizar_combo_emisores()
            
            messagebox.showinfo("Éxito", "Emisor agregado correctamente")
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Guardar", command=guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        entry_nombre.focus()
    
    def editar_emisor(self):
        """Abre un diálogo para editar el emisor seleccionado."""
        emisor_seleccionado = self.obtener_emisor_seleccionado()
        if not emisor_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un emisor para editar")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Emisor")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar el diálogo
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos con valores actuales
        ttk.Label(main_frame, text="Nombre del Emisor:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_nombre = ttk.Entry(main_frame, width=35)
        entry_nombre.insert(0, emisor_seleccionado.get("nombre", ""))
        entry_nombre.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="NIT:").grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_nit = ttk.Entry(main_frame, width=35)
        entry_nit.insert(0, emisor_seleccionado.get("nit", ""))
        entry_nit.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Dirección:").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_direccion = ttk.Entry(main_frame, width=35)
        entry_direccion.insert(0, emisor_seleccionado.get("direccion", ""))
        entry_direccion.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Gmail:").grid(row=3, column=0, sticky=tk.W, pady=5)
        entry_gmail = ttk.Entry(main_frame, width=35)
        entry_gmail.insert(0, emisor_seleccionado.get("gmail", ""))
        entry_gmail.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="Teléfono:").grid(row=4, column=0, sticky=tk.W, pady=5)
        entry_telefono = ttk.Entry(main_frame, width=35)
        entry_telefono.insert(0, emisor_seleccionado.get("telefono", ""))
        entry_telefono.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            nit = entry_nit.get().strip()
            direccion = entry_direccion.get().strip()
            gmail = entry_gmail.get().strip()
            telefono = entry_telefono.get().strip()
            
            if not nombre or not nit:
                messagebox.showwarning("Advertencia", "Nombre y NIT son obligatorios")
                return
            
            # Verificar que no exista otro emisor con el mismo nombre o NIT (excepto el actual)
            for emisor in self.emisores:
                if emisor != emisor_seleccionado:
                    if emisor["nombre"].lower() == nombre.lower() or emisor["nit"] == nit:
                        messagebox.showwarning("Advertencia", "Ya existe otro emisor con ese nombre o NIT")
                        return
            
            # Actualizar el emisor
            emisor_seleccionado["nombre"] = nombre
            emisor_seleccionado["nit"] = nit
            emisor_seleccionado["direccion"] = direccion if direccion else ""
            emisor_seleccionado["gmail"] = gmail if gmail else ""
            emisor_seleccionado["telefono"] = telefono if telefono else ""
            
            self.guardar_emisores()
            self.actualizar_combo_emisores()
            
            # Actualizar la vista previa si hay datos de factura
            if hasattr(self, 'text_preview') and self.datos_factura:
                self.mostrar_vista_previa_ticket()
            
            messagebox.showinfo("Éxito", "Emisor actualizado correctamente")
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Guardar", command=guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        entry_nombre.focus()
    
    def eliminar_emisor(self):
        """Elimina el emisor seleccionado."""
        if len(self.emisores) <= 1:
            messagebox.showwarning("Advertencia", 
                "Debe mantener al menos un emisor")
            return
        
        emisor_seleccionado = self.obtener_emisor_seleccionado()
        if not emisor_seleccionado:
            messagebox.showwarning("Advertencia", 
                "Seleccione un emisor para eliminar")
            return
        
        respuesta = messagebox.askyesno("Confirmar", 
            f"¿Desea eliminar el emisor '{emisor_seleccionado['nombre']}'?")
        
        if respuesta:
            self.emisores.remove(emisor_seleccionado)
            self.guardar_emisores()
            self.actualizar_combo_emisores()
            messagebox.showinfo("Éxito", "Emisor eliminado correctamente")
    
    # Funciones de impresora
    def seleccionar_impresora(self):
        """Muestra un diálogo para seleccionar la impresora."""
        try:
            import win32print
            
            # Obtener lista de impresoras
            impresoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            
            if not impresoras:
                messagebox.showwarning("Advertencia", 
                    "No se encontraron impresoras instaladas")
                return False
            
            # Crear diálogo de selección
            dialog = tk.Toplevel(self.root)
            dialog.title("Seleccionar Impresora")
            dialog.geometry("550x420")  # Aumentado para 3 botones
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Centrar el diálogo
            dialog.geometry("+%d+%d" % (
                self.root.winfo_rootx() + 50,
                self.root.winfo_rooty() + 50
            ))
            
            # Frame principal con scroll si es necesario
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            ttk.Label(main_frame, text="Seleccione una impresora:", 
                     font=("Arial", 11, "bold")).pack(pady=(0, 10))
            
            # Información sobre impresoras térmicas
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            info_text = tk.Text(info_frame, height=2, wrap=tk.WORD, font=("Arial", 9),
                               bg="#FFFFCC", relief=tk.FLAT, padx=8, pady=8)
            info_text.pack(fill=tk.X)
            info_text.insert("1.0", 
                "💡 NOTA: Sistema diseñado para impresoras térmicas de 80mm.\n"
                "Si tiene impresora normal, el ticket se imprimirá en formato pequeño.")
            info_text.config(state=tk.DISABLED)
            
            # Frame para lista de impresoras con scrollbar
            list_frame = ttk.Frame(main_frame)
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            # Scrollbar para la lista
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Lista de impresoras
            listbox = tk.Listbox(list_frame, height=10, font=("Arial", 10),
                                yscrollcommand=scrollbar.set)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=listbox.yview)
            
            for impresora in impresoras:
                listbox.insert(tk.END, impresora)
            
            # Seleccionar la impresora guardada o la primera por defecto
            if self.impresora_seleccionada and self.impresora_seleccionada in impresoras:
                idx = impresoras.index(self.impresora_seleccionada)
                listbox.selection_set(idx)
                listbox.see(idx)
            elif impresoras:
                listbox.selection_set(0)
            
            # Variable para el resultado
            resultado = [False]
            
            def generar_ticket_prueba_fn():
                """Genera un ticket de prueba y lo abre para revisar."""
                seleccion = listbox.curselection()
                if seleccion:
                    nombre_impresora = impresoras[seleccion[0]]
                    try:
                        from ticket_genrator import generar_ticket_prueba, imprimir_ticket
                        
                        # Generar ticket de prueba
                        ruta_prueba = generar_ticket_prueba(nombre_impresora)
                        
                        # Preguntar si desea imprimir o solo ver
                        respuesta = messagebox.askyesno("Ticket de Prueba Generado",
                            f"Ticket de prueba generado.\n\n"
                            f"¿Desea enviarlo a la impresora '{nombre_impresora}'?\n\n"
                            f"• SÍ: Enviar a imprimir y eliminar el archivo\n"
                            f"• NO: Solo abrir para visualizar",
                            icon='question')
                        
                        if respuesta:
                            # Imprimir
                            if imprimir_ticket(ruta_prueba, nombre_impresora):
                                messagebox.showinfo("Prueba Enviada",
                                    f"✅ Ticket de prueba enviado a '{nombre_impresora}'.\n\n"
                                    f"El archivo de prueba se eliminará automáticamente.\n\n"
                                    f"Si no imprime:\n"
                                    f"1. Verifique que la impresora esté encendida\n"
                                    f"2. Revise la cola de impresión de Windows\n"
                                    f"3. Verifique que tenga papel")
                                
                                # Eliminar el ticket de prueba después de imprimir
                                try:
                                    import time
                                    time.sleep(2)  # Esperar para que termine de enviar a imprimir
                                    if os.path.exists(ruta_prueba):
                                        os.remove(ruta_prueba)
                                        print(f"✓ Ticket de prueba eliminado: {ruta_prueba}")
                                except Exception as e:
                                    print(f"⚠ No se pudo eliminar ticket de prueba: {e}")
                            else:
                                messagebox.showerror("Error", "No se pudo enviar el ticket a la impresora")
                        else:
                            # Solo abrir el PDF
                            os.startfile(ruta_prueba)
                            messagebox.showinfo("Visualización",
                                "El ticket de prueba se abrió para visualización.\n"
                                "Recuerde eliminarlo manualmente de la carpeta tickets_generados/")
                            
                    except Exception as e:
                        messagebox.showerror("Error", f"Error en prueba de impresión:\n{str(e)}")
                else:
                    messagebox.showwarning("Advertencia", "Seleccione una impresora primero")
            
            def confirmar():
                seleccion = listbox.curselection()
                if seleccion:
                    self.impresora_seleccionada = impresoras[seleccion[0]]
                    self.guardar_impresora_seleccionada()
                    resultado[0] = True
                    dialog.destroy()
                else:
                    messagebox.showwarning("Advertencia", 
                        "Por favor seleccione una impresora de la lista")
            
            def cancelar():
                dialog.destroy()
            
            # Frame para botones (separado y visible)
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Centrar los botones
            btn_container = ttk.Frame(btn_frame)
            btn_container.pack()
            
            # Botón Generar Ticket de Prueba (Amarillo/Naranja)
            btn_prueba = tk.Button(btn_container, text="🖨️ Generar Ticket", 
                                  command=generar_ticket_prueba_fn,
                                  bg="#FF9800", fg="white", 
                                  font=("Arial", 10, "bold"),
                                  padx=15, pady=10, cursor="hand2",
                                  relief=tk.RAISED, borderwidth=2)
            btn_prueba.pack(side=tk.LEFT, padx=5)
            
            # Botón Confirmar (Verde)
            btn_confirmar = tk.Button(btn_container, text="✓ Confirmar", 
                                     command=confirmar,
                                     bg="#4CAF50", fg="white", 
                                     font=("Arial", 10, "bold"),
                                     padx=20, pady=10, cursor="hand2",
                                     relief=tk.RAISED, borderwidth=2)
            btn_confirmar.pack(side=tk.LEFT, padx=5)
            
            # Botón Cancelar (Rojo)
            btn_cancelar = tk.Button(btn_container, text="✗ Cancelar", 
                                    command=cancelar,
                                    bg="#F44336", fg="white",
                                    font=("Arial", 10, "bold"),
                                    padx=20, pady=10, cursor="hand2",
                                    relief=tk.RAISED, borderwidth=2)
            btn_cancelar.pack(side=tk.LEFT, padx=5)
            
            # Hacer que Enter confirme
            dialog.bind('<Return>', lambda e: confirmar())
            dialog.bind('<Escape>', lambda e: cancelar())
            
            # Esperar a que se cierre el diálogo
            dialog.wait_window()
            
            return resultado[0]
            
        except ImportError:
            messagebox.showerror("Error", 
                "No se puede acceder a las impresoras. Instale pywin32.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener impresoras: {str(e)}")
            return False
    
    def guardar_impresora_seleccionada(self):
        """Guarda la impresora seleccionada en un archivo JSON."""
        import json
        try:
            with open("impresora.json", "w", encoding="utf-8") as f:
                json.dump({"impresora": self.impresora_seleccionada}, f)
        except Exception as e:
            print(f"Error al guardar impresora: {e}")
    
    def cargar_impresora_guardada(self):
        """Carga la impresora guardada desde un archivo JSON."""
        import json
        try:
            if os.path.exists("impresora.json"):
                with open("impresora.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.impresora_seleccionada = data.get("impresora")
        except Exception as e:
            print(f"Error al cargar impresora: {e}")
            self.impresora_seleccionada = None
    
    def cargar_configuracion_inventario(self):
        """Carga la configuración de inventario desde el archivo de configuración."""
        import json
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    inventario_habilitado = config.get("inventario_habilitado", True)
                    self.inventario_habilitado.set(inventario_habilitado)
                    print(f"Configuración de inventario cargada: {'Habilitado' if inventario_habilitado else 'Deshabilitado'}")
        except Exception as e:
            print(f"Error al cargar configuración de inventario: {e}")
            self.inventario_habilitado.set(True)  # Por defecto habilitado
    
    def guardar_configuracion_inventario(self):
        """Guarda la configuración de inventario en el archivo de configuración."""
        import json
        try:
            config = {}
            # Cargar configuración existente
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            # Actualizar configuración de inventario
            config["inventario_habilitado"] = self.inventario_habilitado.get()
            
            # Guardar configuración
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            estado = "habilitado" if self.inventario_habilitado.get() else "deshabilitado"
            print(f"Configuración de inventario guardada: {estado}")
        except Exception as e:
            print(f"Error al guardar configuración de inventario: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TicketGeneratorApp(root)
    root.mainloop()