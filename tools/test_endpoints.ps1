# Script de pruebas para endpoints del backend Hanna RiskPro
# Ejecutar desde la raíz del repo:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\test_endpoints.ps1

$base = 'http://127.0.0.1:8092/api'
$ErrorActionPreference = 'Stop'

function Try-Invoke($Description, [scriptblock]$Action) {
    Write-Host "---- $Description ----" -ForegroundColor Cyan
    try {
        $res = & $Action
        Write-Host "OK:" -ForegroundColor Green
        $res | ConvertTo-Json -Depth 5 | Write-Host
        return $res
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}
#!/usr/bin/env pwsh
# Script de pruebas para endpoints del backend Hanna RiskPro
# Ejecutar desde la raíz del repo: powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\test_endpoints.ps1

$base = 'http://127.0.0.1:8092/api'
$ErrorActionPreference = 'Stop'

function Try-Invoke($Description, [scriptblock]$Action) {
    Write-Host "---- $Description ----" -ForegroundColor Cyan
    try {
        $res = & $Action
        Write-Host "OK:" -ForegroundColor Green
        $res | ConvertTo-Json -Depth 5 | Write-Host
        return $res
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# 1) Registrar admin (si la base está vacía o permitido)
$regBody = @{ username = 'admin1'; password = 'pa$$w0rd'; nombre_completo = 'Administrador Uno'; email = 'admin1@example.com'; rol = 'Administrador' } | ConvertTo-Json
$register = Try-Invoke 'Register admin1' { Invoke-RestMethod -Uri "$base/auth/register" -Method Post -Body $regBody -ContentType 'application/json' }

# 2) Login
<#
Script de pruebas para endpoints del backend Hanna RiskPro
Ejecutar desde la raíz del repo:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\test_endpoints.ps1
#>

$base = 'http://127.0.0.1:8092/api'
$ErrorActionPreference = 'Stop'

function Try-Invoke($Description, [scriptblock]$Action) {
    Write-Host "---- $Description ----" -ForegroundColor Cyan
    try {
        $res = & $Action
        Write-Host "OK:" -ForegroundColor Green
        $res | ConvertTo-Json -Depth 5 | Write-Host
        return $res
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# 1) Registrar admin (si la base está vacía o permitido)
$regBody = @{ username = 'admin1'; password = 'pa$$w0rd'; nombre_completo = 'Administrador Uno'; email = 'admin1@example.com'; rol = 'Administrador' } | ConvertTo-Json
$register = Try-Invoke 'Register admin1' { Invoke-RestMethod -Uri "$base/auth/register" -Method Post -Body $regBody -ContentType 'application/json' }

# 2) Login
$loginBody = @{ username = 'admin1'; password = 'pa$$w0rd' } | ConvertTo-Json
$login = Try-Invoke 'Login admin1' { Invoke-RestMethod -Uri "$base/auth/login" -Method Post -Body $loginBody -ContentType 'application/json' }

$token = $null
if ($login -and $login.access_token) { $token = $login.access_token } else {
    Write-Host 'No se obtuvo token; abortando pruebas que requieran autenticación.' -ForegroundColor Yellow
}

function AuthHeaders($t) {
    if ($t) { return @{ Authorization = "Bearer $t" } } else { return @{} }
}

# 3) Crear empresa (requiere admin)
$empresa = $null
if ($token) {
    $empresaBody = @{ nombre = 'Empresa Test'; ruc = '1234567890'; direccion = 'Calle Falsa 123' } | ConvertTo-Json
    $empresa = Try-Invoke 'Crear empresa' { Invoke-RestMethod -Uri "$base/empresas" -Method Post -Body $empresaBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 4) Crear plantilla (admin)
$plantilla = $null
if ($token) {
    $plantillaBody = @{ nombre = 'Plantilla Test'; descripcion = 'Plantilla creada por script'; contenido = @{ ejemplo = 'ok' } } | ConvertTo-Json
    $plantilla = Try-Invoke 'Crear plantilla' { Invoke-RestMethod -Uri "$base/plantillas" -Method Post -Body $plantillaBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 5) Crear metodología (admin)
$metodologia = $null
if ($token) {
    $metBody = @{ nombre = 'Metodologia Test'; descripcion = 'Descr metodologia' } | ConvertTo-Json
    $metodologia = Try-Invoke 'Crear metodologia' { Invoke-RestMethod -Uri "$base/metodologias" -Method Post -Body $metBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 6) Crear estudio (usa empresa_id y plantilla_id si están disponibles)
$estudio = $null
if ($token) {
    $empresa_id = $null
    if ($empresa -and $empresa.empresa_id) { $empresa_id = $empresa.empresa_id }
    $plantilla_id = $null
    if ($plantilla -and $plantilla.plantilla_id) { $plantilla_id = $plantilla.plantilla_id }

    $estBody = @{ nombre = 'Estudio Automático'; empresa_id = $empresa_id; ubicacion = 'Planta A'; objetivos = 'Validación automática'; plantilla_id = $plantilla_id } | ConvertTo-Json
    $estudio = Try-Invoke 'Crear estudio' { Invoke-RestMethod -Uri "$base/estudios" -Method Post -Body $estBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 7) Crear nodo (usa estudio_id)
$nodo = $null
if ($token -and $estudio -and $estudio.estudio_id) {
    $nodoBody = @{ estudio_id = $estudio.estudio_id; nombre = 'Nodo Script'; tipo = 'tipo-test' } | ConvertTo-Json
    $nodo = Try-Invoke 'Crear nodo' { Invoke-RestMethod -Uri "$base/nodos" -Method Post -Body $nodoBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 8) Crear parametro
$parametro = $null
if ($token -and $nodo -and $nodo.nodo_id) {
    $paramBody = @{ nodo_id = $nodo.nodo_id; nombre = 'Presion'; valor = '1.0'; unidad = 'bar' } | ConvertTo-Json
    $parametro = Try-Invoke 'Crear parametro' { Invoke-RestMethod -Uri "$base/parametros" -Method Post -Body $paramBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 9) Crear desviacion
$desviacion = $null
if ($token -and $nodo -and $nodo.nodo_id) {
    $desvBody = @{ nodo_id = $nodo.nodo_id; palabra_guia = 'Alta'; parametro = 'Presion'; descripcion = 'Desviacion ejemplo' } | ConvertTo-Json
    $desviacion = Try-Invoke 'Crear desviacion' { Invoke-RestMethod -Uri "$base/desviaciones" -Method Post -Body $desvBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 10) Crear pregunta whatif
$preg = $null
if ($token) {
    $pregBody = @{ pregunta = '¿Qué pasa si falla la bomba?' ; descripcion = 'Test whatif' } | ConvertTo-Json
    $preg = Try-Invoke 'Crear pregunta_whatif' { Invoke-RestMethod -Uri "$base/preguntas_whatif" -Method Post -Body $pregBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 11) Crear checklist item
$chk = $null
if ($token) {
    $chkBody = @{ categoria = 'Operación'; item = 'Verificar válvulas'; aplicable = $true; cumplido = $false } | ConvertTo-Json
    $chk = Try-Invoke 'Crear checklist_item' { Invoke-RestMethod -Uri "$base/checklist_items" -Method Post -Body $chkBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 12) Crear salvaguarda
$salv = $null
if ($token) {
    $salvBody = @{ estudio_id = ($estudio.estudio_id -as [int]); descripcion = 'Cierre automático'; tipo = 'Ingeniería'; eficacia = 'Alta' } | ConvertTo-Json
    $salv = Try-Invoke 'Crear salvaguarda' { Invoke-RestMethod -Uri "$base/salvaguardas" -Method Post -Body $salvBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 13) Crear recomendacion
$rec = $null
if ($token -and $estudio -and $estudio.estudio_id) {
    $recBody = @{ estudio_id = $estudio.estudio_id; descripcion = 'Instalar alarma'; prioridad = 2 } | ConvertTo-Json
    $rec = Try-Invoke 'Crear recomendacion' { Invoke-RestMethod -Uri "$base/recomendaciones" -Method Post -Body $recBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 14) Crear analisis
$analisis = $null
if ($token -and $metodologia -and $nodo -and $estudio) {
    $analBody = @{ estudio_id = $estudio.estudio_id; metodologia_id = $metodologia.metodologia_id; nodo_id = $nodo.nodo_id; descripcion = 'Analisis demo' } | ConvertTo-Json
    $analisis = Try-Invoke 'Crear analisis' { Invoke-RestMethod -Uri "$base/analisis" -Method Post -Body $analBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 15) Crear causa y consecuencia
$causa = $null; $cons = $null
if ($token -and $analisis -and $analisis.analisis_id) {
    $causaBody = @{ analisis_id = $analisis.analisis_id; descripcion = 'Fallo mecanico' } | ConvertTo-Json
    $causa = Try-Invoke 'Crear causa' { Invoke-RestMethod -Uri "$base/causas" -Method Post -Body $causaBody -ContentType 'application/json' -Headers (AuthHeaders $token) }

    $consBody = @{ analisis_id = $analisis.analisis_id; descripcion = 'Perdida produccion' } | ConvertTo-Json
    $cons = Try-Invoke 'Crear consecuencia' { Invoke-RestMethod -Uri "$base/consecuencias" -Method Post -Body $consBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 16) Crear historial recomendacion
$hist = $null
if ($token -and $rec -and $rec.recomendacion_id) {
    $histBody = @{ recomendacion_id = $rec.recomendacion_id; cambio = 'Creada via script'; usuario_id = $null } | ConvertTo-Json
    $hist = Try-Invoke 'Crear historial_recomendaciones' { Invoke-RestMethod -Uri "$base/historial_recomendaciones" -Method Post -Body $histBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
}

# 17) Crear risk matrix y una celda (celda requiere admin)
$matrix = $null; $cell = $null
if ($token) {
    $matBody = @{ estudio_id = ($estudio.estudio_id -as [int]); nombre = 'Matriz Demo'; descripcion = 'Demo' } | ConvertTo-Json
    $matrix = Try-Invoke 'Crear risk_matrix' { Invoke-RestMethod -Uri "$base/risk_matrices" -Method Post -Body $matBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
    if ($matrix -and $matrix.risk_matrix_id) {
        $cellBody = @{ matrix_id = $matrix.risk_matrix_id; fila = 1; columna = 1; nivel = 'Alto'; codigo = 'A1' } | ConvertTo-Json
        $cell = Try-Invoke 'Crear risk_matrix_cell' { Invoke-RestMethod -Uri "$base/risk_matrix_cells" -Method Post -Body $cellBody -ContentType 'application/json' -Headers (AuthHeaders $token) }
    }
}

# 18) Listados finales
Try-Invoke 'Listar estudios' { Invoke-RestMethod -Uri "$base/estudios" -Method Get -Headers (AuthHeaders $token) }
Try-Invoke 'Listar nodos' { Invoke-RestMethod -Uri "$base/nodos" -Method Get -Headers (AuthHeaders $token) }
Try-Invoke 'Listar recomendaciones' { Invoke-RestMethod -Uri "$base/recomendaciones" -Method Get -Headers (AuthHeaders $token) }
Try-Invoke 'Listar analisis' { Invoke-RestMethod -Uri "$base/analisis" -Method Get -Headers (AuthHeaders $token) }

Write-Host 'Pruebas finalizadas.' -ForegroundColor Magenta
Try-Invoke 'Listar analisis' { Invoke-RestMethod -Uri "$base/analisis" -Method Get -Headers (AuthHeaders $token) }

Write-Host 'Pruebas finalizadas.' -ForegroundColor Magenta
