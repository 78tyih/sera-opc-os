# Sera Design Intelligence System

> 版本：1.0.0
> 定位：Sera Agent OS 的设计智能子系统
> 核心理念：**发现优秀设计 → 拆解其价值 → 提取为资产与规则 → 复用至新产品**

---

## 系统架构

```
Design Intelligence System
│
├── 01 Case Study Engine    ← 审美分析：这个网站为什么好看？
├── 02 Asset Library        ← 资产提取：它由什么组成？
├── 03 Style Registry       ← 风格分类：什么产品适合什么风格？
├── 04 Design Skill         ← 设计规则：它遵循什么规律？
├── 05 Template Library     ← 模板复用：怎么快速复用？
└── 06 Design Department    ← Agent 编排：谁来执行？
```

## 目录

| 目录 | 说明 |
|---|---|
| `SKILL.md` | Design Intelligence Skill 定义 |
| `SYSTEM.md` | 系统架构文档 |
| `awesome-design.md` | 核心视觉语言（Sera FinTech Visual Language V1.0） |
| `case-studies/` | 设计案例研究 |
| `templates/` | 模板库（Case Study 模板 + 页面模板） |
| `styles/` | 风格注册表 |
| `assets/` | 资产库索引 |
| `workflows/` | 设计提取工作流 |
| `references/` | 详细设计规则 |

## 快速开始

```bash
# 新增一个设计案例
1. 复制 templates/design-case-study-template.md
2. 填写分析
3. 提取资产到 assets/<case>/
4. 注册风格到 styles/registry.json
5. 更新 awesome-design.md（如有新规则）
```

## 第一批案例

| 案例 | 状态 | 类型 | 风格 |
|---|---|---|---|
| HTX OTC Landing | ✅ active | 金融 Landing Page | Premium · Trust |
| HTX OTC Progress Hub | ✅ active | 运营 Dashboard | Data-Driven |
| PropFirm TV | ⏳ pending | 内容平台 | — |
| TradeSpan | ⏳ pending | 交易 SaaS | — |

## 设计经验积累路线

```
Phase 1: HTX OTC          ✅ 金融产品 + Dashboard
Phase 2: PropFirm TV      ⏳ 内容平台
Phase 3: TradeSpan        ⏳ 交易 SaaS
Phase 4: 牛牛 AI          ⏳ AI 产品
Phase 5: Sera Design Language V1.0  🎯 合并
```