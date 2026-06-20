# Start lightweight mock API for frontend demo (Python 3.13 friendly).
# From repo root:
#   .\backend\scripts\start_mock_demo.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "Installing mock API deps (fastapi + uvicorn only)..." -ForegroundColor Cyan
python -m pip install -r requirements-mock.txt

Write-Host "Starting mock API at http://127.0.0.1:8000/api/v1" -ForegroundColor Green
Write-Host "In the frontend, turn OFF Mock mode in the header to use this server." -ForegroundColor Yellow
python scripts/mock_api_server.py
