# Sera Agent OS

**Build once, execute everywhere.**

Sera Agent OS 是一个跨 Agent 的个人 AI 操作系统。它把孤立的 AI 工具（WorkBuddy / Codex / Trae / Claude Code / Cursor）统一为一个人工智能系统。

> Skill 不属于任何单一 AI 平台 —— **Skill 属于 Sera Agent OS。**

---

## 架构（V1.0）

```
                    Sera Agent OS
                         User
                          |
              Agent Orchestrator Layer
                    |
        ----------------------------
        |            |             |
   Codex        WorkBuddy       Trae
        ----------------------------
                          |
              Skill Registry Layer
        Core | Business | Creative | Platform
                          |
              Memory System
        Context Hub | Obsidian | Project State | Decision Logs
                          |
              Compute Layer
        Mac | Serawin | Cloud GPU | API Services
```

完整架构文档：[`architecture/sera-agent-os-v1.md`](architecture/sera-agent-os-v1.md)

## Skill Registry

### 🧠 core/ — 核心系统层

| Skill | 来源 | 用途 |
|---|---|---|
| [`sera-agent-orchestrator`](core/sera-agent-orchestrator/SKILL.md) | 新建 | 任务路由 / Agent 选择 / 执行规划 / 冲突检测 |
| [`sera-memory-system`](core/sera-memory-system/SKILL.md) | 新建 | 共享记忆层：Context Hub + Obsidian + Project State + Decision Logs |
| [`sera-skill-registry`](core/sera-skill-registry/SKILL.md) | 新建 | Skill 注册表与标准格式 |
| [`sera-context-system`](core/sera-context-system/SKILL.md) | context-hub | 多 Agent 共享上下文（Sera Context Hub 协议） |
| [`sera-knowledge-sync`](core/sera-knowledge-sync/SKILL.md) | obsidian-sync | 知识资产同步（Obsidian 归档/去重/版本化） |
| [`sera-compute-control`](core/sera-compute-control/SKILL.md) | serawin-remote | 远程算力控制（Mac→serawin→ComfyUI/Ollama） |

### 📈 business/ — 商业情报层

| Skill | 来源 | 用途 |
|---|---|---|
| [`sera-intelligence-monitor`](business/sera-intelligence-monitor/SKILL.md) | propfirm-feed | PropFirm 商业情报（采集→过滤→门禁→推送企微） |
| [`sera-content-factory`](business/sera-content-factory/SKILL.md) | propfirm-official-site-assets | 官网素材工厂（capture→事实→5s B-roll×5→Eagle） |

### 🎬 creative/ — 内容创作层

| Skill | 来源 | 用途 |
|---|---|---|
| [`sera-video-pipeline`](creative/sera-video-pipeline/SKILL.md) | heygen-knowledge-shortvideo | 数字人口播→知识短视频合成（图卡+字幕+BGM） |
| [`sera-asset-manager`](creative/sera-asset-manager/SKILL.md) | propfirm-eagle-import | 素材资产管理（Eagle 自动导入/打标） |
| [`sera-design-studio`](creative/sera-design-studio/SKILL.md) | frontend-dev | 前端设计开发规范（设计+动效+AI 素材+文案） |

### 🔌 adapters/ — 平台适配层

| Skill | 来源 | 用途 |
|---|---|---|
| [`sera-lark-suite`](adapters/sera-lark-suite/SKILL.md) | lark-unified | 飞书/Lark 套件（18 域 + Meegle 子技能） |
| [`sera-wecom-suite`](adapters/sera-wecom-suite/SKILL.md) | wecom-unified | 企业微信套件（通讯录/文档/日程/会议/消息） |
| [`sera-mail-hub`](adapters/sera-mail-hub/SKILL.md) | gmail | 邮件（Gmail API） |
| [`sera-browser-automation`](adapters/sera-browser-automation/SKILL.md) | browser-use | 浏览器自动化 |
| [`sera-macos-ui`](adapters/sera-macos-ui/SKILL.md) | peekaboo | macOS UI 自动化 |

### 📋 模板

| 文件 | 用途 |
|---|---|
| [`SKILL.template.md`](templates/SKILL.template.md) | 新 Skill 标准格式模板 |
| [`workflow.yaml`](templates/workflow.yaml) | 多 Skill 工作流编排模板 |
| [`agent.yaml`](templates/agent.yaml) | 领域专家 Agent 定义模板 |

