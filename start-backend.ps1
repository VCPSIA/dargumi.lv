# Backend rit WSL terminali — šis skripts NEDER WSL procesa apturēšanai.
#
# Lai restartētu backendu:
# 1. Atver WSL termināli kur backend rit
# 2. Ctrl+C
# 3. Palaid: cd /mnt/c/Users/USER/kolekcija/backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
#
# Vai ja backend rit Windows (ne WSL):
$pids = (Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue).OwningProcess | Select-Object -Unique
foreach ($p in $pids) {
    try { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue } catch {}
}
Start-Sleep -Seconds 1
$env:PYTHONUTF8 = "1"
Set-Location "C:\Users\USER\kolekcija\backend"
.\venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8001 --reload
