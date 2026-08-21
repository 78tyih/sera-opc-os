# Models

> 模型管理 — AI 模型路由与配置。

## 目录结构

```
models/
├── config/             # 模型配置
├── routing/            # 模型路由规则
├── cost/               # 成本追踪
└── benchmarks/         # 模型基准测试
```

## 模型层

| 层 | 模型 | 用途 |
|----|------|------|
| 战略层 | Claude Sonnet 4 | 高管决策、产品定义、复杂分析 |
| 执行层 | GPT-4o | 市场研究、内容生成、数据分析 |
| 创意层 | Claude Sonnet 4 + Midjourney | 设计、视频、创意内容 |
| 工程层 | Claude Sonnet 4 | 代码生成、架构设计 |
| 运营层 | GPT-4o | 销售、CRM、自动化 |

## 当前状态

从 `model-router/` 迁移。保留现有配置，此目录为统一管理层。