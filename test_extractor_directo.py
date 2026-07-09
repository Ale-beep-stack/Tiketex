from extractor import extraer_datos_factura

texto = '''Ver.1DOCUMENTO TRIBUTARIO ELECTRÓNICOFACTURANúmero de Control :Sello de Recepción:DTE-01-M001P001-000000000000170202520B96786AEC748DFBC95334935CFA506RP4BModelo de Facturación:Tipo de Transmisión:Fecha y Hora de Generación:PrevioNormal2025-12-31 10:34:5810F9BC65-65A1-4AB2-8EC2-56B9F6103FFE Código de Generación:'''

print("=== PRUEBA DIRECTA DEL EXTRACTOR ===")
datos = extraer_datos_factura(texto)
print(f"Sello encontrado: '{datos.get('sello_recepcion', 'NO ENCONTRADO')}'")
print(f"Longitud: {len(datos.get('sello_recepcion', ''))}")