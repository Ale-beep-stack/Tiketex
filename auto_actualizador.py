# auto_actualizador.py
# Sistema de auto-actualización desde GitHub con logging detallado

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
import logging

# Configurar logging
def configurar_logging():
    """Configura el sistema de logging para debugging."""
    try:
        # Carpeta de logs en Documentos del usuario
        log_dir = Path.home() / "Documents" / "GeneradorTickets" / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"actualizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        logging.info(f"Sistema de logging iniciado. Archivo: {log_file}")
        return str(log_file)
    except Exception as e:
        print(f"Error al configurar logging: {e}")
        return None

LOG_FILE = configurar_logging()

# Configuración
GITHUB_REPO = "Ale-beep-stack/Tiketex"
VERSION_ACTUAL = "1.0.0"
VERSION_FILE = "version.json"

def obtener_version_actual():
    """Obtiene la versión actual del archivo version.json"""
    try:
        logging.info("=== Obteniendo versión actual ===")
        
        # Si estamos en ejecutable, buscar version.json en la carpeta de instalación
        if getattr(sys, 'frozen', False):
            directorio = os.path.dirname(sys.executable)
            version_file = os.path.join(directorio, VERSION_FILE)
            logging.info(f"Modo ejecutable. Buscando en: {version_file}")
        else:
            version_file = VERSION_FILE
            logging.info(f"Modo desarrollo. Buscando en: {version_file}")
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = data.get("version", VERSION_ACTUAL)
                logging.info(f"Versión encontrada en archivo: {version}")
                return version
        else:
            logging.warning(f"Archivo version.json no encontrado en: {version_file}")
            logging.info(f"Usando versión por defecto: {VERSION_ACTUAL}")
            return VERSION_ACTUAL
    except Exception as e:
        logging.error(f"Error al leer versión actual: {e}", exc_info=True)
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
        logging.error(f"Error al comparar versiones: {e}", exc_info=True)
        return 0

def verificar_actualizacion():
    """
    Verifica si hay una nueva versión disponible en GitHub.
    Retorna: (hay_actualizacion, version_nueva, url_descarga, cambios) o (False, None, None, None)
    """
    try:
        logging.info("=== Verificando actualizaciones ===")
        # URL de la API de GitHub para obtener el último release
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        
        logging.info(f"Consultando: {url}")
        
        # Hacer petición a GitHub
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"Error HTTP: {response.status_code}")
            return False, None, None, None
        
        data = response.json()
        
        # Obtener información del release
        version_nueva = data.get("tag_name", "").replace("v", "")
        version_actual = obtener_version_actual()
        
        logging.info(f"Versión actual: {version_actual}")
        logging.info(f"Versión en GitHub: {version_nueva}")
        
        # Comparar versiones
        comparacion = comparar_versiones(version_nueva, version_actual)
        logging.info(f"Resultado de comparación: {comparacion}")
        
        if comparacion > 0:
            # Hay una versión más nueva
            logging.info("¡Nueva versión disponible!")
            
            # Buscar el archivo .exe en los assets
            assets = data.get("assets", [])
            url_descarga = None
            
            logging.info(f"Assets encontrados: {len(assets)}")
            for asset in assets:
                nombre = asset.get("name", "")
                logging.info(f"  - {nombre}")
                if nombre.endswith(".exe") and "Instalador" not in nombre:
                    url_descarga = asset.get("browser_download_url")
                    logging.info(f"✓ Ejecutable encontrado: {nombre}")
                    break
            
            if not url_descarga:
                logging.error("No se encontró archivo .exe en el release")
                return False, None, None, None
            
            # Obtener notas del release (cambios)
            cambios = data.get("body", "")
            
            return True, version_nueva, url_descarga, cambios
        else:
            logging.info("No hay actualizaciones disponibles")
            return False, None, None, None
            
    except requests.exceptions.Timeout:
        logging.error("Timeout al verificar actualizaciones")
        return False, None, None, None
    except Exception as e:
        logging.error(f"Error al verificar actualizaciones: {e}", exc_info=True)
        return False, None, None, None

