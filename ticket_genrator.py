# ticket_genrator.py
# Genera tickets en formato PDF

from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as mm_unit
from datetime import datetime
import os
from settings import EMPRESA, TICKET_CONFIG, RUTA_TICKETS
from reportlab.lib.utils import ImageReader
from PIL import ImageWin  # Necesario para imprimir imágenes con win32print

def numero_a_letras(numero):
    """Convierte un número a su representación en letras (simplificado)."""
    unidades = ['', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
    decenas = ['', '', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
    especiales = ['DIEZ', 'ONCE', 'DOCE', 'TRECE', 'CATORCE', 'QUINCE', 'DIECISÉIS', 'DIECISIETE', 'DIECIOCHO', 'DIECINUEVE']
    
    entero = int(numero)
    decimales = int(round((numero - entero) * 100))
    
    if entero == 0:
        return "CERO DÓLARES"
    
    resultado = ""
    
    if entero >= 100:
        centenas = entero // 100
        if centenas == 1:
            resultado = "CIENTO "
        elif centenas == 5:
            resultado = "QUINIENTOS "
        else:
            resultado = unidades[centenas] + "CIENTOS "
        entero = entero % 100
    
    if 10 <= entero < 20:
        resultado += especiales[entero - 10]
    else:
        if entero >= 20:
            resultado += decenas[entero // 10]
            if entero % 10 > 0:
                resultado += " Y " + unidades[entero % 10]
        else:
            resultado += unidades[entero]
    
    resultado = resultado.strip() + " DÓLARES"
    
    if decimales > 0:
        resultado += f" CON {decimales}/100"
    
    return resultado

def generar_ticket(datos: dict, ruta_salida: str = None) -> str:
    """
    Genera un ticket en PDF a partir de los datos de la factura.
    
    Args:
        datos: Diccionario con los datos de la factura
        ruta_salida: Ruta donde guardar el PDF (opcional)
        
    Returns:
        Ruta del archivo generado
    """
    # Crear directorio si no existe
    if not os.path.exists(RUTA_TICKETS):
        os.makedirs(RUTA_TICKETS)
    
    # Generar nombre de archivo si no se proporciona
    if not ruta_salida:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        numero_factura = datos.get("numero_factura", "SN").replace("/", "-")
        ruta_salida = os.path.join(RUTA_TICKETS, f"ticket_{numero_factura}_{timestamp}.pdf")
    
    # Configurar tamaño del ticket (80mm de ancho)
    ancho = TICKET_CONFIG["ancho_mm"] * mm_unit
    alto = 297 * mm_unit  # A4 height, se ajustará según contenido
    
    # Crear el PDF con pagesize
    from reportlab.lib.pagesizes import letter
    c = canvas.Canvas(ruta_salida, pagesize=(ancho, alto))
    
    # Posición inicial
    y = alto - 10 * mm_unit
    margen = TICKET_CONFIG["margen"] * mm_unit
    
    # ENCABEZADO: COMPROBANTE DE VENTA
    c.setFont("Courier-Bold", 10)
    y = dibujar_texto_centrado(c, "COMPROBANTE DE VENTA", ancho / 2, y)
    y -= 5 * mm_unit
    
    # FACTURA
    c.setFont("Courier-Bold", 11)
    y = dibujar_texto_centrado(c, "FACTURA", ancho / 2, y)
    y -= 5 * mm_unit
    
    # REF. DTE (usar número de control completo si existe)
    c.setFont("Courier", 8)
    numero_control = datos.get("numero_control", "")
    if not numero_control:
        # Si no hay número de control, construir uno con el número de factura
        numero_factura = datos.get("numero_factura", "000000000000157")
        numero_control = f"DTE-01-M001P001-{numero_factura}"
    y = dibujar_texto_centrado(c, f"REF. {numero_control}", ancho / 2, y)
    y -= 6 * mm_unit
    
    # EMISOR (centrado)
    c.setFont("Courier-Bold", 9)
    # Usar emisor de los datos si existe, sino usar el de settings
    emisor = datos.get("emisor", EMPRESA)
    emisor_nombre = emisor.get("nombre", EMPRESA.get("nombre", "NOMBRE EMISOR"))
    y = dibujar_texto_centrado(c, f"EMISOR: {emisor_nombre}", ancho / 2, y)
    y -= 4 * mm_unit
    
    emisor_nit = emisor.get("nit", emisor.get("ruc", EMPRESA.get("ruc", "00000000-0")))
    y = dibujar_texto_centrado(c, f"NIT: {emisor_nit}", ancho / 2, y)
    y -= 4 * mm_unit
    
    # Dirección del negocio (centrada, fuente más pequeña)
    c.setFont("Courier", 7)
    emisor_direccion = emisor.get("direccion", "")
    if emisor_direccion:
        # Dividir la dirección en líneas si es muy larga (máximo 40 caracteres por línea)
        palabras = emisor_direccion.split()
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
        
        # Dibujar cada línea de dirección
        for linea in lineas_direccion:
            y = dibujar_texto_centrado(c, linea, ancho / 2, y)
            y -= 3 * mm_unit
        
        y -= 2 * mm_unit
    
    # Código de Generación (si existe, centrado)
    codigo_generacion = datos.get("codigo_generacion", "")
    if codigo_generacion:
        c.setFont("Courier", 7)
        y = dibujar_texto_centrado(c, "Código de Generación:", ancho / 2, y)
        y -= 3 * mm_unit
        y = dibujar_texto_centrado(c, codigo_generacion, ancho / 2, y)
        y -= 4 * mm_unit
    
    # Sello de Recepción (si existe, centrado)
    sello_recepcion = datos.get("sello_recepcion", "")
    if sello_recepcion:
        c.setFont("Courier", 7)
        y = dibujar_texto_centrado(c, "Sello de Recepción:", ancho / 2, y)
        y -= 3 * mm_unit
        y = dibujar_texto_centrado(c, sello_recepcion, ancho / 2, y)
        y -= 4 * mm_unit
    
    # Fecha y hora de generación
    c.setFont("Courier", 8)
    fecha = datos.get("fecha", "")
    if fecha:
        c.drawString(margen, y, f"Fecha: {fecha}")
        y -= 6 * mm_unit
    else:
        y -= 2 * mm_unit
    
    # RECEPTOR
    cliente = datos.get("cliente", {})
    receptor_nombre = cliente.get("nombre", "CLIENTE")
    c.drawString(margen, y, f"RECEPTOR: {receptor_nombre}")
    y -= 6 * mm_unit
    
    # Línea separadora con guiones
    c.setFont("Courier", 9)
    linea = "-" * 34
    c.drawString(margen, y, linea)
    y -= 4 * mm_unit
    
    # Encabezado de tabla
    c.setFont("Courier-Bold", 8)
    c.drawString(margen, y, "CANT. DESCRIPCIÓN         VALOR")
    y -= 3 * mm_unit
    
    c.drawString(margen, y, linea)
    y -= 4 * mm_unit
    
    # Items
    c.setFont("Courier", 8)
    items = datos.get("items", [])
    
    for item in items:
        cantidad = item.get("cantidad", 1)
        descripcion = item.get("descripcion", "Item")[:20]  # Limitar a 20 caracteres
        total_item = item.get('total', item.get('precio_unitario', 0) * cantidad)
        
        # Formato: "1.00 Unidad consulta      10.00"
        linea_item = f"{cantidad:.2f} {descripcion:<20} {total_item:>6.2f}"
        c.drawString(margen, y, linea_item)
        y -= 3.5 * mm_unit
    
    # Línea separadora
    y -= 1 * mm_unit
    c.setFont("Courier", 9)
    c.drawString(margen, y, linea)
    y -= 6 * mm_unit
    
    # TOTAL
    total = datos.get("total", 0)
    c.setFont("Courier", 9)
    c.drawString(margen, y, "TOTAL US$...")
    
    c.setFont("Courier-Bold", 11)
    total_str = f"**{total:.2f}**"
    c.drawRightString(ancho - margen, y, total_str)
    y -= 6 * mm_unit
    
    # SON: (total en letras)
    c.setFont("Courier", 8)
    total_letras = numero_a_letras(total)
    c.drawString(margen, y, f"SON: {total_letras}.")
    y -= 6 * mm_unit
    
    # Nota legal (centrado, puede ocupar varias líneas)
    c.setFont("Courier", 7)
    nota = "(ESTE TICKET ES UNA REPRESENTACIÓN GRÁFICA"
    y = dibujar_texto_centrado(c, nota, ancho / 2, y)
    y -= 3 * mm_unit
    nota2 = "DEL DTE OFICIAL)"
    y = dibujar_texto_centrado(c, nota2, ancho / 2, y)
    y -= 6 * mm_unit
    
    # Mensaje de agradecimiento
    c.setFont("Courier-Bold", 9)
    y = dibujar_texto_centrado(c, "GRACIAS POR SU COMPRA", ancho / 2, y)
    y -= 6 * mm_unit
    
    # Línea final
    c.setFont("Courier", 9)
    c.drawString(margen, y, linea)
    y -= 6 * mm_unit
    
    # CÓDIGO QR al final (si existe)
    qr_path = datos.get("qr_path")
    
    # Información de contacto del emisor (SIEMPRE mostrar, incluso sin QR)
    emisor_gmail = emisor.get("gmail", "")
    emisor_telefono = emisor.get("telefono", "")
    
    if qr_path and os.path.exists(qr_path):
        try:
            from PIL import Image
            
            # Abrir la imagen para verificar que sea válida
            img = Image.open(qr_path)
            print(f"DEBUG QR: Modo original de la imagen: {img.mode}, Tamaño: {img.size}")
            
            # Convertir a escala de grises para mejor contraste
            if img.mode != 'L':
                img = img.convert('L')
                print(f"DEBUG QR: Convertido a escala de grises")
            
            # Aplicar umbral para asegurar que sea blanco y negro puro
            # Esto ayuda a que el QR sea más legible
            from PIL import ImageOps
            img = ImageOps.autocontrast(img, cutoff=0)
            
            # Convertir a modo 1-bit (blanco y negro puro)
            threshold = 128
            img = img.point(lambda x: 255 if x > threshold else 0, mode='1')
            print(f"DEBUG QR: Aplicado umbral blanco/negro")
            
            # Guardar la imagen procesada
            qr_path_temp = "temp_qr_processed.png"
            img.save(qr_path_temp, "PNG")
            qr_path = qr_path_temp
            
            # Tamaño del QR (35mm x 35mm para mejor visibilidad)
            qr_size = 35 * mm_unit
            # Posición centrada
            qr_x = (ancho - qr_size) / 2
            qr_y = y - qr_size
            
            # Dibujar el QR usando ImageReader para mejor compatibilidad
            img_reader = ImageReader(qr_path)
            c.drawImage(img_reader, qr_x, qr_y, width=qr_size, height=qr_size, 
                       preserveAspectRatio=True, mask='auto')
            
            y = qr_y - 3 * mm_unit
            
            # Texto debajo del QR
            c.setFont("Courier", 7)
            y = dibujar_texto_centrado(c, "Consulte su DTE", ancho / 2, y)
            y -= 4 * mm_unit
            
            print(f"✓ Código QR agregado al ticket correctamente")
        except Exception as e:
            print(f"⚠ Error al agregar QR al ticket: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⚠ No se encontró QR code para agregar al ticket")
        # Dejar espacio para info de contacto aunque no haya QR
        y -= 5 * mm_unit
    
    # Mostrar información de contacto SIEMPRE (con o sin QR)
    c.setFont("Courier", 7)
    if emisor_gmail:
        y = dibujar_texto_centrado(c, f"Gmail: {emisor_gmail}", ancho / 2, y)
        y -= 3 * mm_unit
    
    if emisor_telefono:
        y = dibujar_texto_centrado(c, f"Telefono: {emisor_telefono}", ancho / 2, y)
        y -= 3 * mm_unit
    
    # Guardar el PDF
    c.save()
    
    return ruta_salida

def dibujar_texto_centrado(c, texto, x, y):
    """
    Dibuja texto centrado en la posición x.
    """
    ancho_texto = c.stringWidth(texto)
    c.drawString(x - ancho_texto / 2, y, texto)
    return y

def imprimir_ticket(ruta_pdf: str, impresora: str = None):
    """
    Envía el ticket a una impresora térmica.
    Convierte el PDF a imagen PNG para mejor compatibilidad con impresoras térmicas.
    
    Args:
        ruta_pdf: Ruta del PDF a imprimir
        impresora: Nombre de la impresora (opcional, usa la predeterminada si no se especifica)
    """
    import subprocess
    import platform
    
    sistema = platform.system()
    
    try:
        if sistema == "Windows":
            # MÉTODO MEJORADO: Convertir PDF a PNG y luego imprimir
            # Esto funciona MUCHO mejor con impresoras térmicas
            try:
                import fitz  # PyMuPDF
                from PIL import Image
                import win32print
                import win32ui
                from win32.lib import win32con
                
                print("Convirtiendo PDF a imagen para impresión térmica...")
                
                # Si no se especifica impresora, usar la predeterminada
                if not impresora:
                    impresora = win32print.GetDefaultPrinter()
                
                print(f"Imprimiendo en: {impresora}")
                
                # 1. Convertir PDF a imagen PNG de alta calidad
                pdf_document = fitz.open(ruta_pdf)
                page = pdf_document[0]  # Primera página
                
                # Renderizar a 300 DPI para buena calidad en térmica
                mat = fitz.Matrix(300/72, 300/72)  # 300 DPI
                pix = pdf_document[0].get_pixmap(matrix=mat, alpha=False)
                
                # Guardar como PNG temporal
                import tempfile
                temp_png = os.path.join(tempfile.gettempdir(), "ticket_temp_print.png")
                pix.save(temp_png)
                pdf_document.close()
                
                print(f"✓ PDF convertido a imagen: {temp_png}")
                
                # 2. Abrir la imagen con PIL y ajustar para impresora térmica
                img = Image.open(temp_png)
                
                # Convertir a escala de grises si no lo está
                if img.mode != 'L':
                    img = img.convert('L')
                
                # Ajustar ancho para impresora térmica de 80mm
                # 80mm a 203 DPI (resolución común de térmicas) = ~640 píxeles
                ancho_termica = 576  # Ancho seguro para 80mm
                
                # Calcular altura proporcional
                ratio = ancho_termica / img.width
                altura_nueva = int(img.height * ratio)
                
                # Redimensionar imagen
                img_redimensionada = img.resize((ancho_termica, altura_nueva), Image.Resampling.LANCZOS)
                
                # Aplicar umbral para blanco y negro puro (mejor para térmicas)
                # Esto mejora la calidad de impresión
                img_bw = img_redimensionada.point(lambda x: 0 if x < 128 else 255, '1')
                
                # Guardar imagen procesada
                temp_png_procesado = os.path.join(tempfile.gettempdir(), "ticket_print_processed.bmp")
                img_bw.save(temp_png_procesado, "BMP")
                
                print(f"✓ Imagen procesada para térmica: {ancho_termica}x{altura_nueva}px")
                
                # 3. Imprimir la imagen directamente usando win32print
                try:
                    # Obtener el handle de la impresora
                    hPrinter = win32print.OpenPrinter(impresora)
                    
                    try:
                        # Crear un contexto de dispositivo para la impresora
                        hDC = win32ui.CreateDC()
                        hDC.CreatePrinterDC(impresora)
                        
                        # Iniciar documento
                        hDC.StartDoc("Ticket Factura")
                        hDC.StartPage()
                        
                        # Abrir la imagen BMP
                        bmp = Image.open(temp_png_procesado)
                        
                        # Obtener dimensiones de la impresora
                        printer_width = hDC.GetDeviceCaps(win32con.HORZRES)
                        printer_height = hDC.GetDeviceCaps(win32con.VERTRES)
                        
                        # Calcular escala para que la imagen ocupe el ancho completo
                        scale = printer_width / bmp.width
                        img_height = int(bmp.height * scale)
                        
                        # Asegurarse de que la altura no exceda la página
                        if img_height > printer_height:
                            scale = printer_height / bmp.height
                            img_height = printer_height
                            img_width = int(bmp.width * scale)
                        else:
                            img_width = printer_width
                        
                        # Dibujar la imagen
                        dib = ImageWin.Dib(bmp)
                        dib.draw(hDC.GetHandleOutput(), (0, 0, img_width, img_height))
                        
                        # Finalizar página y documento
                        hDC.EndPage()
                        hDC.EndDoc()
                        
                        print("✓ Imagen enviada a la impresora correctamente")
                        
                    finally:
                        win32print.ClosePrinter(hPrinter)
                        hDC.DeleteDC()
                    
                    # Limpiar archivos temporales
                    try:
                        os.remove(temp_png)
                        os.remove(temp_png_procesado)
                    except:
                        pass
                    
                    return True
                    
                except Exception as e:
                    print(f"⚠ Error con impresión directa de imagen: {e}")
                    # Continuar con métodos alternativos
                
            except ImportError as e:
                print(f"⚠ Dependencias no disponibles para conversión PDF→PNG: {e}")
            except Exception as e:
                print(f"⚠ Error al convertir PDF a imagen: {e}")
                import traceback
                traceback.print_exc()
            
            # FALLBACK: Métodos anteriores si la conversión a imagen falla
            try:
                import win32print
                import win32api
                
                if not impresora:
                    impresora = win32print.GetDefaultPrinter()
                
                print(f"Usando método alternativo de impresión para: {impresora}")
                
                # Intentar con SumatraPDF si está disponible
                try:
                    import os
                    sumatra_paths = [
                        os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'SumatraPDF', 'SumatraPDF.exe'),
                        os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'SumatraPDF', 'SumatraPDF.exe'),
                        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'SumatraPDF', 'SumatraPDF.exe')
                    ]
                    
                    sumatra_exe = None
                    for path in sumatra_paths:
                        if os.path.exists(path):
                            sumatra_exe = path
                            break
                    
                    if sumatra_exe:
                        print(f"Usando SumatraPDF para imprimir")
                        subprocess.Popen([
                            sumatra_exe,
                            '-print-to', impresora,
                            '-silent',
                            ruta_pdf
                        ])
                        print("✓ Ticket enviado a la impresora usando SumatraPDF")
                        return True
                except Exception as e:
                    print(f"⚠ SumatraPDF no disponible: {e}")
                
                # Método estándar de Windows
                print("Usando método estándar de Windows (ShellExecute)...")
                win32api.ShellExecute(
                    0,
                    "print",
                    ruta_pdf,
                    f'/d:"{impresora}"',
                    ".",
                    0
                )
                print("✓ Ticket enviado a la impresora usando ShellExecute")
                print("⚠ Si no imprime correctamente, instala SumatraPDF para mejor compatibilidad")
                return True
                
            except ImportError:
                print("⚠ win32print no disponible, usando método básico...")
                if impresora:
                    subprocess.run(["print", f"/D:{impresora}", ruta_pdf], shell=True, check=True)
                else:
                    os.startfile(ruta_pdf, "print")
                print("✓ Ticket enviado usando método básico")
                return True
                
        elif sistema == "Linux":
            if impresora:
                subprocess.run(["lp", "-d", impresora, ruta_pdf], check=True)
            else:
                subprocess.run(["lp", ruta_pdf], check=True)
            return True
            
        elif sistema == "Darwin":  # macOS
            if impresora:
                subprocess.run(["lpr", "-P", impresora, ruta_pdf], check=True)
            else:
                subprocess.run(["lpr", ruta_pdf], check=True)
            return True
        
        return True
    except Exception as e:
        print(f"Error al imprimir: {e}")
        import traceback
        traceback.print_exc()
        return False


