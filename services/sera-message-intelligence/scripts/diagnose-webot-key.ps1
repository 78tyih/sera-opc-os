param(
  [Parameter(Mandatory=$true)]
  [string]$WebotRoot,
  [string]$ExpectedWindowsUser = "",
  [string]$WebotEnvFile = "",
  [int]$TailLines = 120
)

$ErrorActionPreference = "Stop"

function Get-ProcessOwner([Microsoft.Management.Infrastructure.CimInstance]$Process) {
  try {
    $owner = Invoke-CimMethod -InputObject $Process -MethodName GetOwner -ErrorAction Stop
    if ($owner.User) { return "$($owner.Domain)\$($owner.User)" }
  } catch {}
  return "unknown"
}

function UserMatches([string]$Owner, [string]$Expected) {
  if (!$Expected) { return $true }
  if ($Owner -eq "unknown") { return $false }
  $short = ($Owner -split '\\')[-1]
  return ($short -ieq $Expected) -or ($Owner -ieq $Expected)
}

Write-Host "=== Sera / WeBot key onboarding doctor ==="
if (!(Test-Path $WebotRoot)) {
  Write-Warning "[BLOCK] Webot root does not exist: $WebotRoot"
  exit 2
}
$root = (Resolve-Path $WebotRoot).Path
Write-Host "Webot root: $root"

$dll = Join-Path $root "native\windows\wx_key.dll"
if (Test-Path $dll) { Write-Host "[OK] wx_key.dll exists: $dll" }
else { Write-Warning "[BLOCK] wx_key.dll missing: $dll" }

$wechat = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('Weixin.exe','WeChat.exe') })
if ($wechat.Count -eq 0) {
  Write-Warning "[WAIT] No WeChat/Weixin process is running. Built-in onboarding will wait for login."
} elseif ($wechat.Count -gt 1) {
  Write-Warning "[BLOCK] Multiple WeChat/Weixin processes detected ($($wechat.Count)). Key onboarding must be one account at a time."
} else {
  Write-Host "[OK] Exactly one WeChat process is running."
}

foreach ($p in $wechat) {
  $owner = Get-ProcessOwner $p
  $matches = UserMatches $owner $ExpectedWindowsUser
  Write-Host ("  PID={0} name={1} session={2} owner={3} expectedOwner={4}" -f $p.ProcessId,$p.Name,$p.SessionId,$owner,$matches)
  if (!$matches) { Write-Warning "[BLOCK] WeChat process owner does not match expected identity user." }
}

if (!$WebotEnvFile) { $WebotEnvFile = Join-Path $root ".env" }
if (Test-Path $WebotEnvFile) {
  Write-Host "[OK] Webot env exists: $WebotEnvFile"
  $keyLine = Get-Content $WebotEnvFile | Where-Object { $_ -match '^WCDB_KEY=' } | Select-Object -Last 1
  if ($keyLine) {
    $value = ($keyLine -split '=',2)[1].Trim()
    if ($value -match '^[0-9A-Fa-f]{64}$') {
      Write-Host "[OK] WCDB_KEY is present and has valid 64-hex shape (value not displayed)."
    } else {
      Write-Warning "[BLOCK] WCDB_KEY exists but does not have 64-hex shape."
    }
  } else {
    Write-Warning "[WAIT] No WCDB_KEY is saved in the selected Webot env yet."
  }
} else {
  Write-Warning "[WAIT] Webot env not found: $WebotEnvFile"
}

$log = Join-Path $root "data\bot.log"
if (Test-Path $log) {
  Write-Host "--- recent key/onboarding log lines ---"
  Get-Content $log -Tail $TailLines |
    Where-Object { $_ -match '密钥|Hook|hook|KEY_|waiting|退出微信|重新登录|wx_key|WCDB|PID|timeout|超时' } |
    Select-Object -Last 40 |
    ForEach-Object { Write-Host $_ }
} else {
  Write-Warning "No bot log found at $log"
}

Write-Host "--- interpretation ---"
if ($wechat.Count -gt 1) {
  Write-Host "Close all non-target WeChat identities before retrying built-in key onboarding."
} elseif ($wechat.Count -eq 1) {
  Write-Host "If the UI spins for a long time, fully exit WeChat from the tray, confirm the process disappears, then relaunch only this account when the built-in onboarding asks."
} else {
  Write-Host "Start/login only the target WeChat identity when the built-in onboarding asks for it."
}
Write-Host "This doctor never prints or extracts key material."
