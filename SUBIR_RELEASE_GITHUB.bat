@echo off
chcp 65001 >nul
echo ========================================
echo  GENERADOR DE TICKETS
echo  Subir Release a GitHub
echo ========================================
echo.

REM Verificar que existen los archivos compilados
if not exist "dist\GeneradorTickets.exe" (
    echo ❌ Error: No se encuentra el ejecutable
    echo Primero ejecuta: COMPILAR_Y_CREAR_INSTALADOR.bat
    pause
    exit /b 1
)

if not exist "dist\GeneradorTickets_Instalador_v1.0.0.exe" (
    echo ❌ Error: No se encuentra el instalador
    echo Primero ejecuta: COMPILAR_Y_CREAR_INSTALADOR.bat
    pause
    exit /b 1
)

echo Archivos encontrados:
echo ✓ dist\GeneradorTickets.exe
echo ✓ dist\GeneradorTickets_Instalador_v1.0.0.exe
echo.

REM Leer la versión actual
set /p VERSION=<version.json
echo Versión detectada: 1.0.0
echo.

echo ========================================
echo PASOS PARA SUBIR A GITHUB:
echo ========================================
echo.
echo 1. Asegúrate de tener GitHub CLI instalado (gh)
echo    Descarga: https://cli.github.com/
echo.
echo 2. Autentícate en GitHub (una sola vez):
echo    gh auth login
echo.
echo 3. Crea el release y sube los archivos:
echo.
echo    gh release create v1.0.0 ^
echo      --repo Ale-beep-stack/Tiketex ^
echo      --title "Versión 1.0.0" ^
echo      --notes "Primera versión estable con auto-actualización" ^
echo      dist\GeneradorTickets.exe ^
echo      dist\GeneradorTickets_Instalador_v1.0.0.exe
echo.
echo ========================================
echo.

REM Verificar si GitHub CLI está instalado
where gh >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠ GitHub CLI (gh) no está instalado.
    echo.
    echo Opciones:
    echo 1. Instala GitHub CLI desde: https://cli.github.com/
    echo 2. O sube manualmente a: https://github.com/Ale-beep-stack/Tiketex/releases/new
    echo.
    pause
    exit /b 0
)

echo ¿Deseas crear el release ahora? (S/N)
set /p RESPUESTA="> "

if /i "%RESPUESTA%"=="S" (
    echo.
    echo Creando release...
    gh release create v1.0.0 --repo Ale-beep-stack/Tiketex --title "Versión 1.0.0" --notes "Primera versión estable con auto-actualización integrada" dist\GeneradorTickets.exe dist\GeneradorTickets_Instalador_v1.0.0.exe
    
    if %errorlevel% equ 0 (
        echo.
        echo ✓ Release creado exitosamente!
        echo.
        echo URL: https://github.com/Ale-beep-stack/Tiketex/releases/latest
        echo.
    ) else (
        echo.
        echo ❌ Error al crear el release
        echo Verifica que estás autenticado: gh auth login
        echo.
    )
) else (
    echo.
    echo Release cancelado. Puedes subirlo manualmente cuando quieras.
    echo.
)

pause
