---
name: serawin-remote
purpose: 通过 SSH 免密远程操控用户的 Windows 台式机（Tailscale 主机名 serawin / Sarwin，IP 100.67.144.108），执行命令、管理文件、控制已部署的 AI 服务（ComfyUI / Ollama / PropFirm.TV 生图实验室）。
inputs: 远程操作指令（PowerShell 命令或 .ps1/.bat 脚本路径）；文件传输需求；需远程调用的 AI 服务（ComfyUI/Ollama）请求。
outputs: Windows 远程命令执行结果、文件操作结果、AI 服务生成结果、日志与进度。
workflow: |
  1. 判断意图 → 组装 ssh 命令（ssh -o BatchMode=yes -o ConnectTimeout=10 serawin "<cmd>"）
  2. 简单命令直接传参；多行逻辑写 .ps1/.bat（纯 ASCII）scp 过去，再 powershell -File 执行
  3. 中文输出接 | iconv -f GBK -t UTF-8
  4. 后台长任务：本地 run_in_background + ssh serawin "cmd /c xxx.bat"（bat 内 > log 2>&1），进度另起 ssh 查看
  5. 常驻服务：schtasks /create /sc onstart（不要 Start-Process）
  6. 把命令输出翻译成人话汇报给用户
tools: Bash（ssh/scp，需 dangerouslyDisableSandbox）, Read
examples: |
  - ssh -o BatchMode=yes serawin "Get-PSDrive C"
  - ssh -o BatchMode=yes serawin "curl.exe -s http://localhost:8188/system_stats"
  - scp x.ps1 serawin:C:/Temp/x.ps1 && ssh serawin "powershell -NoProfile -ExecutionPolicy Bypass -File C:\\Temp\\x.ps1"
  - 下载大模型：ssh serawin "cmd /c C:\\AI\\download.bat"（run_in_background）
iron_rules: |
  - 远程默认 shell 是 PowerShell；裸 curl 是 Invoke-WebRequest 别名，必须写 curl.exe
  - 禁止通过 stdin 喂脚本（会静默失效）；.bat 必须 CRLF 行尾；远程 ps1 必须纯 ASCII
  - 破坏性操作先向用户确认；用户密码绝不写入任何文件/记忆/技能
source: ~/.workbuddy/skills/serawin-remote/SKILL.md
---

# serawin-remote

## Purpose
通过 SSH 免密远程操控用户的 Windows 台式机（Tailscale 主机名 `serawin` / `Sarwin`，IP `100.67.144.108`），执行命令、管理文件、控制已部署的 AI 服务（ComfyUI / Ollama / PropFirm.TV 生图实验室）。免密已于 2026-08-15 配好。

## Inputs
- 远程操作指令：PowerShell 命令，或需 scp 上传的 `.ps1` / `.bat` 脚本
- 文件传输需求（本地 ↔ serawin）
- 需远程调用的 AI 服务请求（ComfyUI 生成、Ollama 推理、ImageLab 预览）

## Outputs
- Windows 远程命令执行结果
- 文件操作结果（上传/下载/robocopy 克隆）
- AI 服务生成结果与进度日志

## Workflow
```
1. 判断意图 → 组装 ssh 命令：ssh -o BatchMode=yes -o ConnectTimeout=10 serawin "<cmd>"
2. 简单命令直接传参；多行逻辑写 .ps1/.bat（纯 ASCII）scp 过去，再 powershell -File 执行
3. 中文输出接 | iconv -f GBK -t UTF-8
4. 后台长任务：本地 run_in_background + ssh serawin "cmd /c xxx.bat"（bat 内 > log 2>&1）
5. 常驻服务：schtasks /create /sc onstart /ru SYSTEM /rl HIGHEST（不要 Start-Process）
6. 把命令输出翻译成人话汇报给用户
```

## Tools
- Bash（`ssh` / `scp`，必须 `dangerouslyDisableSandbox: true`——沙箱内访问 ~/.ssh 会 EPERM）
- Read（查看远程日志 / 校验文件）

## Examples
```bash
# 基本探测
ssh -o BatchMode=yes -o ConnectTimeout=10 serawin "hostname"
ssh -o BatchMode=yes serawin "Get-PSDrive C"

# 跑多行脚本（标准打法：scp + powershell -File）
scp x.ps1 serawin:C:/Temp/x.ps1
ssh serawin "powershell -NoProfile -ExecutionPolicy Bypass -File C:\Temp\x.ps1"

# 查 ComfyUI / Ollama 服务
ssh serawin "curl.exe -s http://localhost:8188/system_stats"
ssh serawin "curl.exe -s http://localhost:11434/api/tags"
```

## Iron Rules（已知坑）
- 远程默认 shell 是 **PowerShell**；裸 `curl` 是 `Invoke-WebRequest` 别名 → 必须写 `curl.exe` 或 `cmd /c "curl ..."`
- **禁止**通过 stdin 喂脚本（`powershell -Command -` 会静默失效）；用 scp + `-File`
- `.bat` 必须 **CRLF 行尾**；远程 `.ps1` 必须**纯 ASCII**（PS5.1 无 BOM 当 GBK 解析，中文直接崩）
- 超过一行的逻辑一律写成 `.bat/.ps1` 文件执行，别在命令行嵌套转义
- 后台长任务标准打法：本地 Bash `run_in_background=true` + ssh 执行（bat 内重定向日志）
- 常驻服务一律 `schtasks`（`Start-Process` 会随 SSH 会话被杀）
- 破坏性操作（删文件、改系统配置）先向用户确认；用户密码**绝不写入任何文件、记忆或技能**
- 断连排查：Tailscale 两端在线 → `nc -z 100.67.144.108 22` → Windows 是否睡眠

## 已部署 AI 服务速查
| 服务 | 端口 | 说明 |
|---|---|---|
| ComfyUI 0.33.1 | 8188 | D:\AI\ComfyUI\ComfyUI_windows_portable，RTX 5080 16G |
| Ollama (qwen3:14b) | 11434 | GPU ~54 tok/s |
| PropFirm.TV ImageLab | 8189 (ComfyUI) / 8899 (预览) | D:\AI\PropFirmTV-ImageLab\，Mac 可直连 http://100.67.144.108:8189 |

## Source
`~/.workbuddy/skills/serawin-remote/SKILL.md`
