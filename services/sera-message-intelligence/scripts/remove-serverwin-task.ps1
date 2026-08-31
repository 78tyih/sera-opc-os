param([string]$TaskName = "Sera Message Intelligence - WeChat Collector")
$ErrorActionPreference = "Stop"
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) {
  Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "Removed: $TaskName"
} else {
  Write-Host "Task not installed: $TaskName"
}
