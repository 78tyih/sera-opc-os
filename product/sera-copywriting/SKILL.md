---
name: sera-copywriting
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

# Sera Copywriting

## Purpose
专业文案撰写 Skill。基于产品定位和用户画像，撰写高质量的营销文案和销售话术。

## When to use
- 需要撰写产品文案时
- 需要销售话术时
- 需要营销内容时

## Inputs
- PROJECT_PROFILE.md
- POSITIONING.md
- PERSONA.md
- 文案类型（官网/广告/邮件/社媒）

## Outputs
- `copywriting/` — 文案输出目录
  - `hero-copy.md` — 主标题与副标题
  - `feature-copy.md` — 功能文案
  - `sales-script.md` — 销售话术
  - `social-copy.md` — 社交媒体文案
  - `email-copy.md` — 邮件文案

## Workflow
```
Step 1：读取产品定位和用户画像
Step 2：核心文案
  - 标题（3-5 个方向）
  - 副标题
  - 品牌口号
Step 3：功能文案
  - 每个功能的价值描述
  - 功能 → 利益转换
Step 4：销售话术
  - 针对不同用户分层的销售角度
  - 反对理由应对
  - 成交话术
Step 5：渠道适配
  - 官网/社交媒体/邮件/广告
Step 6：输出文案包
```

## Dependencies
- sera-positioning（上游）
- sera-user-persona（上游）

## Iron Rules
- 不做空洞的营销话术
- 每个文案必须基于产品真实功能