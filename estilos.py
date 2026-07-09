# estilos.py
# Configuración de estilos y diseño de la interfaz

from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys

# Colores del tema
COLOR_FONDO = "#595959"
COLOR_PANEL = "#595959"
COLOR_TEXTO = "#000000"  # Negro para labels (Fecha, DUI, Cliente, etc.)
COLOR_TEXTO_RESULTADO = "#ffffff"  # Blanco para los valores extraídos
COLOR_TEXTO_BOTON = "#000000"  # Negro para texto de botones
COLOR_BOTON = "#000000"
COLOR_BOTON_HOVER = "#5cb885"
COLOR_BOTON_DISABLED = "#666666"

def obtener_ruta_recurso(ruta_relativa):
    """
    Obtiene la ruta absoluta del recurso, funciona tanto en desarrollo como en .exe
    """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        ruta_base = sys._MEIPASS
    except Exception:
        # Si no es un .exe, usa la ruta normal
        ruta_base = os.path.abspath(".")
    
    return os.path.join(ruta_base, ruta_relativa)

# Ruta de la imagen del botón
RUTA_IMAGEN_BOTON = obtener_ruta_recurso(os.path.join("disenos", "button-859346_1280.png"))

def cargar_imagen_boton(ancho=200, alto=40):
    """Carga y redimensiona la imagen del botón."""
    try:
        print(f"DEBUG: Intentando cargar imagen desde: {RUTA_IMAGEN_BOTON}")
        print(f"DEBUG: Archivo existe: {os.path.exists(RUTA_IMAGEN_BOTON)}")
        
        imagen = Image.open(RUTA_IMAGEN_BOTON)
        imagen = imagen.resize((ancho, alto), Image.Resampling.LANCZOS)
        print(f"DEBUG: Imagen cargada exitosamente")
        return ImageTk.PhotoImage(imagen)
    except Exception as e:
        print(f"ERROR al cargar imagen del botón: {e}")
        print(f"DEBUG: Ruta intentada: {RUTA_IMAGEN_BOTON}")
        return None

def crear_boton_personalizado(parent, texto, comando, ancho=200, alto=40, estado="normal"):
    """
    Crea un botón personalizado con la imagen de fondo.
    Si la imagen no se carga, usa un color de fondo celeste visible.
    
    Args:
        parent: Widget padre
        texto: Texto del botón
        comando: Función a ejecutar al hacer clic
        ancho: Ancho del botón en píxeles
        alto: Alto del botón en píxeles
        estado: Estado del botón ("normal" o "disabled")
    
    Returns:
        Botón tk.Button con imagen de fondo o color celeste
    """
    import tkinter as tk
    
    # Cargar imagen
    imagen = cargar_imagen_boton(ancho, alto)
    
    # Si NO se cargó la imagen, usar color de fondo visible
    if not imagen:
        print("⚠ Usando botón con color de fondo (sin imagen)")
        # Usar color celeste visible como fallback
        bg_color = "#5DADE2"  # Azul celeste
        fg_color = "#000000"  # Texto negro
        hover_color = "#3498DB"  # Azul más oscuro al pasar el mouse
    else:
        # Si hay imagen, usar el color del panel como fondo
        bg_color = COLOR_PANEL
        fg_color = COLOR_TEXTO_BOTON
        hover_color = COLOR_BOTON_HOVER
    
    # Crear botón con fuente Arial Black y texto negro
    boton = tk.Button(
        parent,
        text=texto,
        command=comando,
        font=("Arial Black", 10, "bold"),  # Fuente Arial Black para botones
        fg=fg_color,  # Texto negro para botones
        bg=bg_color,
        activebackground=hover_color,
        activeforeground="#000000",  # Texto negro también al hacer hover
        relief="raised" if not imagen else "flat",  # Relieve visible si no hay imagen
        borderwidth=2 if not imagen else 0,
        cursor="hand2",
        state=estado,
        compound="center",  # Texto sobre la imagen
        padx=10,
        pady=5
    )
    
    # Si se cargó la imagen, usarla como fondo
    if imagen:
        boton.config(image=imagen)
        boton.image = imagen  # Mantener referencia para evitar que se borre
    
    return boton

