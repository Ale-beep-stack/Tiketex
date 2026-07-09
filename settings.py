# settings.py
# Configuración general del sistema

# Configuración de la empresa emisora
EMPRESA = {
    "nombre": "Mi Empresa S.A.",
    "ruc": "20123456789",
    "direccion": "Av. Principal 123, Lima",
    "telefono": "(01) 234-5678",
    "email": "contacto@miempresa.com"
}

# Configuración del ticket
TICKET_CONFIG = {
    "ancho_mm": 80,  # Ancho del ticket en mm (estándar para impresoras térmicas)
    "margen": 5,
    "fuente": "Helvetica",
    "fuente_bold": "Helvetica-Bold",
    "tamano_titulo": 12,
    "tamano_normal": 9,
    "tamano_pequeno": 7
}

# Ruta por defecto para guardar tickets
RUTA_TICKETS = "tickets_generados"
