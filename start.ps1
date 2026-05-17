# Kolekcija — palaid abus serverus
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .\venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8001"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\web'; npm run dev"
Write-Host "Backend: http://localhost:8001"
Write-Host "Web:     http://localhost:5173"
Write-Host "API docs: http://localhost:8001/docs"