def configurar_estilos():
    """Configura los estilos personalizados para todos los widgets de la aplicación."""
    style = ttk.Style()
    
    # Estilo para frames - SIN BORDES
    style.configure("Custom.TFrame", background=COLOR_FONDO, relief="flat", borderwidth=0)
    style.configure("Panel.TFrame", background=COLOR_PANEL, relief="flat", borderwidth=0)
    
    # Estilo para labels - Fuente Rockwell
    style.configure("Custom.TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO,
                   font=("Rockwell", 10))
    style.configure("Title.TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO, 
                   font=("Rockwell", 18, "bold"))
    style.configure("Panel.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXTO,
                   font=("Rockwell", 10))
    style.configure("PanelBold.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXTO,
                   font=("Rockwell", 10, "bold"))
    style.configure("PanelResult.TLabel", background=COLOR_PANEL, foreground=COLOR_TEXTO_RESULTADO,
                   font=("Rockwell", 9))
    
    # Estilo para LabelFrame - CON BORDES para encuadrar secciones
    style.configure("Custom.TLabelframe", background=COLOR_PANEL, foreground=COLOR_TEXTO,
                   relief="groove", borderwidth=2)
    style.configure("Custom.TLabelframe.Label", background=COLOR_PANEL, foreground=COLOR_TEXTO,
                   font=("Rockwell", 11, "bold"))
    
    # Estilo para botones ttk (si se usan) - Fuente Arial Black
    style.configure("Custom.TButton", 
                   background=COLOR_BOTON,
                   foreground=COLOR_TEXTO,
                   borderwidth=0,
                   relief="flat",
                   font=("Arial Black", 10, "bold"),
                   padding=6)
    style.map("Custom.TButton",
             background=[("active", COLOR_BOTON_HOVER), ("disabled", COLOR_BOTON_DISABLED)],
             foreground=[("disabled", "#999999")])
    
    # Estilo para Combobox - Fuente Rockwell
    style.configure("Custom.TCombobox", 
                   fieldbackground="white", 
                   background=COLOR_PANEL,
                   foreground="#000000",
                   font=("Rockwell", 10),
                   borderwidth=0)
    
    # Estilo para Treeview (tabla) - Fuente Rockwell
    style.configure("Custom.Treeview",
                   background="white",
                   foreground="black",
                   fieldbackground="white",
                   rowheight=25,
                   font=("Rockwell", 9),
                   borderwidth=0)
    style.configure("Custom.Treeview.Heading",
                   background=COLOR_PANEL,
                   foreground=COLOR_TEXTO,
                   font=("Rockwell", 10, "bold"),
                   borderwidth=0)
    style.map("Custom.Treeview",
             background=[("selected", COLOR_BOTON)])
    
    # Estilo para Scrollbar
    style.configure("Custom.Vertical.TScrollbar",
                   background=COLOR_PANEL,
                   troughcolor=COLOR_FONDO,
                   bordercolor=COLOR_PANEL,
                   arrowcolor=COLOR_TEXTO)
    
    # Estilo para Checkbutton
    style.configure("Custom.TCheckbutton",
                   background=COLOR_PANEL,
                   foreground=COLOR_TEXTO,
                   font=("Rockwell", 10),
                   borderwidth=0)
    
    # Estilo para Separator - mismo color que el fondo
    style.configure("TSeparator", background=COLOR_PANEL)
    
    return style

def obtener_colores():
    """Retorna un diccionario con los colores del tema."""
    return {
        "fondo": COLOR_FONDO,
        "panel": COLOR_PANEL,
        "texto": COLOR_TEXTO,
        "boton": COLOR_BOTON,
        "boton_hover": COLOR_BOTON_HOVER,
        "boton_disabled": COLOR_BOTON_DISABLED
    }
