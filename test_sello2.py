import re

texto = 'Sello de Recepción:DTE-01-M001P001-0000000000001632025840C657127C944759F185E4F1E9F778DPTKNModelo'

print('Texto:', texto)
print()

# Patrón actual
patron1 = r'Sello\s+de\s+Recepción\s*:\s*(?:DTE-\d{2}-[A-Z0-9]+-\d{12,15})?([A-Z0-9]{40,50}?)(?=Modelo|MODELO|Tipo|TIPO|Fecha)'
match1 = re.search(patron1, texto, re.IGNORECASE)
print('Patrón 1 (actual):', match1)
if match1:
    print('  Sello:', match1.group(1))

# Patrón sin lookahead, solo capturar hasta antes de Modelo
patron2 = r'Sello\s+de\s+Recepción\s*:\s*DTE-\d{2}-[A-Z0-9]+-\d{12,15}([A-Z0-9]+?)Modelo'
match2 = re.search(patron2, texto, re.IGNORECASE)
print('Patrón 2 (sin lookahead):', match2)
if match2:
    print('  Sello:', match2.group(1))
    print('  Longitud:', len(match2.group(1)))
