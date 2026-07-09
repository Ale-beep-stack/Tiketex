import re

texto = 'Sello de Recepción:DTE-01-M001P001-0000000000001502025F96753CCC25D4EB5BD2EBA8F1D57E722ZOQSModelo'

print('=== TEST DIRECTO ===')
print('Texto:', texto[:100])

match = re.search(r'Sello\s+de\s+Recepción\s*:\s*(?:DTE-\d{2}-[A-Z0-9]+-\d{12,15})?([A-Z0-9]{40,50}?)(?=Modelo|MODELO|Tipo|TIPO|Fecha)', texto, re.IGNORECASE)

print('Match encontrado:', match is not None)
if match:
    print('Sello extraído:', match.group(1))
    print('Longitud:', len(match.group(1)))
else:
    print('NO SE ENCONTRÓ MATCH')
