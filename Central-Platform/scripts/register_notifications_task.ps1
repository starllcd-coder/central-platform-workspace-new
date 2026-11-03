param(
  [string]$TaskName = "CentralPlatform-ProcessNotifications",
  [string]$ScheduleUser = $env:USERNAME
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
$runner = Join-Path $scriptRoot "run_notifications_once.ps1"

if (-not (Test-Path -LiteralPath $runner)) {
  throw "Runner script not found: $runner"
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
  -RepetitionInterval (New-TimeSpan -Minutes 1) `
  -RepetitionDuration ([TimeSpan]::MaxValue)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -User $ScheduleUser -RunLevel Highest -Force | Out-Null

Write-Host "Scheduled task '$TaskName' registered to process notifications every minute."
