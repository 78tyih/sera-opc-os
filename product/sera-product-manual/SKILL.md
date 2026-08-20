---
name: sera-product-manual
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

# Sera Product Manual

## Purpose
产品手册生成 Skill。汇总所有分析成果，生成完整的产品手册文档。

## When to use
- 当所有产品分析完成后，需要输出完整产品手册时
- 为销售团队、客户或合作伙伴准备产品资料时
- 作为 Product Factory 工作流的最后一步

## Inputs
- PROJECT_PROFILE.md
- product-analysis.md
- market-research.md
- PERSONA.md
- POSITIONING.md
- copywriting/ 目录

## Outputs
- `PRODUCT_MANUAL.md` — 完整产品手册（使用 templates/product/PRODUCT_MANUAL.md）

## Workflow
```
Step 1：汇总所有上游分析文档
Step 2：产品介绍
  - 产品概述
  - 核心价值主张
  - 目标用户
Step 3：功能详解
  - 功能列表
  - 使用流程
  - 最佳实践
Step 4：FAQ
  - 常见问题
  - 反对理由应对
Step 5：销售话术
  - 不同场景的话术
  - 竞品对比话术
Step 6：案例
  - 使用案例
  - 成功案例（如可用）
Step 7：输出 PRODUCT_MANUAL.md
```

## Dependencies
- 所有上游 Product Skills
- templates/product/PRODUCT_MANUAL.md

## Iron Rules
- PRODUCT_MANUAL.md 必须引用所有上游文档
- 保持一致性 — 所有信息必须与上游文档一致