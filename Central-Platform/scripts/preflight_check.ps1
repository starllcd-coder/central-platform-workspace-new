$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
Set-Location $projectRoot

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
  throw "Python venv not found at $python"
}

Write-Host "[1/3] Django system check..."
& $python manage.py check

Write-Host "[2/3] Pending migrations visibility..."
& $python manage.py showmigrations

Write-Host "[3/3] Python runtime validation..."
& $python --version | Out-Null

Write-Host "Preflight checks completed."
