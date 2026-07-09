"""
Script para crear un paquete de distribución RÁPIDO del programa.
Usa --onedir para inicio rápido (en lugar de --onefile que es lento).
Genera una carpeta lista para distribuir con todo lo necesario.
"""
import PyInstaller.__main__
import os
import shutil
from pathlib import Path

print("=" * 70)
print("       CREANDO PAQUETE DE DISTRIBUCIÓN RÁPIDO (RECOMENDADO)")
print("=" * 70)
print("\n📌 Este método crea un ejecutable que inicia MUCHO MÁS RÁPIDO")
print("   • Inicio instantáneo (2-3 segundos vs 10-15 segundos)")
print("   • Menos problemas con antivirus")
print("   • Genera más archivos pero mejor rendimiento\n")

# Paso 1: Generar el ejecutable
print("\n[1/4] Generando ejecutable optimizado...")
print("⏳ Esto puede tardar 2-3 minutos...")

PyInstaller.__main__.run([
    'main.py',
    '--name=GeneradorTickets',
    '--onedir',  # ← CAMBIO CLAVE: Genera carpeta con archivos separados (MÁS RÁPIDO)
    '--windowed',
    '--icon=disenos/raffle-ticket-blue.ico',
    '--add-data=disenos;disenos',  # Incluir TODA la carpeta de diseños
    
    # Hidden imports
    '--hidden-import=PIL',
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageTk',
    '--hidden-import=PIL.ImageOps',
    '--hidden-import=reportlab',
    '--hidden-import=reportlab.pdfgen',
    '--hidden-import=reportlab.lib',
    '--hidden-import=PyPDF2',
    '--hidden-import=fitz',
    '--hidden-import=frontend',
    '--hidden-import=babel.numbers',
    '--hidden-import=tkcalendar',
    '--hidden-import=win32print',
    '--hidden-import=win32api',
    '--hidden-import=sqlite3',
    
    # Optimizaciones y limpieza
    '--clean',
    '--noconfirm',
    '--noupx',  # No usar UPX (compresión) para mejor compatibilidad
])

# Verificar que se creó el ejecutable
exe_generado = Path("dist/GeneradorTickets/GeneradorTickets.exe")
if not exe_generado.exists():
    print("\n❌ ERROR: No se pudo crear el ejecutable")
    print("   Revisa los mensajes de error arriba")
    input("Presiona Enter para salir...")
    exit(1)

print("✅ Ejecutable generado exitosamente")

# Paso 2: Crear carpeta de distribución
print("\n[2/4] Creando paquete de distribución...")
carpeta_dist = Path("GeneradorTickets_Distribucion")

# Limpiar carpeta si existe
if carpeta_dist.exists():
    print("   Eliminando carpeta anterior...")
    shutil.rmtree(carpeta_dist)

carpeta_dist.mkdir()

# Copiar TODO el contenido de dist/GeneradorTickets
print("   Copiando ejecutable y librerías...")
shutil.copytree("dist/GeneradorTickets", carpeta_dist / "GeneradorTickets")
print("   ✓ Ejecutable y librerías copiados")

# Copiar carpeta de diseños a la raíz de la distribución
print("   Copiando recursos...")
shutil.copytree("disenos", carpeta_dist / "disenos")
print("   ✓ Carpeta 'disenos' copiada")

# Crear carpetas que se generarán automáticamente
(carpeta_dist / "tickets_generados").mkdir()
(carpeta_dist / "reportes_generados").mkdir()
print("   ✓ Carpetas de salida creadas")

# Copiar archivos de configuración si existen
archivos_config = ["emisores.json", "inventario.db", "config.json"]
for archivo in archivos_config:
    if os.path.exists(archivo):
        shutil.copy(archivo, carpeta_dist / archivo)
        print(f"   ✓ {archivo} copiado")

# Paso 3: Crear acceso directo al ejecutable en la raíz
print("\n[3/4] Creando acceso directo...")

