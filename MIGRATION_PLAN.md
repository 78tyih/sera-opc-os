# Sera OPC OS — Migration Plan V1.0

> 生成时间：2026-08-21
> 原则：不破坏已有仓库。先建立软连接/注册/映射，逐步迁移。

---

## 一、迁移策略

### 分层策略

```
Phase A — Registry（当前阶段）
  建立所有仓库的注册表映射
  不修改任何源仓库
  → 已完成：docs/repository-map.md + registry/*.json

Phase B — 目录建立
  在 sera-agent-os 内创建 projects/ 目录
  为每个活跃项目建立子目录
  通过 README 链接到源仓库

Phase C — 技能集成
  将设计参考库（kimi, htx）作为 git submodule 引入
  将 SVG 工作台作为 adapters 引入

Phase D — 工厂集成
  将 video-factory / pipeline 作为子模块注册
  在 control-center 中显示状态

Phase E — 控制中心接入
  所有项目状态在 Sera Agent Console 中可查看
  通过 registry/ 数据驱动
```

---

## 二、Per-Repository 迁移计划

### Core Infrastructure（6 个）

| # | 仓库 | 当前作用 | 迁移 | 目标位置 | 保留方式 | 未来调用方式 |
|---|------|---------|------|---------|---------|------------|
| 1 | **ai-gateway** | 多模型聊天网关 | 否 | `core/sera-compute-control/` | 保留源仓库，添加 README 链接 | `python3 core/sera-compute-control/gateway.py` |
| 2 | **ai-workflow-monitor** | 运行时监控 | 否 | `core/sera-agent-orchestrator/` | 保留源仓库，添加 README 链接 | Web UI 集成到 Control Center |
| 3 | **chatgpt-codex-claude-bridge** | 跨 IDE 桥接 | 否 | `adapters/` | 保留源仓库 | 通过 CLI 调用 |
| 4 | **docs-bridge-mcp** | MCP 文档桥接 | 否 | `adapters/` | 保留源仓库 | MCP 协议调用 |
| 5 | **smart-mail-hub** | 邮件工作流 | 否 | `adapters/sera-mail-hub/` | 保留源仓库 | `python3 -m smart_mail_hub` |
| 6 | **mac-automation-scripts** | Mac 自动化 | 否 | `adapters/sera-macos-ui/` | 保留源仓库 | 通过 CLI 调用 |

### Skill Library（3 个）

| # | 仓库 | 当前作用 | 迁移 | 目标位置 | 保留方式 | 未来调用方式 |
|---|------|---------|------|---------|---------|------------|
| 7 | **kimi-design-refer** | Kimi 设计风格 | **子模块** | `creative/sera-design-intelligence/references/kimi/` | git submodule | `sera-design-intelligence` 自动读取 |
| 8 | **htx-design-refer** | HTX 设计风格 | **子模块** | `creative/sera-design-intelligence/case-studies/htx-otc-v1/` | git submodule | `sera-design-intelligence` 自动读取 |
| 9 | **svg-sketch-workbench** | SVG 草图工作台 | 否 | `creative/sera-design-studio/` | 保留源仓库 | `sera-design-studio` 调用 |

### Factory System（2 个）

| # | 仓库 | 当前作用 | 迁移 | 目标位置 | 保留方式 | 未来调用方式 |
|---|------|---------|------|---------|---------|------------|
| 10 | **propfirm-tv-video-factory** | 视频自动化工厂 | **子模块** | `video-factory/` | git submodule | `video-agent` 通过 CLI 调用 |
| 11 | **propfirm-tv-pipeline** | 处理流水线 | **子模块** | `product-factory/` | git submodule | `product-agent` 通过 CLI 调用 |

### Project Case Studies（15 个）

