param(
  [string]$RepoRoot = "D:\Sera\sera-opc-os",
  [string]$RuntimeRoot = "D:\Sera\MessageIntelligence",
  [string]$WebotRoot = "D:\Sera\deps\webot",
  [switch]$InstallWebot,
  [ValidatePattern('^$|^(?:[01]\d|2[0-3]):[0-5]\d$')]
  [string]$DailyReportAt = ""
)

$ErrorActionPreference = "Stop"
$ServiceRoot = Join-Path $RepoRoot "services\sera-message-intelligence"
if (!(Test-Path $ServiceRoot)) { throw "Service root not found: $ServiceRoot" }

if (!(Get-Command python -ErrorAction SilentlyContinue)) { throw "Python 3.12+ is required" }
if (!(Get-Command docker -ErrorAction SilentlyContinue)) { throw "Docker Desktop / docker CLI is required" }

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
$Venv = Join-Path $RuntimeRoot ".venv"
if (!(Test-Path (Join-Path $Venv "Scripts\python.exe"))) {
  python -m venv $Venv
}
$PythonExe = Join-Path $Venv "Scripts\python.exe"
$PipExe = Join-Path $Venv "Scripts\pip.exe"

& $PythonExe -m pip install --upgrade pip
& $PipExe install -e "$ServiceRoot[dev]"

if (!(Test-Path $WebotRoot)) {
  if ($InstallWebot) {
    if (!(Get-Command git -ErrorAction SilentlyContinue)) { throw "git is required to install webot" }
    New-Item -ItemType Directory -Force -Path (Split-Path $WebotRoot -Parent) | Out-Null
    git clone https://github.com/GuMu599/webot.git $WebotRoot
  } else {
    Write-Warning "webot is not installed at $WebotRoot. Re-run with -InstallWebot or place a vetted checkout there."
  }
}

if (Test-Path (Join-Path $WebotRoot "requirements.txt")) {
  & $PipExe install -r (Join-Path $WebotRoot "requirements.txt")
}

$CoreEnv = Join-Path $ServiceRoot ".env"
if (!(Test-Path $CoreEnv)) {
  Copy-Item (Join-Path $ServiceRoot ".env.example") $CoreEnv
  Write-Warning "Created .env. Review SMI_INGEST_API_KEY and LLM settings before production use."
}
$CollectorEnv = Join-Path $ServiceRoot "serverwin.env"
if (!(Test-Path $CollectorEnv)) {
  Copy-Item (Join-Path $ServiceRoot "serverwin.env.example") $CollectorEnv
  Write-Warning "Created serverwin.env. Set SMI_WECHAT_ACCOUNT_ID and verify SMI_WEBOT_ROOT."
}

Push-Location $ServiceRoot
try {
  docker compose up -d postgres
} finally {
  Pop-Location
}

& (Join-Path $ServiceRoot "scripts\install-serverwin-core-task.ps1") -RepoRoot $RepoRoot -PythonExe $PythonExe
& (Join-Path $ServiceRoot "scripts\install-serverwin-task.ps1") -RepoRoot $RepoRoot -PythonExe $PythonExe
if ($DailyReportAt) {
  & (Join-Path $ServiceRoot "scripts\install-serverwin-report-task.ps1") -RepoRoot $RepoRoot -PythonExe $PythonExe -At $DailyReportAt
}

Write-Host "Bootstrap complete. Review .env and serverwin.env, then start the Core + Collector tasks."
Write-Host "Core: Sera Message Intelligence - Core"
Write-Host "Collector: Sera Message Intelligence - WeChat Collector"
if ($DailyReportAt) { Write-Host "Daily Brief: $DailyReportAt" } else { Write-Host "Daily Brief schedule not installed. Pass -DailyReportAt HH:mm when ready." }
Write-Host "Health: powershell -ExecutionPolicy Bypass -File scripts\health-check-serverwin.ps1"
