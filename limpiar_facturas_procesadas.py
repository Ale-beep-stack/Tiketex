"""
Script para limpiar el registro de facturas procesadas.
Permite reprocesar PDFs sin el mensaje de duplicados.
"""

from inventario_db import InventarioDB

def main():
    print("=" * 60)
    print("LIMPIEZA DE FACTURAS PROCESADAS")
    print("=" * 60)
    print()
    
    db = InventarioDB()
    
    # Mostrar facturas actuales
    facturas = db.obtener_facturas_procesadas(100)
    print(f"Facturas procesadas actualmente: {len(facturas)}")
    
    if facturas:
        print("\nÚltimas 5 facturas:")
        for i, f in enumerate(facturas[:5], 1):
            print(f"  {i}. {f['numero_control']} - {f['fecha_procesamiento']}")
    
    print("\n" + "=" * 60)
    print("OPCIONES:")
    print("1. Limpiar TODAS las facturas procesadas")
    print("2. Eliminar una factura específica")
    print("3. Cancelar")
    print("=" * 60)
    
    opcion = input("\nSelecciona una opción (1-3): ").strip()
    
    if opcion == "1":
        confirmacion = input("\n⚠️ ¿Estás seguro de eliminar TODAS las facturas? (si/no): ").strip().lower()
        if confirmacion == "si":
            if db.limpiar_facturas_procesadas():
                print("\n✅ Base de datos limpiada. Ahora puedes reprocesar los PDFs.")
            else:
                print("\n❌ Error al limpiar la base de datos.")
        else:
            print("\n❌ Operación cancelada.")
    
    elif opcion == "2":
        numero_control = input("\nIngresa el número de control de la factura: ").strip()
        if numero_control:
            if db.eliminar_factura_procesada(numero_control):
                print(f"\n✅ Factura {numero_control} eliminada. Ahora puedes reprocesarla.")
            else:
                print(f"\n❌ No se pudo eliminar la factura.")
        else:
            print("\n❌ Número de control vacío.")
    
    else:
        print("\n❌ Operación cancelada.")
    
    print()

if __name__ == "__main__":
    main()
