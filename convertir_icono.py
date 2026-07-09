# convertir_icono.py
# Convierte la imagen PNG a formato ICO para el ejecutable

from PIL import Image
import os

# Ruta de la imagen PNG
png_path = os.path.join("disenos", "raffle-ticket-blue.png")
ico_path = os.path.join("disenos", "raffle-ticket-blue.ico")

try:
    # Abrir la imagen PNG
    img = Image.open(png_path)
    
    # Convertir a ICO con múltiples tamaños
    # Windows usa diferentes tamaños según el contexto
    img.save(ico_path, format='ICO', sizes=[
        (16, 16),   # Tamaño pequeño
        (32, 32),   # Tamaño mediano
        (48, 48),   # Tamaño grande
        (64, 64),   # Tamaño extra grande
        (128, 128), # Tamaño muy grande
        (256, 256)  # Tamaño máximo
    ])
    
    print(f"✓ Icono convertido exitosamente!")
    print(f"  Archivo creado: {ico_path}")
    print(f"\nAhora puedes ejecutar:")
    print(f"  python build_exe.py")
    
except Exception as e:
    print(f"✗ Error al convertir el icono: {e}")
    print(f"\nIntenta instalar Pillow:")
    print(f"  pip install pillow")
