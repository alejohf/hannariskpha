$ErrorActionPreference = 'Stop'
$base = 'http://127.0.0.1:8092/api'
$creds = @{ username = 'admin'; password = 'pa$$wr0rd' }

Write-Host "== Validating backend ($base) =="
try {
    Write-Host "Attempting login..."
    $login = Invoke-RestMethod -Uri "$base/auth/login" -Method Post -Body ($creds | ConvertTo-Json) -ContentType 'application/json'
    Write-Host "LOGIN RESULT:" -ForegroundColor Green
    $login | ConvertTo-Json -Depth 5 | Write-Host

    if ($login.access_token) {
        $token = $login.access_token
        Write-Host "Got token, fetching /estudios..."
        $hdr = @{ Authorization = "Bearer $token" }
        $est = Invoke-RestMethod -Uri "$base/estudios" -Method Get -Headers $hdr
        Write-Host "ESTUDIOS:" -ForegroundColor Green
        $est | ConvertTo-Json -Depth 5 | Write-Host
    } else {
        Write-Host "No access_token returned." -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    if ($_.Exception.Response -ne $null) {
        try { Write-Host "HTTP Response:"; $_.Exception.Response | Format-List -Force } catch {}
    }
}
