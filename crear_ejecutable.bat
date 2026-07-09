@echo off
echo ========================================
echo   Generador de Tickets - Crear EXE
echo ========================================
echo.

echo [1/4] Verificando dependencias...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

pip show pillow >nul 2>&1
if errorlevel 1 (
    echo Instalando Pillow...
    pip install pillow
)

echo.
echo [2/4] Convirtiendo icono PNG a ICO...
python convertir_icono.py

echo.
echo [3/4] Creando ejecutable...
echo Esto puede tardar varios minutos...
pyinstaller --name=GeneradorTickets --onefile --windowed --icon="disenos/raffle-ticket-blue.ico" --add-data="disenos;disenos" --hidden-import=PIL --hidden-import=reportlab --hidden-import=PyPDF2 --hidden-import=fitz --hidden-import=frontend --clean --noconfirm main.py

if not exist "dist\GeneradorTickets.exe" (
    echo.
    echo ERROR: No se pudo crear el ejecutable
    echo Revisa los mensajes de error arriba
    pause
    exit /b 1
)

echo.
echo [4/4] Limpiando archivos temporales...
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo ========================================
echo   PROCESO COMPLETADO EXITOSAMENTE
echo ========================================
echo.
echo El ejecutable se encuentra en: dist\GeneradorTickets.exe
echo.
pause
explorer dist
