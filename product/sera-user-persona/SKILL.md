---
name: sera-user-persona
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

# Sera User Persona

## Purpose
用户画像创建 Skill。基于产品定义和调研，创建精准的目标用户画像。

## When to use
- 需要定义产品的目标用户时
- 需要理解用户痛点和购买动机时
- 为产品定位和营销提供用户洞察时

## Inputs
- PROJECT_PROFILE.md
- product-analysis.md
- market-research.md

## Outputs
- `PERSONA.md` — 用户画像文档（使用 templates/product/PERSONA.md）

## Workflow
```
Step 1：读取产品定义和市场研究
Step 2：定义核心用户群体
  - 主要用户
  - 次要用户
  - 边缘用户
Step 3：为每个用户群体创建 Persona
  - 人口统计
  - 职业/角色
  - 技术能力
  - 行为模式
Step 4：痛点分析
  - 核心痛点
  - 隐性痛点
  - 购买理由
Step 5：决策因素
  - 决策流程
  - 关键决策因素
  - 反对理由
  - 替代方案
Step 6：输出 PERSONA.md
```

## Dependencies
- sera-product-analysis（上游）
- sera-market-research（上游）
- templates/product/PERSONA.md