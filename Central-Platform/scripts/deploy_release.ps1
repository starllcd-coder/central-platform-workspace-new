param(
  [ValidateSet("staging", "production")]
  [string]$Environment,
  [Parameter(Mandatory = $true)]
  [string]$Revision,
  [string]$DeployPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
  [string]$HealthUrl = "http://127.0.0.1:8000/healthz/",
  [switch]$SkipPreviousRevisionRecord
)

$ErrorActionPreference = "Stop"
$stateDirectory = Join-Path $DeployPath ".deployments\$Environment"
$previousRevisionFile = Join-Path $stateDirectory "previous_revision.txt"

Push-Location $DeployPath
try {
  if (-not (Test-Path "docker-compose.yml")) {
    throw "docker-compose.yml was not found in $DeployPath"
  }

  $currentRevision = (git rev-parse HEAD).Trim()
  git fetch --tags --prune
  git rev-parse --verify "$Revision^{commit}" | Out-Null

  if (-not $SkipPreviousRevisionRecord) {
    New-Item -ItemType Directory -Force -Path $stateDirectory | Out-Null
    Set-Content -LiteralPath $previousRevisionFile -Value $currentRevision -NoNewline
  }

  git checkout --detach $Revision
  docker compose up -d --build --remove-orphans

  $healthy = $false
  for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
      $response = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 5
      if ($response.status -eq "ok") {
        $healthy = $true
        break
      }
    } catch {
      Start-Sleep -Seconds 5
    }
  }
  if (-not $healthy) {
    throw "Deployment health check failed: $HealthUrl"
  }

  Write-Host "Deployed $Revision to $Environment successfully."
} finally {
  Pop-Location
}
