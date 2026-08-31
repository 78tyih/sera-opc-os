param(
  [ValidateSet('status','doctor','start-current','stop-current','key-doctor')]
  [string]$Action = 'status',
  [string]$ManifestPath = '',
  [string]$InstanceName = ''
)

$ErrorActionPreference = 'Stop'
$ServiceRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (!$ManifestPath) { $ManifestPath = Join-Path $ServiceRoot 'instances\wechat-runtime.example.json' }
if (!(Test-Path $ManifestPath)) { throw "Runtime manifest not found: $ManifestPath" }
$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
if ($manifest.schema_version -ne 1) { throw "Unsupported runtime manifest schema_version=$($manifest.schema_version)" }

function Get-Owner([Microsoft.Management.Infrastructure.CimInstance]$Process) {
  try {
    $o = Invoke-CimMethod -InputObject $Process -MethodName GetOwner -ErrorAction Stop
    if ($o.User) { return "$($o.Domain)\$($o.User)" }
  } catch {}
  return 'unknown'
}

function OwnerMatches([string]$Owner,[string]$User) {
  if ($Owner -eq 'unknown') { return $false }
  return (($Owner -split '\\')[-1] -ieq $User) -or ($Owner -ieq $User)
}

function Get-WeChatProcesses {
  return @(Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('Weixin.exe','WeChat.exe') })
}

$instances = @($manifest.instances | Where-Object { $_.enabled -eq $true })
if ($InstanceName) {
  $instances = @($instances | Where-Object { $_.name -eq $InstanceName })
  if ($instances.Count -eq 0) { throw "Enabled instance not found: $InstanceName" }
}

if ($Action -eq 'status') {
  $all = Get-WeChatProcesses
  $rows = foreach ($i in $instances) {
    $owned = @($all | Where-Object { OwnerMatches (Get-Owner $_) $i.windows_user })
    $taskName = "Sera Message Intelligence - WeChat - $($i.name)"
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    [pscustomobject]@{
      instance = $i.name
      windows_user = $i.windows_user
      wechat_processes = $owned.Count
      pids = ($owned.ProcessId -join ',')
      collector_task = if ($task) { $task.State } else { 'missing' }
      collector_env = $i.collector_env
      expected_wxid_dir = $i.expected_wxid_dir
    }
  }
  $rows | Format-Table -AutoSize
  exit 0
}

if ($Action -eq 'doctor') {
  foreach ($i in $instances) {
    Write-Host "=== $($i.name) ==="
    if (Test-Path $i.wechat_executable) { Write-Host '[OK] WeChat executable' } else { Write-Warning "[BLOCK] WeChat executable missing: $($i.wechat_executable)" }
    if (Test-Path $i.webot_root) { Write-Host '[OK] Webot root' } else { Write-Warning "[BLOCK] Webot root missing: $($i.webot_root)" }
    if (Test-Path $i.collector_env) { Write-Host '[OK] collector env' } else { Write-Warning "[BLOCK] collector env missing: $($i.collector_env)" }
    if (Test-Path $i.webot_env_file) { Write-Host '[OK] webot env' } else { Write-Warning "[WAIT] webot env not created yet: $($i.webot_env_file)" }
    $taskName = "Sera Message Intelligence - WeChat - $($i.name)"
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) { Write-Host "[OK] collector task: $($task.State)" } else { Write-Warning "[WAIT] collector task missing: $taskName" }
  }
  exit 0
}

if ($instances.Count -ne 1) { throw 'start-current, stop-current and key-doctor require exactly one -InstanceName' }
$i = $instances[0]
$current = $env:USERNAME
if ($Action -in @('start-current','stop-current') -and $current -ine $i.windows_user) {
  throw "Current Windows user '$current' does not own instance '$($i.name)' (expected '$($i.windows_user)'). Switch to that Windows user first."
}

if ($Action -eq 'start-current') {
  if (!(Test-Path $i.wechat_executable)) { throw "WeChat executable missing: $($i.wechat_executable)" }
  Start-Process -FilePath $i.wechat_executable
  Write-Host "Started WeChat normally for current Windows user: $current"
  Write-Host 'No single-instance bypass or client patch was used.'
  exit 0
}

if ($Action -eq 'stop-current') {
  $owned = @(Get-WeChatProcesses | Where-Object { OwnerMatches (Get-Owner $_) $i.windows_user })
  foreach ($p in $owned) { Stop-Process -Id $p.ProcessId -ErrorAction SilentlyContinue }
  Write-Host "Stopped $($owned.Count) WeChat process(es) owned by $($i.windows_user)."
  exit 0
}

if ($Action -eq 'key-doctor') {
  $doctor = Join-Path $PSScriptRoot 'diagnose-webot-key.ps1'
  & $doctor -WebotRoot $i.webot_root -ExpectedWindowsUser $i.windows_user -WebotEnvFile $i.webot_env_file
  if ($LASTEXITCODE) { exit $LASTEXITCODE }
  exit 0
}
