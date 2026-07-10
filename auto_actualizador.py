# auto_actualizador.py
# Sistema de auto-actualización desde GitHub

import requests
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from tkinter import messagebox
import threading
from datetime import datetime

# Configuración
GITHUB_REPO = "Ale-beep-stack/Tiketex"
VERSION_ACTUAL = "1.0.0"
VERSION_FILE = "version.json"

def obtener_version_actual():
    """Obtiene la versión actual del archivo version.json"""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("version", VERSION_ACTUAL)
    except Exception as e:
        print(f"Error al leer versión actual: {e}")
    return VERSION_ACTUAL

def comparar_versiones(v1, v2):
    """
    Compara dos versiones en formato X.Y.Z
    Retorna: 1 si v1 > v2, -1 si v1 < v2, 0 si son iguales
    """
    try:
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_num = v1_parts[i] if i < len(v1_parts) else 0
            v2_num = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1_num > v2_num:
                return 1
            elif v1_num < v2_num:
                return -1
        
        return 0
    except Exception as e:
        print(f"Error al comparar versiones: {e}")
        return 0

def verificar_actualizacion():
    """
    Verifica si hay una nueva versión disponible en GitHub.
    Retorna: (hay_actualizacion, version_nueva, url_descarga, cambios) o (False, None, None, None)
    """
    try:
        # URL de la API de GitHub para obtener el último release
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        
        print(f"Verificando actualizaciones en: {url}")
        
        # Hacer petición a GitHub
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"Error al verificar actualizaciones: {response.status_code}")
            return False, None, None, None
        
        data = response.json()
        
        # Obtener información del release
        version_nueva = data.get("tag_name", "").replace("v", "")
        version_actual = obtener_version_actual()
        
        print(f"Versión actual: {version_actual}")
        print(f"Versión en GitHub: {version_nueva}")
        
        # Comparar versiones
        if comparar_versiones(version_nueva, version_actual) > 0:
            # Hay una versión más nueva
            
            # Buscar el archivo .exe en los assets
            assets = data.get("assets", [])
            url_descarga = None
            
            for asset in assets:
                nombre = asset.get("name", "")
                if nombre.endswith(".exe") and "Instalador" not in nombre:
                    # Es el ejecutable actualizado
                    url_descarga = asset.get("browser_download_url")
                    break
            
            if not url_descarga:
                print("No se encontró archivo .exe en el release")
                return False, None, None, None
            
            # Obtener notas del release (cambios)
            cambios = data.get("body", "")
            
            return True, version_nueva, url_descarga, cambios
        else:
            print("No hay actualizaciones disponibles")
            return False, None, None, None
            
    except requests.exceptions.Timeout:
        print("Timeout al verificar actualizaciones")
        return False, None, None, None
    except Exception as e:
        print(f"Error al verificar actualizaciones: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None, None

def descargar_actualizacion(url, callback_progreso=None):
    """
    Descarga la actualización desde la URL proporcionada.
    Retorna la ruta del archivo descargado o None si hay error.
    """
    try:
        print(f"Descargando actualización desde: {url}")
        
        # Crear carpeta temporal
        temp_dir = tempfile.gettempdir()
        nombre_archivo = "GeneradorTickets_nuevo.exe"
        ruta_descarga = os.path.join(temp_dir, nombre_archivo)
        
        # Descargar con progreso
        response = requests.get(url, stream=True, timeout=30)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(ruta_descarga, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if callback_progreso and total_size > 0:
                        porcentaje = (downloaded / total_size) * 100
                        callback_progreso(porcentaje)
        
        print(f"✓ Actualización descargada en: {ruta_descarga}")
        return ruta_descarga
        
    except Exception as e:
        print(f"Error al descargar actualización: {e}")
        return None

def aplicar_actualizacion(ruta_nuevo_exe, version_nueva):
    """
    Aplica la actualización reemplazando el ejecutable actual.
    """
    try:
        # Obtener ruta del ejecutable actual
        if getattr(sys, 'frozen', False):
            # Estamos corriendo como ejecutable
            ruta_actual = sys.executable
            directorio_instalacion = os.path.dirname(ruta_actual)
        else:
            # Estamos corriendo como script (desarrollo)
            print("Modo desarrollo: no se puede aplicar actualización automática")
            return False
        
        # Actualizar version.json ANTES de reemplazar el ejecutable
        version_file = os.path.join(directorio_instalacion, "version.json")
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": version_nueva,
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "cambios": ["Actualización automática"]
                }, f, indent=2, ensure_ascii=False)
            print(f"✓ Archivo version.json actualizado a v{version_nueva}")
        except Exception as e:
            print(f"⚠ No se pudo actualizar version.json: {e}")
        
        # Crear script de actualización mejorado
        script_actualizacion = os.path.join(tempfile.gettempdir(), "actualizar.bat")
        
        with open(script_actualizacion, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write('chcp 65001 >nul\n')
            f.write('echo Cerrando aplicación...\n')
            f.write('timeout /t 3 /nobreak >nul\n')  # Esperar 3 segundos
            f.write('echo Aplicando actualización...\n')
            f.write(f'taskkill /F /IM "{os.path.basename(ruta_actual)}" >nul 2>&1\n')  # Forzar cierre
            f.write('timeout /t 1 /nobreak >nul\n')
            f.write(f'move /y "{ruta_nuevo_exe}" "{ruta_actual}" >nul 2>&1\n')
            f.write('if %errorlevel% neq 0 (\n')
            f.write('    echo Error al reemplazar el archivo\n')
            f.write('    pause\n')
            f.write('    exit /b 1\n')
            f.write(')\n')
            f.write('echo Actualización completada. Iniciando...\n')
            f.write('timeout /t 1 /nobreak >nul\n')
            f.write(f'start "" "{ruta_actual}"\n')  # Reiniciar la aplicación
            f.write(f'del "%~f0"\n')  # Eliminar el script
        
        print(f"Ejecutando script de actualización: {script_actualizacion}")
        
        # Ejecutar el script
        subprocess.Popen(['cmd', '/c', script_actualizacion], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        # Cerrar la aplicación actual
        sys.exit(0)
        
    except Exception as e:
        print(f"Error al aplicar actualización: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_y_actualizar_async(ventana_principal=None, silencioso=False):
    """
    Verifica y aplica actualizaciones de forma asíncrona.
    
    Args:
        ventana_principal: Ventana Tkinter principal (opcional)
        silencioso: Si es True, no muestra mensajes si no hay actualizaciones
    """
    def tarea():
        hay_actualizacion, version_nueva, url_descarga, cambios = verificar_actualizacion()
        
        if hay_actualizacion:
            # Mostrar mensaje de actualización disponible
            mensaje = f"Nueva versión disponible: v{version_nueva}\n\n"
            
            if cambios:
                mensaje += "Cambios:\n" + cambios[:200]
                if len(cambios) > 200:
                    mensaje += "..."
            
            mensaje += "\n\n¿Desea descargar e instalar la actualización ahora?"
            
            respuesta = messagebox.askyesno("Actualización Disponible", mensaje)
            
            if respuesta:
                # Descargar actualización
                messagebox.showinfo("Descargando", 
                    "Descargando actualización...\nEsto puede tomar unos momentos.")
                
                ruta_descarga = descargar_actualizacion(url_descarga)
                
                if ruta_descarga:
                    messagebox.showinfo("Actualización", 
                        "Actualización descargada.\nLa aplicación se reiniciará ahora.")
                    aplicar_actualizacion(ruta_descarga, version_nueva)
                else:
                    messagebox.showerror("Error", 
                        "No se pudo descargar la actualización.\nIntente más tarde.")
        else:
            if not silencioso:
                messagebox.showinfo("Sin Actualizaciones", 
                    "Ya tienes la última versión instalada.")
    
    # Ejecutar en hilo separado para no bloquear la interfaz
    thread = threading.Thread(target=tarea, daemon=True)
    thread.start()

def verificar_actualizacion_al_iniciar():
    """
    Verifica actualizaciones al iniciar la aplicación de forma silenciosa.
    Solo muestra mensaje si hay actualización disponible.
    """
    verificar_y_actualizar_async(silencioso=True)

# Para testing
if __name__ == "__main__":
    print("=== Probando Auto-actualizador ===")
    print(f"Versión actual: {obtener_version_actual()}")
    
    hay_actualizacion, version_nueva, url, cambios = verificar_actualizacion()
    
    if hay_actualizacion:
        print(f"\n✓ Nueva versión disponible: {version_nueva}")
        print(f"URL de descarga: {url}")
        print(f"Cambios:\n{cambios}")
    else:
        print("\n✓ No hay actualizaciones disponibles")
