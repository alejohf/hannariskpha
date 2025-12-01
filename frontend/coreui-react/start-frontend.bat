@echo off
echo ========================================
echo HannaRiskPro - Frontend Development Server
echo ========================================

REM Puerto a usar
set PORT=5501

echo Buscando procesos que usan el puerto %PORT%...

REM Buscar procesos usando el puerto especificado
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%PORT% "') do (
    echo Encontrado proceso PID: %%a usando puerto %PORT%
    echo Terminando proceso %%a...
    taskkill /F /PID %%a >nul 2>&1
    if %errorlevel% equ 0 (
        echo Proceso %%a terminado exitosamente.
    ) else (
        echo Error al terminar proceso %%a.
    )
)

REM Esperar un momento para que el puerto se libere
timeout /t 2 /nobreak >nul

echo Iniciando servidor de desarrollo en puerto %PORT%...
echo URL: http://localhost:%PORT%/
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar el servidor de desarrollo
npx vite --port %PORT% --host

pause