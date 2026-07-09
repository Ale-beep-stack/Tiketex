@echo off
echo ========================================
echo Compilando para Windows 7 32 bits
echo Python 3.7.9
echo ========================================
echo.

REM Verificar versión de Python
python --version
echo.

REM Verificar que sea 32 bits
python -c "import struct; print('Arquitectura:', '32 bits' if struct.calcsize('P') * 8 == 32 else '64 bits')"
echo.

echo Limpiando carpetas anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

echo Instalando dependencias compatibles...
pip install -r requirements_win7.txt
echo.

echo Compilando ejecutable...
python build_exe_win7.py
echo.

echo ========================================
echo Proceso completado
echo El ejecutable esta en: dist\GeneradorTickets.exe
echo ========================================
pause
