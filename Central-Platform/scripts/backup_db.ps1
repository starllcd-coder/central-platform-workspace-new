param(
  [string]$BackupDir = "",
  [ValidateSet("auto", "sqlite", "postgresql")]
  [string]$Backend = "auto",
  [switch]$CentralOnly,
  [int]$RetentionDays = 14,
  [string]$PostgresContainer = "central_platform_db"
)

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
Set-Location $projectRoot

function Get-ConfigValue([string]$Name, [string]$Default = "") {
  $environmentValue = [Environment]::GetEnvironmentVariable($Name)
  if (-not [string]::IsNullOrWhiteSpace($environmentValue)) { return $environmentValue }
  $envPath = Join-Path $projectRoot ".env"
  if (Test-Path -LiteralPath $envPath) {
    $line = Get-Content -LiteralPath $envPath | Where-Object { $_ -match "^$([regex]::Escape($Name))=" } | Select-Object -First 1
    if ($line) { return ($line -split "=", 2)[1].Trim().Trim('"').Trim("'") }
  }
  return $Default
}

if ($Backend -eq "auto") {
  $configuredBackend = (Get-ConfigValue "DJANGO_DB_BACKEND" "sqlite").ToLowerInvariant()
  $Backend = if ($configuredBackend -in @("postgres", "postgresql", "psql")) { "postgresql" } else { "sqlite" }
}

if ([string]::IsNullOrWhiteSpace($BackupDir)) {
  $BackupDir = Join-Path $env:USERPROFILE "CentralPlatformBackups"
}
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$runDir = Join-Path $BackupDir $stamp
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$resolvedBackupRoot = (Resolve-Path -LiteralPath $BackupDir).Path.TrimEnd('\', '/')
if ([IO.Path]::GetPathRoot($resolvedBackupRoot).TrimEnd('\', '/') -eq $resolvedBackupRoot) {
  throw "BackupDir cannot be a filesystem root."
}

$manifest = [ordered]@{
  created_at = (Get-Date).ToUniversalTime().ToString("o")
  backend = $Backend
  files = @()
}

if ($Backend -eq "sqlite") {
  $dbPath = Join-Path $projectRoot "db.sqlite3"
  if (-not (Test-Path -LiteralPath $dbPath)) { throw "Database file not found: $dbPath" }
  $target = Join-Path $runDir "central.sqlite3"
  Copy-Item -LiteralPath $dbPath -Destination $target -Force
  $manifest.files += @{ database = "central"; file = (Split-Path -Leaf $target) }
} else {
  $dbName = Get-ConfigValue "DJANGO_DB_NAME" "central_platform"
  $dbUser = Get-ConfigValue "DJANGO_DB_USER" "central"
  $running = (& docker inspect -f "{{.State.Running}}" $PostgresContainer 2>$null)
  if ($LASTEXITCODE -ne 0 -or $running -ne "true") {
    throw "PostgreSQL container '$PostgresContainer' is not running."
  }

  $databases = @($dbName)
  if (-not $CentralOnly) {
    $query = "SELECT DISTINCT database_name FROM tenants_tenantdatabaseconfiguration WHERE mode='managed' AND engine='postgresql' AND status='ready' AND database_name <> '';"
    $tenantDatabases = & docker exec $PostgresContainer psql -U $dbUser -d $dbName -At -c $query
    if ($LASTEXITCODE -ne 0) { throw "Unable to inventory managed tenant databases." }
    $databases += @($tenantDatabases | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  }

  foreach ($database in ($databases | Sort-Object -Unique)) {
    if ($database -notmatch '^[A-Za-z0-9_]+$') { throw "Unsafe database name returned by inventory: $database" }
    $fileName = "${database}_${stamp}.dump"
    $containerPath = "/tmp/$fileName"
    $target = Join-Path $runDir $fileName
    & docker exec $PostgresContainer pg_dump -U $dbUser -d $database -Fc -f $containerPath
    if ($LASTEXITCODE -ne 0) { throw "pg_dump failed for database '$database'." }
    try {
      & docker cp "${PostgresContainer}:${containerPath}" $target
      if ($LASTEXITCODE -ne 0) { throw "docker cp failed for database '$database'." }
    } finally {
      & docker exec $PostgresContainer rm -f $containerPath | Out-Null
    }
    $manifest.files += @{
      database = $database
      file = $fileName
      sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash
    }
  }
}

$manifestPath = Join-Path $runDir "manifest.json"
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding utf8
Write-Host "Backup completed: $runDir"

if ($RetentionDays -gt 0) {
  $cutoff = (Get-Date).AddDays(-1 * $RetentionDays)
  $expiredDirectories = Get-ChildItem -LiteralPath $BackupDir -Directory |
    Where-Object { $_.LastWriteTime -lt $cutoff -and $_.Name -match '^\d{8}_\d{6}$' }
  foreach ($directory in $expiredDirectories) {
    $resolvedDirectory = $directory.FullName.TrimEnd('\', '/')
    if (-not $resolvedDirectory.StartsWith("$resolvedBackupRoot$([IO.Path]::DirectorySeparatorChar)")) {
      throw "Refusing retention cleanup outside backup root: $resolvedDirectory"
    }
    Remove-Item -LiteralPath $resolvedDirectory -Recurse -Force
  }
  Write-Host "Retention cleanup complete (days=$RetentionDays)."
}
