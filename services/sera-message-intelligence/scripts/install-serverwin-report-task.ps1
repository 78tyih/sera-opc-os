param(
  [string]$RepoRoot = "D:\Sera\sera-opc-os",
  [string]$PythonExe = "python",
  [Parameter(Mandatory=$true)]
  [ValidatePattern('^(?:[01]\d|2[0-3]):[0-5]\d$')]
  [string]$At,
  [string]$TaskName = "Sera Message Intelligence - Daily Brief"
)

$ErrorActionPreference = "Stop"
$ServiceRoot = Join-Path $RepoRoot "services\sera-message-intelligence"
$Script = Join-Path $ServiceRoot "scripts\generate_daily_brief.py"
if (!(Test-Path $Script)) { throw "Daily brief script not found: $Script" }

$AtTime = [DateTime]::ParseExact($At, "HH:mm", [System.Globalization.CultureInfo]::InvariantCulture)
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$Script`"" -WorkingDirectory $ServiceRoot
$Trigger = New-ScheduledTaskTrigger -Daily -At $AtTime
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Host "Installed daily brief task: $TaskName at $At"
