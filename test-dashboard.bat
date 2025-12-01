@echo off
echo ========================================
echo HannaRiskPro - Test Dashboard
echo ========================================

echo.
echo 1. Verificando que el backend esté funcionando...
curl -s -o nul -w "%%{http_code}" "http://localhost:8092/api/health" > temp_code.txt
set /p STATUS=<temp_code.txt
del temp_code.txt

if "%STATUS%"=="200" (
    echo ✅ Backend funcionando correctamente
) else (
    echo ❌ Backend no responde. Inicia el backend primero.
    echo Comando: .venv\Scripts\activate.bat ^&^& uvicorn backend.main:app --reload --port 8092
    pause
    exit /b 1
)

echo.
echo 2. Probando login...
curl -s -X POST "http://localhost:8092/api/auth/login" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"username\": \"admin\", \"password\": \"pa$$wr0rd\"}" > temp_login.txt

findstr "access_token" temp_login.txt >nul
if %errorlevel% equ 0 (
    echo ✅ Login exitoso
    for /f "tokens=2 delims=:," %%a in ('findstr "access_token" temp_login.txt') do set TOKEN=%%a
    set TOKEN=%TOKEN:"=%
    set TOKEN=%TOKEN: =%
) else (
    echo ❌ Login falló
    type temp_login.txt
    del temp_login.txt
    pause
    exit /b 1
)
del temp_login.txt

echo.
echo 3. Probando endpoint de KPIs...
curl -s -H "Authorization: Bearer %TOKEN%" "http://localhost:8092/api/dashboard/kpis" > temp_kpis.txt

findstr "total_estudios" temp_kpis.txt >nul
if %errorlevel% equ 0 (
    echo ✅ Dashboard KPIs funcionando correctamente
    echo Datos obtenidos:
    type temp_kpis.txt
) else (
    echo ❌ Error al obtener KPIs
    type temp_kpis.txt
)
del temp_kpis.txt

echo.
echo 4. Instrucciones para probar el frontend:
echo.
echo    1. Abrir navegador en: http://localhost:5501/login
echo    2. Ingresar usuario: admin, contraseña: pa$$wr0rd
echo    3. Hacer clic en "Entrar"
echo    4. Deberías ver el dashboard con datos reales
echo.
echo    Si el puerto 5501 no funciona, usa: npm run dev
echo.

pause