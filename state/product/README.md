# Sera Product Factory — Product State

管理所有产品项目的当前状态

## 目录结构

```
product/
├── projects/          # 活跃项目状态
│   └── {project-name}/
│       ├── status.yaml    # 当前阶段/进度/阻塞
│       └── next-actions   # 下一步行动
├── completed/         # 已完成项目归档
└── README.md          # 本文件
```

## 状态字段

每个项目状态文件包含：

```yaml
name: {project-name}
stage: project-profile | product-analysis | market-research | persona | positioning | copywriting | product-manual | design | landing | video | growth | launch
progress: 0-100
blockers: []
next_actions: []
last_updated: {timestamp}
outputs:
  - PROJECT_PROFILE.md
  - product-analysis.md
  - market-research.md
  - PERSONA.md
  - POSITIONING.md
  - PRODUCT_MANUAL.md
```