def obtener_impresoras_disponibles():
    """
    Obtiene la lista de impresoras disponibles en el sistema.
    
    Returns:
        Lista de nombres de impresoras disponibles
    """
    import platform
    
    sistema = platform.system()
    impresoras = []
    
    try:
        if sistema == "Windows":
            import win32print
            # Obtener todas las impresoras instaladas
            impresoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        elif sistema == "Linux":
            import subprocess
            result = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            impresoras = [line.split()[1] for line in lines if line.startswith('printer')]
        elif sistema == "Darwin":  # macOS
            import subprocess
            result = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            impresoras = [line.split()[1] for line in lines if line.startswith('printer')]
    except Exception as e:
        print(f"Error al obtener impresoras: {e}")
    
    return impresoras


def obtener_impresora_predeterminada():
    """
    Obtiene el nombre de la impresora predeterminada del sistema.
    
    Returns:
        Nombre de la impresora predeterminada o None
    """
    import platform
    
    sistema = platform.system()
    
    try:
        if sistema == "Windows":
            import win32print
            return win32print.GetDefaultPrinter()
        elif sistema in ["Linux", "Darwin"]:
            import subprocess
            result = subprocess.run(["lpstat", "-d"], capture_output=True, text=True)
            if result.returncode == 0:
                # La salida es algo como "system default destination: nombre_impresora"
                return result.stdout.split(':')[1].strip()
    except Exception as e:
        print(f"Error al obtener impresora predeterminada: {e}")
    
    return None


