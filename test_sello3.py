import re

texto = 'Sello de Recepción:DTE-01-M001P001-000000000000170202520B96786AEC748DFBC95334935CFA506RP4BModelo'

print('Texto:', texto)
print()

# Patrón actual
patron1 = r'Sello\s+de\s+Recepción\s*:\s*(?:DTE-\d{2}-[A-Z0-9]+-\d{12,15})?([A-Z0-9]{40,50}?)(?=Modelo|MODELO|Tipo|TIPO|Fecha)'
match1 = re.search(patron1, texto, re.IGNORECASE)
print('Patrón 1 (actual):', match1)
if match1:
    print('  Sello:', match1.group(1))
    print('  Longitud:', len(match1.group(1)))

# Buscar el sello después del número de factura (15 dígitos)
patron_simple = r'DTE-\d{2}-[A-Z0-9]+-(\d{15})([A-Z0-9]{40,50})(?=Modelo)'
match_simple = re.search(patron_simple, texto, re.IGNORECASE)
print('Patrón simple:', match_simple)
if match_simple:
    print('  Número factura:', match_simple.group(1))
    print('  Sello:', match_simple.group(2))
    print('  Longitud sello:', len(match_simple.group(2)))