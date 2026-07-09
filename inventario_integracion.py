# inventario_integracion.py
# Integración del inventario con el procesamiento de facturas

from inventario_db import InventarioDB
from typing import List, Dict, Tuple
import re

class InventarioIntegracion:
    def __init__(self):
        self.db = InventarioDB()
    
    def procesar_factura(self, datos_factura: Dict) -> Dict:
        """
        Procesa una factura y actualiza el inventario automáticamente.
        
        Args:
            datos_factura: Datos extraídos de la factura
            
        Returns:
            Diccionario con el resultado del procesamiento
        """
        print("DEBUG INTEGRACION: Iniciando procesamiento de factura...")
        
        resultado = {
            'exito': True,
            'productos_procesados': [],
            'productos_no_encontrados': [],
            'alertas': [],
            'errores': [],
            'factura_duplicada': False
        }
        
        # Obtener número de control de la factura
        numero_control = datos_factura.get('numero_control', '')
        
        if not numero_control:
            print("⚠️ ADVERTENCIA: Factura sin número de control, no se puede verificar duplicados")
        else:
            # Verificar si la factura ya fue procesada
            if self.db.factura_ya_procesada(numero_control):
                resultado['exito'] = False
                resultado['factura_duplicada'] = True
                resultado['errores'].append(
                    f"Esta factura ya fue procesada anteriormente.\n"
                    f"Número de control: {numero_control}\n\n"
                    f"Para evitar descuentos duplicados en el inventario, "
                    f"no se procesará nuevamente."
                )
                print(f"❌ FACTURA DUPLICADA: {numero_control} - Procesamiento cancelado")
                return resultado
        
        items = datos_factura.get('items', [])
        numero_factura = datos_factura.get('numero_factura', 'SIN_NUMERO')
        
        print(f"DEBUG INTEGRACION: Procesando {len(items)} items de la factura {numero_control or numero_factura}")
        
        for item in items:
            try:
                nombre_producto = item.get('descripcion', '').strip()
                cantidad = int(item.get('cantidad', 0))
                precio_unitario = float(item.get('precio_unitario', 0))
                
                print(f"\n{'='*60}")
                print(f"DEBUG INTEGRACION: Procesando item de factura:")
                print(f"  Nombre: '{nombre_producto}'")
                print(f"  Cantidad: {cantidad}")
                print(f"  Precio unitario: ${precio_unitario}")
                print(f"{'='*60}\n")
                
                if not nombre_producto or cantidad <= 0:
                    print(f"DEBUG INTEGRACION: Item inválido, saltando...")
                    continue
                
                # Buscar producto en inventario usando nombre y precio
                producto = self.buscar_producto_similar(nombre_producto, precio_unitario)
                
                if producto:
                    print(f"\n✅ PRODUCTO ENCONTRADO:")
                    print(f"  Nombre en inventario: {producto['nombre']}")
                    print(f"  ID: {producto['id']}")
                    print(f"  Precio venta: ${producto.get('precio_venta', 'N/A')}")
                    print(f"  Stock actual: {producto['stock_actual']}\n")
                    # Verificar stock disponible
                    if producto['stock_actual'] >= cantidad:
                        # Descontar del inventario
                        exito = self.db.descontar_stock(
                            producto['id'], 
                            cantidad, 
                            numero_factura
                        )
                        
                        if exito:
                            nuevo_stock = producto['stock_actual'] - cantidad
                            resultado['productos_procesados'].append({
                                'nombre': producto['nombre'],
                                'cantidad_vendida': cantidad,
                                'stock_anterior': producto['stock_actual'],
                                'stock_nuevo': nuevo_stock
                            })
                            
                            print(f"DEBUG INTEGRACION: Stock descontado: {producto['stock_actual']} -> {nuevo_stock}")
                            
                            # Verificar si queda stock bajo
                            if nuevo_stock <= producto['stock_minimo']:
                                resultado['alertas'].append({
                                    'tipo': 'stock_bajo',
                                    'producto': producto['nombre'],
                                    'stock_actual': nuevo_stock,
                                    'stock_minimo': producto['stock_minimo']
                                })
                        else:
                            resultado['errores'].append(
                                f"Error al descontar stock de {producto['nombre']}"
                            )
                    else:
                        print(f"DEBUG INTEGRACION: Stock insuficiente: disponible {producto['stock_actual']}, solicitado {cantidad}")
                        # Stock insuficiente
                        resultado['alertas'].append({
                            'tipo': 'stock_insuficiente',
                            'producto': producto['nombre'],
                            'cantidad_solicitada': cantidad,
                            'stock_disponible': producto['stock_actual']
                        })
                        
                        # Descontar lo que se pueda
                        if producto['stock_actual'] > 0:
                            self.db.descontar_stock(
                                producto['id'], 
                                producto['stock_actual'], 
                                numero_factura
                            )
                            resultado['productos_procesados'].append({
                                'nombre': producto['nombre'],
                                'cantidad_vendida': producto['stock_actual'],
                                'stock_anterior': producto['stock_actual'],
                                'stock_nuevo': 0,
                                'nota': f'Stock insuficiente (se solicitaron {cantidad})'
                            })
                else:
                    print(f"DEBUG INTEGRACION: Producto NO encontrado: '{nombre_producto}'")
                    # Producto no encontrado
                    resultado['productos_no_encontrados'].append({
                        'nombre': nombre_producto,
                        'cantidad': cantidad
                    })
                    
            except Exception as e:
                print(f"DEBUG INTEGRACION: Error procesando {nombre_producto}: {str(e)}")
                resultado['errores'].append(f"Error procesando {nombre_producto}: {str(e)}")
        
        # Si el procesamiento fue exitoso y hay número de control, registrar la factura
        if resultado['exito'] and numero_control and resultado['productos_procesados']:
            codigo_generacion = datos_factura.get('codigo_generacion', '')
            fecha_factura = datos_factura.get('fecha', '')
            
            # Calcular total de la factura
            total_factura = sum(item.get('total', 0) for item in items)
            
            # Registrar factura como procesada
            self.db.registrar_factura_procesada(
                numero_control,
                codigo_generacion,
                fecha_factura,
                total_factura,
                len(resultado['productos_procesados'])
            )
        
        print(f"DEBUG INTEGRACION: Procesamiento completado. Productos procesados: {len(resultado['productos_procesados'])}, No encontrados: {len(resultado['productos_no_encontrados'])}")
        return resultado
    
    def buscar_producto_similar(self, nombre_factura: str, precio_factura: float = None) -> Dict:
        """
        Busca un producto similar en el inventario usando nombre, alias y precio.
        
        Args:
            nombre_factura: Nombre del producto en la factura
            precio_factura: Precio del producto en la factura (opcional)
            
        Returns:
            Producto encontrado o None
        """
        # Limpiar nombre
        nombre_limpio = self.limpiar_nombre_producto(nombre_factura)
        
        print(f"DEBUG BUSQUEDA: Buscando '{nombre_factura}' (limpio: '{nombre_limpio}'), precio: {precio_factura}")
        
        # Estrategia 1: Búsqueda exacta por nombre
        producto = self.db.buscar_producto_por_nombre(nombre_limpio)
        if producto:
            print(f"DEBUG BUSQUEDA: Coincidencia exacta encontrada: {producto['nombre']}")
            return producto
        
        # Estrategia 2: Búsqueda en alias
        productos = self.db.obtener_productos()
        for producto in productos:
            if producto.get('alias'):
                alias_list = [a.strip().lower() for a in producto['alias'].split(',')]
                if nombre_limpio.lower() in alias_list:
                    print(f"DEBUG BUSQUEDA: Coincidencia por alias encontrada: {producto['nombre']}")
                    return producto
        
        # Estrategia 3: Búsqueda con similitud de nombre + precio
        candidatos = []
        
        for producto in productos:
            # Calcular similitud de nombre
            score_nombre = self.calcular_similitud(nombre_limpio, producto['nombre'])
            
            # También verificar similitud con alias
            if producto.get('alias'):
                alias_list = [a.strip() for a in producto['alias'].split(',')]
                for alias in alias_list:
                    score_alias = self.calcular_similitud(nombre_limpio, alias)
                    score_nombre = max(score_nombre, score_alias)
            
            # Si la similitud es muy baja, descartar
            if score_nombre < 0.5:
                continue
            
            # Calcular score de precio si está disponible
            score_precio = 0
            if precio_factura and producto.get('precio_venta'):
                # Tolerancia del 10% en el precio
                diferencia_precio = abs(precio_factura - producto['precio_venta']) / producto['precio_venta']
                if diferencia_precio <= 0.10:  # Dentro del 10%
                    score_precio = 1.0 - diferencia_precio
                else:
                    score_precio = max(0, 1.0 - (diferencia_precio / 2))
            
            # Score combinado: 60% nombre + 40% precio
            if precio_factura and producto.get('precio_venta'):
                score_total = (score_nombre * 0.6) + (score_precio * 0.4)
            else:
                score_total = score_nombre
            
            candidatos.append({
                'producto': producto,
                'score_nombre': score_nombre,
                'score_precio': score_precio,
                'score_total': score_total
            })
            
            print(f"DEBUG BUSQUEDA: Candidato: {producto['nombre']} - Score nombre: {score_nombre:.2f}, Score precio: {score_precio:.2f}, Total: {score_total:.2f}")
        
        # Ordenar por score total
        candidatos.sort(key=lambda x: x['score_total'], reverse=True)
        
        # Si el mejor candidato tiene un score alto, retornarlo
        if candidatos and candidatos[0]['score_total'] > 0.7:
            mejor = candidatos[0]
            print(f"DEBUG BUSQUEDA: Mejor coincidencia: {mejor['producto']['nombre']} (score: {mejor['score_total']:.2f})")
            return mejor['producto']
        
        # Si hay múltiples candidatos similares, verificar con precio
        if len(candidatos) >= 2 and precio_factura:
            # Si los dos mejores tienen scores de nombre similares pero precios diferentes
            if abs(candidatos[0]['score_nombre'] - candidatos[1]['score_nombre']) < 0.2:
                # Usar el que tenga mejor coincidencia de precio
                mejor_con_precio = max(candidatos[:3], key=lambda x: x['score_precio'])
                if mejor_con_precio['score_precio'] > 0.7:
                    print(f"DEBUG BUSQUEDA: Seleccionado por precio: {mejor_con_precio['producto']['nombre']}")
                    return mejor_con_precio['producto']
        
        print(f"DEBUG BUSQUEDA: No se encontró coincidencia suficiente")
        return None
    
    def limpiar_nombre_producto(self, nombre: str) -> str:
        """Limpia y normaliza el nombre del producto."""
        # Convertir a minúsculas
        nombre = nombre.lower().strip()
        
        # Remover espacios múltiples
        nombre = re.sub(r'\s+', ' ', nombre)
        
        # NO remover caracteres especiales como / que son importantes
        # Solo remover caracteres realmente problemáticos
        nombre = re.sub(r'[^\w\s/\-]', '', nombre)
        
        return nombre
    
    def extraer_palabras_clave(self, nombre: str) -> List[str]:
        """Extrae palabras clave del nombre del producto."""
        palabras = nombre.split()
        
        # Ordenar por longitud (palabras más largas primero)
        palabras_ordenadas = sorted(palabras, key=len, reverse=True)
        
        return palabras_ordenadas
    
    def calcular_similitud(self, str1: str, str2: str) -> float:
        """
        Calcula la similitud entre dos strings usando el algoritmo de Levenshtein.
        
        Returns:
            Valor entre 0 y 1 (1 = idénticos)
        """
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        str1 = str1.lower()
        str2 = str2.lower()
        
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(str1, str2)
        return 1 - (distance / max_len)
    
    def generar_reporte_procesamiento(self, resultado: Dict) -> str:
        """Genera un reporte legible del procesamiento."""
        reporte = []
        reporte.append("=== REPORTE DE PROCESAMIENTO DE INVENTARIO ===\n")
        
        # Productos procesados
        if resultado['productos_procesados']:
            reporte.append("✅ PRODUCTOS PROCESADOS:")
            for producto in resultado['productos_procesados']:
                reporte.append(f"  • {producto['nombre']}")
                reporte.append(f"    Cantidad vendida: {producto['cantidad_vendida']}")
                reporte.append(f"    Stock: {producto['stock_anterior']} → {producto['stock_nuevo']}")
                if 'nota' in producto:
                    reporte.append(f"    Nota: {producto['nota']}")
                reporte.append("")
        
        # Productos no encontrados
        if resultado['productos_no_encontrados']:
            reporte.append("❌ PRODUCTOS NO ENCONTRADOS EN INVENTARIO:")
            for producto in resultado['productos_no_encontrados']:
                reporte.append(f"  • {producto['nombre']} (Cantidad: {producto['cantidad']})")
            reporte.append("")
        
        # Alertas
        if resultado['alertas']:
            reporte.append("⚠️ ALERTAS:")
            for alerta in resultado['alertas']:
                if alerta['tipo'] == 'stock_bajo':
                    reporte.append(f"  • Stock bajo: {alerta['producto']}")
                    reporte.append(f"    Stock actual: {alerta['stock_actual']} (Mínimo: {alerta['stock_minimo']})")
                elif alerta['tipo'] == 'stock_insuficiente':
                    reporte.append(f"  • Stock insuficiente: {alerta['producto']}")
                    reporte.append(f"    Solicitado: {alerta['cantidad_solicitada']}, Disponible: {alerta['stock_disponible']}")
                reporte.append("")
        
        # Errores
        if resultado['errores']:
            reporte.append("❌ ERRORES:")
            for error in resultado['errores']:
                reporte.append(f"  • {error}")
            reporte.append("")
        
        return "\n".join(reporte)


def integrar_inventario_con_factura(datos_factura: Dict) -> Dict:
    """
    Función principal para integrar el inventario con el procesamiento de facturas.
    
    Args:
        datos_factura: Datos extraídos de la factura
        
    Returns:
        Resultado del procesamiento del inventario
    """
    integracion = InventarioIntegracion()
    return integracion.procesar_factura(datos_factura)