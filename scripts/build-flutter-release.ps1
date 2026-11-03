param(
  [Parameter(Mandatory=$true)][ValidateSet("drivesphere-customer","drivesphere-staff","staylux-customer","staylux-owner")][string]$App,
  [Parameter(Mandatory=$true)][string]$ProductBaseUrl,
  [ValidateSet("apk","appbundle","web","windows")][string]$Target="apk"
)
$ErrorActionPreference="Stop"
$targetUri=[Uri]$ProductBaseUrl
if ($targetUri.Scheme -ne "https" -or $targetUri.Host -in @("localhost","127.0.0.1") -or $targetUri.Host.EndsWith(".invalid")) { throw "A real HTTPS product backend URL is required for a release build." }
if ($targetUri.AbsolutePath -ne "/" -or $targetUri.Query -or $targetUri.Fragment) { throw "Use the product's base origin; the script adds the appropriate API prefix." }
$root=Split-Path -Parent $PSScriptRoot
$baseUrl=$ProductBaseUrl.TrimEnd('/')
$jobs=@{
 "drivesphere-customer"=@{Path="DriveSphere/mobile/drivesphere_app";Define="API_BASE_URL=$baseUrl/api"}
 "drivesphere-staff"=@{Path="DriveSphere/mobile/drivesphere_staff_app";Define="API_BASE_URL=$baseUrl/api/v1"}
 "staylux-customer"=@{Path="StayLux/mobile";Define="STAYLUX_API_BASE_URL=$baseUrl/api/mobile"}
 "staylux-owner"=@{Path="StayLux/owner_admin_app";Define="STAYLUX_API_BASE_URL=$baseUrl"}
}
Get-Command flutter -ErrorAction Stop | Out-Null
$job=$jobs[$App]
Push-Location (Join-Path $root $job.Path)
try {
 & flutter pub get
 if ($LASTEXITCODE -ne 0) { throw "Flutter dependencies failed." }
 & flutter analyze
 if ($LASTEXITCODE -ne 0) { throw "Flutter analysis failed." }
 & flutter test
 if ($LASTEXITCODE -ne 0) { throw "Flutter tests failed." }
 & flutter build $Target --release "--dart-define=$($job.Define)" --dart-define=APP_ENV=Production
 if ($LASTEXITCODE -ne 0) { throw "Flutter release build failed." }
} finally { Pop-Location }
