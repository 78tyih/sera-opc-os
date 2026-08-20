# Sera Agent Skills

Sera 个人 AI Agent 技能库（私有仓库）。把 WorkBuddy 中**用户自定义**的 Skill 转换为标准 Agent Skill 格式，供 WorkBuddy / Trae / Codex / ChatGPT 等 Agent 跨环境复用。

> 只包含用户级 Skill。WorkBuddy 内置 Skill、Tencent/Feishu Connector、Marketplace Skill **不迁移**。

---

## Skill Registry

共 **13** 个用户级 Skill。

### P0（核心，7 个）

| Skill | 用途 | 关键输入 | 关键输出 |
|---|---|---|---|
| [`context-hub`](skills/context-hub/SKILL.md) | 读取/维护 Sera Context Hub 跨 Agent 上下文（SESSION START/END 协议） | 项目任务、多 Agent 交接需求 | 项目上下文、CURRENT_STATE/AGENT_HANDOFF 更新、MEMORY.jsonl 追加 |
| [`obsidian-sync`](skills/obsidian-sync/SKILL.md) | 产物自动归档到 Obsidian Vault（分类/去重/版本化/Front Matter） | 产物文件或目录、可选 --category | 归档文件、重建 index.md、同步日志 |
| [`serawin-remote`](skills/serawin-remote/SKILL.md) | SSH 免密远程操控 Windows 台式机（serawin）+ 远程 AI 服务 | PowerShell 命令 / .ps1 脚本 / 文件 | 远程命令结果、AI 服务输出（ComfyUI/Ollama） |
| [`propfirm-feed`](skills/propfirm-feed/SKILL.md) | PropFirm.TV 资讯推送管线（采集→过滤→门禁→隔离→企微推送） | JSON 原始情报、settings.json | feed_items、企业微信推送 |
| [`propfirm-official-site-assets`](skills/propfirm-official-site-assets/SKILL.md) | 考试盘官网素材工厂（capture→事实/品牌色→HyperFrames 5s B-roll×5→Eagle） | 官网 URL、firm key、截图 | 5s 无声 B-roll mp4×5、Eagle 入库、manifest |
| [`heygen-knowledge-shortvideo`](skills/heygen-knowledge-shortvideo/SKILL.md) | HeyGen 口播 → 16:9 1080p 知识型短视频合成（图卡+字幕+BGM） | HeyGen 口播 mp4、文案、分镜 | 合成短视频（PIL+numpy+ffmpeg 全本地） |
| [`propfirm-eagle-import`](skills/propfirm-eagle-import/SKILL.md) | 媒体文件自动导入 Eagle「Sera 资源库」（V2 API 优先） | 媒体文件/staging 目录、tags/annotation | Eagle item ID、.eagle.imported.json |

### P1（6 个）

| Skill | 用途 | 关键输入 | 关键输出 |
|---|---|---|---|
| [`frontend-dev`](skills/frontend-dev/SKILL.md) | 全栈前端开发（设计+动画+AI 素材+文案+视觉艺术） | 页面需求、品牌信息 | 完整网页工程、本地媒体资产、转化文案 |
| [`lark-unified`](skills/lark-unified/SKILL.md) | 飞书/Lark CLI 套件（18 域 200+ 命令，Meegle 按需转子技能） | 飞书操作意图、lark-cli 授权 | 各域业务结果、OpenAPI 响应 |
| [`wecom-unified`](skills/wecom-unified/SKILL.md) | 企业微信 CLI 套件（通讯录/文档/表格/日程/会议/待办/微盘/邮件/消息） | 办公意图、企微链接、授权 | 可读名称形式的业务结果 |
| [`gmail`](skills/gmail/SKILL.md) | Gmail API（托管 OAuth）读写邮件/线程/标签/草稿 | MATON_API_KEY、Gmail 连接 | 邮件列表/正文、发送回执 |
| [`browser-use`](skills/browser-use/SKILL.md) | 浏览器自动化（导航/点击/截图/提取/多会话/云浏览器） | URL、操作意图 | 页面状态、截图、交互结果 |
| [`peekaboo`](skills/peekaboo/SKILL.md) | macOS UI 自动化（截图/元素定位/输入驱动/应用管理） | UI 操作意图、定位参数 | 截图、UI 快照、操作结果 |

## 支持的 Agent

