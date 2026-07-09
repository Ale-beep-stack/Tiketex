@echo off
cd /d "%~dp0"
chcp 65001 >nul 2>&1
title Crear Paquete de Distribución Rápido

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║    GENERADOR DE TICKETS - CREAR PAQUETE RÁPIDO             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 💡 Este script crea un ejecutable que inicia MUY RÁPIDO
echo    (2-3 segundos vs 10-15 segundos del método anterior)
echo.
echo ⏳ El proceso tomará 2-3 minutos...
echo.
pause

echo.
echo [1/3] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
) else (
    echo ✓ PyInstaller ya está instalado
)

echo.
echo [2/3] Verificando dependencias...
pip show pillow >nul 2>&1
if errorlevel 1 (
    echo Instalando Pillow...
    pip install pillow
)

pip show reportlab >nul 2>&1
if errorlevel 1 (
    echo Instalando ReportLab...
    pip install reportlab
)

pip show PyPDF2 >nul 2>&1
if errorlevel 1 (
    echo Instalando PyPDF2...
    pip install PyPDF2
)

pip show pymupdf >nul 2>&1
if errorlevel 1 (
    echo Instalando PyMuPDF...
    pip install pymupdf
)

pip show tkcalendar >nul 2>&1
if errorlevel 1 (
    echo Instalando tkcalendar...
    pip install tkcalendar
)

pip show pywin32 >nul 2>&1
if errorlevel 1 (
    echo Instalando pywin32...
    pip install pywin32
)

echo.
echo [3/3] Creando paquete de distribución...
echo Directorio actual: %CD%
echo Verificando archivo crear_paquete_rapido.py...

if not exist "crear_paquete_rapido.py" (
    echo.
    echo ❌ ERROR: No se encuentra el archivo crear_paquete_rapido.py
    echo Ubicación esperada: %CD%\crear_paquete_rapido.py
    echo.
    echo Archivos Python disponibles:
    dir /b *.py
    echo.
    pause
    exit /b 1
)

echo ✓ Archivo encontrado, ejecutando...
python crear_paquete_rapido.py

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Ocurrió un problema al crear el paquete
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo ✅ PROCESO COMPLETADO
echo ═══════════════════════════════════════════════════════════════
echo.
