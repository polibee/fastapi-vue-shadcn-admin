[CmdletBinding()]
param(
    [string]$BaseUrl = "http://127.0.0.1:8013",
    [string]$ApiToken = "",
    [switch]$SkipDatabase,
    [switch]$CheckOpenApi,
    [string]$TestDatabaseUrl = ""
)

$ErrorActionPreference = "Stop"
$failures = [System.Collections.Generic.List[string]]::new()

function Test-Endpoint([string]$Path, [string]$Name, [hashtable]$Headers = @{}) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl$Path" -Headers $Headers
        if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 300) { $failures.Add("$Name returned $($response.StatusCode)") }
    } catch { $failures.Add("$Name failed") }
}

# This script is read-only by default. It does not migrate, seed, backup, restore, or restart services.
Test-Endpoint "/api/v1/health/live" "liveness"
Test-Endpoint "/api/v1/health/ready" "readiness"
if ($CheckOpenApi) {
    Test-Endpoint "/openapi.json" "openapi"
}

if ($ApiToken) {
    Test-Endpoint "/api/v1/health/detail" "health detail" @{ Authorization = "Bearer $ApiToken" }
}

if (-not $SkipDatabase -and -not $TestDatabaseUrl -and -not $env:TEST_DATABASE_URL) {
    $failures.Add("TEST_DATABASE_URL is required for database acceptance; use -SkipDatabase only for an API-only check")
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output "Production acceptance read-only checks passed."
