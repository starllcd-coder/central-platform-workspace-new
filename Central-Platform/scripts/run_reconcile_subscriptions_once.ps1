param(
  [int]$Limit = 500,
  [switch]$DryRun,
  [string]$LogFile = ""
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot

Set-Location $projectRoot

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
  throw "Python venv not found at $python"
}

if ([string]::IsNullOrWhiteSpace($LogFile)) {
  $logDir = Join-Path $projectRoot "release_logs"
  if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
  }
  $LogFile = Join-Path $logDir "subscription_reconcile.log"
}

$args = @("manage.py", "reconcile_subscriptions", "--limit", "$Limit")
if ($DryRun) {
  $args += "--dry-run"
}

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$stamp] running: $python $($args -join ' ')" | Tee-Object -FilePath $LogFile -Append | Out-Null

& $python @args 2>&1 | Tee-Object -FilePath $LogFile -Append

$endStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$endStamp] done" | Tee-Object -FilePath $LogFile -Append | Out-Null
