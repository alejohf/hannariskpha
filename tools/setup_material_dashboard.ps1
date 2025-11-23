# Script PowerShell para clonar e instalar Material Dashboard React
# Ejecútalo desde la raíz del proyecto D:\DEVFULLAPP\appPHAV3

$frontendDir = Join-Path $PSScriptRoot '..\frontend' | Resolve-Path
Set-Location $frontendDir

if (Test-Path .\material-dashboard-react) {
    Write-Host "La carpeta 'material-dashboard-react' ya existe. Si quieres reinstalar, elimínala primero." -ForegroundColor Yellow
    exit 1
}

Write-Host "Clonando repo..."
git clone https://github.com/creativetimofficial/material-dashboard-react.git material-dashboard-react

if ($LASTEXITCODE -ne 0) {
    Write-Error "Error clonando el repositorio. Asegúrate de tener git instalado y acceso a internet."
    exit 2
}

Set-Location .\material-dashboard-react
Write-Host "Instalando dependencias (npm)... Esto puede tardar varios minutos."
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Error "npm install falló. Revisa la salida para más detalles."; exit 3
}

Write-Host "Instalación completada. Ejecuta 'npm start' dentro de frontend\material-dashboard-react para iniciar la plantilla." -ForegroundColor Green