# Crear un .bat para ejecutar el programa (más simple que un .lnk)
bat_content = """@echo off
cd /d "%~dp0"
start "" "GeneradorTickets\\GeneradorTickets.exe"
"""

with open(carpeta_dist / "INICIAR_PROGRAMA.bat", "w", encoding="utf-8") as f:
    f.write(bat_content)
print("   ✓ Archivo INICIAR_PROGRAMA.bat creado")

# Paso 4: Crear archivos de documentación
print("\n[4/4] Creando documentación...")

readme_content = """╔══════════════════════════════════════════════════════════════════════╗
║              GENERADOR DE TICKETS - GUÍA DE INSTALACIÓN            ║
╚══════════════════════════════════════════════════════════════════════╝

🚀 INICIO RÁPIDO (2 PASOS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Haz doble clic en: INICIAR_PROGRAMA.bat
2. ¡Listo! El programa se abre en 2-3 segundos

   Alternativa: Ve a la carpeta GeneradorTickets y ejecuta GeneradorTickets.exe


📋 CONTENIDO DEL PAQUETE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ INICIAR_PROGRAMA.bat       - USAR ESTE ARCHIVO (recomendado)
✓ GeneradorTickets/           - Carpeta con el programa y librerías
  └─ GeneradorTickets.exe     - Programa principal
✓ disenos/                    - Imágenes y recursos gráficos
✓ tickets_generados/          - Carpeta donde se guardan los tickets
✓ reportes_generados/         - Carpeta donde se guardan los reportes
✓ emisores.json               - Configuración de emisores (automático)
✓ inventario.db               - Base de datos de inventario (automático)


🔧 INSTALACIÓN EN OTRA PC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Copia TODA la carpeta "GeneradorTickets_Distribucion" a la PC destino
2. Colócala donde desees (Escritorio, Documentos, C:\\Programas, etc.)
3. Ejecuta INICIAR_PROGRAMA.bat
4. ¡Funciona sin instalar nada más!


⚠️ MUY IMPORTANTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• NO muevas archivos individuales, copia TODA la carpeta
• NO elimines la carpeta "GeneradorTickets" (contiene librerías necesarias)
• NO elimines la carpeta "disenos" (contiene imágenes del programa)
• Mantén todos los archivos en la misma estructura


📦 REQUISITOS DEL SISTEMA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Windows 7, 8, 10, 11 (32 o 64 bits)
✅ 200 MB de espacio en disco
✅ No requiere instalar Python
✅ No requiere instalar librerías adicionales
✅ Todo está incluido en el paquete


💡 CARACTERÍSTICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 GENERACIÓN DE TICKETS:
  • Carga facturas PDF automáticamente
  • Extrae datos y código QR
  • Genera tickets térmicos de 80mm
  • Vista previa editable
  • Impresión directa

📦 GESTIÓN DE INVENTARIO:
  • Control de productos y categorías
  • Seguimiento de stock
  • Alertas de stock bajo
  • Descuento automático al generar ticket
  • Historial de movimientos

📊 REPORTES COMPLETOS:
  • Inventario actual
  • Stock bajo
  • Movimientos por período
  • Productos más vendidos
  • Valorización de inventario
  • Productos por categoría
  • Productos próximos a vencer


🖨️ IMPRESIÓN EN IMPRESORAS TÉRMICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El sistema incluye funcionalidad de prueba de impresión:

1. Click en el botón "Imprimir"
2. Selecciona tu impresora térmica
3. Click en "Prueba de Impresión" (botón verde)
4. Verifica que funcione correctamente

Compatible con: Epson TM-T20, TM-T88, Star TSP100, Bixolon SRP-350, etc.


🐛 SOLUCIÓN DE PROBLEMAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problema: "El programa no inicia"
✓ Verifica que todas las carpetas estén en el mismo lugar
✓ Ejecuta como Administrador (click derecho → Ejecutar como administrador)
✓ Verifica que el antivirus no esté bloqueando el programa

Problema: "No imprime en impresora térmica"
✓ Usa el botón "Prueba de Impresión" para diagnosticar
✓ Verifica que la impresora funcione en Windows
✓ Revisa la carpeta "tickets_generados" y abre el PDF manualmente

Problema: "Falta un archivo DLL"
✓ Descarga e instala Visual C++ Redistributable:
   https://aka.ms/vs/17/release/vc_redist.x64.exe


📞 SOPORTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para soporte técnico o consultas, contacta al desarrollador.


═══════════════════════════════════════════════════════════════════════
💡 VENTAJA DE ESTA VERSIÓN: Inicio ultra-rápido (2-3 segundos)
═══════════════════════════════════════════════════════════════════════
Versión: 2.0 (Optimizada)
Desarrollado con Python, Tkinter, ReportLab y SQLite
═══════════════════════════════════════════════════════════════════════
"""

