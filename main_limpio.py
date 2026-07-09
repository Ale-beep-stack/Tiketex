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
            
            # Procesar inventario si está habilitado
            self.inventario_manager.procesar_inventario_factura(self.datos_factura)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la factura: {str(e)}")
    
    def abrir_inventario(self):
        """Cambia a la pantalla de inventario."""
        self.mostrar_pantalla_inventario()
    
    # ... resto de funciones del main.py original (sin las de inventario)
    
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


if __name__ == "__main__":
    root = tk.Tk()
    app = TicketGeneratorApp(root)
    root.mainloop()