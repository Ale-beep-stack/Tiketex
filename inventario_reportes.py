"""
Módulo para generación de reportes del sistema de inventario.
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os


class GeneradorReportes:
    """Clase para generar reportes del inventario."""
    
    def __init__(self, db_path: str = "inventario.db"):
        """Inicializa el generador de reportes."""
        self.db_path = db_path
        # Usar ruta absoluta para la carpeta de reportes
        self.carpeta_reportes = os.path.abspath("reportes_generados")
        
        # Crear carpeta si no existe
        if not os.path.exists(self.carpeta_reportes):
            os.makedirs(self.carpeta_reportes)
    
    def _obtener_conexion(self):
        """Obtiene una conexión a la base de datos."""
        return sqlite3.connect(self.db_path, timeout=10.0)
    
    def _crear_encabezado(self, titulo: str):
        """Crea el encabezado del reporte."""
        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        fecha_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        
        elementos = []
        elementos.append(Paragraph(titulo, titulo_style))
        elementos.append(Paragraph(
            f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            fecha_style
        ))
        elementos.append(Spacer(1, 20))
        
        return elementos
    
    def generar_inventario_actual(self) -> str:
        """Genera reporte de inventario actual."""
        try:
            # Nombre del archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{self.carpeta_reportes}/inventario_actual_{timestamp}.pdf"
            
            # Crear documento
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elementos = []
            
            # Encabezado
            elementos.extend(self._crear_encabezado("REPORTE DE INVENTARIO ACTUAL"))
            
            # Obtener datos
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.codigo, p.nombre, c.nombre as categoria, 
                           p.stock_actual, p.unidad_medida, p.precio_compra, 
                           p.precio_venta, (p.stock_actual * p.precio_compra) as valor_stock
                    FROM productos p
                    LEFT JOIN categorias c ON p.categoria_id = c.id
                    WHERE p.activo = 1
                    ORDER BY p.nombre
                ''')
                productos = cursor.fetchall()
            
            # Crear tabla
            datos_tabla = [['Código', 'Producto', 'Categoría', 'Stock', 'Unidad', 
                           'P. Compra', 'P. Venta', 'Valor Stock']]
            
            total_valor = 0
            for prod in productos:
                codigo, nombre, categoria, stock, unidad, p_compra, p_venta, valor = prod
                datos_tabla.append([
                    codigo or 'N/A',
                    nombre,
                    categoria or 'Sin categoría',
                    str(stock),
                    unidad,
                    f"${p_compra:.2f}" if p_compra else 'N/A',
                    f"${p_venta:.2f}" if p_venta else 'N/A',
                    f"${valor:.2f}" if valor else '$0.00'
                ])
                total_valor += valor if valor else 0
            
            # Agregar fila de total
            datos_tabla.append(['', '', '', '', '', '', 'TOTAL:', f"${total_valor:.2f}"])
            
            # Crear y estilizar tabla
            tabla = Table(datos_tabla, colWidths=[0.8*inch, 1.8*inch, 1.2*inch, 0.7*inch, 
                                                   0.7*inch, 0.9*inch, 0.9*inch, 1*inch])
            
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('GRID', (0, 0), (-1, -2), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F5E9')),
                ('SPAN', (0, -1), (6, -1)),
            ]))
            
            elementos.append(tabla)
            elementos.append(Spacer(1, 20))
            elementos.append(Paragraph(f"Total de productos: {len(productos)}", 
                                      getSampleStyleSheet()['Normal']))
            
            # Generar PDF
            doc.build(elementos)
            print(f"Reporte generado: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"Error al generar reporte de inventario: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generar_stock_bajo(self) -> str:
        """Genera reporte de productos con stock bajo."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{self.carpeta_reportes}/stock_bajo_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elementos = []
            
            elementos.extend(self._crear_encabezado("REPORTE DE PRODUCTOS CON STOCK BAJO"))
            
            # Obtener productos con stock bajo
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.codigo, p.nombre, c.nombre as categoria, 
                           p.stock_actual, p.stock_minimo, p.unidad_medida
                    FROM productos p
                    LEFT JOIN categorias c ON p.categoria_id = c.id
                    WHERE p.activo = 1 AND p.stock_actual <= p.stock_minimo
                    ORDER BY p.stock_actual ASC
                ''')
                productos = cursor.fetchall()
            
            if not productos:
                elementos.append(Paragraph("No hay productos con stock bajo.", 
                                          getSampleStyleSheet()['Normal']))
            else:
                datos_tabla = [['Código', 'Producto', 'Categoría', 'Stock Actual', 
                               'Stock Mínimo', 'Unidad']]
                
                for prod in productos:
                    codigo, nombre, categoria, stock_actual, stock_min, unidad = prod
                    datos_tabla.append([
                        codigo or 'N/A',
                        nombre,
                        categoria or 'Sin categoría',
                        str(stock_actual),
                        str(stock_min),
                        unidad
                    ])
                
                tabla = Table(datos_tabla, colWidths=[1*inch, 2.5*inch, 1.5*inch, 
                                                       1*inch, 1*inch, 1*inch])
                
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D32F2F')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFEBEE')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elementos.append(tabla)
                elementos.append(Spacer(1, 20))
                elementos.append(Paragraph(f"Total de productos con stock bajo: {len(productos)}", 
                                          getSampleStyleSheet()['Normal']))
            
            doc.build(elementos)
            print(f"Reporte generado: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"Error al generar reporte de stock bajo: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generar_movimientos(self, fecha_inicio: datetime = None, fecha_fin: datetime = None) -> str:
        """Genera reporte de movimientos de inventario."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{self.carpeta_reportes}/movimientos_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elementos = []
            
            # Determinar rango de fechas
            if not fecha_fin:
                fecha_fin = datetime.now()
            if not fecha_inicio:
                fecha_inicio = fecha_fin - timedelta(days=30)
            
            titulo = f"REPORTE DE MOVIMIENTOS DE INVENTARIO\n{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
            elementos.extend(self._crear_encabezado(titulo))
            
            # Obtener movimientos
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT m.fecha_movimiento, p.nombre, m.tipo_movimiento, m.cantidad, 
                           m.precio_unitario, m.motivo, m.numero_factura
                    FROM movimientos m
                    JOIN productos p ON m.producto_id = p.id
                    WHERE DATE(m.fecha_movimiento) BETWEEN DATE(?) AND DATE(?)
                    ORDER BY m.fecha_movimiento DESC
                ''', (fecha_inicio.strftime('%Y-%m-%d'), fecha_fin.strftime('%Y-%m-%d')))
                movimientos = cursor.fetchall()
            
            if not movimientos:
                elementos.append(Paragraph("No hay movimientos en el período seleccionado.", 
                                          getSampleStyleSheet()['Normal']))
            else:
                datos_tabla = [['Fecha', 'Producto', 'Tipo', 'Cantidad', 'P. Unit.', 'Motivo']]
                
                for mov in movimientos:
                    fecha, producto, tipo, cantidad, precio, motivo, factura = mov
                    fecha_str = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
                    datos_tabla.append([
                        fecha_str,
                        producto[:25],
                        tipo,
                        str(cantidad),
                        f"${precio:.2f}" if precio else 'N/A',
                        motivo[:30] if motivo else 'N/A'
                    ])
                
                tabla = Table(datos_tabla, colWidths=[1.3*inch, 1.8*inch, 0.8*inch, 
                                                       0.8*inch, 0.8*inch, 2.5*inch])
                
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                elementos.append(tabla)
                elementos.append(Spacer(1, 20))
                elementos.append(Paragraph(f"Total de movimientos: {len(movimientos)}", 
                                          getSampleStyleSheet()['Normal']))
            
            doc.build(elementos)
            print(f"Reporte generado: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"Error al generar reporte de movimientos: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generar_productos_mas_vendidos(self, fecha_inicio: datetime = None, fecha_fin: datetime = None, top: int = 10) -> str:
        """Genera reporte de productos más vendidos."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{self.carpeta_reportes}/mas_vendidos_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elementos = []
            
            if not fecha_fin:
                fecha_fin = datetime.now()
            if not fecha_inicio:
                fecha_inicio = fecha_fin - timedelta(days=30)
            
            titulo = f"REPORTE DE PRODUCTOS MÁS VENDIDOS (TOP {top})\n{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
            elementos.extend(self._crear_encabezado(titulo))
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.nombre, c.nombre as categoria, 
                           SUM(m.cantidad) as total_vendido,
                           p.unidad_medida,
                           AVG(m.precio_unitario) as precio_promedio
                    FROM movimientos m
                    JOIN productos p ON m.producto_id = p.id
                    LEFT JOIN categorias c ON p.categoria_id = c.id
                    WHERE m.tipo_movimiento = 'SALIDA' 
                    AND DATE(m.fecha_movimiento) BETWEEN DATE(?) AND DATE(?)
                    GROUP BY p.id, p.nombre, c.nombre, p.unidad_medida
                    ORDER BY total_vendido DESC
                    LIMIT ?
                ''', (fecha_inicio.strftime('%Y-%m-%d'), fecha_fin.strftime('%Y-%m-%d'), top))
                productos = cursor.fetchall()
            
            if not productos:
                elementos.append(Paragraph("No hay ventas en el período seleccionado.", 
                                          getSampleStyleSheet()['Normal']))
            else:
                datos_tabla = [['#', 'Producto', 'Categoría', 'Total Vendido', 'Unidad', 'Precio Prom.']]
                
                for idx, prod in enumerate(productos, 1):
                    nombre, categoria, total, unidad, precio_prom = prod
                    datos_tabla.append([
                        str(idx),
                        nombre,
                        categoria or 'Sin categoría',
                        str(total),
                        unidad,
                        f"${precio_prom:.2f}" if precio_prom else 'N/A'
                    ])
                
                tabla = Table(datos_tabla, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 
                                                       1*inch, 0.8*inch, 1.2*inch])
                
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F57C00')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elementos.append(tabla)
            
            doc.build(elementos)
            print(f"Reporte generado: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"Error al generar reporte de más vendidos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generar_valorizacion_inventario(self) -> str:
        """Genera reporte de valorización del inventario."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{self.carpeta_reportes}/valorizacion_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elementos = []
            
            elementos.extend(self._crear_encabezado("REPORTE DE VALORIZACIÓN DE INVENTARIO"))
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.nombre as categoria,
                           COUNT(p.id) as cantidad_productos,
                           SUM(p.stock_actual) as stock_total,
                           SUM(p.stock_actual * p.precio_compra) as valor_compra,
                           SUM(p.stock_actual * p.precio_venta) as valor_venta
                    FROM productos p
                    LEFT JOIN categorias c ON p.categoria_id = c.id
                    WHERE p.activo = 1
                    GROUP BY c.id, c.nombre
                    ORDER BY valor_compra DESC
                ''')
                categorias = cursor.fetchall()
            
            if not categorias:
                elementos.append(Paragraph("No hay productos en el inventario.", 
                                          getSampleStyleSheet()['Normal']))
            else:
                datos_tabla = [['Categoría', 'Cant. Productos', 'Stock Total', 
                               'Valor Compra', 'Valor Venta', 'Margen']]
                
                total_productos = 0
                total_valor_compra = 0
                total_valor_venta = 0
                
                for cat in categorias:
                    categoria, cant_prod, stock, val_compra, val_venta = cat
                    margen = ((val_venta - val_compra) / val_compra * 100) if val_compra and val_compra > 0 else 0
                    
                    datos_tabla.append([
                        categoria or 'Sin categoría',
                        str(cant_prod),
                        str(int(stock)) if stock else '0',
                        f"${val_compra:.2f}" if val_compra else '$0.00',
                        f"${val_venta:.2f}" if val_venta else '$0.00',
                        f"{margen:.1f}%"
                    ])
                    
                    total_productos += cant_prod
                    total_valor_compra += val_compra if val_compra else 0
                    total_valor_venta += val_venta if val_venta else 0
                
                margen_total = ((total_valor_venta - total_valor_compra) / total_valor_compra * 100) if total_valor_compra > 0 else 0
                
                datos_tabla.append([
                    'TOTAL',
                    str(total_productos),
                    '',
                    f"${total_valor_compra:.2f}",
                    f"${total_valor_venta:.2f}",
                    f"{margen_total:.1f}%"
                ])
                
                tabla = Table(datos_tabla, colWidths=[2*inch, 1.2*inch, 1*inch, 
                                                       1.3*inch, 1.3*inch, 1*inch])
                
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#388E3C')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                    ('GRID', (0, 0), (-1, -2), 1, colors.black),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#C8E6C9')),
                ]))
                
                elementos.append(tabla)
            
            doc.build(elementos)
            print(f"Reporte generado: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"Error al generar reporte de valorización: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generar_productos_por_categoria(self) -> str:
        """Genera reporte de productos agrupados por categoría."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{self.carpeta_reportes}/por_categoria_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elementos = []
            
            elementos.extend(self._crear_encabezado("REPORTE DE PRODUCTOS POR CATEGORÍA"))
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.nombre as categoria, c.id
                    FROM categorias c
                    ORDER BY c.nombre
                ''')
                categorias = cursor.fetchall()
                
                # Agregar categoría "Sin categoría"
                categorias.append(('Sin categoría', None))
            
            styles = getSampleStyleSheet()
            
            for categoria, cat_id in categorias:
                with self._obtener_conexion() as conn:
                    cursor = conn.cursor()
                    if cat_id:
                        cursor.execute('''
                            SELECT p.codigo, p.nombre, p.stock_actual, p.unidad_medida,
                                   p.precio_compra, p.precio_venta
                            FROM productos p
                            WHERE p.categoria_id = ? AND p.activo = 1
                            ORDER BY p.nombre
                        ''', (cat_id,))
                    else:
                        cursor.execute('''
                            SELECT p.codigo, p.nombre, p.stock_actual, p.unidad_medida,
                                   p.precio_compra, p.precio_venta
                            FROM productos p
                            WHERE p.categoria_id IS NULL AND p.activo = 1
                            ORDER BY p.nombre
                        ''')
                    productos = cursor.fetchall()
                
                if productos:
                    # Título de categoría
                    cat_style = ParagraphStyle(
                        'CategoryTitle',
                        parent=styles['Heading2'],
                        fontSize=12,
                        textColor=colors.HexColor('#1976D2'),
                        spaceAfter=10
                    )
                    elementos.append(Paragraph(f"<b>{categoria}</b>", cat_style))
                    
                    # Tabla de productos
                    datos_tabla = [['Código', 'Producto', 'Stock', 'Unidad', 'P. Compra', 'P. Venta']]
                    
                    for prod in productos:
                        codigo, nombre, stock, unidad, p_compra, p_venta = prod
                        datos_tabla.append([
                            codigo or 'N/A',
                            nombre,
                            str(stock),
                            unidad,
                            f"${p_compra:.2f}" if p_compra else 'N/A',
                            f"${p_venta:.2f}" if p_venta else 'N/A'
                        ])
                    
                    tabla = Table(datos_tabla, colWidths=[1*inch, 2.5*inch, 0.8*inch, 
                                                           0.8*inch, 1*inch, 1*inch])
                    
                    tabla.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    
                    elementos.append(tabla)
                    elementos.append(Paragraph(f"Total: {len(productos)} productos", styles['Normal']))
                    elementos.append(Spacer(1, 20))
            
            doc.build(elementos)
            print(f"Reporte generado: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"Error al generar reporte por categoría: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generar_productos_por_vencer(self, dias: int = 30) -> str:
        """Genera reporte de productos próximos a vencer."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{self.carpeta_reportes}/por_vencer_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elementos = []
            
            elementos.extend(self._crear_encabezado(f"REPORTE DE PRODUCTOS POR VENCER (Próximos {dias} días)"))
            
            fecha_limite = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.codigo, p.nombre, c.nombre as categoria, 
                           p.stock_actual, p.unidad_medida, p.fecha_vencimiento
                    FROM productos p
                    LEFT JOIN categorias c ON p.categoria_id = c.id
                    WHERE p.activo = 1 
                    AND p.fecha_vencimiento IS NOT NULL 
                    AND DATE(p.fecha_vencimiento) <= DATE(?)
                    ORDER BY p.fecha_vencimiento ASC
                ''', (fecha_limite,))
                productos = cursor.fetchall()
            
            if not productos:
                elementos.append(Paragraph(f"No hay productos por vencer en los próximos {dias} días.", 
                                          getSampleStyleSheet()['Normal']))
            else:
                datos_tabla = [['Código', 'Producto', 'Categoría', 'Stock', 'Unidad', 'Vencimiento']]
                
                for prod in productos:
                    codigo, nombre, categoria, stock, unidad, fecha_venc = prod
                    fecha_venc_str = datetime.strptime(fecha_venc, '%Y-%m-%d').strftime('%d/%m/%Y')
                    datos_tabla.append([
                        codigo or 'N/A',
                        nombre,
                        categoria or 'Sin categoría',
                        str(stock),
                        unidad,
                        fecha_venc_str
                    ])
                
                tabla = Table(datos_tabla, colWidths=[0.8*inch, 2.2*inch, 1.5*inch, 
                                                       0.8*inch, 0.8*inch, 1.2*inch])
                
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F57C00')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF3E0')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elementos.append(tabla)
                elementos.append(Spacer(1, 20))
                elementos.append(Paragraph(f"Total de productos por vencer: {len(productos)}", 
                                          getSampleStyleSheet()['Normal']))
            
            doc.build(elementos)
            print(f"Reporte generado: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"Error al generar reporte de productos por vencer: {e}")
            import traceback
            traceback.print_exc()
            return None
