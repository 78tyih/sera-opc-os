# Sera Skill Audit Report

> 生成时间：2026-08-21 · 审计范围：WorkBuddy 全量 151 Skill（含 flova）· 审计者：WorkBuddy Agent

## 一、核心结论

1. **151 个 Skill 不是聊天记录，而是接近标准 Agent Skill Registry 的资产** —— 分类分层后，**23 个属于 Sera 个人资产（Layer 1）**，124 个是平台/Connector/Marketplace 依赖（Layer 0），3 个通用能力（Layer 3）。
2. **合并后应维护约 20 个超级 Skill**，而不是 151 个碎片。按能力域合并后：`sera-finance-suite` 吸收 52 个、`sera-lark-suite` 吸收 29 个、`sera-doc-pipeline` 吸收 16 个……
3. **Layer 2 行业专家 Skill 目前缺失**（propfirm-product-manager / otc-bd-agent / trading-analysis-agent 等散落在 prompt 中），需要显式补齐。
4. **改名建议**：7 个核心 P0 Skill 需 Sera 化命名（`sera-*`），与平台解耦。

---

## 二、四层分类

| Layer | 数量 | 说明 | 处置 |
|---|---|---|---|
| **Layer 0** 平台/Connector/Marketplace | 124 | 依赖 WorkBuddy Runtime / MCP / OAuth，脱离平台无法运行 | **不迁移**，作为依赖记录 |
| **Layer 1** Sera 个人核心 | 23 | 用户自建/沉淀的工作 Skill | **重点迁移** → 20 超级 Skill |
| **Layer 2** 行业专家 | 0→需新建 | propfirm-PM / OTC-BD / trading / liquidity / AI-video / Figma 审查 | **补齐** |
| **Layer 3** 通用能力 | 3 | humanizer / skill-creator / skill-library | 保留，放 external-skills/ |

---

## 三、Layer 1 明细（Sera 个人资产，23 个）

| # | 当前名称 | 归属度 | 迁移价值 | 重构 | 合并到 | 建议新名 |
|---|---|---|---|---|---|---|
| 1 | `agently-mail` | ★★★★ | ★★★★ | review | `sera-mail-hub` | `sera-mail-hub` |
| 2 | `browser-use` | ★★★★ | ★★★★★ | review | `sera-browser-automation` | `sera-browser-automation` |
| 3 | `context-hub` | ★★★★★ | ★★★★★ | rename | `sera-context-system` | `sera-context-system` |
| 4 | `flova` | ★★★★★ | ★★★★★ | review | `sera-video-pipeline` | `sera-video-pipeline` |
| 5 | `frontend-dev` | ★★★★★ | ★★★★ | review | `sera-frontend-studio` | `sera-frontend-studio` |
| 6 | `gmail` | ★★★★ | ★★★★★ | review | `sera-mail-hub` | `sera-mail-hub` |
| 7 | `grill-me` | ★★★★★ | ★★★★ | review | `sera-grill` | `sera-grill` |
| 8 | `haina-shopping-assistant` | ★★★★ | ★★★★ | review | `sera-shopping` | `sera-shopping` |
| 9 | `heygen-knowledge-shortvideo` | ★★★★★ | ★★★★ | rename | `sera-video-pipeline` | `sera-video-pipeline` |
| 10 | `lark-unified` | ★★★★★ | ★★★★ | review | `sera-lark-suite` | `sera-lark-suite` |
| 11 | `libtv-cli` | ★★★★★ | ★★★★★ | review | `sera-libtv` | `sera-libtv` |
| 12 | `meegle` | ★★★★★ | ★★★★ | review | `sera-lark-suite` | `sera-lark-suite` |
| 13 | `meituan-coupon-workbuddy` | ★★★★ | ★★★★ | review | `sera-shopping` | `sera-shopping` |
| 14 | `obsidian` | ★★★★ | ★★★★ | review | `sera-knowledge-sync` | `sera-knowledge-sync` |
| 15 | `obsidian-sync` | ★★★★★ | ★★★★★ | rename | `sera-knowledge-sync` | `sera-knowledge-sync` |
| 16 | `peekaboo` | ★★★★ | ★★★★★ | review | `sera-macos-ui` | `sera-macos-ui` |
| 17 | `propfirm-eagle-import` | ★★★★★ | ★★★★ | rename | `sera-asset-manager` | `sera-asset-manager` |
| 18 | `propfirm-feed` | ★★★★★ | ★★★★★ | rename | `sera-intelligence-monitor` | `sera-intelligence-monitor` |
| 19 | `propfirm-official-site-assets` | ★★★★★ | ★★★★ | rename | `sera-content-factory` | `sera-content-factory` |
| 20 | `serawin-remote` | ★★★★★ | ★★★★★ | rename | `sera-compute-control` | `sera-compute-control` |
| 21 | `skills-security-check` | ★★★★★ | ★★★★ | review | `sera-skill-meta` | `sera-skill-meta` |
| 22 | `wecom-unified` | ★★★★★ | ★★★★ | review | `sera-wecom-suite` | `sera-wecom-suite` |
| 23 | `weread-skills` | ★★★★ | ★★★★ | review | `sera-knowledge-reader` | `sera-knowledge-reader` |

