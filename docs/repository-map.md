# Sera Agent OS — Repository Map

> 生成时间：2026-08-21
> 扫描范围：GitHub @78tyih — 32 repositories

---

## 一、架构总览

```
Sera Agent OS
│
├── Core Infrastructure       (6 repos)
├── Agent System              (1 repo — sera-agent-os 自身)
├── Skill Library             (3 repos)
├── Factory System            (2 repos)
├── Project Case Studies      (12 repos)
├── Adapters & Tools          (4 repos)
└── Other / Legacy            (4 repos)
```

---

## 二、Core Infrastructure（核心基础设施）

| # | Repository | 语言 | 可见性 | 当前作用 | Sera OS 映射 |
|---|-----------|------|--------|---------|-------------|
| 1 | **ai-gateway** | JavaScript | PRIV | 多模型聊天网关，支持 API/SSE/Web UI | `core/sera-compute-control/` — 模型路由与计算控制 |
| 2 | **ai-workflow-monitor** | TypeScript | PRIV | AI Agent 运行时监控与治理控制台 | `core/sera-agent-orchestrator/` — 编排状态监控 |
| 3 | **chatgpt-codex-claude-bridge** | Python | PUBL | ChatGPT 隔空指挥本地 Codex/Claude Code | `adapters/` — 跨 IDE 桥接 |
| 4 | **docs-bridge-mcp** | TypeScript | PRIV | MCP 集成与文档自动化工具 | `adapters/` — MCP 文档桥接 |
| 5 | **smart-mail-hub** | Python | PRIV | 邮件工作流工具（候选/附件分类） | `adapters/sera-mail-hub/` — 邮件适配器 |
| 6 | **mac-automation-scripts** | Python | PRIV | Mac 自动化脚本与工作流 | `adapters/sera-macos-ui/` — Mac 自动化适配器 |

---

## 三、Agent System（Agent 系统）

| # | Repository | 语言 | 可见性 | 当前作用 | Sera OS 映射 |
|---|-----------|------|--------|---------|-------------|
| 7 | **sera-agent-os** | Python | PRIV | 核心 Agent OS — 跨平台 AI 操作系统 | `./` — 根仓库自身 |

当前已注册 Agent（5 个）：
- `agents/product-agent/` — 产品发布专家
- `agents/design-agent/` — 设计专家
- `agents/video-agent/` — 视频内容专家
- `agents/propfirm-agent/` — PropFirm 行业专家
- `agents/otc-agent/` — OTC 商务专家
- `agents/trading-agent/` — 交易研究专家
- `agents/design-department/` — 设计部门（6 个子 Agent）

---

## 四、Skill Library（技能库）

| # | Repository | 语言 | 可见性 | 当前作用 | Sera OS 映射 |
|---|-----------|------|--------|---------|-------------|
| 8 | **kimi-design-refer** | N/A | PUBL | Kimi 设计风格参考库 | `creative/sera-design-intelligence/references/kimi/` |
| 9 | **htx-design-refer** | N/A | PUBL | 火币 HTX 设计风格参考 | `creative/sera-design-intelligence/case-studies/htx-otc-v1/` |
| 10 | **svg-sketch-workbench** | Shell | PRIV | 终端优先的 SVG UI 草图工作台 | `creative/sera-design-studio/` — SVG 设计工具 |

---

## 五、Factory System（工厂系统）

| # | Repository | 语言 | 可见性 | 当前作用 | Sera OS 映射 |
|---|-----------|------|--------|---------|-------------|
| 11 | **propfirm-tv-video-factory** | TypeScript | PUBL | PropFirm.TV 视频自动化工厂 | `video-factory/` — 视频生产流水线 |
| 12 | **propfirm-tv-pipeline** | Python | PRIV | PropFirm.TV 完整处理流水线 | `product-factory/` — 产品处理流水线 |

---

## 六、Project Case Studies（项目案例）

