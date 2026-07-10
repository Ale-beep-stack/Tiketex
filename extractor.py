# extractor.py
# Extrae datos de facturas en PDF

import PyPDF2
import re
from typing import Dict, List, Optional
import numpy as np

def leer_pdf(path: str) -> Dict:
    """
    Lee un PDF de factura y extrae los datos clave.
    
    Args:
        path: Ruta al archivo PDF
        
    Returns:
        Diccionario con los datos extraídos de la factura
    """
    try:
        import fitz  # PyMuPDF
        
        # Intentar primero con PyMuPDF (mejor para tablas)
        try:
            pdf_document = fitz.open(path)
            texto_completo = ""
            
            # Extraer texto de todas las páginas
            for page in pdf_document:
                texto_completo += page.get_text()
            
            pdf_document.close()
            print("✓ Texto extraído con PyMuPDF (fitz)")
            
        except Exception as e:
            print(f"⚠ PyMuPDF falló, usando PyPDF2: {e}")
            # Fallback a PyPDF2
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                texto_completo = ""
                
                # Extraer texto de todas las páginas
                for page in pdf_reader.pages:
                    texto_completo += page.extract_text()
            print("✓ Texto extraído con PyPDF2")
        
        # Extraer datos usando expresiones regulares
        datos = extraer_datos_factura(texto_completo)
        return datos
            
    except Exception as e:
        return {
            "error": f"Error al leer el PDF: {str(e)}",
            "exito": False
        }