---

## 四、合并映射：151 → 20 超级 Skill

| 超级 Skill | 类别 | 用途 | 吸收的 Skill |
|---|---|---|---|
| `sera-agent-registry` | core | Agent 注册与能力发现 | 需新建 |
| `sera-asset-manager` | creative | 素材资产管理（Eagle 自动导入/打标） | 1 个：propfirm-eagle-import |
| `sera-browser-automation` | platform | 浏览器自动化（导航/点击/截图/提取） | 1 个：browser-use |
| `sera-compute-control` | core | 远程算力控制（Mac→Windows serawin→ComfyUI/Ollama） | 1 个：serawin-remote |
| `sera-content-factory` | business | 官网素材工厂（capture→事实→5s B-roll×5→Eagle） | 1 个：propfirm-official-site-assets |
| `sera-context-system` | core | 多 Agent 共享记忆层（Sera Context Hub 协议） | 1 个：context-hub |
| `sera-deploy` | development | 静态站点部署（CloudStudio） | 0 个（cloudstudio-deploy 为 WorkBuddy 内置，登记为依赖） |
| `sera-design-studio` | creative | Ardot 画布设计（UI/幻灯片/海报/设计转码） | 6 个：ardot-design-core、ardot-design-router、ardot-design-to-code、ardot-poster、ardot-slides、ardot-ui-design |
| `sera-figma-review` | creative | Figma 设计审查 | 需新建 |
| `sera-frontend-studio` | development | 前端开发规范（设计+动效+AI 素材+文案） | 1 个：frontend-dev |
| `sera-github` | development | GitHub 仓库/PR/Issue 管理 | 1 个：github（Layer 0 Connector 依赖） |
| `sera-intelligence-monitor` | business | 商业情报监控（PropFirm 资讯/竞品/规则推送） | 1 个：propfirm-feed |
| `sera-knowledge-sync` | core | 知识资产同步（Obsidian 归档/去重/版本化） | 2 个：obsidian、obsidian-sync |
| `sera-lark-suite` | platform | 飞书/Lark 套件（18 域+Meegle 子技能） | 29 个：lark-approval、lark-apps、lark-attendance、lark-base、lark-calendar、lark-contact 等 |
| `sera-macos-ui` | platform | macOS UI 自动化 | 1 个：peekaboo |
| `sera-mail-hub` | platform | 统一邮件（Gmail + agently） | 2 个：agently-mail、gmail |
| `sera-otc-bd` | business | OTC 商务拓展代理（散落于 prompt） | 需新建 |
| `sera-trading-research` | business | 交易研究与分析 | 需新建 |
| `sera-video-pipeline` | creative | 数字人口播→知识短视频合成流水线 | 2 个：flova、heygen-knowledge-shortvideo |
| `sera-wecom-suite` | platform | 企业微信套件（通讯录/文档/日程/会议/消息） | 1 个：wecom-unified |

