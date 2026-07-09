"""
Script para crear un paquete completo de distribución del programa.
Genera el .exe y copia todos los archivos necesarios en una carpeta lista para distribuir.
"""
import PyInstaller.__main__
import os
import shutil
from pathlib import Path

print("=" * 60)
print("CREANDO PAQUETE DE DISTRIBUCIÓN")
print("=" * 60)

# Paso 1: Generar el ejecutable
print("\n[1/3] Generando ejecutable...")
PyInstaller.__main__.run([
    'main.py',
    '--name=GeneradorTickets',
    '--onefile',
    '--windowed',
    '--icon=disenos/raffle-ticket-blue.ico',
    '--add-data=disenos;disenos',
    '--hidden-import=PIL',
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=reportlab',
    '--hidden-import=PyPDF2',
    '--hidden-import=fitz',
    '--hidden-import=frontend',
    '--hidden-import=babel.numbers',
    '--hidden-import=tkcalendar',
    '--clean',
    '--noconfirm',
])

# Paso 2: Crear carpeta de distribución
print("\n[2/3] Creando carpeta de distribución...")
carpeta_dist = Path("Distribucion_GeneradorTickets")

# Limpiar carpeta si existe
if carpeta_dist.exists():
    shutil.rmtree(carpeta_dist)

carpeta_dist.mkdir()

# Copiar el ejecutable
shutil.copy("dist/GeneradorTickets.exe", carpeta_dist / "GeneradorTickets.exe")
print("  ✓ Ejecutable copiado")

# Copiar carpeta de diseños
shutil.copytree("disenos", carpeta_dist / "disenos")
print("  ✓ Carpeta 'disenos' copiada")

# Crear carpetas que se generarán automáticamente (opcional)
(carpeta_dist / "tickets_generados").mkdir()
(carpeta_dist / "reportes_generados").mkdir()
print("  ✓ Carpetas de salida creadas")

# Copiar emisores.json si existe
if os.path.exists("emisores.json"):
    shutil.copy("emisores.json", carpeta_dist / "emisores.json")
    print("  ✓ emisores.json copiado")

# Copiar base de datos si existe
if os.path.exists("inventario.db"):
    shutil.copy("inventario.db", carpeta_dist / "inventario.db")
    print("  ✓ inventario.db copiado")

# Paso 3: Crear archivo README
print("\n[3/3] Creando archivo de instrucciones...")
readme_content = """
╔══════════════════════════════════════════════════════════════╗
║          GENERADOR DE TICKETS - INSTRUCCIONES               ║
╔══════════════════════════════════════════════════════════════╗

📋 CONTENIDO DEL PAQUETE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ GeneradorTickets.exe    - Programa principal
✓ disenos/                - Imágenes y recursos gráficos
✓ tickets_generados/      - Carpeta donde se guardan los tickets
✓ reportes_generados/     - Carpeta donde se guardan los reportes
✓ emisores.json           - Configuración de emisores (se crea automáticamente)
✓ inventario.db           - Base de datos del inventario (se crea automáticamente)


🚀 INSTALACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Copia TODA esta carpeta a la ubicación deseada
2. Haz doble clic en GeneradorTickets.exe
3. ¡Listo para usar!


⚠️ IMPORTANTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• NO muevas el .exe fuera de esta carpeta
• NO elimines la carpeta "disenos"
• Mantén todos los archivos juntos en la misma carpeta


📦 REQUISITOS DEL SISTEMA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Windows 7 o superior (32/64 bits)
• 100 MB de espacio en disco
• No requiere instalación de Python


💡 USO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PANTALLA DE TICKETS:
  1. Selecciona o agrega un emisor
  2. Carga una factura PDF
  3. El ticket se genera automáticamente
  4. Imprime o guarda el ticket

PANTALLA DE INVENTARIO:
  1. Gestiona productos y categorías
  2. Controla stock y movimientos
  3. Recibe alertas de stock bajo
  4. Genera reportes detallados

PANTALLA DE REPORTES:
  1. Selecciona el tipo de reporte
  2. Configura fechas si es necesario
  3. Genera el PDF
  4. Abre y visualiza el reporte


📞 SOPORTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para soporte técnico o consultas, contacta al desarrollador.


═══════════════════════════════════════════════════════════════
Versión: 1.0.0
Desarrollado con Python, Tkinter y ReportLab
═══════════════════════════════════════════════════════════════
"""

with open(carpeta_dist / "LEEME.txt", "w", encoding="utf-8") as f:
    f.write(readme_content)
print("  ✓ Archivo LEEME.txt creado")

# Resumen final
print("\n" + "=" * 60)
print("✓ PAQUETE DE DISTRIBUCIÓN CREADO EXITOSAMENTE")
print("=" * 60)
print(f"\n📁 Ubicación: {carpeta_dist.absolute()}")
print("\n📦 Contenido:")
print("  • GeneradorTickets.exe")
print("  • disenos/ (carpeta con imágenes)")
print("  • tickets_generados/ (carpeta de salida)")
print("  • reportes_generados/ (carpeta de salida)")
print("  • LEEME.txt (instrucciones)")
if os.path.exists("emisores.json"):
    print("  • emisores.json")
if os.path.exists("inventario.db"):
    print("  • inventario.db")

print("\n" + "=" * 60)
print("PARA DISTRIBUIR:")
print("  1. Comprime la carpeta 'Distribucion_GeneradorTickets'")
print("  2. Envía el archivo .zip a los usuarios")
print("  3. Los usuarios deben extraer TODO el contenido")
print("  4. Ejecutar GeneradorTickets.exe")
print("=" * 60)
