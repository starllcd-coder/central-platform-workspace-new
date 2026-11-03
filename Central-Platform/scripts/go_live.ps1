param(
  [string]$TargetEnvironment = "production",
  [string]$BaseUrl = "",
  [switch]$Notify,
  [string]$NotifyRecipient = "ops",
  [string]$NotifyChannel = "in_app",
  [switch]$SkipBackup,
  [switch]$SkipPreflight,
  [switch]$SkipSmoke
)

$ErrorActionPreference = "Stop"

function Get-StatusCodeFromError {
  param([object]$ErrorRecord)
  try {
    return [int]$ErrorRecord.Exception.Response.StatusCode.value__
  } catch {
    return -1
  }
}

function Test-Endpoint {
  param(
    [string]$Url,
    [int[]]$AllowedStatusCodes
  )

  try {
    $response = Invoke-WebRequest -Uri $Url -Method Get -MaximumRedirection 0 -ErrorAction Stop
    $statusCode = [int]$response.StatusCode
  } catch {
    $statusCode = Get-StatusCodeFromError -ErrorRecord $_
  }

  $ok = $AllowedStatusCodes -contains $statusCode
  [PSCustomObject]@{
    Url = $Url
    StatusCode = $statusCode
    Passed = $ok
  }
}

function Send-GoLiveNotification {
  param(
    [string]$PythonPath,
    [string]$Channel,
    [string]$Recipient,
    [string]$Subject,
    [string]$Body,
    [string]$EnvironmentName,
    [string]$StatusValue,
    [string]$ReleaseLogPath
  )

  if (-not (Test-Path -LiteralPath $PythonPath)) {
    throw "Python venv not found at $PythonPath"
  }

  $tmpFile = Join-Path $env:TEMP ("central_platform_notify_" + [Guid]::NewGuid().ToString("N") + ".py")
  $safeSubject = $Subject.Replace("`"", "'")
  $safeBody = $Body.Replace("`"", "'")
  $safeRecipient = $Recipient.Replace("`"", "'")
  $safeChannel = $Channel.Replace("`"", "'")
  $safeEnv = $EnvironmentName.Replace("`"", "'")
  $safeStatus = $StatusValue.Replace("`"", "'")
  $safeReleaseLog = $ReleaseLogPath.Replace("\", "\\").Replace("`"", "'")

  $py = @"
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from apps.ops.services import queue_notification
queue_notification(
    channel="$safeChannel",
    recipient="$safeRecipient",
    subject="$safeSubject",
    body="$safeBody",
    context={
        "environment": "$safeEnv",
        "status": "$safeStatus",
        "release_log": "$safeReleaseLog",
    },
)
print("notification_queued")
"@
  Set-Content -LiteralPath $tmpFile -Value $py -Encoding UTF8
  try {
    & $PythonPath $tmpFile
  } finally {
    if (Test-Path -LiteralPath $tmpFile) {
      Remove-Item -LiteralPath $tmpFile -Force
    }
  }
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
Set-Location $projectRoot

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$releaseDir = Join-Path $projectRoot "release_logs"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
$releaseLog = Join-Path $releaseDir ("go_live_" + $timestamp + ".log")

function Write-ReleaseLog {
  param([string]$Message)
  $line = ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message)
  Write-Host $line
  Add-Content -LiteralPath $releaseLog -Value $line -Encoding UTF8
}

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$runStatus = "success"
$failureMessage = ""

try {
  Write-ReleaseLog "Go-live started. Environment=$TargetEnvironment"

  $deployScript = Join-Path $scriptRoot "deploy_release.ps1"
  $deployArgs = @()
  if ($SkipPreflight) { $deployArgs += "-SkipPreflight" }
  if ($SkipBackup) { $deployArgs += "-SkipBackup" }

  Write-ReleaseLog "Running deployment helper..."
  if ($deployArgs.Count -gt 0) {
    & $deployScript @deployArgs
  } else {
    & $deployScript
  }
  Write-ReleaseLog "Deployment helper finished."

  if (-not $SkipSmoke) {
    if (-not [string]::IsNullOrWhiteSpace($BaseUrl)) {
      $base = $BaseUrl.TrimEnd("/")
      Write-ReleaseLog "Running HTTP smoke checks against $base"
      $checks = @(
        (Test-Endpoint -Url "$base/accounts/login/" -AllowedStatusCodes @(200)),
        (Test-Endpoint -Url "$base/" -AllowedStatusCodes @(200, 301, 302)),
        (Test-Endpoint -Url "$base/billing/disputes/?status=pending" -AllowedStatusCodes @(200, 301, 302))
      )

      foreach ($c in $checks) {
        if ($c.Passed) {
          Write-ReleaseLog "SMOKE PASS: $($c.Url) -> $($c.StatusCode)"
        } else {
          Write-ReleaseLog "SMOKE FAIL: $($c.Url) -> $($c.StatusCode)"
          throw "Smoke check failed for $($c.Url)"
        }
      }
    } else {
      Write-ReleaseLog "BaseUrl not provided; running local smoke checks."
      if (-not (Test-Path -LiteralPath $python)) {
        throw "Python venv not found at $python"
      }
      & $python manage.py check
      & $python manage.py showmigrations | Out-Null
      Write-ReleaseLog "Local smoke checks passed."
    }
  }

  Write-ReleaseLog "Go-live completed successfully."
} catch {
  $runStatus = "failed"
  $failureMessage = $_.Exception.Message
  Write-ReleaseLog "Go-live failed: $failureMessage"
  throw
} finally {
  if ($Notify) {
    $subject = "Go-live $runStatus ($TargetEnvironment)"
    if ($runStatus -eq "success") {
      $body = "Go-live completed successfully. Environment=$TargetEnvironment. Release log: $releaseLog"
    } else {
      $body = "Go-live failed. Environment=$TargetEnvironment. Error: $failureMessage. Release log: $releaseLog"
    }
    try {
      Send-GoLiveNotification `
        -PythonPath $python `
        -Channel $NotifyChannel `
        -Recipient $NotifyRecipient `
        -Subject $subject `
        -Body $body `
        -EnvironmentName $TargetEnvironment `
        -StatusValue $runStatus `
        -ReleaseLogPath $releaseLog
      Write-ReleaseLog "Go-live notification queued for recipient '$NotifyRecipient'."
    } catch {
      Write-ReleaseLog "WARNING: unable to queue go-live notification. $($_.Exception.Message)"
    }
  }
  Write-Host "Release log: $releaseLog"
}
