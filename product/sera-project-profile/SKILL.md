---
name: sera-project-profile
version: 1.0.0
author: Sera
category: product
status: active
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
---

# Sera Project Profile

## Purpose
项目初始化核心 Skill。把模糊的产品想法转化为结构化、可执行的项目文档。Product Factory 的入口。

## When to use
- 当一个新产品想法需要被正式立项时
- 当需要从零开始定义一个产品项目时
- 作为 Product Factory 工作流的第一个 Skill

## Inputs
- 产品想法描述（自然语言）
- 参考链接/资料（可选）
- 项目名称（可选）

## Outputs
- `PROJECT_PROFILE.md` — 完整项目档案（使用 templates/product/PROJECT_PROFILE.md）
- 更新 state/product/ 中的项目状态

## Workflow
```
Step 1：解析用户输入 → 提取关键信息
Step 2：项目基本定义（名称/类别/阶段）
Step 3：产品定义（What/Why/Who）
Step 4：用户画像初稿
Step 5：竞品初步扫描
Step 6：价值主张定义
Step 7：商业模式定义
Step 8：发布目标设定
Step 9：所需资产清单
Step 10：输出 PROJECT_PROFILE.md
```

## Dependencies
- 模板：templates/product/PROJECT_PROFILE.md
- 输出目录：product/ 或用户指定目录

## Examples
```bash
# 输入示例
"我要推广牛牛 AI，这是一个 AI 教育平台"

# 输出
PROJECT_PROFILE.md 包含完整的项目定义、用户画像、竞品分析和发布计划
```

## Iron Rules
- 必须使用 templates/product/PROJECT_PROFILE.md 模板
- 所有输出保存到 product/ 目录
- 不编造数据 — 标记为 "待研究" 而不是伪造