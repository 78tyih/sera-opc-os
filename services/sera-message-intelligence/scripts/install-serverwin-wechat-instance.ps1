param(
  [string]$RepoRoot = "D:\Sera\sera-opc-os",
  [string]$PythonExe = "python",
  [Parameter(Mandatory=$true)]
  [ValidatePattern('^[A-Za-z0-9._-]+$')]
  [string]$InstanceName,
  [Parameter(Mandatory=$true)]
  [string]$EnvFile
)

$ErrorActionPreference = "Stop"
$ServiceRoot = Join-Path $RepoRoot "services\sera-message-intelligence"
$Script = Join-Path $ServiceRoot "scripts\run_serverwin_wechat_collector.py"
if (!(Test-Path $Script)) { throw "Collector script not found: $Script" }
if (!(Test-Path $EnvFile)) { throw "Instance env file not found: $EnvFile" }
$ResolvedEnv=(Resolve-Path $EnvFile).Path
$TaskName="Sera Message Intelligence - WeChat - $InstanceName"

$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$Script`" --env `"$ResolvedEnv`"" -WorkingDirectory $ServiceRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Seconds 0)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Host "Installed WeChat collector instance: $InstanceName"
Write-Host "Task: $TaskName"
Write-Host "Env: $ResolvedEnv"
