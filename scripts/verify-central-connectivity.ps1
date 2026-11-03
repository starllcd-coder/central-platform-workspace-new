param(
  [string]$CentralBaseUrl = "http://127.0.0.1:8000",
  [string]$ConnectorSecret = $env:CENTRAL_CONNECTOR_SECRET,
  [string]$DriveSphereTenant = "",
  [string]$StayLuxTenant = "",
  [string]$LaundrexTenant = "",
  [string]$PythonExecutable = "python",
  [switch]$RunConnectorPush
)

$ErrorActionPreference = "Stop"
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$CentralBaseUrl = $CentralBaseUrl.TrimEnd('/')

function Test-JsonEndpoint {
  param([string]$Name, [string]$Url, [string]$ExpectedKey)
  $payload = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 15
  if ($null -eq $payload.PSObject.Properties[$ExpectedKey]) {
    throw "$Name returned an unexpected response (missing $ExpectedKey)."
  }
  if ($ExpectedKey -eq "status" -and $payload.status -ne "ok") {
    throw "$Name reported an unhealthy status."
  }
  Write-Host "OK: $Name"
}

# Default mode is read-only. A passing preflight is not a complete booking test.
Test-JsonEndpoint "Central health" "$CentralBaseUrl/api/health/" "status"
Test-JsonEndpoint "Connector health" "$CentralBaseUrl/api/connectors/health/" "status"
Test-JsonEndpoint "Marketplace tenants" "$CentralBaseUrl/api/platform/tenants/" "results"
Test-JsonEndpoint "Marketplace listings" "$CentralBaseUrl/api/listings/" "results"

if ($RunConnectorPush) {
  if (-not $ConnectorSecret -or $ConnectorSecret -eq "dev-connector-secret") {
    throw "Provide a configured connector secret for tenant sync."
  }
  if (-not $DriveSphereTenant -or -not $StayLuxTenant -or -not $LaundrexTenant) {
    throw "Provide all three tenant codes explicitly before running tenant sync."
  }
  $jobs = @(
    @{ Name = "DriveSphere"; RelativePath = "DriveSphere/web"; Tenant = $DriveSphereTenant },
    @{ Name = "StayLux"; RelativePath = "StayLux/web"; Tenant = $StayLuxTenant },
    @{ Name = "Laundrex"; RelativePath = "Laundrex"; Tenant = $LaundrexTenant }
  )
  $envKeys = @("CENTRAL_PLATFORM_URL", "CENTRAL_CONNECTOR_SECRET", "CENTRAL_TENANT_CODE", "CENTRAL_CONNECTOR_SIGNED")
  $savedEnv = @{}
  foreach ($key in $envKeys) { $savedEnv[$key] = [Environment]::GetEnvironmentVariable($key, "Process") }
  try {
    foreach ($job in $jobs) {
      $workdir = Join-Path $workspaceRoot $job.RelativePath
      $venvPython = Join-Path $workdir ".venv/Scripts/python.exe"
      $runner = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { $PythonExecutable }
      Push-Location -LiteralPath $workdir
      try {
        $env:CENTRAL_PLATFORM_URL = $CentralBaseUrl
        $env:CENTRAL_CONNECTOR_SECRET = $ConnectorSecret
        $env:CENTRAL_TENANT_CODE = $job.Tenant
        $env:CENTRAL_CONNECTOR_SIGNED = "1"
        & $runner manage.py push_central_connector --kind tenant
        if ($LASTEXITCODE -ne 0) { throw "Tenant sync failed for $($job.Name)." }
        Write-Host "OK: $($job.Name) tenant sync"
      } finally { Pop-Location }
    }
  } finally {
    foreach ($key in $envKeys) { [Environment]::SetEnvironmentVariable($key, $savedEnv[$key], "Process") }
  }
}
Write-Host "Preflight completed. Provider booking creation and return status still require an end-to-end test."
