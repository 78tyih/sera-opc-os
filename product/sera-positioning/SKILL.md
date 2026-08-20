---
name: sera-positioning
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

# Sera Positioning

## Purpose
产品定位 Skill。基于市场研究和用户画像，制定清晰的产品定位和差异化策略。

## When to use
- 需要定义产品的市场定位时
- 需要制定差异化策略时
- 需要为营销和品牌提供方向时

## Inputs
- PROJECT_PROFILE.md
- product-analysis.md
- market-research.md
- PERSONA.md

## Outputs
- `POSITIONING.md` — 定位文档（使用 templates/product/POSITIONING.md）

## Workflow
```
Step 1：读取产品分析、市场研究和用户画像
Step 2：定位声明（Positioning Statement 格式）
  For: [目标用户]
  Who: [用户痛点]
  Our product: [产品名称]
  Is: [产品类别]
  That: [核心价值]
  Unlike: [竞品]
  We: [差异化优势]
  Because: [理由]
Step 3：价值主张
  - 功能价值
  - 情感价值
  - 社会价值
Step 4：品牌调性
  - 品牌个性
  - 语气与语调
  - 视觉方向
Step 5：信息架构
  - 核心信息
  - 支撑信息
  - 证据/社会证明
Step 6：输出 POSITIONING.md
```

## Dependencies
- sera-product-analysis（上游）
- sera-market-research（上游）
- sera-user-persona（上游）
- templates/product/POSITIONING.md