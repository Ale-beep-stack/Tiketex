@echo off
chcp 65001 >nul
echo ========================================
echo  GENERADOR DE TICKETS
echo  Compilar y Crear Instalador
echo ========================================
echo.

echo [1/3] Limpiando archivos anteriores...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo ✓ Limpieza completada
echo.

echo [2/3] Compilando ejecutable con PyInstaller...
python build_exe.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error al compilar el ejecutable
    pause
    exit /b 1
)
echo ✓ Ejecutable compilado
echo.

echo [3/3] Creando instalador con Inno Setup...
echo.
echo NOTA: Necesitas tener Inno Setup instalado.
echo Descárgalo desde: https://jrsoftware.org/isdl.php
echo.

REM Buscar Inno Setup en ubicaciones comunes
set INNO_PATH=""

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set INNO_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set INNO_PATH="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
)

if %INNO_PATH%=="" (
    echo.
    echo ⚠ Inno Setup no encontrado.
    echo Por favor, instala Inno Setup desde: https://jrsoftware.org/isdl.php
    echo.
    echo El ejecutable está listo en: dist\GeneradorTickets.exe
    echo Después de instalar Inno Setup, ejecuta este script nuevamente.
    echo.
    pause
    exit /b 0
)

REM Compilar el instalador
%INNO_PATH% "crear_instalador.iss"

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error al crear el instalador
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ ¡PROCESO COMPLETADO!
echo ========================================
echo.
echo Archivos generados:
echo 📁 dist\GeneradorTickets.exe (Ejecutable)
echo 📁 dist\GeneradorTickets_Instalador_v1.0.0.exe (Instalador)
echo.
echo Ya puedes:
echo 1. Probar el instalador localmente
echo 2. Subir a GitHub Release con: SUBIR_RELEASE_GITHUB.bat
echo.
pause