**未合并的独立 Skill**：`lark-unified` 作为 `sera-lark-suite` 主入口保留；`grill-me` → `sera-grill`；`weread-skills` → `sera-knowledge-reader`；`libtv-cli` → `sera-libtv`；`meituan`/`haina` → `sera-shopping`；`tencent-pptx`/`ppt-template-creator` → `sera-ppt`；`weixinpay-*` → `sera-payment`；写作专家 7 个 → `sera-writing-experts`。

---

## 五、Layer 2 待补齐的行业专家 Skill

这些能力目前散落在用户 Prompt / 历史对话中，应显式建为 SKILL.md：

| 建议 Skill | 类别 | 覆盖能力 |
|---|---|---|
| `propfirm-product-manager` | business | PropFirm 产品研究、竞品定价、规则对比、offer 设计 |
| `otc-bd-agent` | business | OTC 商务拓展：客户画像、报价策略、跟进话术、CRM 对接 |
| `trading-analysis-agent` | business | 交易数据复盘、胜率/盈亏比分析、策略回测报告 |
| `crypto-liquidity-agent` | business | 流动性监控、做市分析、价差监控 |
| `ai-video-producer` | creative | AI 视频生产规范：分镜/提示词/素材管理/质量门禁 |
| `figma-design-reviewer` | creative | 设计稿审查：视觉层级/品牌一致性/可交付性检查 |

---

## 六、Layer 0 摘要（不迁移，作为依赖）

124 个平台/Connector/Marketplace Skill 依赖 WorkBuddy Runtime + MCP + OAuth，**脱离平台无法运行**，不迁移。典型：

```
ardot-design-core / tencent-docs / tencent-docx / lark-doc / lark-calendar /
stock-research-report-expert / comps-analysis / dcf-model / tear-sheet / ...
```

处置原则：在 README 的「依赖清单」中登记，新 Agent 需要时按官方方式安装对应 Connector/Marketplace 插件，而非从本仓库复制。

---

## 七、目标仓库结构（重构蓝图）

```
sera-agent-os/
├── README.md
├── core/                  # Sera 核心（记忆/知识/算力/注册）
│   ├── sera-context-system/
│   ├── sera-knowledge-sync/
│   ├── sera-compute-control/
│   └── sera-agent-registry/
├── business/              # 商业与情报
│   ├── sera-intelligence-monitor/
│   ├── sera-content-factory/
│   ├── sera-otc-bd/
│   └── sera-trading-research/
├── creative/              # 内容创作
│   ├── sera-video-pipeline/
│   ├── sera-asset-manager/
│   ├── sera-design-studio/
│   └── sera-figma-review/
├── development/           # 工程开发
│   ├── sera-frontend-studio/
│   ├── sera-deploy/
│   └── sera-github-manager/
├── platform/              # 平台集成套件（依赖但常用）
│   ├── sera-lark-suite/
│   ├── sera-wecom-suite/
│   ├── sera-mail-hub/
│   ├── sera-browser-automation/
│   └── sera-macos-ui/
├── templates/             # 模板
│   ├── SKILL.template.md
│   ├── workflow.yaml
│   └── agent.yaml
└── external-skills/       # Layer 3 通用能力（外部引用）
    ├── humanizer/
    └── skill-creator/
```

---

## 八、行动路线图

| 阶段 | 动作 | 产出 |
|---|---|---|
| P0 | 7 个核心 Skill 改名 `sera-*` + 更新 SKILL.md 为多 Agent 标准格式 | core/ + business/ + creative/ 就绪 |
| P1 | 平台套件（lark/wecom/mail/browser/macos）适配标准格式 | platform/ 就绪 |
| P2 | 补齐 Layer 2 行业专家（从 prompt 提炼） | business/creative 新增 6 个 |
| P3 | 模板体系（SKILL.template/workflow.yaml/agent.yaml） | templates/ 就绪 |
| P4 | external-skills/ 挂载通用能力 | 依赖闭环 |