| # | 仓库 | 当前作用 | 迁移 | 目标位置 | 保留方式 | 未来调用方式 |
|---|------|---------|------|---------|---------|------------|
| 12 | **htx-otc-landing** | HTX OTC 落地页 | 否 | `projects/htx-otc/landing/` | 软链接/reference | 通过 Control Center 查看 |
| 13 | **htx-otc-progress-hub** | HTX OTC 进度中心 | 否 | `projects/htx-otc/progress-hub/` | 软链接/reference | 通过 Control Center 查看 |
| 14 | **propfirm-tv** | PropFirm.TV 网站 | 否 | `projects/propfirm-tv/` | 软链接/reference | 通过 Control Center 查看 |
| 15 | **poff-trading** | 泡芙交易 | 否 | `projects/poff-trading/` | 软链接/reference | 通过 Control Center 查看 |
| 16 | **deltapex-site** | Deltapex 官网 | 否 | `projects/deltapex/site/` | 软链接/reference | 通过 Control Center 查看 |
| 17 | **DPxPropfirm1** | 德湃考试盘 v1 | 否 | `projects/deltapex/propfirm1/` | 软链接/reference | 归档 |
| 18 | **DPxPropfirm** | 德湃考试盘 | 否 | `projects/deltapex/propfirm/` | 软链接/reference | 通过 Control Center 查看 |
| 19 | **DP-** | DP 满意度调研 | 否 | `projects/deltapex/survey/` | 软链接/reference | 归档 |
| 20 | **Deltapex-Trading-Group-** | 德湃官网 | 否 | `projects/deltapex/website/` | 软链接/reference | 通过 Control Center 查看 |
| 21 | **traderbti** | Trader BTI | 否 | `projects/traderbti/` | 软链接/reference | 通过 Control Center 查看 |
| 22 | **Trader-DNA** | 交易性格画像 | 否 | `projects/trader-dna/` | 软链接/reference | 通过 Control Center 查看 |
| 23 | **ququ** | 蛐蛐语音输入 | 否 | `projects/ququ/` | 软链接/reference | 通过 Control Center 查看 |
| 24 | **knowledgestar-galaxy** | 知识星系可视化 | 否 | `projects/knowledgestar/` | 软链接/reference | 通过 Control Center 查看 |
| 25 | **clone-website** | 网站克隆 | 否 | `projects/clone-website/` | 软链接/reference | 工具引用 |
| 26 | **Flomo2md** | Flomo 转换器 | 否 | `projects/flomo2md/` | 软链接/reference | 工具引用 |

### Adapters & Tools（2 个）

| # | 仓库 | 当前作用 | 迁移 | 目标位置 | 保留方式 | 未来调用方式 |
|---|------|---------|------|---------|---------|------------|
| 27 | **CC-statusline-kit** | Claude Code 状态条 | 否 | `adapters/claude-code-statusline/` | 保留源仓库 | 自动加载 |
| 28 | **flomo-auto-tagger** | flomo 自动标签 | 否 | `core/sera-knowledge-sync/` | 保留源仓库 | 定时任务 |

### Other / Legacy（4 个）

| # | 仓库 | 当前作用 | 迁移 | 目标位置 | 保留方式 | 未来调用方式 |
|---|------|---------|------|---------|---------|------------|
| 29 | **78tyih.github.io** | 个人 GitHub Pages | 否 | `projects/personal-site/` | 保留源仓库 | 不迁移 |
| 30 | **SeraYue-s-Blog** | 博客 | 否 | `projects/blog/` | 保留源仓库 | 不迁移 |
| 31 | **Instructions** | 说明文档 | 否 | `docs/instructions/` | 保留源仓库 | 引用 |
| 32 | **sera-agent-os** | 根仓库 | — | `./` | — | 唯一入口 |

---

## 三、时间线建议

```
Phase A (当前) — Registry 建立
  ✅ 扫描全部 32 个仓库
  ✅ 创建 docs/repository-map.md
  ✅ 创建 registry/agents.json
  ✅ 创建 registry/skills.json
  ✅ 创建 registry/projects.json
  ✅ 创建 registry/workflows.json
  ✅ 创建 registry/styles.json
  → 当前阶段

Phase B — 项目目录建立（建议 1-2 天）
  □ 创建 projects/ 目录结构
  □ 为每个活跃项目添加 README（链接到源仓库）
  □ 在 Control Center 中显示项目列表

Phase C — 技能子模块集成（建议 1 天）
  □ git submodule add kimi-design-refer
  □ git submodule add htx-design-refer
  □ git submodule add propfirm-tv-video-factory
  □ git submodule add propfirm-tv-pipeline

Phase D — 工厂工厂集成（建议 1-2 天）
  □ 在 product-factory/ 中注册流水线
  □ 在 video-factory/ 中注册视频工厂
  □ 在 Control Center 中显示工厂状态

Phase E — 控制中心完整接入（建议 2-3 天）
  □ 所有项目状态可视化
  □ 所有 Agent 状态可视化
  □ 所有工作流可触发
  □ 所有 Registry 可搜索
```

---

## 四、不破坏已有仓库的原则

```
1. 不删除任何源仓库
2. 不修改源仓库的内容
3. 不强制迁移 — 每个仓库保留独立 git history
4. 不使用 git submodule 的项目：用 README 引用 + registry 注册
5. 使用 git submodule 的项目：父仓库只跟踪引用，不修改子模块
6. 所有软链接/子模块在 sera-agent-os 的 install.sh 中统一管理
```

---

## 五、依赖关系图

```
ai-gateway
  └─→ sera-compute-control (model routing)

ai-workflow-monitor
  └─→ sera-agent-orchestrator (runtime monitoring)

kimi-design-refer + htx-design-refer
  └─→ sera-design-intelligence (design memory)

propfirm-tv-video-factory + propfirm-tv-pipeline
  └─→ product-factory + video-factory (production pipelines)

projects/* (15 repos)
  └─→ sera-agent-console (visualization)

smart-mail-hub + mac-automation-scripts + CC-statusline-kit
  └─→ adapters/ (tool integration)
```

---

*本计划由 Sera OPC OS — Ecosystem Integration V1.0 自动生成*