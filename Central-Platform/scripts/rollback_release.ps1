param(
  [ValidateSet("staging", "production")]
  [string]$Environment = "production",
  [string]$Revision = "",
  [string]$DeployPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
  [string]$HealthUrl = "http://127.0.0.1:8000/healthz/"
)

$ErrorActionPreference = "Stop"
$previousRevisionFile = Join-Path $DeployPath ".deployments\$Environment\previous_revision.txt"
if (-not $Revision) {
  if (-not (Test-Path -LiteralPath $previousRevisionFile)) {
    throw "No previous revision is recorded for $Environment. Pass -Revision explicitly."
  }
  $Revision = (Get-Content -LiteralPath $previousRevisionFile -Raw).Trim()
}
if (-not $Revision) {
  throw "Rollback revision cannot be empty."
}

& (Join-Path $PSScriptRoot "deploy_release.ps1") `
  -Environment $Environment `
  -Revision $Revision `
  -DeployPath $DeployPath `
  -HealthUrl $HealthUrl `
  -SkipPreviousRevisionRecord

Write-Host "Rollback to $Revision completed. Database migrations were not reversed."