---

## 九、重复能力识别（合并收益）

审计发现约 40 个 Skill 可归并，压缩比约 3:1：

| 能力域 | 现状 | 合并后 | 压缩 |
|---|---|---|---|
| 金融分析（Marketplace 53+wb-finance） | 52 | 1 (`sera-finance-suite`) | 52:1 |
| 飞书（Connector 27+lark-unified+meegle） | 29 | 1 (`sera-lark-suite`) | 29:1 |
| 文档流水线（tencent-docx 系） | 16 | 1 (`sera-doc-pipeline`) | 16:1 |
| 设计（Ardot 系） | 6 | 1 (`sera-design-studio`) | 6:1 |
| 写作专家（tencent-docx experts） | 7 | 1 (`sera-writing-experts`) | 7:1 |
| 支付（weixinpay 系） | 3 | 1 (`sera-payment`) | 3:1 |

> 注意：合并是「入口统一 + references 分层引用」，不删除原始能力文件；单个 Connector 能力仍作为 references/ 下的子文档保留。

---

## 十、附录：全部 151 Skill 审计清单

| 名称 | Layer | 归属 | 迁移 | 合并目标 |
|---|---|---|---|---|
| `3-statements` | L0 | 1 | 1 | `sera-finance-suite` |
| `academic-paper-expert` | L0 | 1 | 1 | `sera-writing-experts` |
| `ardot-design-core` | L0 | 1 | 1 | `sera-design-studio` |
| `ardot-design-router` | L0 | 1 | 1 | `sera-design-studio` |
| `ardot-design-to-code` | L0 | 1 | 1 | `sera-design-studio` |
| `ardot-poster` | L0 | 1 | 1 | `sera-design-studio` |
| `ardot-slides` | L0 | 1 | 1 | `sera-design-studio` |
| `ardot-ui-design` | L0 | 1 | 1 | `sera-design-studio` |
| `bond-futures-basis` | L0 | 1 | 1 | `sera-finance-suite` |
| `bond-relative-value` | L0 | 1 | 1 | `sera-finance-suite` |
| `business-copy-expert` | L0 | 1 | 1 | `sera-copywriter` |
| `buyer-list` | L0 | 1 | 1 | `sera-finance-suite` |
| `catalyst-calendar` | L0 | 1 | 1 | `sera-finance-suite` |
| `check-deck` | L0 | 1 | 1 | `sera-finance-suite` |
| `check-model` | L0 | 1 | 1 | `sera-finance-suite` |
| `cim-builder` | L0 | 1 | 1 | `sera-finance-suite` |
| `client-report` | L0 | 1 | 1 | `sera-finance-suite` |
| `client-review` | L0 | 1 | 1 | `sera-finance-suite` |
| `cloudstudio-deploy` | L0 | 1 | 1 | 依赖，不迁移 |
| `competitive-analysis` | L0 | 1 | 1 | `sera-finance-suite` |
| `comps-analysis` | L0 | 1 | 1 | `sera-finance-suite` |
| `datapack-builder` | L0 | 1 | 1 | `sera-finance-suite` |
| `dcf-model` | L0 | 1 | 1 | `sera-finance-suite` |
| `dd-checklist` | L0 | 1 | 1 | `sera-finance-suite` |
| `dd-meeting-prep` | L0 | 1 | 1 | `sera-finance-suite` |
| `deal-screening` | L0 | 1 | 1 | `sera-finance-suite` |
| `deal-sourcing` | L0 | 1 | 1 | `sera-finance-suite` |
| `deal-tracker` | L0 | 1 | 1 | `sera-finance-suite` |
| `design-token` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `doc-typeset` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `earnings-analysis` | L0 | 1 | 1 | `sera-finance-suite` |
| `earnings-preview` | L0 | 1 | 1 | `sera-finance-suite` |
| `earnings-preview-single` | L0 | 1 | 1 | `sera-finance-suite` |
| `equity-research` | L0 | 1 | 1 | `sera-finance-suite` |
| `financial-plan` | L0 | 1 | 1 | `sera-finance-suite` |
| `fixed-income-portfolio` | L0 | 1 | 1 | `sera-finance-suite` |
| `format-extract` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `funding-digest` | L0 | 1 | 1 | `sera-finance-suite` |
| `fx-carry-trade` | L0 | 1 | 1 | `sera-finance-suite` |
| `general-writer` | L0 | 1 | 1 | `sera-copywriter` |
| `generate-fillable-contract-html` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `geo-map-compliance-guard` | L0 | 1 | 1 | 依赖，不迁移 |
| `github` | L0 | 1 | 1 | `sera-github` |
| `html-review` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `html-to-docx` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `ic-memo` | L0 | 1 | 1 | `sera-finance-suite` |
| `idea-generation` | L0 | 1 | 1 | `sera-finance-suite` |
| `initiating-coverage` | L0 | 1 | 1 | `sera-finance-suite` |
| `investment-proposal` | L0 | 1 | 1 | `sera-finance-suite` |
| `lark-approval` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-apps` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-attendance` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-base` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-calendar` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-contact` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-doc` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-drive` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-event` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-im` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-mail` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-markdown` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-minutes` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-note` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-okr` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-openapi-explorer` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-shared` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-sheets` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-skill-maker` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-slides` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-task` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-vc` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-vc-agent` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-whiteboard` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-wiki` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-workflow-meeting-summary` | L0 | 1 | 1 | `sera-lark-suite` |
| `lark-workflow-standup-report` | L0 | 1 | 1 | `sera-lark-suite` |
| `lbo-model` | L0 | 1 | 1 | `sera-finance-suite` |
| `legal-contract-expert` | L0 | 1 | 1 | `sera-writing-experts` |
| `macro-rates-monitor` | L0 | 1 | 1 | `sera-finance-suite` |
| `merger-model` | L0 | 1 | 1 | `sera-finance-suite` |
| `model-update` | L0 | 1 | 1 | `sera-finance-suite` |
| `morning-note` | L0 | 1 | 1 | `sera-finance-suite` |
| `option-vol-analysis` | L0 | 1 | 1 | `sera-finance-suite` |
| `pitch-deck` | L0 | 1 | 1 | `sera-finance-suite` |
| `poetry-prose-expert` | L0 | 1 | 1 | `sera-writing-experts` |
| `portfolio-monitoring` | L0 | 1 | 1 | `sera-finance-suite` |
| `portfolio-rebalance` | L0 | 1 | 1 | `sera-finance-suite` |
| `ppt-template-creator` | L0 | 1 | 1 | `sera-ppt` |
| `process-letter` | L0 | 1 | 1 | `sera-finance-suite` |
| `returns-analysis` | L0 | 1 | 1 | `sera-finance-suite` |
| `science-writing-expert` | L0 | 1 | 1 | `sera-writing-experts` |
| `sector-overview` | L0 | 1 | 1 | `sera-finance-suite` |
| `skill-buddy-multimodal-generation` | L0 | 1 | 1 | `sera-3d-fx` |
| `skill-creator` | L0 | 1 | 1 | `sera-skill-meta` |
| `skill-expert-manager` | L0 | 1 | 1 | `sera-skill-meta` |
| `skill-marketplace-skill-installer` | L0 | 1 | 1 | `sera-skill-meta` |
| `skill-recommend-connectors` | L0 | 1 | 1 | `sera-skill-meta` |
| `skill-recommend-experts` | L0 | 1 | 1 | `sera-skill-meta` |
| `stock-research-report-expert` | L0 | 1 | 1 | `sera-writing-experts` |
| `strip-profile` | L0 | 1 | 1 | `sera-finance-suite` |
| `swap-curve-strategy` | L0 | 1 | 1 | `sera-finance-suite` |
| `tax-loss-harvesting` | L0 | 1 | 1 | `sera-finance-suite` |
| `tdoc-orchestrator` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `tear-sheet` | L0 | 1 | 1 | `sera-finance-suite` |
| `teaser` | L0 | 1 | 1 | `sera-finance-suite` |
| `tech-blog-expert` | L0 | 1 | 1 | `sera-writing-experts` |
| `tencent-docs` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `tencent-docs-routing` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `tencent-docs-sheet-generation` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `tencent-docs-sheetagent` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `tencent-docx` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `tencent-local-office-edit` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `tencent-pptx` | L0 | 1 | 1 | `sera-ppt` |
| `tencent-saas-docs` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `thesis-tracker` | L0 | 1 | 1 | `sera-finance-suite` |
| `tmeet-skill` | L0 | 1 | 1 | `sera-tmeet` |
| `underline-toolkit` | L0 | 1 | 1 | `sera-doc-pipeline` |
| `unit-economics` | L0 | 1 | 1 | `sera-finance-suite` |
| `value-creation-plan` | L0 | 1 | 1 | `sera-finance-suite` |
| `wb-finance-skill` | L0 | 1 | 1 | `sera-finance-suite` |
| `weixinpay-feedback` | L0 | 1 | 1 | `sera-payment` |
| `weixinpay-pay` | L0 | 1 | 1 | `sera-payment` |
| `weixinpay-register` | L0 | 1 | 1 | `sera-payment` |
| `work-report-expert` | L0 | 1 | 1 | `sera-writing-experts` |
| `agently-mail` | L1 | 4 | 4 | `sera-mail-hub` |
| `browser-use` | L1 | 4 | 5 | `sera-browser-automation` |
| `context-hub` | L1 | 5 | 5 | `sera-context-system` |
| `flova` | L1 | 5 | 5 | `sera-video-pipeline` |
| `frontend-dev` | L1 | 5 | 4 | `sera-frontend-studio` |
| `gmail` | L1 | 4 | 5 | `sera-mail-hub` |
| `grill-me` | L1 | 5 | 4 | `sera-grill` |
| `haina-shopping-assistant` | L1 | 4 | 4 | `sera-shopping` |
| `heygen-knowledge-shortvideo` | L1 | 5 | 4 | `sera-video-pipeline` |
| `lark-unified` | L1 | 5 | 4 | `sera-lark-suite` |
| `libtv-cli` | L1 | 5 | 5 | `sera-libtv` |
| `meegle` | L1 | 5 | 4 | `sera-lark-suite` |
| `meituan-coupon-workbuddy` | L1 | 4 | 4 | `sera-shopping` |
| `obsidian` | L1 | 4 | 4 | `sera-knowledge-sync` |
| `obsidian-sync` | L1 | 5 | 5 | `sera-knowledge-sync` |
| `peekaboo` | L1 | 4 | 5 | `sera-macos-ui` |
| `propfirm-eagle-import` | L1 | 5 | 4 | `sera-asset-manager` |
| `propfirm-feed` | L1 | 5 | 5 | `sera-intelligence-monitor` |
| `propfirm-official-site-assets` | L1 | 5 | 4 | `sera-content-factory` |
| `serawin-remote` | L1 | 5 | 5 | `sera-compute-control` |
| `skills-security-check` | L1 | 5 | 4 | `sera-skill-meta` |
| `wecom-unified` | L1 | 5 | 4 | `sera-wecom-suite` |
| `weread-skills` | L1 | 4 | 4 | `sera-knowledge-reader` |
| `humanizer` | L3 | 1 | 3 | `sera-doc-pipeline` |
| `humanizer-zh` | L3 | 1 | 3 | `sera-copywriter` |
| `skill-library` | L3 | 1 | 3 | `sera-library` |