def generar_ticket_prueba(impresora_nombre: str = None) -> str:
    """
    Genera un ticket de prueba simple para verificar la impresión.
    
    Args:
        impresora_nombre: Nombre de la impresora para incluir en el ticket
        
    Returns:
        Ruta del archivo de prueba generado
    """
    from datetime import datetime
    
    # Crear directorio si no existe
    if not os.path.exists(RUTA_TICKETS):
        os.makedirs(RUTA_TICKETS)
    
    # Generar nombre de archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_salida = os.path.join(RUTA_TICKETS, f"ticket_prueba_{timestamp}.pdf")
    
    # Configurar tamaño del ticket (80mm de ancho)
    ancho = TICKET_CONFIG["ancho_mm"] * mm_unit
    alto = 150 * mm_unit  # Ticket corto de prueba
    
    # Crear el PDF
    c = canvas.Canvas(ruta_salida, pagesize=(ancho, alto))
    
    # Posición inicial
    y = alto - 10 * mm_unit
    margen = TICKET_CONFIG["margen"] * mm_unit
    
    # TÍTULO
    c.setFont("Courier-Bold", 12)
    y = dibujar_texto_centrado(c, "TICKET DE PRUEBA", ancho / 2, y)
    y -= 8 * mm_unit
    
    # Línea separadora
    c.setFont("Courier", 9)
    linea = "-" * 34
    c.drawString(margen, y, linea)
    y -= 6 * mm_unit
    
    # Información de prueba
    c.setFont("Courier", 9)
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.drawString(margen, y, f"Fecha: {fecha_hora}")
    y -= 5 * mm_unit
    
    if impresora_nombre:
        c.setFont("Courier", 8)
        # Dividir nombre de impresora en líneas si es muy largo
        if len(impresora_nombre) > 30:
            c.drawString(margen, y, "Impresora:")
            y -= 4 * mm_unit
            c.drawString(margen, y, impresora_nombre[:30])
            y -= 4 * mm_unit
            if len(impresora_nombre) > 30:
                c.drawString(margen, y, impresora_nombre[30:60])
                y -= 5 * mm_unit
        else:
            c.drawString(margen, y, f"Impresora: {impresora_nombre}")
            y -= 5 * mm_unit
    
    # Línea separadora
    c.setFont("Courier", 9)
    c.drawString(margen, y, linea)
    y -= 6 * mm_unit
    
    # Mensaje de prueba
    c.setFont("Courier-Bold", 10)
    y = dibujar_texto_centrado(c, "IMPRESION EXITOSA", ancho / 2, y)
    y -= 6 * mm_unit
    
    c.setFont("Courier", 8)
    y = dibujar_texto_centrado(c, "Si puede leer este texto,", ancho / 2, y)
    y -= 4 * mm_unit
    y = dibujar_texto_centrado(c, "su impresora funciona", ancho / 2, y)
    y -= 4 * mm_unit
    y = dibujar_texto_centrado(c, "correctamente.", ancho / 2, y)
    y -= 6 * mm_unit
    
    # Línea final
    c.setFont("Courier", 9)
    c.drawString(margen, y, linea)
    y -= 6 * mm_unit
    
    # Texto de verificación de formato
    c.setFont("Courier", 8)
    y = dibujar_texto_centrado(c, "Formato: 80mm", ancho / 2, y)
    y -= 4 * mm_unit
    y = dibujar_texto_centrado(c, "Generador de Tickets", ancho / 2, y)
    
    # Guardar el PDF
    c.save()
    
    print(f"✓ Ticket de prueba generado: {ruta_salida}")
    return ruta_salida


