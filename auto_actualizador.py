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
        
        # Usar AppData para evitar problemas de permisos en Program Files
        appdata_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "GeneradorTickets")
        version_file_appdata = os.path.join(appdata_dir, VERSION_FILE)
        
        # Si estamos en ejecutable, buscar primero en AppData, luego en carpeta de instalación
        if getattr(sys, 'frozen', False):
            # Intentar AppData primero
            if os.path.exists(version_file_appdata):
                logging.info(f"Modo ejecutable. Encontrado en AppData: {version_file_appdata}")
                with open(version_file_appdata, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version = data.get("version", VERSION_ACTUAL)
                    logging.info(f"Versión encontrada en AppData: {version}")
                    return version
            
            # Fallback: buscar en carpeta de instalación
            directorio = os.path.dirname(sys.executable)
            version_file = os.path.join(directorio, VERSION_FILE)
            logging.info(f"No encontrado en AppData. Buscando en instalación: {version_file}")
        else:
            version_file = VERSION_FILE
            logging.info(f"Modo desarrollo. Buscando en: {version_file}")
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = data.get("version", VERSION_ACTUAL)
                logging.info(f"Versión encontrada en archivo: {version}")
                
                # Copiar a AppData para futuras actualizaciones
                if getattr(sys, 'frozen', False):
                    try:
                        os.makedirs(appdata_dir, exist_ok=True)
                        with open(version_file_appdata, 'w', encoding='utf-8') as f_out:
                            json.dump(data, f_out, indent=2, ensure_ascii=False)
                        logging.info(f"Versión copiada a AppData para futuras actualizaciones")
                    except Exception as e:
                        logging.warning(f"No se pudo copiar version.json a AppData: {e}")
                
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
                # Aceptar cualquier archivo .exe (incluyendo los que tienen "Instalador")
                if nombre.endswith(".exe"):
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
    Ejecuta el instalador descargado para actualizar el programa.
    El instalador se encarga de reemplazar los archivos y actualizar version.json.
    """
    try:
        logging.info("=== Aplicando actualización ===")
        logging.info(f"Instalador descargado: {ruta_nuevo_exe}")
        
        # Actualizar version.json en AppData para registrar la nueva versión
        appdata_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "GeneradorTickets")
        os.makedirs(appdata_dir, exist_ok=True)
        version_file_appdata = os.path.join(appdata_dir, "version.json")
        
        logging.info(f"Actualizando version.json en AppData: {version_file_appdata}")
        
        try:
            with open(version_file_appdata, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": version_nueva,
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "cambios": ["Actualización automática"]
                }, f, indent=2, ensure_ascii=False)
            logging.info(f"✓ version.json actualizado en AppData correctamente")
        except Exception as e:
            logging.error(f"⚠ No se pudo actualizar version.json en AppData: {e}", exc_info=True)
        
        # Ejecutar el instalador
        logging.info("Ejecutando instalador...")
        logging.info("El instalador se ejecutará en 2 segundos...")
        
        # Ejecutar el instalador con /SILENT para que se instale automáticamente
        # Usamos /DIR para especificar la misma carpeta de instalación
        if getattr(sys, 'frozen', False):
            directorio_instalacion = os.path.dirname(sys.executable)
            logging.info(f"Directorio de instalación actual: {directorio_instalacion}")
            
            # Dar tiempo para que el log se escriba
            import time
            time.sleep(1)
            
            # Ejecutar instalador en modo SILENCIOSO con parámetros de Inno Setup
            # /VERYSILENT = instalación completamente silenciosa sin ventanas
            # /SUPPRESSMSGBOXES = suprime cuadros de mensaje
            # /NORESTART = no reinicia el sistema
            # /DIR = especifica el directorio de instalación
            logging.info(f"Lanzando: {ruta_nuevo_exe} /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR={directorio_instalacion}")
            
            subprocess.Popen([
                ruta_nuevo_exe,
                '/VERYSILENT',
                '/SUPPRESSMSGBOXES', 
                '/NORESTART',
                f'/DIR={directorio_instalacion}'
            ])
        else:
            # Modo desarrollo
            subprocess.Popen([ruta_nuevo_exe])
        
        logging.info("Instalador lanzado correctamente")
        logging.info(f"Log guardado en: {LOG_FILE}")
        logging.info("Cerrando aplicación actual para que el instalador pueda actualizar...")
        
        # Forzar cierre de la aplicación
        import os
        if getattr(sys, 'frozen', False):
            # En ejecutable, forzar cierre del proceso
            os._exit(0)
        else:
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