def extraer_datos_factura(texto: str) -> Dict:
    """
    Extrae información específica del texto de la factura.
    """
    # Debug: Imprimir una muestra del texto extraído
    print("=== TEXTO EXTRAÍDO DEL PDF (primeros 1000 caracteres) ===")
    print(texto[:1000])
    print("=== FIN MUESTRA ===\n")
    
    datos = {
        "exito": True,
        "numero_factura": "",
        "numero_control": "",  # Número de control DTE completo
        "codigo_generacion": "",  # Código de Generación
        "sello_recepcion": "",  # Sello de Recepción
        "fecha": "",
        "cliente": {
            "nombre": "",
            "ruc_dni": "",
            "direccion": ""
        },
        "items": [],
        "subtotal": 0.0,
        "otros_montos": 0.0,
        "igv": 0.0,
        "total": 0.0
    }
    
    # Extraer número de control DTE (formato: DTE-01-M001P001-000000000000129)
    match_dte = re.search(r'(DTE-\d{2}-[A-Z0-9]+-\d+)', texto)
    if match_dte:
        datos["numero_control"] = match_dte.group(1)
        # Extraer solo el número final como número de factura
        partes = match_dte.group(1).split('-')
        if len(partes) >= 4:
            datos["numero_factura"] = partes[-1]
    
    # Extraer Código de Generación (formato: 346F6909-42FF-4255-A0C7-D184492BA29B)
    # El código aparece ANTES de "Código de Generación:" en el texto
    # Buscar cualquier UUID en el texto
    match_codigo_gen = re.search(r'([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})', texto, re.IGNORECASE)
    if match_codigo_gen:
        datos["codigo_generacion"] = match_codigo_gen.group(1)
        print(f"DEBUG: Código de Generación encontrado: {datos['codigo_generacion']}")
    
    # Extraer Sello de Recepción (formato: 2025A6FEC43660F84BB093C7376BC8EF5FF3ABXF)
    print(f"DEBUG: Buscando sello de recepción en el texto... [VERSIÓN MEJORADA 2026-07-10]")
    
    # Buscar la parte específica del texto que contiene el sello para debug
    sello_parte = re.search(r'Sello\s+de\s+Recepción\s*:.*?(?:Modelo|MODELO|EMISOR)', texto, re.IGNORECASE | re.DOTALL)
    if sello_parte:
        print(f"DEBUG: Parte del sello encontrada: '{sello_parte.group(0)[:150]}...'")
    else:
        print("DEBUG: No se encontró la sección 'Sello de Recepción'")
    
    # Patrón 1: Buscar directamente después de "Sello de Recepción:" con el DTE pegado
    # Formato extraído: "Sello de Recepción:DTE-01-M001P001-0000000000001532025478AA53AEFD74A3EA9E0820E4B418618TFYB"
    # Capturamos el hash después del número de DTE
    patron1 = r'Sello\s+de\s+Recepción\s*:\s*DTE-\d{2}-[A-Z0-9]+-(\d{12,15})([A-Z0-9]{35,50}?)(?=Modelo|MODELO|EMISOR|Tipo|TIPO)'
    match_sello = re.search(patron1, texto, re.IGNORECASE)
    if match_sello:
        # El sello es el segundo grupo (el hash después del número)
        datos["sello_recepcion"] = match_sello.group(2)
        print(f"DEBUG: Sello de Recepción encontrado (patrón 1): {datos['sello_recepcion']}")
    else:
        print(f"DEBUG: Patrón 1 no encontró sello, intentando patrón 2...")
        
        # Patrón 2: Buscar después de "Sello de Recepción:" sin el DTE pegado
        # Formato en PDF: "Sello de Recepción: 202577BF84C583F1410E90628990A08EB89D2MQ4"
        patron2 = r'Sello\s+de\s+Recepción\s*:\s*([A-Z0-9]{35,50}?)(?=\s*(?:Modelo|MODELO|EMISOR|Tipo|TIPO))'
        match_sello2 = re.search(patron2, texto, re.IGNORECASE)
        if match_sello2:
            datos["sello_recepcion"] = match_sello2.group(1)
            print(f"DEBUG: Sello de Recepción encontrado (patrón 2): {datos['sello_recepcion']}")
        else:
            print(f"DEBUG: Patrón 2 no encontró sello, intentando patrón 3...")
            
            # Patrón 3: Buscar cualquier cadena larga después del número de DTE 
            # Formato: DTE-01-M001P001-0000000000001352025A6FEC43660F84BB093C7376BC8EF5FF3ABXFModelo
            patron3 = r'DTE-\d{2}-[A-Z0-9]+-\d{12,15}([A-Z0-9]{35,50}?)(?=Modelo|MODELO|EMISOR|Tipo|TIPO)'
            match_sello3 = re.search(patron3, texto, re.IGNORECASE)
            if match_sello3:
                datos["sello_recepcion"] = match_sello3.group(1)
                print(f"DEBUG: Sello de Recepción encontrado (patrón 3): {datos['sello_recepcion']}")
            else:
                print(f"DEBUG: Patrón 3 no encontró sello, intentando patrón 4...")
                
                # Patrón 4: Buscar hash largo antes de la palabra "Modelo"
                # Esto captura cualquier hash que esté justo antes de "Modelo"
                patron4 = r'([A-Z0-9]{35,50})\s*(?:Modelo|MODELO)'
                match_sello4 = re.search(patron4, texto, re.IGNORECASE)
                if match_sello4:
                    candidato = match_sello4.group(1)
                    # Verificar que no sea el número de DTE (no debe contener guiones)
                    if '-' not in candidato:
                        datos["sello_recepcion"] = candidato
                        print(f"DEBUG: Sello de Recepción encontrado (patrón 4): {datos['sello_recepcion']}")
                    else:
                        print(f"DEBUG: Patrón 4 descartó candidato con guiones: {candidato}")
                else:
                    print(f"DEBUG: No se pudo encontrar el sello de recepción con ningún patrón")
    
    # Si no se encuentra DTE, buscar número de factura tradicional
    if not datos["numero_factura"]:
        match_factura = re.search(r'(?:FACTURA|Factura|N°|Nº)\s*:?\s*([A-Z0-9\-]+)', texto)
        if match_factura:
            datos["numero_factura"] = match_factura.group(1)
            datos["numero_control"] = match_factura.group(1)
    
    # Extraer fecha y hora (formato: 2025-12-03 14:20:54)
    # Intentar varios patrones de fecha
    
    # Patrón 1: Fecha y Hora de Generación: 2025-12-03 14:20:54
    match_fecha_hora = re.search(r'Fecha\s+y\s+Hora\s+de\s+Generación\s*:?\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', texto, re.IGNORECASE)
    if match_fecha_hora:
        datos["fecha"] = match_fecha_hora.group(1)
        print(f"DEBUG: Fecha encontrada (patrón 1): {datos['fecha']}")
    
    # Patrón 2: Buscar cualquier fecha en formato YYYY-MM-DD HH:MM:SS
    if not datos["fecha"]:
        match_fecha_hora2 = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', texto)
        if match_fecha_hora2:
            datos["fecha"] = match_fecha_hora2.group(1)
            print(f"DEBUG: Fecha encontrada (patrón 2): {datos['fecha']}")
    
    # Patrón 3: Solo fecha YYYY-MM-DD
    if not datos["fecha"]:
        match_fecha = re.search(r'(\d{4}-\d{2}-\d{2})', texto)
        if match_fecha:
            datos["fecha"] = match_fecha.group(1)
            print(f"DEBUG: Fecha encontrada (patrón 3): {datos['fecha']}")
    
    # Patrón 4: Fecha en formato DD/MM/YYYY o DD-MM-YYYY
    if not datos["fecha"]:
        match_fecha_alt = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', texto)
        if match_fecha_alt:
            datos["fecha"] = match_fecha_alt.group(1)
            print(f"DEBUG: Fecha encontrada (patrón 4): {datos['fecha']}")
    
    # Extraer DUI del cliente (formato: 06580922-3)
    match_dui = re.search(r'DUI\s*:?\s*(\d{8}-\d)', texto, re.IGNORECASE)
    if match_dui:
        datos["cliente"]["ruc_dni"] = match_dui.group(1)
    
    # Extraer nombre del cliente del RECEPTOR (formato: "Nombre o razón social: daniela zometa")
    # Buscar en la sección RECEPTOR
    match_receptor = re.search(r'RECEPTOR.*?Nombre\s+o\s+razón\s+social\s*:?\s*([^\n]+)', texto, re.IGNORECASE | re.DOTALL)
    if match_receptor:
        nombre = match_receptor.group(1).strip()
        # Limpiar el nombre (quitar DUI y otros datos que puedan venir después)
        nombre = re.split(r'\s*(?:DUI|Correo|Dirección)', nombre, flags=re.IGNORECASE)[0].strip()
        datos["cliente"]["nombre"] = nombre
    else:
        # Buscar patrón más simple
        match_nombre = re.search(r'Nombre\s+o\s+razón\s+social\s*:?\s*([^\n]+)', texto, re.IGNORECASE)
        if match_nombre:
            nombre = match_nombre.group(1).strip()
            nombre = re.split(r'\s*(?:DUI|Correo|Dirección)', nombre, flags=re.IGNORECASE)[0].strip()
            datos["cliente"]["nombre"] = nombre
    
    # Extraer total con formato "Total a Pagar: 15.00"
    match_total_pagar = re.search(r'Total\s+a\s+Pagar\s*:?\s*([\d,]+\.?\d*)', texto, re.IGNORECASE)
    if match_total_pagar:
        datos["total"] = float(match_total_pagar.group(1).replace(',', ''))
    else:
        # Buscar otros formatos de total
        match_total = re.search(r'(?:TOTAL|Total)\s*:?\s*(?:US\$|S/|Q)?\s*([\d,]+\.?\d*)', texto)
        if match_total:
            datos["total"] = float(match_total.group(1).replace(',', ''))
    
    # Extraer Monto Total de la Operación (subtotal)
    match_monto_operacion = re.search(r'Monto\s+Total\s+de\s+la\s+Operación\s*:?\s*([\d,]+\.?\d*)', texto, re.IGNORECASE)
    if match_monto_operacion:
        datos["subtotal"] = float(match_monto_operacion.group(1).replace(',', ''))
    else:
        # Si no se encuentra, usar el total como subtotal
        datos["subtotal"] = datos["total"]
    
    # Extraer Total Otros Montos No Afectos
    match_otros_montos = re.search(r'Total\s+Otros\s+Montos\s+No\s+Afectos\s*:?\s*([\d,]+\.?\d*)', texto, re.IGNORECASE)
    if match_otros_montos:
        datos["otros_montos"] = float(match_otros_montos.group(1).replace(',', ''))
    
    match_igv = re.search(r'(?:IGV|I\.G\.V\.)\s*(?:\(18%\))?\s*:?\s*S/?\s*([\d,]+\.?\d*)', texto)
    if match_igv:
        datos["igv"] = float(match_igv.group(1).replace(',', ''))
    
    # Extraer items (patrón básico)
    datos["items"] = extraer_items(texto)
    
    return datos

