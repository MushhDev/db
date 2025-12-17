@echo off
echo ========================================
echo SecureVault - Compilador Completo
echo ========================================
echo.

echo [1/2] Compilando instalador...
python build_installer.py
if errorlevel 1 (
    echo Error al compilar instalador
    pause
    exit /b 1
)

echo.
echo [2/2] Compilando aplicación...
python build_app.py
if errorlevel 1 (
    echo Error al compilar aplicación
    pause
    exit /b 1
)

echo.
echo ========================================
echo Compilación completada exitosamente!
echo ========================================
echo.
echo Archivos generados:
echo - dist\SecureVault-Installer.exe (Instalador)
echo - dist\SecureVault.exe (Aplicación)
echo.
pause

