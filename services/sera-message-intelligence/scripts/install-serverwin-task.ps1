param(
  [string]$RepoRoot = "D:\Sera\sera-opc-os",
  [string]$PythonExe = "python",
  [string]$TaskName = "Sera Message Intelligence - WeChat Collector"
)

$ErrorActionPreference = "Stop"
$ServiceRoot = Join-Path $RepoRoot "services\sera-message-intelligence"
$Script = Join-Path $ServiceRoot "scripts\run_serverwin_wechat_collector.py"
$EnvFile = Join-Path $ServiceRoot "serverwin.env"

if (!(Test-Path $Script)) { throw "Collector script not found: $Script" }
if (!(Test-Path $EnvFile)) {
  Copy-Item (Join-Path $ServiceRoot "serverwin.env.example") $EnvFile
  Write-Warning "Created $EnvFile. Edit it before starting the task."
}

$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$Script`"" -WorkingDirectory $ServiceRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Seconds 0)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Host "Installed scheduled task: $TaskName"
Write-Host "After editing serverwin.env, run: Start-ScheduledTask -TaskName `"$TaskName`""