| Agent | 说明 |
|---|---|
| **WorkBuddy** | 原生支持：`~/.workbuddy/skills/` 或项目 `.workbuddy/skills/` 目录放置 SKILL.md |
| **Trae** | 读取 `~/SeraContextHub/99_System/adapters/ADAPTER_TRAE.md` 接入细则 |
| **Codex** | 读取 `~/SeraContextHub/99_System/adapters/ADAPTER_CODEX.md` 接入细则 |
| **ChatGPT Desktop** | 读取 `~/SeraContextHub/99_System/adapters/ADAPTER_CHATGPT_DESKTOP.md` 接入细则 |
| **Claude/通用 Agent** | SKILL.md 遵循 Anthropic Agent Skills 标准格式（name/purpose 前置 YAML + Markdown 正文） |

## 安装方式

### 方式 A：WorkBuddy（推荐，一键）

```bash
# 克隆到用户级 skills 目录
git clone https://github.com/<your-gh>/sera-agent-skills.git ~/.workbuddy/skills-src/sera-agent-skills

# 软链每个 skill 到 WorkBuddy 用户级 skills 目录
for d in ~/.workbuddy/skills-src/sera-agent-skills/skills/*/; do
  ln -s "$d" ~/.workbuddy/skills/$(basename "$d")
done
```

重启 WorkBuddy 后，对话中直接说对应触发词即可（如「导入 Eagle」「让 serawin 做 XX」「跑 propfirm 管线」）。

### 方式 B：手动复制

把 `skills/<name>/` 整个目录复制到目标 Agent 的 skills 目录：

```bash
cp -r skills/context-hub ~/.workbuddy/skills/context-hub
```

### 方式 C：Claude Code / 通用 Agent

把 `skills/<name>/SKILL.md` 放入 Agent 的 skills 目录（如 Claude Code 的 `.claude/skills/`），frontmatter 满足 `name` + `description`（或 `purpose`）即可被识别。

## 前提依赖

| Skill | 依赖 |
|---|---|
| context-hub | `~/SeraContextHub/` 仓库（AGENT_CONTEXT_PROTOCOL.md） |
| obsidian-sync | Python 3.13+、`~/.workbuddy/obsidian-sync/workbuddy_obsidian_sync.py`、Obsidian Sera Vault |
| serawin-remote | Tailscale、SSH 免密（密钥 `~/.ssh/id_ed25519`）、Windows 端 sshd |
| propfirm-feed | Python 3.13、项目 `/Users/a1234/WorkBuddy/2026-08-17-03-48-26/propfirm-feed/`、企微 webhook |
| propfirm-official-site-assets | Node 22（hyperframes）、browser-use（CDP）、ffmpeg、Eagle |
| heygen-knowledge-shortvideo | ffmpeg、Python（PIL/numpy）、HeyGen 口播视频 |
| propfirm-eagle-import | Eagle（本地 API :41595）、Python 3 |
| frontend-dev | Node/npm、MiniMax API key（`MINIMAX_API_KEY`） |
| lark-unified | `lark-cli`（npx @larksuite/cli）、`meegle`（按需） |
| wecom-unified | `wecom-cli`（npm @wecom/cli ≥1.1.0）、企微授权 |
| gmail | Maton CLI、`MATON_API_KEY`、Google OAuth 连接 |
| browser-use | browser-use CLI（daemon） |
| peekaboo | Peekaboo CLI（macOS 权限：屏幕录制+辅助功能） |

## 仓库结构

```
sera-agent-skills/
├── README.md                      # 本文件（Skill Registry / 支持 Agent / 安装方式）
├── skills/                        # 13 个用户级 Skill
│   ├── context-hub/SKILL.md
│   ├── obsidian-sync/SKILL.md
│   ├── serawin-remote/SKILL.md
│   ├── propfirm-feed/SKILL.md
│   ├── propfirm-official-site-assets/SKILL.md
│   ├── heygen-knowledge-shortvideo/SKILL.md
│   ├── propfirm-eagle-import/SKILL.md
│   ├── frontend-dev/SKILL.md
│   ├── lark-unified/SKILL.md
│   ├── wecom-unified/SKILL.md
│   ├── gmail/SKILL.md
│   ├── browser-use/SKILL.md
│   └── peekaboo/SKILL.md
└── archive/                       # （本地保留）2026-08-21 全量扫描归档，不推 GitHub
```

## SKILL.md 标准格式

每个 Skill 采用统一标准格式：

```yaml
---
name: <skill 名>
purpose: <一句话用途>
inputs: <输入>
outputs: <输出>
workflow: <多步流程>
tools: <依赖工具>
examples: <示例命令>
---
# <skill 名>
## Purpose / Inputs / Outputs / Workflow / Tools / Examples / Iron Rules
```

---

*私人技能库 · 由 WorkBuddy 扫描转换生成（2026-08-21）*
