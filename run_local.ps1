# Local fallback check-in, invoked by Windows scheduled task / logon Run key.
# ASCII-only on purpose: Windows PowerShell 5.1 reads .ps1 as ANSI, non-ASCII may break parsing.
param(
    [int]$MaxDelayMin = 0,
    [switch]$LogonMode
)

$ErrorActionPreference = 'Continue'
$base = 'C:\Users\xx\Documents\deepseek-harness\default-workspace\telegram-checkin'
$py = 'C:\Users\xx\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
$logDir = Join-Path $base 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ('checkin-' + (Get-Date -Format 'yyyyMMdd') + '.log')

if ($LogonMode) {
    # wait 2 minutes after logon to avoid competing with startup apps
    Start-Sleep -Seconds 120
}

if ($MaxDelayMin -gt 0) {
    $sec = Get-Random -Minimum 0 -Maximum ($MaxDelayMin * 60)
    Start-Sleep -Seconds $sec
    "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') start (random delay ${sec}s) ===" | Add-Content -Path $log -Encoding utf8
} else {
    "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') start ===" | Add-Content -Path $log -Encoding utf8
}

try {
    $c = Get-Content (Join-Path $base 'config.json') -Raw | ConvertFrom-Json
    $env:TG_API_ID = "$($c.api_id)"
    $env:TG_API_HASH = $c.api_hash
    $env:TG_SESSION = (Get-Content (Join-Path $base 'session_string.txt') -Raw).Trim()
    $env:TG_PROXY = 'http://127.0.0.1:10808'
    $env:PYTHONIOENCODING = 'utf-8'

    & $py (Join-Path $base 'checkin.py') 2>&1 | Add-Content -Path $log -Encoding utf8
    $code = $LASTEXITCODE
    "exit=$code" | Add-Content -Path $log -Encoding utf8

    if ($code -ne 0) {
        $env:NOTIFY_TEXT = "WARN: local fallback check-in failed (exit=$code), check proxy / bot rules. Log: $log"
        & $py (Join-Path $base 'notify.py') 2>&1 | Add-Content -Path $log -Encoding utf8
    }
} catch {
    "ERROR: $_" | Add-Content -Path $log -Encoding utf8
}