def extraer_items(texto: str) -> List[Dict]:
    """
    Extrae los items/productos de la factura.
    Soporta múltiples formatos de tabla de productos.
    """
    items = []
    
    print("\n=== DEBUG: Buscando items en el texto ===")
    print(f"DEBUG: Texto completo (primeros 2000 caracteres):\n{texto[:2000]}\n")
    
    # Patrón 0A: Con columna "Código" vacía (mostrada como "-")
    # Formato: N° | Cantidad | Unidad | Código | Descripción | Precio
    # Ejemplo: "1  1.00  Unidad  -  drontal 35kg  8.50"
    patron0a = r'(\d+)\s+([\d\.]+)\s+Unidad\s+[-\s]+([A-Za-zÁ-Úá-ú0-9][A-Za-zÁ-Úá-ú0-9\s\.\-/]+?)\s+([\d,]+\.[\d]{2})\s+[\d\.]+'
    
    matches0a = re.finditer(patron0a, texto, re.IGNORECASE)
    
    for match in matches0a:
        numero = match.group(1)
        cantidad = match.group(2)
        descripcion = match.group(3).strip()
        precio = match.group(4)
        
        # Limpiar descripción
        descripcion = ' '.join(descripcion.split())
        # Quitar guiones al inicio/final
        descripcion = descripcion.strip('- ')
        
        # Validar
        try:
            precio_float = float(precio.replace(',', ''))
            cantidad_float = float(cantidad)
            
            if (precio_float > 0 and precio_float < 100000 
                and cantidad_float > 0 and cantidad_float <= 1000
                and len(descripcion) >= 2
                and not descripcion.isdigit()):
                item = {
                    "cantidad": cantidad_float,
                    "unidad": "Unidad",
                    "descripcion": descripcion,
                    "precio_unitario": precio_float,
                    "total": cantidad_float * precio_float
                }
                items.append(item)
                print(f"DEBUG: Item encontrado (patrón 0A - con columna Código) - {item}")
        except ValueError:
            continue
    
    # Patrón 0B: Con columna "Código" SIN el guion explícito
    # Formato: N° | Cantidad | Unidad | Código | Descripción | Precio
    # Ejemplo: "1  1.00  Unidad       drontal 35kg  8.50" (código está vacío, solo espacios)
    if len(items) == 0:
        patron0b = r'(\d+)\s+([\d\.]+)\s+Unidad\s+([A-Za-zÁ-Úá-ú0-9][A-Za-zÁ-Úá-ú0-9\s\.\-/]+?)\s+([\d,]+\.[\d]{2})\s+[\d\.]+'
        
        matches0b = re.finditer(patron0b, texto, re.IGNORECASE)
        
        for match in matches0b:
            numero = match.group(1)
            cantidad = match.group(2)
            descripcion = match.group(3).strip()
            precio = match.group(4)
            
            # Limpiar descripción
            descripcion = ' '.join(descripcion.split())
            descripcion = descripcion.strip('- ')
            
            try:
                precio_float = float(precio.replace(',', ''))
                cantidad_float = float(cantidad)
                
                if (precio_float > 0 and precio_float < 100000 
                    and cantidad_float > 0 and cantidad_float <= 1000
                    and len(descripcion) >= 2
                    and not descripcion.isdigit()):
                    item = {
                        "cantidad": cantidad_float,
                        "unidad": "Unidad",
                        "descripcion": descripcion,
                        "precio_unitario": precio_float,
                        "total": cantidad_float * precio_float
                    }
                    items.append(item)
                    print(f"DEBUG: Item encontrado (patrón 0B - con columna Código vacía) - {item}")
            except ValueError:
                continue
    
    # Patrón 1: Formato completo con N°, Cantidad, Unidad, Descripción, Precio
    # Ejemplo: "1  1.00  Unidad  nexgard 4.5 a 10 kg  25.00"
    # Mejorado para aceptar descripciones más cortas y con caracteres especiales
    if len(items) == 0:
        patron1 = r'(\d+)\s+([\d\.]+)\s+(Unidad|Servicio|Pieza|Caja|Litro|Kg|Metro|Hora)\s+([A-Za-zÁ-Úá-ú0-9\s\.\-/]+?)\s+([\d,]+\.00)'
        
        matches = re.finditer(patron1, texto, re.IGNORECASE)
        
        for match in matches:
            numero = match.group(1)
            cantidad = match.group(2)
            unidad = match.group(3)
            descripcion = match.group(4).strip()
            precio = match.group(5)
            
            # Validar que el precio sea razonable (mayor a 0 y menor a 100000)
            precio_float = float(precio.replace(',', ''))
            cantidad_float = float(cantidad)
            
            # Aceptar descripciones más cortas (mínimo 2 caracteres)
            if (precio_float > 0 and precio_float < 100000 
                and cantidad_float > 0 and cantidad_float <= 1000
                and len(descripcion) >= 2):
                item = {
                    "cantidad": cantidad_float,
                    "unidad": unidad,
                    "descripcion": descripcion,
                    "precio_unitario": precio_float,
                    "total": cantidad_float * precio_float
                }
                items.append(item)
                print(f"DEBUG: Item encontrado (patrón 1) - {item}")
    
    # Si no se encontraron items con el patrón 1, intentar patrón 2
    if len(items) == 0:
        print("DEBUG: No se encontraron items con patrón 1, intentando patrón 2...")
        
        # Patrón 2: Buscar líneas que contengan cantidad, unidad y precio al final
        # Ejemplo: "1.00 Unidad nexgard 4.5 a 10 kg 25.00"
        # Mejorado para aceptar descripciones cortas y con /
        patron2 = r'([\d\.]+)\s+(Unidad|Servicio|Pieza|Caja|Litro|Kg|Metro|Hora)\s+([A-Za-zÁ-Úá-ú0-9][A-Za-zÁ-Úá-ú0-9\s\.\-/]+?)\s+([\d,]+\.00)(?:\s|$)'
        
        matches2 = re.finditer(patron2, texto, re.IGNORECASE)
        
        for match in matches2:
            cantidad = match.group(1)
            unidad = match.group(2)
            descripcion = match.group(3).strip()
            precio = match.group(4)
            
            # Validar que sea un item válido
            precio_float = float(precio.replace(',', ''))
            cantidad_float = float(cantidad)
            
            if (cantidad_float > 0 and cantidad_float <= 1000 
                and precio_float > 0 and precio_float < 100000
                and len(descripcion) >= 2):
                item = {
                    "cantidad": cantidad_float,
                    "unidad": unidad,
                    "descripcion": descripcion,
                    "precio_unitario": precio_float,
                    "total": cantidad_float * precio_float
                }
                items.append(item)
                print(f"DEBUG: Item encontrado (patrón 2) - {item}")
    
    # Si aún no se encontraron items, intentar patrón 2B (SIN palabra "Unidad")
    if len(items) == 0:
        print("DEBUG: No se encontraron items con patrón 2, intentando patrón 2B (sin unidad)...")
        
        # Patrón 2B: N°, Cantidad, Descripción, Precio (SIN unidad explícita)
        # Ejemplo: "1  1.00  collar para perro  4.50"
        # Este patrón es para cuando la columna "Unidad" está vacía
        patron2b = r'(\d+)\s+([\d\.]+)\s+([A-Za-zÁ-Úá-ú][A-Za-zÁ-Úá-ú0-9\s\.\-/]{2,50}?)\s+([\d,]+\.00)(?:\s|$)'
        
        matches2b = re.finditer(patron2b, texto, re.IGNORECASE)
        
        for match in matches2b:
            numero = match.group(1)
            cantidad = match.group(2)
            descripcion = match.group(3).strip()
            precio = match.group(4)
            
            # Validar que sea un item válido
            precio_float = float(precio.replace(',', ''))
            cantidad_float = float(cantidad)
            
            # Filtrar falsos positivos
            if (cantidad_float > 0 and cantidad_float <= 1000 
                and precio_float > 0 and precio_float < 100000
                and len(descripcion) >= 2
                and not re.match(r'^\d{4}-\d{2}-\d{2}', descripcion)  # No es una fecha
                and not re.match(r'^[\d\-\s]+$', descripcion)):  # No es solo números
                item = {
                    "cantidad": cantidad_float,
                    "unidad": "Unidad",
                    "descripcion": descripcion,
                    "precio_unitario": precio_float,
                    "total": cantidad_float * precio_float
                }
                items.append(item)
                print(f"DEBUG: Item encontrado (patrón 2B) - {item}")
    
    # Si aún no se encontraron items, intentar patrón 3 (más flexible, sin unidad)
    if len(items) == 0:
        print("DEBUG: No se encontraron items con patrón 2B, intentando patrón 3...")
        
        # Patrón 3: Cantidad, descripción y precio (sin unidad explícita, sin número)
        # Ejemplo: "1.00 hills c/d 91.74"
        # Mejorado para aceptar descripciones muy cortas
        patron3 = r'([\d\.]+)\s+([A-Za-zÁ-Úá-ú][A-Za-zÁ-Úá-ú0-9\s\.\-/]{1,50}?)\s+([\d,]+\.00)(?:\s|$)'
        
        matches3 = re.finditer(patron3, texto, re.IGNORECASE)
        
        for match in matches3:
            cantidad = match.group(1)
            descripcion = match.group(2).strip()
            precio = match.group(3)
            
            # Validar que sea un item válido
            precio_float = float(precio.replace(',', ''))
            cantidad_float = float(cantidad)
            
            # Filtrar falsos positivos (evitar fechas, códigos largos, etc.)
            if (cantidad_float > 0 and cantidad_float <= 1000 
                and precio_float > 0 and precio_float < 100000
                and len(descripcion) >= 2
                and not re.match(r'^\d{4}-\d{2}-\d{2}', descripcion)  # No es una fecha
                and not re.match(r'^[\d\-]+$', descripcion)):  # No es solo números y guiones
                item = {
                    "cantidad": cantidad_float,
                    "unidad": "Unidad",
                    "descripcion": descripcion,
                    "precio_unitario": precio_float,
                    "total": cantidad_float * precio_float
                }
                items.append(item)
                print(f"DEBUG: Item encontrado (patrón 3) - {item}")
    
    # Si aún no hay items, intentar patrón 4 (buscar en tabla estructurada)
    if len(items) == 0:
        print("DEBUG: No se encontraron items con patrón 3, intentando patrón 4 (tabla)...")
        
        # Buscar la sección de items (después de "Cuerpo del Documento" o similar)
        seccion_items = re.search(r'(?:Cuerpo del Documento|CUERPO DEL DOCUMENTO|Detalle|DETALLE|N°\s+Cantidad\s+Unidad\s+Descripción)(.*?)(?:Suma de Ventas|Resumen|RESUMEN|Total|Sub-Total)', 
                                  texto, re.IGNORECASE | re.DOTALL)
        
        if seccion_items:
            texto_items = seccion_items.group(1)
            print(f"DEBUG: Sección de items encontrada, longitud: {len(texto_items)}")
            print(f"DEBUG: Contenido de la sección:\n{texto_items[:500]}")
            
            # Patrón 4A: Con la palabra "Unidad" - SIMPLIFICADO
            # Capturar todo entre "Unidad" y "0.00", luego separar descripción y precio
            # Ejemplo: "1 1.00 Unidad puppy small bittes hills 25.70 0.00"
            patron4a = r'(\d+)\s+([\d\.]+)\s+Unidad\s+(.+?)\s+0\.00'
            matches4a = list(re.finditer(patron4a, texto_items, re.IGNORECASE))
            
            print(f"DEBUG: Patrón 4A encontró {len(matches4a)} coincidencias")
            
            for match in matches4a:
                numero = match.group(1)
                cantidad = match.group(2)
                contenido = match.group(3).strip()
                
                # Separar descripción y precio
                # El último elemento separado por espacios es el precio
                partes = contenido.split()
                if len(partes) >= 2:
                    precio = partes[-1]
                    descripcion = ' '.join(partes[:-1])
                    
                    try:
                        precio_float = float(precio.replace(',', ''))
                        cantidad_float = float(cantidad)
                        
                        print(f"DEBUG: Evaluando item - Cant:{cantidad}, Desc:'{descripcion}', Precio:{precio}")
                        
                        if (cantidad_float > 0 and cantidad_float <= 1000 
                            and precio_float > 0 and precio_float < 100000
                            and len(descripcion) >= 2):
                            item = {
                                "cantidad": cantidad_float,
                                "unidad": "Unidad",
                                "descripcion": descripcion,
                                "precio_unitario": precio_float,
                                "total": cantidad_float * precio_float
                            }
                            items.append(item)
                            print(f"DEBUG: ✓ Item agregado (patrón 4A) - {item}")
                    except ValueError:
                        print(f"DEBUG: Error al convertir precio '{precio}' a float")
            
            # Patrón 4B: Sin la palabra "Unidad"
            if len(items) == 0:
                print("DEBUG: Intentando patrón 4B (sin palabra Unidad)...")
                # Ejemplo: "1 1.00 collar para perro 4.50 0.00"
                # Capturar todo entre cantidad y "0.00"
                patron4b = r'(\d+)\s+([\d\.]+)\s+([A-Za-zÁ-Úá-ú].+?)\s+0\.00'
                matches4b = list(re.finditer(patron4b, texto_items, re.IGNORECASE))
                
                print(f"DEBUG: Patrón 4B encontró {len(matches4b)} coincidencias")
                
                for match in matches4b:
                    numero = match.group(1)
                    cantidad = match.group(2)
                    contenido = match.group(3).strip()
                    
                    # Separar descripción y precio
                    partes = contenido.split()
                    if len(partes) >= 2:
                        precio = partes[-1]
                        descripcion = ' '.join(partes[:-1])
                        
                        try:
                            precio_float = float(precio.replace(',', ''))
                            cantidad_float = float(cantidad)
                            
                            print(f"DEBUG: Evaluando item - Cant:{cantidad}, Desc:'{descripcion}', Precio:{precio}")
                            
                            # Filtrar falsos positivos
                            if (cantidad_float > 0 and cantidad_float <= 1000 
                                and precio_float > 0 and precio_float < 100000
                                and len(descripcion) >= 3
                                and not re.match(r'^\d{4}-\d{2}-\d{2}', descripcion)
                                and not re.match(r'^[\d\-\s]+$', descripcion)
                                and 'Precio' not in descripcion
                                and 'Descuento' not in descripcion
                                and 'Otros montos' not in descripcion
                                and 'Ventas' not in descripcion):
                                item = {
                                    "cantidad": cantidad_float,
                                    "unidad": "Unidad",
                                    "descripcion": descripcion,
                                    "precio_unitario": precio_float,
                                    "total": cantidad_float * precio_float
                                }
                                items.append(item)
                                print(f"DEBUG: ✓ Item agregado (patrón 4B) - {item}")
                        except ValueError:
                            print(f"DEBUG: Error al convertir precio '{precio}' a float")
    
    print(f"DEBUG: Total de items encontrados: {len(items)}\n")
    
    return items
    
    print(f"DEBUG: Total de items encontrados: {len(items)}\n")
    
    return items


