import re

texto = "1 1.00 Unidad puppy small bittes hills 25.70 0.00 0.00 0.00 0.00 25.70"

# Capturar todo entre "Unidad" y el primer "0.00"
patron = r'(\d+)\s+([\d\.]+)\s+Unidad\s+(.+?)\s+0\.00'
matches = list(re.finditer(patron, texto, re.IGNORECASE))
print(f"Patrón encontró: {len(matches)} coincidencias")
for m in matches:
    contenido = m.group(3).strip()
    print(f"  Contenido capturado: '{contenido}'")
    
    # Separar por espacios y tomar todo excepto el último elemento (que es el precio)
    partes = contenido.split()
    if len(partes) > 1:
        # El último elemento debería ser el precio
        precio = partes[-1]
        descripcion = ' '.join(partes[:-1])
        print(f"  - Cant:{m.group(2)}, Desc:'{descripcion}', Precio:{precio}")