| # | Repository | 语言 | 可见性 | 当前作用 | Sera OS 映射 |
|---|-----------|------|--------|---------|-------------|
| 13 | **htx-otc-landing** | JavaScript | PRIV | HTX OTC 落地页 | `projects/htx-otc/landing/` |
| 14 | **htx-otc-progress-hub** | JavaScript | PUBL | HTX OTC 进度中心 | `projects/htx-otc/progress-hub/` |
| 15 | **propfirm-tv** | HTML | PRIV | PropFirm.TV 网站 | `projects/propfirm-tv/` |
| 16 | **poff-trading** | TypeScript | PRIV | 泡芙交易 — 期货考试盘平台 | `projects/poff-trading/` |
| 17 | **deltapex-site** | TypeScript | PRIV | Deltapex 官网 | `projects/deltapex/site/` |
| 18 | **DPxPropfirm1** | HTML | PUBL | 德湃考试盘 v1 | `projects/deltapex/propfirm1/` |
| 19 | **DPxPropfirm** | JavaScript | PUBL | 德湃考试盘 | `projects/deltapex/propfirm/` |
| 20 | **DP-** | TypeScript | PUBL | DP 满意度调研 | `projects/deltapex/survey/` |
| 21 | **Deltapex-Trading-Group-** | TypeScript | PRIV | 德湃官网 | `projects/deltapex/website/` |
| 22 | **traderbti** | TypeScript | PRIV | Trader BTI 平台 | `projects/traderbti/` |
| 23 | **Trader-DNA** | HTML | PUBL | 交易性格画像测评 | `projects/trader-dna/` |
| 24 | **ququ** | JavaScript | PRIV | 蛐蛐中文语音输入工具 | `projects/ququ/` |
| 25 | **knowledgestar-galaxy** | TypeScript | PUBL | Obsidian 笔记知识星系可视化 | `projects/knowledgestar/` |
| 26 | **clone-website** | TypeScript | PUBL | 网站克隆工具 | `projects/clone-website/` |
| 27 | **Flomo2md** | Python | PUBL | Flomo HTML → Markdown 转换 | `projects/flomo2md/` |

---

## 七、Adapters & Tools（适配器与工具）

| # | Repository | 语言 | 可见性 | 当前作用 | Sera OS 映射 |
|---|-----------|------|--------|---------|-------------|
| 28 | **CC-statusline-kit** | Shell | PUBL | Claude Code 双行状态条 | `adapters/claude-code-statusline/` |
| 29 | **flomo-auto-tagger** | Python | PUBL | flomo 自动三级标签 | `core/sera-knowledge-sync/` — 知识同步 |

---

## 八、Other / Legacy（其他）

| # | Repository | 语言 | 可见性 | 当前作用 | Sera OS 映射 |
|---|-----------|------|--------|---------|-------------|
| 30 | **78tyih.github.io** | HTML | PUBL | 个人 GitHub Pages | `projects/personal-site/` |
| 31 | **SeraYue-s-Blog** | HTML | PUBL | SeraYue 博客 | `projects/blog/` |
| 32 | **Instructions** | N/A | PUBL | 通用说明文档 | `docs/instructions/` |

---

## 九、分类统计

| 分类 | 数量 | 已迁移 |
|------|------|--------|
| Core Infrastructure | 6 | ✅ 已注册 core/ 与 adapters/ |
| Agent System | 1 | ✅ 已注册 agents/ |
| Skill Library | 3 | ✅ 已注册 creative/ |
| Factory System | 2 | 🔶 待注册 product-factory/ 与 video-factory/ |
| Project Case Studies | 15 | ❌ 待创建 projects/ 目录 |
| Adapters & Tools | 2 | ✅ 已注册 adapters/ 与 core/ |
| Other / Legacy | 4 | ❌ 待归档或忽略 |

---

## 十、Registry 注册状态

| Registry | 文件 | 状态 |
|----------|------|------|
| Agents | `registry/agents.json` | ✅ 已创建 |
| Skills | `registry/skills.json` | ✅ 已创建 |
| Projects | `registry/projects.json` | ✅ 已创建 |
| Workflows | `registry/workflows.json` | ✅ 已创建 |
| Styles | `registry/styles.json` | ✅ 已创建 |

---

*本映射由 Sera Agent OS — Ecosystem Integration V1.0 自动生成*