# Palaiž backend + frontend un uzrauga abus — ja kāds apstājas, restartē automātiski.
# Palaišana: C:\Users\USER\kolekcija\start-all.ps1

$BackendDir   = "C:\Users\USER\kolekcija\backend"
$FrontendDir  = "C:\Users\USER\kolekcija\web"
$BackendPort  = 8001
$FrontendPort = 5173

function Start-Backend {
    $pids = (Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue).OwningProcess | Select-Object -Unique
    foreach ($p in $pids) { try { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue } catch {} }
    Start-Sleep -Seconds 1
    $cmd = "cd '$BackendDir'; `$env:PYTHONUTF8='1'; .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port $BackendPort --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd -WindowStyle Normal
}

function Start-Frontend {
    $pids = (Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue).OwningProcess | Select-Object -Unique
    foreach ($p in $pids) { try { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue } catch {} }
    Start-Sleep -Seconds 1
    $cmd = "cd '$FrontendDir'; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd -WindowStyle Normal
}

function Test-Port($port) {
    return ($null -ne (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue))
}

Write-Host "=== dargumi.lv serveri ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Port $BackendPort)) {
    Write-Host "Palaiž backend  (port $BackendPort)..." -ForegroundColor Yellow
    Start-Backend
    Start-Sleep -Seconds 6
} else {
    Write-Host "Backend jau darbojas (port $BackendPort)" -ForegroundColor Green
}

if (-not (Test-Port $FrontendPort)) {
    Write-Host "Palaiž frontend (port $FrontendPort)..." -ForegroundColor Yellow
    Start-Frontend
    Start-Sleep -Seconds 5
} else {
    Write-Host "Frontend jau darbojas (port $FrontendPort)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Lapa: http://localhost:$FrontendPort" -ForegroundColor White
Write-Host ""
Write-Host "Uzraudziba aktiva (pārbaude ik 30s). Ctrl+C lai apturetu." -ForegroundColor Gray
Write-Host ""

while ($true) {
    Start-Sleep -Seconds 30

    if (-not (Test-Port $BackendPort)) {
        Write-Host "$(Get-Date -Format 'HH:mm:ss')  Backend apstajas — restarte..." -ForegroundColor Red
        Start-Backend
        Start-Sleep -Seconds 6
        if (Test-Port $BackendPort) {
            Write-Host "$(Get-Date -Format 'HH:mm:ss')  Backend OK" -ForegroundColor Green
        } else {
            Write-Host "$(Get-Date -Format 'HH:mm:ss')  Backend nesaka!" -ForegroundColor Red
        }
    }

    if (-not (Test-Port $FrontendPort)) {
        Write-Host "$(Get-Date -Format 'HH:mm:ss')  Frontend apstajas — restarte..." -ForegroundColor Red
        Start-Frontend
        Start-Sleep -Seconds 5
        if (Test-Port $FrontendPort) {
            Write-Host "$(Get-Date -Format 'HH:mm:ss')  Frontend OK" -ForegroundColor Green
        } else {
            Write-Host "$(Get-Date -Format 'HH:mm:ss')  Frontend nesaka!" -ForegroundColor Red
        }
    }
}
