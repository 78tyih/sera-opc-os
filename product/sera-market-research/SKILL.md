---
name: sera-market-research
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

# Sera Market Research

## Purpose
市场研究与竞品分析 Skill。深入分析市场格局、目标用户和竞争对手。

## When to use
- 需要了解产品所在市场的规模和趋势时
- 需要分析竞品的产品、定价和策略时
- 需要为产品定位提供数据支撑时

## Inputs
- PROJECT_PROFILE.md
- product-analysis.md
- 市场/行业关键词

## Outputs
- `market-research.md` — 市场研究报告

## Workflow
```
Step 1：定义研究范围（市场/行业/地域）
Step 2：市场规模分析
  - TAM / SAM / SOM
  - 市场增长率
  - 市场趋势
Step 3：竞品分析
  - 直接竞品
  - 间接竞品
  - 替代方案
Step 4：竞品对比矩阵
  - 功能对比
  - 定价对比
  - 定位对比
  - 优势对比
Step 5：市场机会分析
  - 空白领域
  - 差异化机会
  - 进入壁垒
Step 6：输出 market-research.md
```

## Dependencies
- WebSearch / Browser（市场数据采集）
- sera-product-analysis（上游）

## Iron Rules
- 所有数据必须标注来源
- 标注 "推测" 与 "已验证" 的区别
- 不编造市场数据