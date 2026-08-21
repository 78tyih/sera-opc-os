# Router

> 调度大脑 — 自然语言 → 公司行动。

## 目录结构

```
router/
├── intent-parser/       # 意图解析
├── department-router/   # 部门路由
├── workflow-planner/    # 工作流规划
└── execution-manager/   # 执行管理
```

## 核心能力

输入：自然语言（"我要发布牛牛 AI"）

输出：结构化任务分配

```yaml
tasks:
  strategy:  CSO
  product:   CPO
  website:   Design
  code:      CTO
  marketing: CMO
  sales:     CRO
```

## 当前状态

从 `core/sera-agent-router/` 迁移路由逻辑到此处。
`core/` 保留引擎层逻辑，`router/` 负责调度编排。