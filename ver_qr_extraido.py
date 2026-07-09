# Script para visualizar las imágenes QR extraídas
from PIL import Image
import os

# Buscar todas las imágenes temp_qr
archivos_qr = [f for f in os.listdir('.') if f.startswith('temp_qr') and f.endswith('.png')]

print(f"Archivos QR encontrados: {len(archivos_qr)}")

for archivo in sorted(archivos_qr):
    if os.path.exists(archivo):
        img = Image.open(archivo)
        print(f"\n{archivo}:")
        print(f"  Tamaño: {img.size}")
        print(f"  Modo: {img.mode}")
        print(f"  Tamaño archivo: {os.path.getsize(archivo)} bytes")
        
        # Abrir la imagen para visualizarla
        if os.path.getsize(archivo) > 1000:  # Solo abrir si tiene contenido
            img.show()
            input(f"Presiona Enter para continuar con la siguiente imagen...")
