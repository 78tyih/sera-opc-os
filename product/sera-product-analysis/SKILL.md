---
name: sera-product-analysis
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

# Sera Product Analysis

## Purpose
产品理解与分析 Skill。深入分析产品本身：它是什么、解决什么痛点、为什么存在。

## When to use
- 当 PROJECT_PROFILE 已创建，需要深入分析产品时
- 当需要理解产品核心价值和差异化时
- 作为 Product Analysis 工作流的第二步

## Inputs
- PROJECT_PROFILE.md（来自 sera-project-profile）
- 产品资料/描述
- 产品 URL/链接（可选）

## Outputs
- `product-analysis.md` — 产品分析报告

## Workflow
```
Step 1：读取 PROJECT_PROFILE 中的产品定义
Step 2：产品核心问题分析
  - 产品是什么？（功能/形态）
  - 解决什么痛点？（问题定义）
  - 为什么存在？（市场背景）
Step 3：产品功能矩阵
  - 核心功能
  - 差异化功能
  - 必备功能
Step 4：产品体验分析
  - 用户旅程
  - 关键交互
  - 痛点与机会
Step 5：产品优势与劣势
  - SWOT 分析
Step 6：输出 product-analysis.md
```

## Dependencies
- sera-project-profile（上游）
- templates/product/ 目录

## Examples
- 分析 AI 教育平台的产品结构
- 分析 SaaS 产品的功能矩阵
- 分析交易软件的用户体验