def extraer_qr_de_pdf(path: str) -> Optional[str]:
    """
    Extrae el código QR del PDF y lo guarda como imagen.
    
    Args:
        path: Ruta al archivo PDF
        
    Returns:
        Ruta de la imagen del QR extraída, o None si no se encuentra
    """
    try:
        import fitz  # PyMuPDF
        from PIL import Image, ImageOps, ImageEnhance
        import io
        
        # Abrir el PDF
        pdf_document = fitz.open(path)
        
        # Buscar en la primera página
        page = pdf_document[0]
        
        # Método 1: Extraer imágenes embebidas
        image_list = page.get_images(full=True)
        print(f"DEBUG QR: Se encontraron {len(image_list)} imágenes embebidas en el PDF")
        
        qr_candidates = []
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Abrir la imagen con PIL
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            
            print(f"DEBUG QR: Imagen embebida {img_index}: {width}x{height}, modo: {image.mode}")
            
            # Verificar si es cuadrada y de tamaño razonable (QR típico)
            aspect_ratio = width / height if height > 0 else 0
            if 0.7 <= aspect_ratio <= 1.3 and width >= 50:
                qr_candidates.append((img_index, width * height, image))
        
        # Si encontramos candidatos, tomar el más grande que sea un QR válido
        if qr_candidates:
            qr_candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Intentar con cada candidato hasta encontrar uno válido
            for img_index, area, image in qr_candidates:
                # Procesar la imagen para asegurar que sea un QR legible
                image_procesada = procesar_imagen_qr(image)
                
                qr_path = f"temp_qr_embebido_{img_index}.png"
                image_procesada.save(qr_path, "PNG")
                print(f"✓ QR extraído (método 1): imagen embebida {img_index}, tamaño {image.size}")
                
                # Guardar también la imagen original sin procesar para comparar
                qr_path_original = f"temp_qr_original_{img_index}.png"
                image.save(qr_path_original, "PNG")
                
                pdf_document.close()
                return qr_path
        
        # Método 2: Renderizar la página y buscar el QR en el área específica
        print("DEBUG QR: Intentando método 2 - renderizar página...")
        
        # Renderizar la página a imagen de alta resolución
        mat = fitz.Matrix(4, 4)  # Zoom 4x para mejor calidad
        pix = page.get_pixmap(matrix=mat)
        
        # Convertir a PIL Image
        img_data = pix.tobytes("png")
        full_image = Image.open(io.BytesIO(img_data))
        
        print(f"DEBUG QR: Página renderizada: {full_image.size}, modo: {full_image.mode}")
        
        # El QR está en el centro superior del PDF, debajo del título "FACTURA"
        width, height = full_image.size
        
        # Área específica donde está SOLO el QR (sin el texto "FACTURA" arriba)
        # Necesitamos empezar más abajo para evitar capturar el texto
        areas_busqueda = [
            # Centro superior - área pequeña solo para el QR (más abajo para evitar "FACTURA")
            (int(width * 0.44), int(height * 0.10), int(width * 0.56), int(height * 0.18)),
            # Centro superior - un poco más amplio
            (int(width * 0.43), int(height * 0.09), int(width * 0.57), int(height * 0.19)),
            # Centro superior - más amplio (fallback)
            (int(width * 0.42), int(height * 0.085), int(width * 0.58), int(height * 0.20)),
        ]
        
        # Buscar el QR en múltiples áreas y guardar todas
        mejor_qr = None
        mejor_area_idx = 0
        
        for idx, area in enumerate(areas_busqueda):
            qr_area = full_image.crop(area)
            print(f"DEBUG QR: Área {idx+1} extraída: {qr_area.size}")
            
            # Procesar la imagen
            qr_area_procesada = procesar_imagen_qr(qr_area)
            
            qr_path_temp = f"temp_qr_area_{idx}.png"
            qr_area_procesada.save(qr_path_temp, "PNG")
            
            # Guardar la primera área como mejor candidato
            if mejor_qr is None:
                mejor_qr = qr_path_temp
                mejor_area_idx = idx
        
        if mejor_qr:
            print(f"✓ QR extraído (método 2): área {mejor_area_idx}, archivo {mejor_qr}")
            pdf_document.close()
            return mejor_qr
        
        print("⚠ No se pudo extraer el QR del PDF")
        pdf_document.close()
        return None
        
    except Exception as e:
        print(f"ERROR al extraer QR del PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def procesar_imagen_qr(image: 'Image') -> 'Image':
    """
    Procesa una imagen de QR para mejorar su legibilidad.
    Convierte a blanco y negro puro con buen contraste y recorta espacios en blanco.
    """
    from PIL import Image, ImageOps, ImageEnhance, ImageChops
    import numpy as np
    
    # Convertir a escala de grises
    if image.mode != 'L':
        image = image.convert('L')
    
    # Aumentar el contraste
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Aplicar autocontraste
    image = ImageOps.autocontrast(image, cutoff=5)
    
    # Convertir a blanco y negro puro (1-bit)
    threshold = 128
    image = image.point(lambda x: 255 if x > threshold else 0, mode='1')
    
    # Convertir a RGB para poder trabajar con ella
    image = image.convert('RGB')
    
    # Convertir a numpy array para análisis más preciso
    img_array = np.array(image.convert('L'))
    
    # Encontrar las filas y columnas que contienen contenido negro (QR)
    # Buscar filas con suficiente contenido negro
    row_has_content = np.sum(img_array < 128, axis=1) > (img_array.shape[1] * 0.1)
    col_has_content = np.sum(img_array < 128, axis=0) > (img_array.shape[0] * 0.1)
    
    # Encontrar los límites del contenido
    rows_with_content = np.where(row_has_content)[0]
    cols_with_content = np.where(col_has_content)[0]
    
    if len(rows_with_content) > 0 and len(cols_with_content) > 0:
        # Recortar al área que contiene el QR
        top = rows_with_content[0]
        bottom = rows_with_content[-1]
        left = cols_with_content[0]
        right = cols_with_content[-1]
        
        # Agregar un pequeño margen
        margin = 5
        top = max(0, top - margin)
        bottom = min(img_array.shape[0], bottom + margin)
        left = max(0, left - margin)
        right = min(img_array.shape[1], right + margin)
        
        image = image.crop((left, top, right, bottom))
        print(f"DEBUG QR: Imagen recortada al contenido del QR, nuevo tamaño: {image.size}")
    
    return image
