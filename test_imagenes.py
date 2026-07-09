from PIL import Image
import numpy as np

# Analizar las imágenes
imagenes = ["disenos/botonmas.png", "disenos/botoneditar.png", "disenos/botonmenos.png"]

for img_path in imagenes:
    print(f"\n=== Analizando {img_path} ===")
    img = Image.open(img_path)
    print(f"Modo: {img.mode}")
    print(f"Tamaño: {img.size}")
    
    # Convertir a RGBA si no lo es
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    # Obtener datos
    data = np.array(img)
    
    # Analizar colores únicos
    print(f"Shape: {data.shape}")
    
    # Ver los colores en las esquinas (donde suelen estar los bordes blancos)
    print(f"Esquina superior izquierda (0,0): {data[0, 0]}")
    print(f"Esquina superior derecha (0,-1): {data[0, -1]}")
    print(f"Esquina inferior izquierda (-1,0): {data[-1, 0]}")
    print(f"Esquina inferior derecha (-1,-1): {data[-1, -1]}")
    
    # Contar píxeles blancos
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    blancos = np.sum((r > 200) & (g > 200) & (b > 200))
    total = data.shape[0] * data.shape[1]
    print(f"Píxeles blancos/claros: {blancos} de {total} ({blancos/total*100:.2f}%)")