def descargar_actualizacion(url, callback_progreso=None):
    """
    Descarga la actualización desde la URL proporcionada.
    Retorna la ruta del archivo descargado o None si hay error.
    """
    try:
        logging.info(f"Descargando actualización desde: {url}")
        
        # Crear carpeta temporal
        temp_dir = tempfile.gettempdir()
        nombre_archivo = "GeneradorTickets_nuevo.exe"
        ruta_descarga = os.path.join(temp_dir, nombre_archivo)
        
        logging.info(f"Guardando en: {ruta_descarga}")
        
        # Descargar con progreso
        response = requests.get(url, stream=True, timeout=30)
        total_size = int(response.headers.get('content-length', 0))
        
        logging.info(f"Tamaño total: {total_size} bytes")
        
        with open(ruta_descarga, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if callback_progreso and total_size > 0:
                        porcentaje = (downloaded / total_size) * 100
                        callback_progreso(porcentaje)
        
        logging.info(f"✓ Actualización descargada correctamente")
        return ruta_descarga
        
    except Exception as e:
        logging.error(f"Error al descargar actualización: {e}", exc_info=True)
        return None

def aplicar_actualizacion(ruta_nuevo_exe, version_nueva):
    """
    Aplica la actualización reemplazando el ejecutable actual.
    """
    try:
        logging.info("=== Aplicando actualización ===")
        
        # Obtener ruta del ejecutable actual
        if getattr(sys, 'frozen', False):
            # Estamos corriendo como ejecutable
            ruta_actual = sys.executable
            directorio_instalacion = os.path.dirname(ruta_actual)
            logging.info(f"Ejecutable actual: {ruta_actual}")
            logging.info(f"Directorio instalación: {directorio_instalacion}")
        else:
            # Estamos corriendo como script (desarrollo)
            logging.warning("Modo desarrollo: no se puede aplicar actualización automática")
            return False
        
        # Actualizar version.json ANTES de reemplazar el ejecutable
        version_file = os.path.join(directorio_instalacion, "version.json")
        logging.info(f"Actualizando {version_file} a versión {version_nueva}")
        
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": version_nueva,
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "cambios": ["Actualización automática"]
                }, f, indent=2, ensure_ascii=False)
            logging.info(f"✓ Archivo version.json actualizado correctamente")
        except Exception as e:
            logging.error(f"⚠ No se pudo actualizar version.json: {e}", exc_info=True)
        
        # Crear script de actualización mejorado con logging
        script_actualizacion = os.path.join(tempfile.gettempdir(), "actualizar.bat")
        nombre_ejecutable = os.path.basename(ruta_actual)
        
        logging.info(f"Creando script de actualización: {script_actualizacion}")
        logging.info(f"Nuevo ejecutable: {ruta_nuevo_exe}")
        
        with open(script_actualizacion, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write('chcp 65001 >nul\n')
            f.write('title Actualizando Generador de Tickets...\n')
            f.write('color 0A\n')
            f.write('echo.\n')
            f.write('echo ========================================\n')
            f.write('echo  ACTUALIZANDO GENERADOR DE TICKETS\n')
            f.write('echo ========================================\n')
            f.write('echo.\n')
            f.write(f'echo Versión actual: {obtener_version_actual()}\n')
            f.write(f'echo Versión nueva: {version_nueva}\n')
            f.write('echo.\n')
            f.write('echo Esperando cierre de la aplicación...\n')
            f.write('timeout /t 3 /nobreak >nul\n')
            f.write(f'echo Cerrando procesos de {nombre_ejecutable}...\n')
            f.write(f'taskkill /F /IM "{nombre_ejecutable}" >nul 2>&1\n')
            f.write('timeout /t 2 /nobreak >nul\n')
            f.write('echo.\n')
            f.write('echo Reemplazando ejecutable...\n')
            f.write(f'echo De: {ruta_nuevo_exe}\n')
            f.write(f'echo A:  {ruta_actual}\n')
            f.write('echo.\n')
            f.write(f'move /y "{ruta_nuevo_exe}" "{ruta_actual}"\n')
            f.write('if %errorlevel% neq 0 (\n')
            f.write('    echo.\n')
            f.write('    color 0C\n')
            f.write('    echo ❌ ERROR: No se pudo actualizar el archivo\n')
            f.write('    echo.\n')
            f.write('    echo Posibles causas:\n')
            f.write('    echo - El programa aun esta abierto\n')
            f.write('    echo - Permisos insuficientes\n')
            f.write('    echo.\n')
            f.write('    pause\n')
            f.write('    exit /b 1\n')
            f.write(')\n')
            f.write('echo.\n')
            f.write('echo ✓ Actualización completada exitosamente!\n')
            f.write('echo.\n')
            f.write('echo Iniciando programa actualizado...\n')
            f.write('timeout /t 2 /nobreak >nul\n')
            f.write(f'start "" "{ruta_actual}"\n')
            f.write('timeout /t 1 /nobreak >nul\n')
            f.write('exit\n')
        
        logging.info(f"✓ Script de actualización creado")
        logging.info("Ejecutando script...")
        
        # Ejecutar el script con ventana visible
        subprocess.Popen(['cmd', '/c', script_actualizacion])
        
        logging.info("Script lanzado. Esperando 1 segundo...")
        
        # Dar tiempo al script para iniciarse
        import time
        time.sleep(1)
        
        logging.info("Cerrando aplicación actual...")
        logging.info(f"Log guardado en: {LOG_FILE}")
        
        # Cerrar la aplicación actual
        sys.exit(0)
        
        return True
        
    except Exception as e:
        logging.error(f"Error al aplicar actualización: {e}", exc_info=True)
        return False

def verificar_y_actualizar_async(ventana_principal=None, silencioso=False):
    """
    Verifica y aplica actualizaciones de forma asíncrona.
    
    Args:
        ventana_principal: Ventana Tkinter principal (opcional)
        silencioso: Si es True, no muestra mensajes si no hay actualizaciones
    """
    def tarea():
        try:
            logging.info("=== Inicio de verificación de actualización ===")
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
                logging.info(f"Usuario respondió: {'Sí' if respuesta else 'No'}")
                
                if respuesta:
                    # Descargar actualización
                    messagebox.showinfo("Descargando", 
                        "Descargando actualización...\nEsto puede tomar unos momentos.")
                    
                    ruta_descarga = descargar_actualizacion(url_descarga)
                    
                    if ruta_descarga:
                        # Cerrar la ventana principal ANTES de aplicar actualización
                        if ventana_principal:
                            try:
                                logging.info("Cerrando ventana principal...")
                                ventana_principal.quit()
                                ventana_principal.destroy()
                            except:
                                pass
                        
                        aplicar_actualizacion(ruta_descarga, version_nueva)
                    else:
                        logging.error("No se pudo descargar la actualización")
                        messagebox.showerror("Error", 
                            "No se pudo descargar la actualización.\nIntente más tarde.")
            else:
                if not silencioso:
                    messagebox.showinfo("Sin Actualizaciones", 
                        "Ya tienes la última versión instalada.")
        except Exception as e:
            logging.error(f"Error en tarea de actualización: {e}", exc_info=True)
    
    # Ejecutar en hilo separado para no bloquear la interfaz
    thread = threading.Thread(target=tarea, daemon=True)
    thread.start()

def verificar_actualizacion_al_iniciar(ventana_principal=None):
    """
    Verifica actualizaciones al iniciar la aplicación de forma silenciosa.
    Solo muestra mensaje si hay actualización disponible.
    """
    verificar_y_actualizar_async(ventana_principal, silencioso=True)

# Para testing
if __name__ == "__main__":
    logging.info("=== Probando Auto-actualizador ===")
    logging.info(f"Versión actual: {obtener_version_actual()}")
    
    hay_actualizacion, version_nueva, url, cambios = verificar_actualizacion()
    
    if hay_actualizacion:
        logging.info(f"\n✓ Nueva versión disponible: {version_nueva}")
        logging.info(f"URL de descarga: {url}")
        logging.info(f"Cambios:\n{cambios}")
    else:
        logging.info("\n✓ No hay actualizaciones disponibles")
