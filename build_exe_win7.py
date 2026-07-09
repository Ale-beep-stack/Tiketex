# build_exe_win7.py
# Script para construir el ejecutable compatible con Windows 7 32 bits

import PyInstaller.__main__
import os

print("Construyendo ejecutable compatible con Windows 7 32 bits...")
print("IMPORTANTE: Debes ejecutar esto en Python 32 bits en Windows 7 o con compatibilidad")

# Configuración para Windows 7 32 bits
PyInstaller.__main__.run([
    'main.py',
    '--name=GeneradorTickets',
    '--onefile',
    '--windowed',
    '--icon=disenos/raffle-ticket-blue.ico',
    '--add-data=disenos;disenos',
    '--add-data=settings.py;.',
    '--add-data=estilos.py;.',
    '--add-data=extractor.py;.',
    '--add-data=ticket_genrator.py;.',
    '--hidden-import=PIL',
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=reportlab',
    '--hidden-import=PyPDF2',
    '--hidden-import=fitz',
    '--hidden-import=frontend',
    '--hidden-import=babel.numbers',
    '--hidden-import=tkcalendar',
    '--target-arch=x86',  # Forzar 32 bits
    '--clean',
    '--noconfirm',
    # Opciones adicionales para compatibilidad con Windows 7
    '--noupx',  # Desactivar UPX que puede causar problemas en Win7
])

print("\n✓ Ejecutable para Windows 7 32 bits creado!")
print("Busca 'GeneradorTickets.exe' en la carpeta 'dist'")