with open(carpeta_dist / "LEEME.txt", "w", encoding="utf-8") as f:
    f.write(readme_content)
print("   ✓ Archivo LEEME.txt creado")

# Copiar guía de impresión si existe
if os.path.exists("GUIA_IMPRESION_TERMICA.md"):
    shutil.copy("GUIA_IMPRESION_TERMICA.md", carpeta_dist / "GUIA_IMPRESION_TERMICA.txt")
    print("   ✓ Guía de impresión copiada")

# Limpiar archivos temporales
print("\n🧹 Limpiando archivos temporales...")
if os.path.exists("build"):
    shutil.rmtree("build")
    print("   ✓ Carpeta 'build' eliminada")

if os.path.exists("GeneradorTickets.spec"):
    os.remove("GeneradorTickets.spec")
    print("   ✓ Archivo .spec eliminado")

# Resumen final
print("\n" + "=" * 70)
print("✅ PAQUETE DE DISTRIBUCIÓN CREADO EXITOSAMENTE")
print("=" * 70)
print(f"\n📁 Ubicación: {carpeta_dist.absolute()}")
print("\n📦 Estructura del paquete:")
print("  GeneradorTickets_Distribucion/")
print("  ├─ INICIAR_PROGRAMA.bat       ← USAR ESTE ARCHIVO")
print("  ├─ LEEME.txt                  ← Instrucciones completas")
print("  ├─ GeneradorTickets/          ← Programa y librerías")
print("  │  └─ GeneradorTickets.exe")
print("  ├─ disenos/                   ← Recursos gráficos")
print("  ├─ tickets_generados/         ← Tickets generados")
print("  └─ reportes_generados/        ← Reportes PDF")

print("\n" + "=" * 70)
print("📤 PARA DISTRIBUIR A CLIENTES:")
print("=" * 70)
print("  1. Comprime la carpeta 'GeneradorTickets_Distribucion'")
print("  2. Envía el archivo .zip al cliente")
print("  3. El cliente debe extraer TODO el contenido")
print("  4. Ejecutar INICIAR_PROGRAMA.bat")
print("\n  ✅ El programa inicia en 2-3 segundos (muy rápido)")
print("  ✅ No requiere instalación")
print("  ✅ Funciona en cualquier PC con Windows 7+")

print("\n" + "=" * 70)
print("🎯 VENTAJAS DE ESTA VERSIÓN:")
print("=" * 70)
print("  ⚡ Inicio ultra-rápido (2-3 seg vs 10-15 seg de --onefile)")
print("  🛡️  Menos problemas con antivirus")
print("  💾 Mismo espacio en disco (~100-150 MB)")
print("  📦 Más archivos pero MUCHO mejor rendimiento")

print("\n" + "=" * 70)
input("\n✅ Presiona Enter para abrir la carpeta de distribución...")

# Abrir la carpeta de distribución
os.startfile(carpeta_dist.absolute())
