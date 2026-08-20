# Sera Style Router

> 版本：1.0.0
> 用途：根据产品属性自动推荐设计风格组合

---

## 工作流程

```
Product Profile（产品属性）
    ↓
Style Router Engine
    ↓
style-selection.json 匹配
    ↓
推荐风格组合（primary + secondary + adjustments）
    ↓
Design Generator Agent 执行
```

## 输入格式

```json
{
  "product": "牛牛 AI",
  "industry": "ai",
  "emotion": "smart",
  "audience": "tech-savvy",
  "product_type": "tool"
}
```

## 输出格式

```json
{
  "recommendation": {
    "primary_style": "sera-fintech-premium",
    "weight": 0.4,
    "secondary_style": "sera-saas-landing",
    "weight": 0.3,
    "custom_adjustments": {
      "technology_level_boost": 2
    }
  }
}
```

## 路由规则

`style-selection.json` 中定义了 4 条规则：
- fintech-premium：金融产品 → sera-fintech-premium
- ai-product：AI 产品 → sera-fintech-premium + sera-saas-landing
- saas-b2b：SaaS → sera-saas-landing
- operations-dashboard：Dashboard → sera-operations-dashboard