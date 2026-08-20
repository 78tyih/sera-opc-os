# Sera Style Router

> 版本：2.0.0
> 用途：根据产品属性自动推荐设计风格组合
> 引擎：`router.py` — 基于规则匹配的智能风格路由引擎

---

## 架构概述

Style Router 是 Sera Design Intelligence 的核心调度模块，负责将产品画像（Product Profile）映射到设计语言（Style DNA）。它由三个核心组件构成：

```
Product Profile（产品属性）
    |
    v
┌────────────────────────────────────────────────┐
│              Style Router Engine                │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  rules.yaml  │  │  registry.json│            │
│  │  (匹配规则)  │  │  (风格DNA)   │            │
│  └──────┬───────┘  └──────┬───────┘            │
│         │                 │                     │
│         v                 v                     │
│  ┌────────────────────────────────────────┐    │
│  │        router.py 匹配引擎               │    │
│  │  - 行业匹配 (权重 50)                   │    │
│  │  - 受众匹配 (权重 30)                   │    │
│  │  - 加权排序与置信度计算                  │    │
│  └────────────────┬───────────────────────┘    │
│                   v                            │
│  ┌────────────────────────────────────────┐    │
│  │     style-selection.json 验证与扩展     │    │
│  │  - 验证推荐结果是否在预定义规则内        │    │
│  │  - 扩展时自动生成新规则                  │    │
│  └────────────────┬───────────────────────┘    │
└───────────────────┬────────────────────────────┘
                    |
                    v
   推荐风格组合（primary + secondary + adjustments）
                    |
                    v
          Design Generator Agent 执行
```

## 引擎详解

### 匹配算法 (`router.py`)

Style Router 使用加权评分算法进行风格匹配：

1. **行业匹配**: 产品行业与规则行业完全匹配时 +50 分
2. **受众匹配**: 产品受众与规则受众完全匹配时 +30 分
3. **最高分筛选**: 选择得分最高的匹配规则
4. **权重归一化**: 将规则中各风格的权重归一化为百分比置信度
5. **输出组合**: 返回主风格、备选风格列表、参考案例和核心组件

### 输入格式

接收来自 Product Factory 的产品画像 JSON：

```json
{
  "product_name": "牛牛 AI",
  "industry": "ai",
  "audience": "developer",
  "goal": "signup",
  "brand_keywords": ["intelligent", "minimal", "fast"],
  "competitors": ["ChatGPT", "Claude"],
  "pages": ["landing", "pricing", "docs"]
}
```

### 输出格式

引擎返回结构化的风格推荐，包含置信度评分和匹配理由：

```json
{
  "profile": {
    "industry": "ai",
    "audience": "developer",
    "goal": "signup"
  },
  "primary_style": "sera-ai-future",
  "recommendations": [
    {
      "style_id": "sera-ai-future",
      "name": "Sera AI Future",
      "weight": "50%",
      "confidence": 0.5,
      "reason": "AI 开发者工具优先科技感，辅以专业信任"
    },
    {
      "style_id": "sera-saas-landing",
      "name": "Sera SaaS Landing",
      "weight": "30%",
      "confidence": 0.3,
      "reason": "AI 开发者工具优先科技感，辅以专业信任"
    },
    {
      "style_id": "sera-fintech-premium",
      "name": "Sera FinTech Premium",
      "weight": "20%",
      "confidence": 0.2,
      "reason": "AI 开发者工具优先科技感，辅以专业信任"
    }
  ],
  "references": ["Kimi", "ChatGPT", "Linear"],
  "components": ["chat-interface", "feature-grid", "pricing-table", "demo-section"],
  "match_rule": "AI 开发者工具优先科技感，辅以专业信任"
}
```

## 路由规则

### `rules.yaml` — 规则定义

`rules.yaml` 定义了 8 条匹配规则，覆盖 `finance`、`ai`、`saas`、`media`、`dashboard` 五个行业，并根据受众细分（如 `retail` vs `institutional`、`developer` vs `consumer`、`enterprise` vs `startup`）提供差异化权重。

每条规则包含：
- **match**: 匹配条件（industry + audience）
- **weights**: 各风格权重（总和为 100）
- **description**: 匹配理由描述

### `style-selection.json` — 规则验证与扩展

`style-selection.json` 包含预定义的详细匹配规则，用于验证引擎输出并支持手动扩展。当引擎推荐的规则不在预定义集合中时，系统可自动生成新规则条目。

## 可用的风格库

| 风格 ID | 名称 | 适用行业 | 信任度 | 技术感 | 极简度 |
|---------|------|---------|--------|--------|--------|
| `sera-fintech-premium` | Sera FinTech Premium | finance | 10 | 8 | 8 |
| `sera-operations-dashboard` | Sera Operations Dashboard | operations | 6 | 7 | 6 |
| `sera-saas-landing` | Sera SaaS Landing | saas | 7 | 9 | 7 |
| `sera-ai-future` | Sera AI Future | ai | 7 | 10 | 9 |
| `sera-content-platform` | Sera Content Platform | media | 8 | 6 | 7 |

## 使用方式

### CLI 调用

```bash
# 基于行业匹配
python router.py --industry ai --audience developer

# 输出 JSON 格式
python router.py --industry finance --audience trader --goal sales --json

# 媒体内容平台
python router.py --industry media --audience general --goal engagement
```

### Python 调用

```python
from style_router import match_style

profile = {
    "industry": "ai",
    "audience": "developer",
    "goal": "signup"
}
result = match_style(profile)
print(result["primary_style"])  # "sera-ai-future"
```

## 扩展指南

### 添加新风格

1. 在 `styles/registry.json` 中添加风格定义
2. 在 `rules.yaml` 中添加匹配规则
3. 在 `style-selection.json` 中添加详细规则条目
4. 运行 `python router.py --industry <new_industry>` 验证

### 调整现有规则

修改 `rules.yaml` 中的权重值即可实时调整推荐策略。权重值总和应为 100，值越大表示该风格在此场景下越优先。