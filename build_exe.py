# build_exe.py
# Script para construir el ejecutable del Generador de Tickets

import PyInstaller.__main__
import os

# Configuración para el ejecutable
PyInstaller.__main__.run([
    'main.py',                          # Archivo principal
    '--name=GeneradorTickets',          # Nombre del ejecutable
    '--onefile',                        # Un solo archivo ejecutable
    '--windowed',                       # Sin consola (interfaz gráfica)
    '--icon=disenos/raffle-ticket-blue.png',  # Icono del ejecutable
    '--add-data=disenos;disenos',       # Incluir carpeta de diseños
    '--add-data=settings.py;.',         # Incluir settings
    '--add-data=estilos.py;.',          # Incluir estilos
    '--add-data=extractor.py;.',        # Incluir extractor
    '--add-data=ticket_genrator.py;.',  # Incluir generador de tickets
    '--hidden-import=PIL',              # Importaciones ocultas
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=reportlab',
    '--hidden-import=PyPDF2',
    '--hidden-import=fitz',             # PyMuPDF
    '--hidden-import=frontend',         # PyMuPDF frontend
    '--clean',                          # Limpiar cache antes de construir
    '--noconfirm',                      # No pedir confirmación
])

print("\n✓ Ejecutable creado exitosamente!")
print("Busca el archivo 'GeneradorTickets.exe' en la carpeta 'dist'")
