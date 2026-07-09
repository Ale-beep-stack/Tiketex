# Script para encontrar el QR en el PDF
# Este script renderiza el PDF y te muestra dónde buscar el QR

import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io
import sys

def encontrar_qr_en_pdf(pdf_path):
    """Renderiza el PDF y muestra las áreas donde se busca el QR"""
    
    pdf_document = fitz.open(pdf_path)
    page = pdf_document[0]
    
    # Renderizar a alta resolución
    mat = fitz.Matrix(4, 4)
    pix = page.get_pixmap(matrix=mat)
    
    # Convertir a PIL Image
    img_data = pix.tobytes("png")
    full_image = Image.open(io.BytesIO(img_data))
    
    print(f"Tamaño de la página renderizada: {full_image.size}")
    
    # Crear una copia para dibujar las áreas de búsqueda
    img_con_areas = full_image.copy()
    draw = ImageDraw.Draw(img_con_areas)
    
    width, height = full_image.size
    
    # Definir las áreas de búsqueda
    areas_busqueda = [
        ("Superior derecha", int(width * 0.60), int(height * 0.02), int(width * 0.98), int(height * 0.30)),
        ("Superior centro-derecha", int(width * 0.45), int(height * 0.02), int(width * 0.75), int(height * 0.30)),
        ("Superior centro", int(width * 0.30), int(height * 0.02), int(width * 0.60), int(height * 0.30)),
        ("Superior izquierda", int(width * 0.02), int(height * 0.02), int(width * 0.35), int(height * 0.30)),
    ]
    
    # Colores para cada área
    colores = ["red", "blue", "green", "yellow"]
    
    # Dibujar rectángulos en cada área
    for idx, (nombre, x1, y1, x2, y2) in enumerate(areas_busqueda):
        color = colores[idx % len(colores)]
        draw.rectangle([x1, y1, x2, y2], outline=color, width=10)
        print(f"Área {idx+1} ({nombre}): ({x1}, {y1}) a ({x2}, {y2}) - Color: {color}")
        
        # Extraer y guardar cada área
        area_img = full_image.crop((x1, y1, x2, y2))
        area_img.save(f"area_{idx+1}_{nombre.replace(' ', '_')}.png")
        print(f"  Guardada como: area_{idx+1}_{nombre.replace(' ', '_')}.png")
    
    # Guardar la imagen con las áreas marcadas
    img_con_areas.save("pdf_con_areas_marcadas.png")
    print(f"\nImagen con áreas marcadas guardada como: pdf_con_areas_marcadas.png")
    
    # Mostrar la imagen
    img_con_areas.show()
    
    pdf_document.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Buscar un PDF en el directorio actual
        import os
        pdfs = [f for f in os.listdir('.') if f.endswith('.pdf') and not f.startswith('ticket_')]
        if pdfs:
            pdf_path = pdfs[0]
            print(f"Usando PDF: {pdf_path}")
        else:
            print("No se encontró ningún PDF. Uso: python encontrar_qr_en_pdf.py <ruta_al_pdf>")
            sys.exit(1)
    
    encontrar_qr_en_pdf(pdf_path)
