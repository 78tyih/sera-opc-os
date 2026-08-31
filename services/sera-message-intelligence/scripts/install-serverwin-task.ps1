param(
  [string]$RepoRoot = "D:\Sera\sera-opc-os",
  [string]$PythonExe = "python",
  [string]$TaskName = "Sera Message Intelligence - WeChat Collector"
)

# Backward-compatible single-account wrapper. New multi-account installs
# should call install-serverwin-wechat-instance.ps1 directly.
$ErrorActionPreference = "Stop"
$ServiceRoot = Join-Path $RepoRoot "services\sera-message-intelligence"
$EnvFile = Join-Path $ServiceRoot "serverwin.env"
if (!(Test-Path $EnvFile)) {
  Copy-Item (Join-Path $ServiceRoot "serverwin.env.example") $EnvFile
  Write-Warning "Created $EnvFile. Edit it before starting the task."
}

$Script = Join-Path $ServiceRoot "scripts\run_serverwin_wechat_collector.py"
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$Script`" --env `"$EnvFile`"" -WorkingDirectory $ServiceRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Seconds 0)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Host "Installed scheduled task: $TaskName"