def verificar_impresora_termica(nombre_impresora: str) -> dict:
    """
    Verifica si una impresora es térmica y obtiene información sobre ella.
    
    Args:
        nombre_impresora: Nombre de la impresora a verificar
        
    Returns:
        Diccionario con información de la impresora
    """
    info = {
        "nombre": nombre_impresora,
        "existe": False,
        "es_termica": False,
        "ancho_papel": "Desconocido",
        "estado": "Desconocido"
    }
    
    try:
        import win32print
        
        # Verificar si la impresora existe
        impresoras = [printer[2] for printer in win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        
        if nombre_impresora in impresoras:
            info["existe"] = True
            
            # Obtener handle de la impresora
            hPrinter = win32print.OpenPrinter(nombre_impresora)
            
            try:
                # Obtener información de la impresora
                printer_info = win32print.GetPrinter(hPrinter, 2)
                info["estado"] = "Disponible"
                
                # Detectar si es térmica por el nombre (heurística común)
                nombre_lower = nombre_impresora.lower()
                palabras_termicas = ["thermal", "pos", "receipt", "ticket", "star", "epson tm", "bixolon"]
                info["es_termica"] = any(palabra in nombre_lower for palabra in palabras_termicas)
                
            finally:
                win32print.ClosePrinter(hPrinter)
        
    except Exception as e:
        print(f"Error al verificar impresora: {e}")
        info["estado"] = f"Error: {str(e)}"
    
    return info

