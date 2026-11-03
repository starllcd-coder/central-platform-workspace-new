param(
  [string]$TaskName = "CentralPlatform-ReconcileSubscriptions",
  [string]$ScheduleUser = $env:USERNAME,
  [string]$AtTime = "01:15",
  [int]$Limit = 500,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptRoot "run_reconcile_subscriptions_once.ps1"

if (-not (Test-Path -LiteralPath $runner)) {
  throw "Runner script not found: $runner"
}

$arg = "-NoProfile -ExecutionPolicy Bypass -File `"$runner`" -Limit $Limit"
if ($DryRun) {
  $arg += " -DryRun"
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg
$trigger = New-ScheduledTaskTrigger -Daily -At ([datetime]::Parse($AtTime))
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -User $ScheduleUser -RunLevel Highest -Force | Out-Null

Write-Host "Scheduled task '$TaskName' registered (daily at $AtTime)."
Write-Host "Runner: $runner"
Write-Host "Limit: $Limit | DryRun: $DryRun"
