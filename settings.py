# settings.py
# Configuración general del sistema

import os
from pathlib import Path

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

# Ruta por defecto para guardar tickets (en la carpeta de Documentos del usuario)
# Esto evita problemas de permisos cuando se instala en C:\Program Files\
def obtener_ruta_tickets():
    """Obtiene la ruta para guardar tickets en la carpeta de Documentos del usuario."""
    try:
        # Intenta usar la carpeta de Documentos del usuario
        documentos = Path.home() / "Documents" / "GeneradorTickets" / "Tickets"
        documentos.mkdir(parents=True, exist_ok=True)
        return str(documentos)
    except Exception as e:
        # Si falla, usa la carpeta temporal del sistema
        import tempfile
        temp_tickets = Path(tempfile.gettempdir()) / "GeneradorTickets" / "Tickets"
        temp_tickets.mkdir(parents=True, exist_ok=True)
        return str(temp_tickets)

RUTA_TICKETS = obtener_ruta_tickets()
