param(
  [string]$RepoRoot = "D:\Sera\sera-opc-os",
  [string]$PythonExe = "python",
  [string]$TaskName = "Sera Message Intelligence - Core"
)

$ErrorActionPreference = "Stop"
$ServiceRoot = Join-Path $RepoRoot "services\sera-message-intelligence"
if (!(Test-Path $ServiceRoot)) { throw "Service root not found: $ServiceRoot" }

$Action = New-ScheduledTaskAction `
  -Execute $PythonExe `
  -Argument "-m uvicorn sera_message_intelligence.main:app --host 127.0.0.1 --port 8800" `
  -WorkingDirectory $ServiceRoot

$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Settings = New-ScheduledTaskSettingsSet `
  -StartWhenAvailable `
  -RestartCount 999 `
  -RestartInterval (New-TimeSpan -Minutes 1) `
  -MultipleInstances IgnoreNew `
  -ExecutionTimeLimit (New-TimeSpan -Seconds 0)
$Principal = New-ScheduledTaskPrincipal `
  -UserId "$env:USERDOMAIN\$env:USERNAME" `
  -LogonType Interactive `
  -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Host "Installed scheduled task: $TaskName"