---

## 支持 Agent

| Agent | 接入方式 |
|---|---|
| **WorkBuddy** | `~/.workbuddy/skills/` 或项目 `.workbuddy/skills/` 放置 SKILL.md |
| **Codex** | 读 `~/SeraContextHub/99_System/adapters/ADAPTER_CODEX.md` 接入细则 |
| **Trae** | 读 `~/SeraContextHub/99_System/adapters/ADAPTER_TRAE.md` 接入细则 |
| **Claude Code** | `.claude/skills/` 目录（frontmatter 即识别） |
| **Cursor / 未来 Agent** | 遵循标准 SKILL.md 格式即可 |

## 安装方式

### 方式 A：WorkBuddy（推荐）

```bash
git clone https://github.com/78tyih/sera-agent-skills.git ~/.workbuddy/skills-src/sera-agent-skills

for d in ~/.workbuddy/skills-src/sera-agent-skills/{core,business,creative,adapters}/*/; do
  ln -s "$d" ~/.workbuddy/skills/$(basename "$d")
done
```

### 方式 B：手动复制

```bash
cp -r core/sera-context-system ~/.workbuddy/skills/sera-context-system
```

### 方式 C：Claude Code / 通用 Agent

把 `skills/<name>/SKILL.md` 放入 Agent 的 skills 目录，frontmatter 满足 `name` + `description` 即可被识别。

## 依赖清单（Layer 0，不迁移）

以下能力来自 WorkBuddy 平台 / Connector / Marketplace，**作为依赖登记**，需要时按官方方式安装，不从本仓库复制：

- **平台内置**：tencent-docx 文档流水线、ardot-* 设计、weixinpay-* 支付、sheetagent 表格、skill-* 元技能
- **飞书 Connector**：lark-* 27 个（本仓库 `sera-lark-suite` 是统一入口封装）
- **金融 Marketplace**：cb_teams_marketplace 53 个（金融分析/权益研究/投行/PE/LSEG/财富管理）
- **写作专家**：tencent-docx experts 9 个
- **GitHub / 腾讯会议** Connector

详见 [`docs/SKILL-AUDIT-REPORT.md`](docs/SKILL-AUDIT-REPORT.md)（151 Skill 四层分类审计，2026-08-21）。

## 仓库结构

```
sera-agent-skills/
├── README.md
├── architecture/
│   └── sera-agent-os-v1.md          # 架构 V1.0 文档
├── core/                             # 系统层
│   ├── sera-agent-orchestrator/
│   ├── sera-memory-system/
│   ├── sera-skill-registry/
│   ├── sera-context-system/
│   ├── sera-knowledge-sync/
│   └── sera-compute-control/
├── business/                         # 商业情报
│   ├── sera-intelligence-monitor/
│   └── sera-content-factory/
├── creative/                         # 内容创作
│   ├── sera-video-pipeline/
│   ├── sera-asset-manager/
│   └── sera-design-studio/
├── adapters/                         # 平台适配
│   ├── sera-lark-suite/
│   ├── sera-wecom-suite/
│   ├── sera-mail-hub/
│   ├── sera-browser-automation/
│   └── sera-macos-ui/
├── templates/                        # 模板
│   ├── SKILL.template.md
│   ├── workflow.yaml
│   └── agent.yaml
├── docs/
│   └── SKILL-AUDIT-REPORT.md         # 审计报告
└── archive/                          # 全量扫描归档（gitignore，不推）
```

## Development Roadmap

- [x] **Phase 1**：仓库落地（README + 架构文档 + 13 Skill 归位 + 系统层骨架 + 模板）
- [ ] **Phase 2**：提取/重命名剩余个人 Skill（已做 7 个 P0 改名 sera-*，P1 已归位）
- [ ] **Phase 3**：创建领域专家（PropFirm PM / OTC BD / Trading Analyst / AI Video Producer / Design Reviewer）
- [ ] **Phase 4**：连接 Codex / Trae / WorkBuddy / Claude 到同一 Skill Registry

---

*Sera Agent OS V1.0 · 2026-08-21 · 由 WorkBuddy 构建*
