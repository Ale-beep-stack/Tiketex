"""
Genera un ticket PDF directamente desde texto plano.
Útil para cuando el usuario edita manualmente la vista previa.
"""
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as mm_unit
from datetime import datetime
import os
from settings import TICKET_CONFIG, RUTA_TICKETS
from reportlab.lib.utils import ImageReader


def generar_ticket_desde_texto(texto: str, ruta_qr: str = None, numero_factura: str = "EDITADO") -> str:
    """
    Genera un ticket PDF directamente desde texto plano.
    
    Args:
        texto: Texto del ticket (tal como aparece en la vista previa)
        ruta_qr: Ruta al código QR (opcional)
        numero_factura: Número de factura para el nombre del archivo
        
    Returns:
        Ruta del archivo PDF generado
    """
    # Crear directorio si no existe
    if not os.path.exists(RUTA_TICKETS):
        os.makedirs(RUTA_TICKETS)
    
    # Generar nombre de archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    numero_factura_limpio = numero_factura.replace("/", "-").replace("\\", "-")
    ruta_salida = os.path.join(RUTA_TICKETS, f"ticket_{numero_factura_limpio}_{timestamp}.pdf")
    
    # Configurar tamaño del ticket (80mm de ancho)
    ancho = TICKET_CONFIG["ancho_mm"] * mm_unit
    alto = 297 * mm_unit  # A4 height
    
    # Crear el PDF
    c = canvas.Canvas(ruta_salida, pagesize=(ancho, alto))
    
    # Posición inicial
    y = alto - 10 * mm_unit
    margen = TICKET_CONFIG["margen"] * mm_unit
    
    # Dividir el texto en líneas
    lineas = texto.split('\n')
    
    # Dibujar cada línea manteniendo el formato original
    for linea in lineas:
        # Saltar líneas vacías pero mantener el espaciado
        if not linea.strip():
            y -= 3 * mm_unit
            continue
        
        # Detectar el formato basado en el contenido y posición
        linea_limpia = linea.strip()
        
        # Determinar fuente y tamaño
        if any(palabra in linea_limpia.upper() for palabra in ['COMPROBANTE DE VENTA', 'FACTURA']):
            fuente = "Courier-Bold"
            tamano = 11 if 'FACTURA' in linea_limpia and len(linea_limpia) < 15 else 10
            centrar = True
        elif linea_limpia.startswith('REF.') or 'Código de Generación' in linea_limpia:
            fuente = "Courier"
            tamano = 8
            centrar = True
        elif linea_limpia.startswith('EMISOR:') or linea_limpia.startswith('NIT:') or linea_limpia.startswith('NRC:'):
            fuente = "Courier-Bold"
            tamano = 9
            centrar = True
        elif linea_limpia.startswith('RECEPTOR:') or linea_limpia.startswith('DUI:') or linea_limpia.startswith('Nombre:'):
            fuente = "Courier-Bold"
            tamano = 9
            centrar = False
        elif 'TOTAL A PAGAR' in linea_limpia.upper() or 'VALOR EN LETRAS' in linea_limpia.upper():
            fuente = "Courier-Bold"
            tamano = 9
            centrar = False
        elif linea_limpia.startswith('$') or (linea_limpia.startswith('Total:') or linea_limpia.startswith('Subtotal:')):
            fuente = "Courier-Bold"
            tamano = 9
            centrar = False
        elif 'GRACIAS' in linea_limpia.upper():
            fuente = "Courier-Bold"
            tamano = 9
            centrar = True
        elif linea_limpia.startswith('-') or linea_limpia.startswith('='):
            # Líneas separadoras
            fuente = "Courier"
            tamano = 8
            centrar = False
        else:
            # Texto normal
            fuente = "Courier"
            tamano = 8
            # Detectar si está centrado por espacios al inicio
            espacios_inicio = len(linea) - len(linea.lstrip())
            centrar = espacios_inicio > 5
        
        c.setFont(fuente, tamano)
        
        # Calcular posición X
        if centrar:
            text_width = c.stringWidth(linea_limpia, fuente, tamano)
            x = (ancho - text_width) / 2
        else:
            x = margen
        
        # Dibujar la línea
        c.drawString(x, y, linea_limpia)
        
        # Ajustar espaciado según el tipo de línea
        if any(palabra in linea_limpia.upper() for palabra in ['COMPROBANTE', 'FACTURA', 'REF.']):
            y -= 5 * mm_unit
        elif linea_limpia.startswith('-') or linea_limpia.startswith('='):
            y -= 3 * mm_unit
        else:
            y -= 4 * mm_unit
        
        # Si llegamos al final de la página, crear nueva página
        if y < 20 * mm_unit:
            c.showPage()
            y = alto - 10 * mm_unit
    
    # Agregar código QR si existe
    if ruta_qr and os.path.exists(ruta_qr):
        try:
            # Asegurar que hay espacio para el QR
            if y < 60 * mm_unit:
                c.showPage()
                y = alto - 10 * mm_unit
            
            y -= 10 * mm_unit
            
            # Centrar el QR
            qr_size = 50 * mm_unit
            x_qr = (ancho - qr_size) / 2
            
            # Dibujar el QR
            img = ImageReader(ruta_qr)
            c.drawImage(img, x_qr, y - qr_size, width=qr_size, height=qr_size, preserveAspectRatio=True, mask='auto')
            
            print(f"✓ Código QR agregado al ticket desde texto")
        except Exception as e:
            print(f"⚠ Error al agregar QR al ticket desde texto: {e}")
    
    # Finalizar el PDF
    c.save()
    
    print(f"✓ Ticket generado desde texto: {ruta_salida}")
    return ruta_salida
