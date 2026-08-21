# Sera OPC OS

**World-Class AI Company Operating System**

> 一个由人类 CEO 驱动、AI 员工执行、持续学习进化的 AI 原生公司操作系统。

| Field | Value |
|-------|-------|
| Version | 2.0 |
| Status | Foundation Architecture → Kernel V0 Implementation |
| Owner | Sarah CEO |
| Legacy | [`sera-agent-os`](https://github.com/78tyih/sera-agent-os) |

---

> **⚠️ 文档冻结公告（2026-08-21 ~ 2026-08-28）**
>
> 根据 [Kimi K3 审计报告](docs/SKILL-AUDIT-REPORT.md) 的建议，本项目进入 **7 天文档冻结期**：
> - **禁止新增任何架构文档**（含 Markdown Blueprint、YAML Schema、设计文档）
> - **唯一实施依据**：[Sera Context Runtime & Learning OS V1.1](architecture/v2/Sera-Context-Runtime-Learning-OS-V1.md)
> - **冻结期间唯一产出**：Kernel V0 的代码实现
> - 所有旧架构文档已添加 `⚠️ Superseded` 警示，仅供参考
>
> 冻结期结束后，将根据 Kernel V0 经验修订并收敛文档体系。

---

## 六层架构

```
Layer 0:  Constitution    公司宪法
Layer 1:  Organization OS 组织系统
Layer 2:  Factory OS      生产系统
Layer 3:  Employee OS     员工系统
Layer 4:  Learning OS     进化系统
Layer 5:  Autonomous      自治公司
```

## 仓库结构

```
sera-opc-os/
├── constitution/       # 公司宪法
├── vision/             # 战略愿景
├── strategy/           # 战略规划
├── organization/       # 组织系统
├── executive/          # 高管智能体
├── departments/        # 部门定义
├── agents/             # AI 员工
├── skills/             # 技能目录
├── workflows/          # 工作流
├── factories/          # 生产工厂
├── revenue/            # 商业变现
├── core/               # 核心引擎
├── runtime/            # 运行时
├── router/             # 调度大脑
├── models/             # 模型管理
├── adapters/           # 外部适配器
├── memory/             # 公司记忆
├── evaluation/         # 智能体评估
├── evolution/          # 进化系统
├── portfolio/          # 项目资产
├── platforms/          # 平台文档
├── docs/               # 文档
└── registry/           # 注册表
```

## 蓝图文档

| # | 文档 | 说明 |
|---|------|------|
| 1 | [Blueprint](docs/blueprints/01-Blueprint.md) | 公司级设计规范，顶层愿景 |
| 2 | [Repo Spec](docs/blueprints/02-Repo-Spec.md) | GitHub 工程规范，DeepSeek 直接执行 |
| 3 | [Factory Blueprint](docs/blueprints/03-Factory-Blueprint.md) | 生产系统设计，5 大工厂定义 |
| 4 | [Employee Blueprint](docs/blueprints/04-Employee-Blueprint.md) | 首批 50 名员工完整目录 |

---

## 核心原则

1. **结果 > 任务** — 所有 Agent 必须回答：这个任务如何创造业务价值？
2. **系统 > 个人** — 每次成功必须沉淀为 Skill / Workflow / Template / Memory
3. **Agent 是员工，不是工具** — 每个 Agent 必须有完整 Contract
4. **世界级 Benchmark** — 每个部门对标行业最佳实践

---

## 架构（V1.0 · 保留参考）

```
                    Sera OPC OS
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

完整架构文档：

- **V2.0 五层架构**（当前）：[`architecture/v2/`](architecture/v2/) — Memory Graph / Memory Engine / SMOP 协议 / Organization OS / Workflow OS
- V1 历史版本：[`architecture/sera-agent-os-v1.md`](architecture/sera-agent-os-v1.md)

## Agent Registry（个人 AI 团队）

Agent = 多个 Skill 的组合，是用户真正直接调用的入口。

| Agent | 类别 | 组合 Skills | 负责 | 状态 |
|---|---|---|---|---|
| [`propfirm-agent`](agents/propfirm-agent/SKILL.md) | business | intelligence-monitor + content-factory + browser-automation + design-studio | 竞品分析 / 网站拆解 / 产品手册 / 营销素材 | ✅ active |
| [`otc-agent`](agents/otc-agent/SKILL.md) | business | mail-hub + crm-adapter + memory-system + context-system + knowledge-sync | 客户分析 / 报价回复 / 跟进 / 风险判断 | ✅ active |
| [`trading-agent`](agents/trading-agent/SKILL.md) | business | trading-analysis + finance-suite + knowledge-reader | ATAS / Order Flow / 市场研究 | ✅ active |
| [`video-agent`](agents/video-agent/SKILL.md) | creative | content-factory + video-pipeline + asset-manager + compute-control | 官网素材 → 数字人视频 → 合成 → 入库（最成熟） | ✅ active |
| [`design-agent`](agents/design-agent/SKILL.md) | creative | design-studio + figma-review | 品牌 / UI / 海报 / 网站 | ✅ active |

调用关系：**Agent → Skill → Adapter → Tool**（分层调用，不混在一起）

## V1.1 新增能力

### 🧩 Agent Contract（Agent 标准）
每个 Agent 目录包含 5 个文件，构成完整 Agent Contract：

```
agents/<agent>/
├── agent.yaml          # 身份/目标/Skill 组合/模型偏好
├── system.md           # 系统提示词（角色/行为/红线）
├── memory-policy.yaml  # Memory 读写策略（读什么/写什么）
├── skill-map.yaml      # Skill 映射（Agent → Skill 调用关系）
└── evaluation.yaml     # 该 Agent 的评估维度
```

### 🧭 Planner（Router 三层升级）
Router 从规则匹配升级为三层决策：

```
Intent Router（意图识别）
    ↓
Agent Planner（Agent 选择）
    ↓
Execution Planner（执行步骤规划）
```

### 📊 Evaluation（Agent 评估）
`evaluation/agent-score.yaml` 记录各 Agent 评估维度与得分，回答「哪个 Agent / 哪个模型做得好」。

### 🎛️ Model Router（模型路由）
`runtime/model-router.yaml` 按任务类型路由模型：
research→DeepSeek / coding→Codex / design→Trae / automation→WorkBuddy / image→Serawin

### 🧠 Memory / State 分离
- **Memory**（`memory/`）：长期——知道什么（偏好/知识/历史），分 long-term / knowledge / preference
- **State**（`state/`）：短期——正在发生什么（项目/任务/Agent 状态），分 projects / tasks / agent-status

## Skill Registry

### 🧠 core/ — 核心系统层

| Skill | 来源 | 用途 |
|---|---|---|
| [`sera-agent-orchestrator`](core/sera-agent-orchestrator/SKILL.md) | 新建 | 任务路由 / Agent 选择 / 执行规划 / 冲突检测（引擎=router） |
| [`sera-agent-router`](core/sera-agent-router/SKILL.md) | 新建 | **Agent Router 规则引擎**：自然语言 → 编排链（router.py，12/12 自测通过） |
| [`sera-memory-system`](core/sera-memory-system/SKILL.md) | 新建 | 共享记忆层：Context Hub + Obsidian + Project State + Decision Logs |
| [`sera-state-manager`](core/sera-state-manager/SKILL.md) | 新建 | 工作状态管理：当前阶段 / 阻塞 / 下一步（Memory 的实时补充） |
| [`sera-skill-registry`](core/sera-skill-registry/SKILL.md) | 新建 | Skill 注册表与标准格式 |
| [`sera-context-system`](core/sera-context-system/SKILL.md) | context-hub | 多 Agent 共享上下文（Sera Context Hub 协议） |
| [`sera-knowledge-sync`](core/sera-knowledge-sync/SKILL.md) | obsidian-sync | 知识资产同步（Obsidian 归档/去重/版本化） |
| [`sera-compute-control`](core/sera-compute-control/SKILL.md) | serawin-remote | 远程算力控制（Mac→serawin→ComfyUI/Ollama） |

### 📈 business/ — 商业情报层

| Skill | 来源 | 用途 |
|---|---|---|
| [`sera-intelligence-monitor`](business/sera-intelligence-monitor/SKILL.md) | propfirm-feed | PropFirm 商业情报（采集→过滤→门禁→推送企微） |
| [`sera-content-factory`](business/sera-content-factory/SKILL.md) | propfirm-official-site-assets | 官网素材工厂（capture→事实→5s B-roll×5→Eagle） |
| [`trading-analysis`](business/trading-analysis/SKILL.md) | 新建 | 交易复盘 / 胜率盈亏比 / 策略回测 / 订单流解读 |

### 🎬 creative/ — 内容创作层

| Skill | 来源 | 用途 |
|---|---|---|
| [`sera-video-pipeline`](creative/sera-video-pipeline/SKILL.md) | heygen-knowledge-shortvideo | 数字人口播→知识短视频合成（图卡+字幕+BGM） |
| [`sera-asset-manager`](creative/sera-asset-manager/SKILL.md) | propfirm-eagle-import | 素材资产管理（Eagle 自动导入/打标） |
| [`sera-design-studio`](creative/sera-design-studio/SKILL.md) | frontend-dev | 前端设计开发规范（设计+动效+AI 素材+文案） |
| [`figma-review`](creative/figma-review/SKILL.md) | 新建 | 设计稿审查（视觉层级/品牌一致性/可交付性） |

### 🔌 adapters/ — 平台适配层

| Skill | 来源 | 用途 |
|---|---|---|
| [`sera-lark-suite`](adapters/sera-lark-suite/SKILL.md) | lark-unified | 飞书/Lark 套件（18 域 + Meegle 子技能） |
| [`sera-wecom-suite`](adapters/sera-wecom-suite/SKILL.md) | wecom-unified | 企业微信套件（通讯录/文档/日程/会议/消息） |
| [`sera-mail-hub`](adapters/sera-mail-hub/SKILL.md) | gmail | 邮件（Gmail API） |
| [`sera-browser-automation`](adapters/sera-browser-automation/SKILL.md) | browser-use | 浏览器自动化 |
| [`sera-macos-ui`](adapters/sera-macos-ui/SKILL.md) | peekaboo | macOS UI 自动化 |
| [`sera-crm-adapter`](adapters/sera-crm-adapter/SKILL.md) | 新建 | CRM 适配层（客户档案/跟进/交易记录） |

### 📋 模板

| 文件 | 用途 |
|---|---|
| [`SKILL.template.md`](templates/SKILL.template.md) | 新 Skill 标准格式模板 |
| [`workflow.yaml`](templates/workflow.yaml) | 多 Skill 工作流编排模板 |
| [`agent.yaml`](templates/agent.yaml) | 领域专家 Agent 定义模板 |

---

## 支持 Agent

| Agent | 接入方式 | 文档 |
|---|---|---|
| **WorkBuddy** | `~/.workbuddy/skills/`（用户级）或项目 `.workbuddy/skills/` | [platforms/workbuddy.md](platforms/workbuddy.md) |
| **Codex** | `~/.codex/skills/`（用户级）或 `.codex/skills/`（项目） | [platforms/codex.md](platforms/codex.md) |
| **Trae** | `.trae/skills/`（项目）或 `~/.trae/skills/`（全局） | [platforms/trae.md](platforms/trae.md) |
| **Claude Code** | `~/.claude/skills/`（个人）或 `.claude/skills/`（项目） | [platforms/claude-code.md](platforms/claude-code.md) |
| **Cursor** | `.cursor/skills/`（项目）或 `~/.cursor/skills/`（全局） | [platforms/cursor.md](platforms/cursor.md) |

所有平台共用同一 Router：`python3 core/sera-agent-router/router.py "<请求>"`（纯 stdlib 零依赖）。

## 安装方式

### 方式 A：一键安装（推荐）

```bash
git clone https://github.com/78tyih/sera-opc-os.git ~/sera-opc-os
cd ~/sera-opc-os
./install.sh --all                  # 安装到全部 5 平台
./install.sh --platform workbuddy   # 或指定平台
./install.sh --copy                 # Windows/无软链环境用复制
```

### 方式 B：手动软链（WorkBuddy）

```bash
for d in ~/sera-opc-os/{core,business,creative,adapters}/*/; do
  [ -f "$d/SKILL.md" ] && ln -s "$d" ~/.workbuddy/skills/$(basename "$d")
done
```

### 方式 C：手动复制

```bash
cp -r core/sera-context-system ~/.workbuddy/skills/sera-context-system
```

### 方式 D：Claude Code / 通用 Agent

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
sera-opc-os/
├── README.md
├── architecture/
│   ├── sera-agent-os-v1.md           # 架构 V1.0 文档
│   └── sera-agent-os-v1.1-upgrade.md # V1.1 架构升级评审
├── core/                             # 系统层
│   ├── sera-agent-orchestrator/
│   ├── sera-agent-router/            # Router 三层规划（router.py + routes.yaml + workflows/）
│   ├── sera-agent-registry/          # Agent 注册表
│   ├── sera-memory-system/
│   ├── sera-state-manager/
│   ├── sera-skill-registry/
│   ├── sera-context-system/
│   ├── sera-knowledge-sync/
│   └── sera-compute-control/
├── agents/                           # Agent 层（每人 6 文件 Agent Contract）
│   ├── propfirm-agent/               #   agent.yaml system.md memory-policy.yaml skill-map.yaml evaluation.yaml
│   ├── otc-agent/
│   ├── trading-agent/
│   ├── video-agent/
│   └── design-agent/
├── business/                         # 商业情报
│   ├── sera-intelligence-monitor/
│   ├── sera-content-factory/
│   └── trading-analysis/
├── creative/                         # 内容创作
│   ├── sera-video-pipeline/
│   ├── sera-asset-manager/
│   ├── sera-design-studio/
│   └── figma-review/
├── adapters/                         # 平台适配（Skill 级）
│   ├── sera-lark-suite/
│   ├── sera-wecom-suite/
│   ├── sera-mail-hub/
│   ├── sera-browser-automation/
│   ├── sera-macos-ui/
│   └── sera-crm-adapter/
├── platforms/                        # 平台接入（Agent 级）
│   ├── README.md
│   ├── workbuddy.md
│   ├── codex.md
│   ├── trae.md
│   ├── claude-code.md
│   └── cursor.md
├── evaluation/                       # Agent 评估体系（V1.1）
│   ├── README.md
│   └── agent-score.yaml
├── runtime/                          # 运行时配置（V1.1）
│   └── model-router.yaml             # 模型路由（DeepSeek/Codex/Trae/WorkBuddy/Serawin）
├── memory/                           # 长期记忆（V1.1）
│   ├── README.md
│   ├── long-term/
│   ├── knowledge/
│   └── preference/
├── state/                            # 工作状态（V1.1）
│   ├── README.md
│   ├── projects/
│   ├── tasks/
│   └── agent-status/
├── install.sh                        # 一键安装脚本
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
- [x] **Phase 2.5**：Agent 层建立（5 个核心 Agent：propfirm/otc/trading/video/design）+ sera-state-manager
- [x] **Phase 3**：补齐领域专家 Skill（figma-review / trading-analysis / sera-crm-adapter），5 个 Agent 全部 active
- [x] **Phase 4**：实现 Agent Router（sera-agent-router：router.py 规则引擎 + routes.yaml，自然语言→编排链，12/12 自测通过）
- [x] **Phase 5**：多 Agent 平台接入（platforms/ 五平台文档 + install.sh 一键安装）
- [x] **V1.1**：Agent Contract 标准化 + Router 三层升级（Planner）+ sera-agent-registry + Evaluation + Model Router + Memory/State 分离

---

*Sera OPC OS V1.1 · 2026-08-21 · 由 WorkBuddy 构建*
