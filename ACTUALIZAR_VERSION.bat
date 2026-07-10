@echo off
chcp 65001 >nul
echo ========================================
echo  ACTUALIZAR Y SUBIR NUEVA VERSIÓN
echo ========================================
echo.

REM Compilar ejecutable
echo [1/3] Compilando ejecutable...
python build_exe.py
if %errorlevel% neq 0 (
    echo ❌ Error al compilar
    pause
    exit /b 1
)
echo ✓ Ejecutable compilado
echo.

REM Crear instalador
echo [2/3] Creando instalador...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "crear_instalador.iss"
if %errorlevel% neq 0 (
    echo ❌ Error al crear instalador
    pause
    exit /b 1
)
echo ✓ Instalador creado
echo.

REM Subir release
echo [3/3] Subiendo a GitHub...
set /p VERSION=<version.json
echo.
echo Versión detectada en version.json
echo.
set /p VERSION_NUM="Ingresa el número de versión (ej: 1.0.2): "
set /p DESCRIPCION="Descripción breve de cambios: "

gh release create v%VERSION_NUM% --repo Ale-beep-stack/Tiketex --title "Versión %VERSION_NUM%" --notes "%DESCRIPCION%" "dist\GeneradorTickets.exe" "dist\GeneradorTickets_Instalador_v%VERSION_NUM%.exe"

if %errorlevel% equ 0 (
    echo.
    echo ✅ Release v%VERSION_NUM% creado exitosamente!
    echo.
    echo URL: https://github.com/Ale-beep-stack/Tiketex/releases/tag/v%VERSION_NUM%
    echo.
) else (
    echo.
    echo ❌ Error al crear el release
    echo.
)

pause
