param(
  [string]$TaskName = "Sera Message Intelligence - WeChat Collector",
  [string]$GatewayUrl = "http://127.0.0.1:8800"
)

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) {
  $info = Get-ScheduledTaskInfo -TaskName $TaskName
  Write-Host "Collector task: $($task.State); last=$($info.LastRunTime); result=$($info.LastTaskResult)"
} else { Write-Warning "Collector task missing" }

$wechat = Get-Process WeChat,Weixin -ErrorAction SilentlyContinue
if ($wechat) { Write-Host "WeChat process: running" } else { Write-Warning "WeChat process not detected" }

try {
  $health = Invoke-RestMethod "$GatewayUrl/healthz" -TimeoutSec 3
  Write-Host "Message Core: $($health.status)"
} catch { Write-Warning "Message Core health check failed: $($_.Exception.Message)" }
