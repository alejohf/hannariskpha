# HannaRiskPro - Frontend Development Server
# Script para iniciar el servidor de desarrollo limpiando procesos previos

param(
    [int]$Port = 5501
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HannaRiskPro - Frontend Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Buscar procesos usando el puerto especificado
Write-Host "Buscando procesos que usan el puerto $Port..." -ForegroundColor Yellow

$processesUsingPort = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" } |
    Select-Object -ExpandProperty OwningProcess

if ($processesUsingPort) {
    foreach ($pid in $processesUsingPort) {
        try {
            $process = Get-Process -Id $pid -ErrorAction Stop
            Write-Host "Encontrado proceso $($process.Name) (PID: $pid) usando puerto $Port" -ForegroundColor Yellow
            Write-Host "Terminando proceso $pid..." -ForegroundColor Red
            Stop-Process -Id $pid -Force
            Write-Host "Proceso $pid terminado exitosamente." -ForegroundColor Green
        } catch {
            Write-Host "Error al terminar proceso $pid : $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    # Esperar un momento para que el puerto se libere
    Write-Host "Esperando que el puerto se libere..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
} else {
    Write-Host "No se encontraron procesos usando el puerto $Port." -ForegroundColor Green
}

Write-Host ""
Write-Host "Iniciando servidor de desarrollo en puerto $Port..." -ForegroundColor Green
Write-Host "URL: http://localhost:$Port/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar el servidor de desarrollo
try {
    & npx vite --port $Port --host
} catch {
    Write-Host "Error al iniciar el servidor: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
}