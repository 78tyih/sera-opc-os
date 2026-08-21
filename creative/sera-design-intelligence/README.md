# Sera Design Intelligence System

> 版本：3.2.0
> 定位：Sera OPC OS 的 Cyber Design Intelligence Engine
> 核心理念：**学习优秀设计 → 提炼 Design DNA → 自动驱动产品设计 → 持续反馈优化**

---

## 系统架构

```
Design Intelligence Engine V3.2
│
├── 01 Knowledge Architecture  ← 设计知识库（原则/心理/模式/商业）
├── 02 Design Benchmark        ← 设计基准评分系统
├── 03 DNA Engine              ← 设计 DNA 提取器
├── 04 Style Registry          ← 风格 DNA 注册表
├── 05 Style Router            ← 风格路由引擎
├── 06 Design Memory           ← 设计记忆循环
├── 07 Design Department       ← 9 个 Agent 编排
├── 08 Product Factory SDK     ← 产品线接口
└── 09 Workflow Pipeline       ← 全自动流水线
```

## 目录

| 目录 | 说明 |
|---|---|
| `SKILL.md` | Design Intelligence Skill 定义 |
| `SYSTEM.md` | 系统架构文档 |
| `knowledge/` | 设计知识库（原则/心理/模式/商业） |
| `benchmark/` | 设计基准评分系统 |
| `dna-engine/` | 设计 DNA 提取器 |
| `styles/` | 风格 DNA 注册表 |
| `style-router/` | 风格路由引擎 |
| `memory/` | 设计记忆循环 |
| `interfaces/` | 产品线接口定义 |
| `workflows/` | 工作流定义 |
| `docs/` | 项目文档 |
| `case-studies/` | 设计案例研究 |
| `templates/` | 模板库 |
| `assets/` | 资产库索引 |
| `references/` | 详细设计规则 |

## 核心能力

1. **学习优秀网站设计** — Design Benchmark + DNA Extractor
2. **提炼 Design DNA** — 自动生成 STYLE_DNA.json
3. **建立视觉知识库** — 4 个知识维度，19 个知识文件
4. **自动选择设计方向** — Style Router 8 条路由规则
5. **自动生成设计系统** — 完整流水线 10 步
6. **持续优化** — Design Memory 反馈循环

## 快速开始

```bash
# 1. 分析产品需求
python style-router/router.py --industry ai --audience trader --goal sales

# 2. 查看基准评分
cat benchmark/benchmark-index.json

# 3. 查看 Design DNA 示例
cat dna-engine/examples/htx-otc-dna.json

# 4. 设计新产品的完整流程
→ 触发 design-intelligence-pipeline 工作流
```

## 已注册风格

| 风格 ID | 行业 | 信任分 | 科技分 | 适用场景 |
|---|---|---|---|---|
| `sera-fintech-premium` | finance | 10 | 8 | 金融/高端 |
| `sera-ai-future` | ai | 7 | 10 | AI 产品 |
| `sera-saas-landing` | saas | 7 | 9 | SaaS 产品 |
| `sera-operations-dashboard` | operations | 6 | 7 | Dashboard |
| `sera-content-platform` | media | 8 | 6 | 内容平台 |

## 设计经验积累路线

```
V1.0: HTX OTC          ✅ 金融产品 + Dashboard
V1.1: Knowledge Engine  ✅ 知识库 + 逆向工程 + DNA Registry
V3.2: Cyber Engine      ✅ 9 Agents + Pipeline + Memory Loop  ← 当前
V3.3: 自动化增强        ⏳ DNA 自动提取 + 评分自动化
V3.4: 智能学习          ⏳ 趋势分析 + 竞品监控
V3.5: 全自动化          ⏳ 端到端设计流水线
```