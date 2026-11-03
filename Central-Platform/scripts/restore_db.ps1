param(
  [Parameter(Mandatory = $true)]
  [string]$BackupFile,
  [ValidateSet("auto", "sqlite", "postgresql")]
  [string]$Backend = "auto",
  [string]$DatabaseName = "",
  [string]$PostgresContainer = "central_platform_db",
  [switch]$StopApplication,
  [switch]$Force
)

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
Set-Location $projectRoot

if (-not $Force) { throw "Restore is destructive. Re-run with -Force after validating the backup and target." }
if (-not (Test-Path -LiteralPath $BackupFile)) { throw "Backup file not found: $BackupFile" }
$resolvedBackup = (Resolve-Path -LiteralPath $BackupFile).Path

if ($Backend -eq "auto") {
  $Backend = if ([IO.Path]::GetExtension($resolvedBackup) -eq ".dump") { "postgresql" } else { "sqlite" }
}

if ($Backend -eq "sqlite") {
  $dbPath = Join-Path $projectRoot "db.sqlite3"
  Copy-Item -LiteralPath $resolvedBackup -Destination $dbPath -Force
  Write-Host "SQLite database restored to: $dbPath"
  exit 0
}

if ([string]::IsNullOrWhiteSpace($DatabaseName)) {
  throw "-DatabaseName is required for PostgreSQL restores."
}
if ($DatabaseName -notmatch '^[A-Za-z0-9_]+$') { throw "Unsafe database name: $DatabaseName" }

$dbUser = [Environment]::GetEnvironmentVariable("DJANGO_DB_USER")
if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = "central" }
$containerPath = "/tmp/central_platform_restore.dump"
$stopped = $false

try {
  if ($StopApplication) {
    & docker compose stop web celery-worker celery-beat
    if ($LASTEXITCODE -ne 0) { throw "Unable to stop application services." }
    $stopped = $true
  }
  & docker cp $resolvedBackup "${PostgresContainer}:${containerPath}"
  if ($LASTEXITCODE -ne 0) { throw "Unable to copy backup into PostgreSQL container." }
  & docker exec $PostgresContainer pg_restore -U $dbUser -d $DatabaseName --clean --if-exists --no-owner --exit-on-error $containerPath
  if ($LASTEXITCODE -ne 0) { throw "pg_restore failed for database '$DatabaseName'." }
  Write-Host "PostgreSQL database restored: $DatabaseName"
} finally {
  & docker exec $PostgresContainer rm -f $containerPath 2>$null | Out-Null
  if ($stopped) { & docker compose start web celery-worker celery-beat }
}
