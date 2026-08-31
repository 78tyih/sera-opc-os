param(
  [string]$TaskName = "Sera Message Intelligence - WeChat Collector",
  [string]$GatewayUrl = "http://127.0.0.1:8800",
  [string]$RepoRoot = "D:\Sera\sera-opc-os"
)

$ServiceRoot=Join-Path $RepoRoot "services\sera-message-intelligence"
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) {
  $info = Get-ScheduledTaskInfo -TaskName $TaskName
  Write-Host "Collector task: $($task.State); last=$($info.LastRunTime); result=$($info.LastTaskResult)"
} else { Write-Warning "Default collector task missing (multi-account instances may use per-instance task names)" }

$wechat = Get-Process WeChat,Weixin -ErrorAction SilentlyContinue
if ($wechat) { Write-Host "WeChat process: running ($($wechat.Count))" } else { Write-Warning "WeChat process not detected" }

try {
  $health = Invoke-RestMethod "$GatewayUrl/healthz" -TimeoutSec 3
  Write-Host "Message Core: $($health.status)"
} catch { Write-Warning "Message Core health check failed: $($_.Exception.Message)"; exit 1 }

$ApiKey=""
$EnvPath=Join-Path $ServiceRoot ".env"
if (Test-Path $EnvPath) {
  foreach ($line in Get-Content $EnvPath) {
    if ($line -match '^SMI_INGEST_API_KEY=(.*)$') { $ApiKey=$Matches[1].Trim(); break }
  }
}
$Headers=@{}
if ($ApiKey) { $Headers["x-smi-api-key"]=$ApiKey }
try {
  $collectors=Invoke-RestMethod "$GatewayUrl/v1/collectors" -Headers $Headers -TimeoutSec 5
  if (!$collectors) { Write-Warning "No collector heartbeat state recorded yet" }
  foreach ($c in $collectors) {
    Write-Host ("Collector {0} account={1} effective={2} reported={3} heartbeatAge={4}s messages={5} errors={6}" -f $c.collector_instance_id,$c.account_id,$c.effective_status,$c.reported_status,$c.heartbeat_age_seconds,$c.messages_received,$c.errors)
  }
} catch { Write-Warning "Collector status query failed: $($_.Exception.Message)" }
