# inventario_db.py
# Manejo de la base de datos del inventario

import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

class InventarioDB:
    def __init__(self, db_path: str = "inventario.db"):
        """Inicializa la conexión a la base de datos."""
        self.db_path = db_path
        self.crear_tablas()
    
    def crear_tablas(self):
        """Crea las tablas necesarias si no existen."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de categorías
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    descripcion TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de productos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    categoria_id INTEGER,
                    precio_compra REAL DEFAULT 0,
                    precio_venta REAL DEFAULT 0,
                    stock_actual INTEGER DEFAULT 0,
                    stock_minimo INTEGER DEFAULT 5,
                    unidad_medida TEXT DEFAULT 'Unidad',
                    fecha_vencimiento DATE,
                    proveedor TEXT,
                    alias TEXT,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
                )
            ''')
            
            # Agregar columna alias si no existe (para bases de datos existentes)
            try:
                cursor.execute('ALTER TABLE productos ADD COLUMN alias TEXT')
                print("DEBUG DB: Columna 'alias' agregada a la tabla productos")
            except sqlite3.OperationalError:
                # La columna ya existe
                pass
            
            # Tabla de movimientos de inventario
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movimientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER NOT NULL,
                    tipo_movimiento TEXT NOT NULL, -- 'ENTRADA', 'SALIDA', 'AJUSTE'
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL,
                    motivo TEXT,
                    numero_factura TEXT,
                    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usuario TEXT DEFAULT 'Sistema',
                    FOREIGN KEY (producto_id) REFERENCES productos (id)
                )
            ''')
            
            # Tabla de facturas procesadas (para evitar duplicados)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facturas_procesadas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_control TEXT UNIQUE NOT NULL,
                    codigo_generacion TEXT,
                    fecha_factura TEXT,
                    total_factura REAL,
                    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    items_procesados INTEGER DEFAULT 0
                )
            ''')
            
            print("DEBUG DB: Tabla 'facturas_procesadas' verificada/creada")
            
            # Insertar categorías por defecto
            categorias_default = [
                ('Medicamentos', 'Medicamentos veterinarios'),
                ('Vacunas', 'Vacunas para animales'),
                ('Accesorios', 'Collares, correas, juguetes'),
                ('Alimentos', 'Alimento para mascotas'),
                ('Higiene', 'Productos de limpieza y cuidado'),
                ('Otros', 'Productos varios')
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO categorias (nombre, descripcion) 
                VALUES (?, ?)
            ''', categorias_default)
            
            conn.commit()
    
    def agregar_producto(self, producto: Dict) -> int:
        """Agrega un nuevo producto al inventario."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar si el código ya existe (solo si se proporciona)
            codigo = producto.get('codigo')
            if codigo:
                cursor.execute("SELECT id FROM productos WHERE codigo = ? AND activo = 1", (codigo,))
                if cursor.fetchone():
                    raise ValueError(f"Ya existe un producto con el código '{codigo}'")
            
            cursor.execute('''
                INSERT INTO productos (
                    codigo, nombre, descripcion, categoria_id, precio_compra, 
                    precio_venta, stock_actual, stock_minimo, unidad_medida, 
                    fecha_vencimiento, proveedor
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                codigo,  # Puede ser None
                producto['nombre'],
                producto.get('descripcion', ''),
                producto.get('categoria_id'),
                producto.get('precio_compra', 0),
                producto.get('precio_venta', 0),
                producto.get('stock_actual', 0),
                producto.get('stock_minimo', 5),
                producto.get('unidad_medida', 'Unidad'),
                producto.get('fecha_vencimiento'),
                producto.get('proveedor', '')
            ))
            return cursor.lastrowid
    
    def obtener_productos(self, filtro: str = "", categoria_id: int = None) -> List[Dict]:
        """Obtiene la lista de productos con filtros opcionales."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT p.*, c.nombre as categoria_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.activo = 1
            '''
            params = []
            
            if filtro:
                query += " AND (p.nombre LIKE ? OR p.codigo LIKE ? OR p.descripcion LIKE ?)"
                filtro_param = f"%{filtro}%"
                params.extend([filtro_param, filtro_param, filtro_param])
            
            if categoria_id:
                query += " AND p.categoria_id = ?"
                params.append(categoria_id)
            
            query += " ORDER BY p.nombre"
            
            print(f"DEBUG DB: Ejecutando query: {query}")
            print(f"DEBUG DB: Con parámetros: {params}")
            
            cursor.execute(query, params)
            resultados = [dict(row) for row in cursor.fetchall()]
            
            print(f"DEBUG DB: Se encontraron {len(resultados)} productos en la base de datos")
            for producto in resultados:
                print(f"DEBUG DB: - {producto['nombre']} (ID: {producto['id']})")
            
            return resultados
    
    def obtener_producto_por_id(self, producto_id: int) -> Optional[Dict]:
        """Obtiene un producto por su ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, c.nombre as categoria_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.id = ?
            ''', (producto_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def buscar_producto_por_nombre(self, nombre: str) -> Optional[Dict]:
        """Busca un producto por nombre (para matching con facturas)."""
        max_intentos = 3
        for intento in range(max_intentos):
            try:
                with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    # Buscar coincidencia exacta primero
                    cursor.execute('''
                        SELECT * FROM productos 
                        WHERE LOWER(nombre) = LOWER(?) AND activo = 1
                    ''', (nombre,))
                    row = cursor.fetchone()
                    
                    if row:
                        return dict(row)
                    
                    # Si no hay coincidencia exacta, buscar similar
                    cursor.execute('''
                        SELECT * FROM productos 
                        WHERE LOWER(nombre) LIKE LOWER(?) AND activo = 1
                        ORDER BY LENGTH(nombre)
                        LIMIT 1
                    ''', (f"%{nombre}%",))
                    row = cursor.fetchone()
                    
                    return dict(row) if row else None
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and intento < max_intentos - 1:
                    print(f"DEBUG DB: Base de datos bloqueada en búsqueda, reintentando... (intento {intento + 1})")
                    import time
                    time.sleep(0.5)
                    continue
                else:
                    print(f"DEBUG DB: Error en búsqueda: {e}")
                    return None
            except Exception as e:
                print(f"DEBUG DB: Error inesperado en búsqueda: {e}")
                return None
        
        return None
    
    def actualizar_stock(self, producto_id: int, nueva_cantidad: int, motivo: str = "Ajuste manual") -> bool:
        """Actualiza el stock de un producto."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Obtener stock actual
            cursor.execute("SELECT stock_actual FROM productos WHERE id = ?", (producto_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            stock_anterior = row[0]
            diferencia = nueva_cantidad - stock_anterior
            
            # Actualizar stock
            cursor.execute('''
                UPDATE productos 
                SET stock_actual = ?, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (nueva_cantidad, producto_id))
            
            # Registrar movimiento
            tipo_movimiento = "ENTRADA" if diferencia > 0 else "SALIDA" if diferencia < 0 else "AJUSTE"
            self.registrar_movimiento(
                producto_id, tipo_movimiento, abs(diferencia), motivo=motivo
            )
            
            return True
    
    def descontar_stock(self, producto_id: int, cantidad: int, numero_factura: str = "") -> bool:
        """Descuenta stock de un producto (por venta)."""
        max_intentos = 3
        for intento in range(max_intentos):
            try:
                with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                    cursor = conn.cursor()
                    
                    # Verificar stock disponible
                    cursor.execute("SELECT stock_actual FROM productos WHERE id = ?", (producto_id,))
                    row = cursor.fetchone()
                    if not row or row[0] < cantidad:
                        return False
                    
                    # Descontar stock
                    nuevo_stock = row[0] - cantidad
                    cursor.execute('''
                        UPDATE productos 
                        SET stock_actual = ?, fecha_modificacion = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (nuevo_stock, producto_id))
                    
                    # Registrar movimiento
                    cursor.execute('''
                        INSERT INTO movimientos (
                            producto_id, tipo_movimiento, cantidad, precio_unitario, 
                            motivo, numero_factura
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (producto_id, "SALIDA", cantidad, None, "Venta", numero_factura))
                    
                    conn.commit()
                    return True
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and intento < max_intentos - 1:
                    print(f"DEBUG DB: Base de datos bloqueada, reintentando... (intento {intento + 1})")
                    import time
                    time.sleep(0.5)  # Esperar medio segundo antes de reintentar
                    continue
                else:
                    print(f"DEBUG DB: Error en base de datos: {e}")
                    return False
            except Exception as e:
                print(f"DEBUG DB: Error inesperado: {e}")
                return False
        
        return False
    
    def registrar_movimiento(self, producto_id: int, tipo: str, cantidad: int, 
                           precio_unitario: float = None, motivo: str = "", 
                           numero_factura: str = ""):
        """Registra un movimiento de inventario."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO movimientos (
                    producto_id, tipo_movimiento, cantidad, precio_unitario, 
                    motivo, numero_factura
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (producto_id, tipo, cantidad, precio_unitario, motivo, numero_factura))
    
    def obtener_categorias(self) -> List[Dict]:
        """Obtiene todas las categorías."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categorias ORDER BY nombre")
            return [dict(row) for row in cursor.fetchall()]
    
    def obtener_productos_stock_bajo(self) -> List[Dict]:
        """Obtiene productos con stock por debajo del mínimo."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, c.nombre as categoria_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.stock_actual <= p.stock_minimo AND p.activo = 1
                ORDER BY (p.stock_actual - p.stock_minimo), p.nombre
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def obtener_productos_por_vencer(self, dias: int = 30) -> List[Dict]:
        """Obtiene productos que vencen en los próximos X días."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, c.nombre as categoria_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.fecha_vencimiento IS NOT NULL 
                AND p.fecha_vencimiento <= date('now', '+' || ? || ' days')
                AND p.activo = 1
                ORDER BY p.fecha_vencimiento
            ''', (dias,))
            return [dict(row) for row in cursor.fetchall()]
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas generales del inventario."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total de productos
            cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
            total_productos = cursor.fetchone()[0]
            
            # Productos con stock bajo
            cursor.execute('''
                SELECT COUNT(*) FROM productos 
                WHERE stock_actual <= stock_minimo AND activo = 1
            ''')
            productos_stock_bajo = cursor.fetchone()[0]
            
            # Valor total del inventario
            cursor.execute('''
                SELECT SUM(stock_actual * precio_compra) 
                FROM productos WHERE activo = 1
            ''')
            valor_inventario = cursor.fetchone()[0] or 0
            
            # Productos por vencer (30 días)
            cursor.execute('''
                SELECT COUNT(*) FROM productos 
                WHERE fecha_vencimiento IS NOT NULL 
                AND fecha_vencimiento <= date('now', '+30 days')
                AND activo = 1
            ''')
            productos_por_vencer = cursor.fetchone()[0]
            
            return {
                'total_productos': total_productos,
                'productos_stock_bajo': productos_stock_bajo,
                'valor_inventario': valor_inventario,
                'productos_por_vencer': productos_por_vencer
            }
    
    def eliminar_producto(self, producto_id: int) -> bool:
            """Elimina un producto (marca como inactivo)."""
            try:
                with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                    cursor = conn.cursor()

                    # Obtener nombre del producto antes de marcarlo como inactivo
                    cursor.execute("SELECT nombre FROM productos WHERE id = ?", (producto_id,))
                    row = cursor.fetchone()

                    if not row:
                        print(f"DEBUG DB: Producto con ID {producto_id} no encontrado")
                        return False

                    nombre_producto = row[0]

                    # Marcar como inactivo en lugar de eliminar físicamente
                    cursor.execute('''
                        UPDATE productos 
                        SET activo = 0, fecha_modificacion = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (producto_id,))

                    # Registrar movimiento de eliminación en la misma transacción
                    cursor.execute('''
                        INSERT INTO movimientos (
                            producto_id, tipo_movimiento, cantidad, precio_unitario, 
                            motivo, numero_factura
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (producto_id, "AJUSTE", 0, None, f"Producto eliminado: {nombre_producto}", ""))

                    conn.commit()
                    print(f"DEBUG DB: Producto {nombre_producto} eliminado correctamente")
                    return cursor.rowcount > 0

            except Exception as e:
                print(f"DEBUG DB: Error al eliminar producto: {e}")
                import traceback
                traceback.print_exc()
                return False

    
    def actualizar_producto(self, producto_id: int, datos_producto: Dict) -> bool:
        """Actualiza un producto existente."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar si el código ya existe en otro producto (solo si se proporciona)
                codigo = datos_producto.get('codigo')
                if codigo:
                    cursor.execute(
                        "SELECT id FROM productos WHERE codigo = ? AND id != ? AND activo = 1", 
                        (codigo, producto_id)
                    )
                    if cursor.fetchone():
                        raise ValueError(f"Ya existe otro producto con el código '{codigo}'")
                
                cursor.execute('''
                    UPDATE productos SET
                        codigo = ?, nombre = ?, descripcion = ?, categoria_id = ?,
                        precio_compra = ?, precio_venta = ?, stock_actual = ?,
                        stock_minimo = ?, unidad_medida = ?, fecha_vencimiento = ?,
                        proveedor = ?, fecha_modificacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    codigo,
                    datos_producto['nombre'],
                    datos_producto.get('descripcion', ''),
                    datos_producto.get('categoria_id'),
                    datos_producto.get('precio_compra', 0),
                    datos_producto.get('precio_venta', 0),
                    datos_producto.get('stock_actual', 0),
                    datos_producto.get('stock_minimo', 5),
                    datos_producto.get('unidad_medida', 'Unidad'),
                    datos_producto.get('fecha_vencimiento'),
                    datos_producto.get('proveedor', ''),
                    producto_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except ValueError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            print(f"DEBUG DB: Error al actualizar producto: {e}")
            return False

    def factura_ya_procesada(self, numero_control: str) -> bool:
        """
        Verifica si una factura ya fue procesada anteriormente.
        
        Args:
            numero_control: Número de control de la factura (DTE)
            
        Returns:
            True si ya fue procesada, False si no
        """
        try:
            with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, fecha_procesamiento 
                    FROM facturas_procesadas 
                    WHERE numero_control = ?
                ''', (numero_control,))
                
                resultado = cursor.fetchone()
                
                if resultado:
                    print(f"⚠️ FACTURA YA PROCESADA: {numero_control}")
                    print(f"   Fecha de procesamiento anterior: {resultado[1]}")
                    return True
                
                return False
                
        except Exception as e:
            print(f"ERROR al verificar factura procesada: {e}")
            return False
    
    def registrar_factura_procesada(self, numero_control: str, codigo_generacion: str = None, 
                                   fecha_factura: str = None, total_factura: float = 0, 
                                   items_procesados: int = 0) -> bool:
        """
        Registra una factura como procesada para evitar duplicados.
        
        Args:
            numero_control: Número de control de la factura (DTE)
            codigo_generacion: Código de generación de la factura
            fecha_factura: Fecha de la factura
            total_factura: Total de la factura
            items_procesados: Cantidad de items procesados
            
        Returns:
            True si se registró correctamente, False si hubo error
        """
        try:
            with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO facturas_procesadas 
                    (numero_control, codigo_generacion, fecha_factura, total_factura, items_procesados)
                    VALUES (?, ?, ?, ?, ?)
                ''', (numero_control, codigo_generacion, fecha_factura, total_factura, items_procesados))
                
                conn.commit()
                print(f"✓ Factura registrada como procesada: {numero_control}")
                return True
                
        except sqlite3.IntegrityError:
            print(f"⚠️ La factura {numero_control} ya estaba registrada")
            return False
        except Exception as e:
            print(f"ERROR al registrar factura procesada: {e}")
            return False
    
    def obtener_facturas_procesadas(self, limite: int = 50) -> List[Dict]:
        """
        Obtiene la lista de facturas procesadas recientemente.
        
        Args:
            limite: Cantidad máxima de facturas a retornar
            
        Returns:
            Lista de facturas procesadas
        """
        try:
            with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT numero_control, codigo_generacion, fecha_factura, 
                           total_factura, fecha_procesamiento, items_procesados
                    FROM facturas_procesadas
                    ORDER BY fecha_procesamiento DESC
                    LIMIT ?
                ''', (limite,))
                
                facturas = []
                for row in cursor.fetchall():
                    facturas.append({
                        'numero_control': row[0],
                        'codigo_generacion': row[1],
                        'fecha_factura': row[2],
                        'total_factura': row[3],
                        'fecha_procesamiento': row[4],
                        'items_procesados': row[5]
                    })
                
                return facturas
                
        except Exception as e:
            print(f"ERROR al obtener facturas procesadas: {e}")
            return []
    
    def limpiar_facturas_procesadas(self) -> bool:
        """
        Limpia todas las facturas procesadas de la base de datos.
        Útil para reprocesar facturas sin restricciones de duplicados.
        
        Returns:
            bool: True si se limpiaron correctamente, False en caso de error
        """
        try:
            with sqlite3.connect(self.db_path, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM facturas_procesadas')
                conn.commit()
                filas_eliminadas = cursor.rowcount
                print(f"✓ Se eliminaron {filas_eliminadas} facturas procesadas de la base de datos")
                return True
        except Exception as e:
            print(f"❌ Error al limpiar facturas procesadas: {e}")
            return False
    
    def eliminar_factura_procesada(self, numero_control: str) -> bool:
        """
        Elimina una factura específica de las procesadas.
        Útil para reprocesar una factura individual.
        
        Args:
            numero_control: Número de control de la factura a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso de error
        """
        try:
            with sqlite3.connect(self.db_path, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM facturas_procesadas WHERE numero_control = ?', (numero_control,))
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"✓ Factura {numero_control} eliminada del registro de procesadas")
                    return True
                else:
                    print(f"⚠️ No se encontró la factura {numero_control} en el registro")
                    return False
        except Exception as e:
            print(f"❌ Error al eliminar factura procesada: {e}")
            return False

    def limpiar_facturas_procesadas(self) -> bool:
        """
        Limpia todas las facturas procesadas de la base de datos.
        Útil para reprocesar facturas sin restricciones de duplicados.

        Returns:
            bool: True si se limpiaron correctamente, False en caso de error
        """
        try:
            with sqlite3.connect(self.db_path, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM facturas_procesadas')
                conn.commit()
                filas_eliminadas = cursor.rowcount
                print(f"✓ Se eliminaron {filas_eliminadas} facturas procesadas de la base de datos")
                return True
        except Exception as e:
            print(f"❌ Error al limpiar facturas procesadas: {e}")
            return False

    def eliminar_factura_procesada(self, numero_control: str) -> bool:
        """
        Elimina una factura específica de las procesadas.
        Útil para reprocesar una factura individual.

        Args:
            numero_control: Número de control de la factura a eliminar

        Returns:
            bool: True si se eliminó correctamente, False en caso de error
        """
        try:
            with sqlite3.connect(self.db_path, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM facturas_procesadas WHERE numero_control = ?', (numero_control,))
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"✓ Factura {numero_control} eliminada del registro de procesadas")
                    return True
                else:
                    print(f"⚠️ No se encontró la factura {numero_control} en el registro")
                    return False
        except Exception as e:
            print(f"❌ Error al eliminar factura procesada: {e}")
            return False

